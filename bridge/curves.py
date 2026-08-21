import bpy
import ctypes
import numpy

from .array import ArnoldArray
from .constants import BTOA_VISIBILITY
from .exportable import ArnoldNodeExportable
from . import utils as bridge_utils
from . import types as bridge_types


class ArnoldCurves(ArnoldNodeExportable):
    def __init__(self, node=None, frame_set=None):
        if node:
            super().__init__(node, frame_set)
        else:
            super().__init__("curves", frame_set)

        self.curves = None

    def __assign_shaders(self):
        materials = []

        for slot in self.datablock.material_slots:
            if slot.material:
                materials.append(slot.material)

        if not materials:
            shader = bridge_utils.get_node_by_name("BTOA_MISSING_SHADER")
            self.set_pointer("shader", shader)
            return

        # Use first material for curves
        shader = bridge_utils.get_node_by_uuid(materials[0].uuid)
        self.set_pointer("shader", shader)

        # Apply displacement if available
        for mat in materials:
            if mat.arnold.node_tree and mat.arnold.node_tree.has_displacement():
                disp_data = mat.arnold.node_tree.export_active_displacement()
                if disp_data and disp_data.type == bridge_types.ExportDataType.GROUP:
                    disp_input, disp_padding, disp_height, disp_zero, disp_autobump = disp_data.value

                    if disp_input.type == bridge_types.ExportDataType.NODE:
                        self.set_pointer("disp_map", disp_input.value)
                    if disp_padding.type == bridge_types.ExportDataType.FLOAT:
                        self.set_float("disp_padding", disp_padding.value)
                    if disp_height.type == bridge_types.ExportDataType.FLOAT:
                        self.set_float("disp_height", disp_height.value)
                    if disp_zero.type == bridge_types.ExportDataType.FLOAT:
                        self.set_float("disp_zero_value", disp_zero.value)
                    self.set_bool("disp_autobump", disp_autobump)
                    break

    def __set_visibility(self):
        data = self.curves.arnold_curves
        visibility = 0

        visibility_options = [
            data.camera,
            data.shadow,
            data.diffuse_transmission,
            data.specular_transmission,
            data.volume,
            data.diffuse_reflection,
            data.specular_reflection,
            data.sss
        ]

        for i in range(0, len(visibility_options)):
            if visibility_options[i]:
                visibility += BTOA_VISIBILITY[i]

        if (self.datablock.indirect_only_get(view_layer=self.depsgraph.view_layer_eval)
            or self.is_instance
            and self.parent.indirect_only_get(view_layer=self.depsgraph.view_layer_eval)):
            visibility -= 1

        self.set_byte("visibility", visibility)

        self.set_bool(
            "matte",
            (self.datablock.holdout_get(view_layer=self.depsgraph.view_layer_eval)
            or self.is_instance
            and self.parent is not None
            and self.parent.holdout_get(view_layer=self.depsgraph.view_layer_eval))
        )

    def __find_parent_mesh(self):
        """Find the parent mesh object that curves are attached to"""
        # Check if curves have surface_uv_map set (indicates attachment)
        if not hasattr(self.curves, 'surface_uv_map') or not self.curves.surface_uv_map:
            print("[CURVES] No surface_uv_map found")
            return None

        # Check for Surface Deform modifier pointing to a mesh
        for mod in self.datablock.modifiers:
            if mod.type == 'SURFACE_DEFORM' and mod.target:
                target_node = bridge_utils.get_node_by_uuid(mod.target.uuid)
                if target_node:
                    print(f"[CURVES] Found parent mesh via Surface Deform: {mod.target.name}")
                    return mod.target

        # Check parent object
        if self.datablock.parent and self.datablock.parent.type == 'MESH':
            print(f"[CURVES] Found parent mesh via parent: {self.datablock.parent.name}")
            return self.datablock.parent

        print("[CURVES] No parent mesh found")
        return None

    def from_datablock(self, depsgraph, datablock):
        self.depsgraph = depsgraph

        self.evaluate_datablock(datablock)
        if not self.datablock:
            return None

        # Get evaluated curves data
        self.curves = self.datablock.evaluated_get(depsgraph).data
        if not self.curves or len(self.curves.curves) == 0:
            return None

        # General settings
        sdata = depsgraph.scene.arnold
        self.set_uuid(self.parent.uuid if self.is_instance else self.datablock.uuid)
        self.set_string("name", self.datablock.name)
        self.set_float("motion_start", sdata.shutter_start)
        self.set_float("motion_end", sdata.shutter_end)

        # Curves settings
        data = self.curves.arnold_curves

        print(f"[CURVES DEBUG] Object: {self.datablock.name}")
        print(f"[CURVES DEBUG] Curve count: {len(self.curves.curves)}")
        print(f"[CURVES DEBUG] Point count: {len(self.curves.points)}")

        # Set curve mode from properties (basis is set in __apply_curve_data
        # because subdivision may override it to 'linear')
        self.set_string("mode", data.mode)
        self.set_float("min_pixel_width", data.min_pixel_width)

        # Find parent mesh for surface attachment
        parent_mesh_node = None
        if data.attach_to_surface:
            parent_mesh_node = self.__find_parent_mesh()

        # Export curve data (also sets basis on the Arnold node)
        self.__apply_curve_data(parent_mesh_node)

        # Set transformation matrix
        matrix = self.get_transform_matrix()
        mw = self.datablock.matrix_world
        print(f"[CURVES DEBUG] matrix_world location: ({mw[0][3]:.4f}, {mw[1][3]:.4f}, {mw[2][3]:.4f})")
        if sdata.enable_motion_blur:
            self.set_array("matrix", matrix)
        else:
            self.set_matrix("matrix", matrix)

        # Assign shaders and visibility
        self.__assign_shaders()
        self.__set_visibility()

        return self

    def __apply_curve_data(self, parent_mesh=None):
        curves_data = self.curves
        num_curves = len(curves_data.curves)
        num_points = len(curves_data.points)
        basis = curves_data.arnold_curves.basis
        subdivide = curves_data.arnold_curves.subdivide_curves

        # Determine if we need phantom endpoints for this basis type
        # catmull-rom and b-spline require duplicated first/last points as tangent guides
        needs_phantom_endpoints = basis in ('catmull-rom', 'b-spline')

        # Get points per curve (original counts) — vectorized via foreach_get
        orig_num_points_array = numpy.zeros(num_curves, dtype=numpy.int32)
        try:
            curves_data.curves.foreach_get("points_length", orig_num_points_array)
        except (AttributeError, TypeError):
            # Fallback for Blender versions where foreach_get isn't available on curves
            for i, curve in enumerate(curves_data.curves):
                orig_num_points_array[i] = curve.points_length
        orig_num_points_array = orig_num_points_array.astype(numpy.uint32)

        # Get point positions (object-local space)
        positions = numpy.zeros(num_points * 3, dtype=numpy.float32)
        curves_data.points.foreach_get("position", positions)
        positions = positions.reshape(-1, 3)

        # --- Read per-point radius ---
        # Blender hair curves store width in the 'radius' attribute (POINT domain).
        # We try multiple approaches for compatibility across Blender versions.
        radii = None

        # Approach 1: Read from custom attributes collection (most reliable for hair)
        if 'radius' in curves_data.attributes:
            radius_attr = curves_data.attributes['radius']
            attr_domain = radius_attr.domain  # 'POINT' or 'CURVE'
            attr_len = len(radius_attr.data)

            print(f"[CURVES] Found 'radius' attribute: domain={attr_domain}, length={attr_len}, type={radius_attr.data_type}")

            if attr_domain == 'POINT' and attr_len == num_points:
                radii = numpy.zeros(num_points, dtype=numpy.float32)
                radius_attr.data.foreach_get('value', radii)
                print(f"[CURVES] Read radius from POINT attribute: min={radii.min():.6f}, max={radii.max():.6f}, mean={radii.mean():.6f}")
                # Blender hair curves can produce negative radius values from sculpting
                # or geometry node operations. Arnold requires non-negative radii;
                # negative values get clamped to 0 internally, killing width variation.
                neg_count = int(numpy.sum(radii < 0))
                if neg_count > 0:
                    print(f"[CURVES] WARNING: {neg_count}/{num_points} radius values are negative, taking abs() to preserve variation")
                    radii = numpy.abs(radii)
            elif attr_domain == 'CURVE' and attr_len == num_curves:
                # Per-curve radius: expand to per-point using numpy.repeat (vectorized)
                per_curve_radii = numpy.zeros(num_curves, dtype=numpy.float32)
                radius_attr.data.foreach_get('value', per_curve_radii)
                radii = numpy.repeat(per_curve_radii, orig_num_points_array.astype(numpy.intp))
                print(f"[CURVES] Expanded CURVE-domain radius to per-point: min={radii.min():.6f}, max={radii.max():.6f}")
                neg_count = int(numpy.sum(radii < 0))
                if neg_count > 0:
                    print(f"[CURVES] WARNING: {neg_count} CURVE-domain radius values are negative, taking abs()")
                    radii = numpy.abs(radii)
            else:
                print(f"[CURVES] WARNING: radius attribute has unexpected domain={attr_domain} or length={attr_len} (expected {num_points} points or {num_curves} curves)")

        # Approach 2: Try built-in CurvePoint.radius
        if radii is None:
            try:
                radii = numpy.zeros(num_points, dtype=numpy.float32)
                curves_data.points.foreach_get("radius", radii)
                print(f"[CURVES] Read radius from CurvePoint.radius: min={radii.min():.6f}, max={radii.max():.6f}, mean={radii.mean():.6f}")
                neg_count = int(numpy.sum(radii < 0))
                if neg_count > 0:
                    print(f"[CURVES] WARNING: {neg_count}/{num_points} radius values are negative, taking abs()")
                    radii = numpy.abs(radii)
            except Exception as e:
                print(f"[CURVES] Could not read CurvePoint.radius: {e}")
                radii = None

        # Approach 3: Default fallback
        if radii is None or numpy.all(radii == 0):
            if radii is not None and numpy.all(radii == 0):
                print("[CURVES] All radii are zero, applying default")
            radii = numpy.full(num_points, 0.005, dtype=numpy.float32)  # 5mm default
            print("[CURVES] Using default radius: 0.005")

        # Debug: print sample data from first curve
        if num_curves > 0:
            n0 = int(orig_num_points_array[0])
            print(f"[CURVES] First curve: {n0} points")
            print(f"[CURVES]   root pos: ({positions[0][0]:.4f}, {positions[0][1]:.4f}, {positions[0][2]:.4f})")
            if n0 > 1:
                print(f"[CURVES]   tip  pos: ({positions[n0-1][0]:.4f}, {positions[n0-1][1]:.4f}, {positions[n0-1][2]:.4f})")
            print(f"[CURVES]   root radius: {radii[0]:.6f}, tip radius: {radii[n0-1]:.6f}")

        # --- Subdivide for taper-preserving export ---
        # When subdivide > 1 and basis uses spline interpolation, evaluate
        # catmull-rom/b-spline at higher resolution for smooth positions,
        # but linearly interpolate radii so taper is preserved exactly.
        # The result is exported as 'linear' basis.
        if subdivide > 1 and basis in ('catmull-rom', 'b-spline'):
            positions, radii, orig_num_points_array = self.__subdivide_curves_for_taper(
                positions, radii, orig_num_points_array, num_curves, subdivide, basis)
            num_points = int(positions.shape[0])
            # Override basis to linear — we already evaluated the spline
            basis = 'linear'
            needs_phantom_endpoints = False
            print(f"[CURVES] Subdivided for taper: {num_points} points, basis overridden to 'linear'")

        # --- Add phantom endpoints for catmull-rom / b-spline basis ---
        # Arnold uses the first and last CVs as tangent guides only;
        # the rendered curve spans from CV[1] to CV[N-2].
        # We duplicate the root and tip so the visible curve covers all original points.
        if needs_phantom_endpoints:
            # Fully vectorized phantom endpoint insertion — no Python loops.
            # For each curve we insert a copy of the first point at the start and
            # a copy of the last point at the end, giving +2 points per curve.

            # Compute cumulative offsets into the flat source array
            offsets = numpy.zeros(num_curves + 1, dtype=numpy.intp)
            numpy.cumsum(orig_num_points_array, out=offsets[1:])

            # Indices of first and last point of each curve in the original array
            first_idx = offsets[:-1].copy()                   # shape (C,)
            last_idx = offsets[1:] - 1                        # shape (C,)

            # New point count per curve (+2 for phantom endpoints)
            new_num_points_array = orig_num_points_array.astype(numpy.uint32) + 2
            total_points = int(new_num_points_array.sum())

            # Compute destination offsets
            new_offsets = numpy.zeros(num_curves + 1, dtype=numpy.intp)
            numpy.cumsum(new_num_points_array, out=new_offsets[1:])

            # Build source index mapping entirely with numpy (no Python loop)
            # Each output curve of length (n+2) maps to: [src_first, src_first..src_last, src_last]
            # We build this by:
            # 1. Create a base arange for all output points
            # 2. Subtract per-curve offsets to get local indices
            # 3. Clamp to [0, n-1] range and add source offsets

            # For each output point, determine which curve it belongs to
            curve_ids = numpy.repeat(numpy.arange(num_curves, dtype=numpy.intp),
                                     new_num_points_array.astype(numpy.intp))

            # Local index within each output curve (0-based)
            local_idx = numpy.arange(total_points, dtype=numpy.intp) - new_offsets[:-1][curve_ids]

            # Map local index to source: local 0 → 0 (phantom), local 1..n → 0..n-1, local n+1 → n-1 (phantom)
            # Subtract 1 to shift (phantom start maps to -1, original maps to 0..n-1, phantom end maps to n)
            # Then clamp to [0, n-1]
            src_local = numpy.clip(local_idx - 1, 0, (orig_num_points_array[curve_ids].astype(numpy.intp) - 1))

            # Add source curve offsets to get global source indices
            src_indices = src_local + offsets[:-1][curve_ids]

            # Gather positions and radii using the index map (single vectorized operation)
            positions = positions[src_indices]

            # For radii, extrapolate phantom values to preserve taper
            new_radii = radii[src_indices]

            # Curves with >= 3 points get extrapolated phantom radii instead of duplicated
            mask_extrap = orig_num_points_array >= 3
            if numpy.any(mask_extrap):
                ext_first = first_idx[mask_extrap]
                ext_last = last_idx[mask_extrap]
                ext_dst_start = new_offsets[:-1][mask_extrap]
                ext_dst_end = new_offsets[1:][mask_extrap] - 1

                # Extrapolate root: max(0, 2*r[0] - r[1])
                new_radii[ext_dst_start] = numpy.maximum(0.0, 2.0 * radii[ext_first] - radii[ext_first + 1])
                # Extrapolate tip: max(0, 2*r[-1] - r[-2])
                new_radii[ext_dst_end] = numpy.maximum(0.0, 2.0 * radii[ext_last] - radii[ext_last - 1])

            radii = new_radii.astype(numpy.float32)
            num_points_array = new_num_points_array

            print(f"[CURVES] Added phantom endpoints for '{basis}': {num_points} -> {total_points} points")
        else:
            total_points = num_points
            num_points_array = orig_num_points_array

        # Flatten positions to 1D and ensure C-contiguous for ctypes
        positions_flat = numpy.ascontiguousarray(positions.flatten(), dtype=numpy.float32)
        radii = numpy.ascontiguousarray(radii, dtype=numpy.float32)
        num_points_array = numpy.ascontiguousarray(num_points_array, dtype=numpy.uint32)

        # Convert to Arnold arrays
        num_points_arnold = ArnoldArray()
        num_points_arnold.convert_from_buffer(num_curves, 1, 'UINT', ctypes.c_void_p(num_points_array.ctypes.data))

        points_arnold = ArnoldArray()
        points_arnold.convert_from_buffer(total_points, 1, 'VECTOR', ctypes.c_void_p(positions_flat.ctypes.data))

        radius_arnold = ArnoldArray()
        radius_arnold.convert_from_buffer(total_points, 1, 'FLOAT', ctypes.c_void_p(radii.ctypes.data))

        # Set the final basis on the Arnold node (may have been overridden
        # from catmull-rom/b-spline to 'linear' by subdivision)
        self.set_string("basis", basis)

        # Set arrays on Arnold node
        self.set_array("num_points", num_points_arnold)
        self.set_array("points", points_arnold)
        self.set_array("radius", radius_arnold)

        # Debug: verify radius variation is preserved
        print(f"[CURVES] Radius array stats: min={radii.min():.6f}, max={radii.max():.6f}, mean={radii.mean():.6f}, std={radii.std():.6f}")
        if num_curves > 0:
            first_curve_len = int(num_points_array[0])
            first_curve_radii = radii[:first_curve_len]
            print(f"[CURVES] First curve radius range: {first_curve_radii.min():.6f} to {first_curve_radii.max():.6f}")

        # Export surface attachment data if parent mesh exists
        if parent_mesh and self.curves.arnold_curves.attach_to_surface:
            self.__export_surface_attachment(parent_mesh, num_curves)

        # Export UVs if available and enabled
        if self.curves.arnold_curves.export_uvs and hasattr(curves_data, 'surface_uv_map') and curves_data.surface_uv_map:
            try:
                if 'surface_uv_coordinate' in curves_data.attributes:
                    uv_attr = curves_data.attributes['surface_uv_coordinate']
                    uv_data = numpy.zeros(num_curves * 3, dtype=numpy.float32)
                    uv_attr.data.foreach_get('vector', uv_data)
                    uvs = uv_data.reshape(-1, 3)[:, :2].flatten().astype(numpy.float32)

                    uvs_arnold = ArnoldArray()
                    uvs_arnold.convert_from_buffer(num_curves, 1, 'VECTOR2', ctypes.c_void_p(uvs.ctypes.data))
                    self.set_array("uvs", uvs_arnold)

                    print(f"[CURVES] Exported surface UVs for {num_curves} curves")
            except Exception as e:
                print(f"[CURVES] Could not export UVs: {e}")

        # Export curve_id as uniform UINT user data.
        # Arnold's standard_hair shader uses curve_id to seed its internal
        # per-curve randomization (melanin_randomize, etc.). Without it,
        # the shader has no stable per-curve identifier and produces
        # unpredictable color variation even with melanin_randomize at 0.
        # Blender stores a stable per-curve identifier in the 'id' attribute.
        # Fall back to sequential indices if it's not available.
        if 'id' in curves_data.attributes:
            id_attr = curves_data.attributes['id']
            if id_attr.domain == 'CURVE' and len(id_attr.data) == num_curves:
                curve_ids = numpy.zeros(num_curves, dtype=numpy.int32)
                id_attr.data.foreach_get('value', curve_ids)
                curve_ids = numpy.ascontiguousarray(curve_ids.astype(numpy.uint32))
                print(f"[CURVES] Using Blender 'id' attribute for curve_id: min={curve_ids.min()}, max={curve_ids.max()}")
            else:
                curve_ids = numpy.arange(num_curves, dtype=numpy.uint32)
                print("[CURVES] Blender 'id' attribute has unexpected domain/length, using sequential curve_id")
        else:
            curve_ids = numpy.arange(num_curves, dtype=numpy.uint32)
            print("[CURVES] No Blender 'id' attribute found, using sequential curve_id")

        self.declare("curve_id", "uniform UINT")
        curve_id_arnold = ArnoldArray()
        curve_id_arnold.convert_from_buffer(num_curves, 1, 'UINT', ctypes.c_void_p(curve_ids.ctypes.data))
        self.set_array("curve_id", curve_id_arnold)
        print(f"[CURVES] Exported curve_id for {num_curves} curves")

        # Export custom attributes as Arnold user data
        self.__export_custom_attributes(curves_data, num_curves, num_points, orig_num_points_array, needs_phantom_endpoints)

        # List all available attributes for debugging
        attr_names = [a.name for a in curves_data.attributes]
        print(f"[CURVES] Available attributes: {attr_names}")
        print(f"[CURVES] Exported {num_curves} curves with {total_points} points, basis='{basis}', mode='{curves_data.arnold_curves.mode}'")

    def __export_custom_attributes(self, curves_data, num_curves, num_points, orig_num_points_array, needs_phantom_endpoints):
        """Export Blender curve custom attributes as Arnold user data.

        This makes attributes like random_value, melanin, is_flyaway, etc.
        available to user_data_* shader nodes in Arnold.

        POINT-domain attributes become 'varying' (per control-point).
        CURVE-domain attributes become 'uniform' (per curve).
        For catmull-rom/b-spline, POINT-domain data gets phantom endpoints
        to match the padded point arrays.
        """
        # Built-in attributes already handled elsewhere.
        SKIP_ATTRS = {'position', 'radius', 'curve_type', 'nurbs_order',
                      'nurbs_weight', 'handle_type_left', 'handle_type_right',
                      'handle_left', 'handle_right', 'surface_uv_coordinate',
                      'curve_index', 'resolution',
                      # Blender internals not useful for shading
                      'selection', 'id', 'color'}

        # Attributes that standard_hair auto-reads from geometry user data.
        # These MUST only be exported as uniform (per-curve). If Blender
        # stores them in the POINT domain, exporting them as varying causes
        # per-point color variation along each strand (banding). When in the
        # CURVE domain they correctly give one value per hair strand.
        CURVE_DOMAIN_ONLY_ATTRS = {'melanin', 'melanin_redness', 'melanin_randomize'}

        exported_count = 0

        for attr in curves_data.attributes:
            if attr.name in SKIP_ATTRS or attr.name.startswith('.'):
                continue

            domain = attr.domain       # 'POINT' or 'CURVE'

            # standard_hair auto-reads these from geometry; only allow
            # per-curve (uniform) export to avoid per-point banding.
            if attr.name in CURVE_DOMAIN_ONLY_ATTRS and domain != 'CURVE':
                continue

            data_type = attr.data_type # 'FLOAT', 'INT', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'BYTE_COLOR', 'BOOLEAN', etc.
            attr_len = len(attr.data)

            if attr_len == 0:
                continue

            # Only handle POINT and CURVE domains
            if domain == 'POINT':
                scope = 'varying'
                expected_len = num_points
            elif domain == 'CURVE':
                scope = 'uniform'
                expected_len = num_curves
            else:
                continue

            if attr_len != expected_len:
                continue

            try:
                if data_type == 'FLOAT':
                    values = numpy.zeros(attr_len, dtype=numpy.float32)
                    attr.data.foreach_get('value', values)

                    if domain == 'POINT' and needs_phantom_endpoints:
                        values = self.__pad_point_attribute(values, num_curves, orig_num_points_array)

                    self.declare(attr.name, f"{scope} FLOAT")
                    arr = ArnoldArray()
                    arr.convert_from_buffer(len(values), 1, 'FLOAT',
                                            ctypes.c_void_p(values.ctypes.data))
                    self.set_array(attr.name, arr)

                elif data_type == 'INT':
                    values = numpy.zeros(attr_len, dtype=numpy.int32)
                    attr.data.foreach_get('value', values)

                    if domain == 'POINT' and needs_phantom_endpoints:
                        values = self.__pad_point_attribute(values, num_curves, orig_num_points_array)

                    values = numpy.ascontiguousarray(values, dtype=numpy.uint32)
                    self.declare(attr.name, f"{scope} UINT")
                    arr = ArnoldArray()
                    arr.convert_from_buffer(len(values), 1, 'UINT',
                                            ctypes.c_void_p(values.ctypes.data))
                    self.set_array(attr.name, arr)

                elif data_type == 'BOOLEAN':
                    values = numpy.zeros(attr_len, dtype=numpy.bool_)
                    attr.data.foreach_get('value', values)
                    float_values = values.astype(numpy.float32)

                    if domain == 'POINT' and needs_phantom_endpoints:
                        float_values = self.__pad_point_attribute(float_values, num_curves, orig_num_points_array)

                    self.declare(attr.name, f"{scope} FLOAT")
                    arr = ArnoldArray()
                    arr.convert_from_buffer(len(float_values), 1, 'FLOAT',
                                            ctypes.c_void_p(float_values.ctypes.data))
                    self.set_array(attr.name, arr)

                elif data_type in ('FLOAT_COLOR', 'BYTE_COLOR'):
                    values = numpy.zeros(attr_len * 4, dtype=numpy.float32)
                    attr.data.foreach_get('color', values)

                    if domain == 'POINT' and needs_phantom_endpoints:
                        values = values.reshape(-1, 4)
                        values = self.__pad_point_attribute_2d(values, num_curves, orig_num_points_array)
                        values = values.flatten()

                    self.declare(attr.name, f"{scope} RGBA")
                    arr = ArnoldArray()
                    arr.convert_from_buffer(len(values) // 4, 1, 'RGBA',
                                            ctypes.c_void_p(values.ctypes.data))
                    self.set_array(attr.name, arr)

                elif data_type == 'FLOAT_VECTOR':
                    values = numpy.zeros(attr_len * 3, dtype=numpy.float32)
                    attr.data.foreach_get('vector', values)

                    if domain == 'POINT' and needs_phantom_endpoints:
                        values = values.reshape(-1, 3)
                        values = self.__pad_point_attribute_2d(values, num_curves, orig_num_points_array)
                        values = values.flatten()

                    self.declare(attr.name, f"{scope} VECTOR")
                    arr = ArnoldArray()
                    arr.convert_from_buffer(len(values) // 3, 1, 'VECTOR',
                                            ctypes.c_void_p(values.ctypes.data))
                    self.set_array(attr.name, arr)

                else:
                    continue

                exported_count += 1
                print(f"[CURVES] Exported user data '{attr.name}': domain={domain}, type={data_type}, count={attr_len}")

            except Exception as e:
                print(f"[CURVES] Could not export attribute '{attr.name}': {e}")

        if exported_count > 0:
            print(f"[CURVES] Exported {exported_count} custom attributes as Arnold user data")

    def __pad_point_attribute(self, values, num_curves, orig_num_points_array):
        """Pad a 1D per-point attribute array with phantom endpoints to match catmull-rom/b-spline.
        Fully vectorized using numpy index gather."""
        offsets = numpy.zeros(num_curves + 1, dtype=numpy.intp)
        numpy.cumsum(orig_num_points_array, out=offsets[1:])

        new_counts = orig_num_points_array.astype(numpy.intp) + 2
        # Curves with < 2 points don't get padded
        short_mask = orig_num_points_array < 2
        new_counts[short_mask] = orig_num_points_array[short_mask]

        total_out = int(new_counts.sum())
        new_offsets = numpy.zeros(num_curves + 1, dtype=numpy.intp)
        numpy.cumsum(new_counts, out=new_offsets[1:])

        # Determine curve ownership for each output point
        curve_ids = numpy.repeat(numpy.arange(num_curves, dtype=numpy.intp), new_counts)
        local_idx = numpy.arange(total_out, dtype=numpy.intp) - new_offsets[:-1][curve_ids]

        # For short curves (< 2 pts), local maps directly; for others, shift by -1 and clamp
        is_long = ~short_mask
        max_local = orig_num_points_array[curve_ids].astype(numpy.intp) - 1

        # Default: direct mapping for short curves
        src_local = local_idx.copy()
        # For long curves: clamp(local - 1, 0, n-1)
        long_mask_pts = is_long[curve_ids]
        src_local[long_mask_pts] = numpy.clip(local_idx[long_mask_pts] - 1, 0, max_local[long_mask_pts])

        src_indices = src_local + offsets[:-1][curve_ids]
        return numpy.ascontiguousarray(values[src_indices], dtype=values.dtype)

    def __pad_point_attribute_2d(self, values, num_curves, orig_num_points_array):
        """Pad a 2D per-point attribute array (N, C) with phantom endpoints.
        Fully vectorized using numpy index gather."""
        offsets = numpy.zeros(num_curves + 1, dtype=numpy.intp)
        numpy.cumsum(orig_num_points_array, out=offsets[1:])

        new_counts = orig_num_points_array.astype(numpy.intp) + 2
        short_mask = orig_num_points_array < 2
        new_counts[short_mask] = orig_num_points_array[short_mask]

        total_out = int(new_counts.sum())
        new_offsets = numpy.zeros(num_curves + 1, dtype=numpy.intp)
        numpy.cumsum(new_counts, out=new_offsets[1:])

        curve_ids = numpy.repeat(numpy.arange(num_curves, dtype=numpy.intp), new_counts)
        local_idx = numpy.arange(total_out, dtype=numpy.intp) - new_offsets[:-1][curve_ids]

        is_long = ~short_mask
        max_local = orig_num_points_array[curve_ids].astype(numpy.intp) - 1

        src_local = local_idx.copy()
        long_mask_pts = is_long[curve_ids]
        src_local[long_mask_pts] = numpy.clip(local_idx[long_mask_pts] - 1, 0, max_local[long_mask_pts])

        src_indices = src_local + offsets[:-1][curve_ids]
        return numpy.ascontiguousarray(values[src_indices], dtype=values.dtype)

    def __subdivide_curves_for_taper(self, positions, radii, orig_num_points_array,
                                     num_curves, subdivide, basis):
        """Subdivide curves using catmull-rom evaluation for smooth positions,
        linear interpolation for radii, preserving exact taper.

        Fully vectorized with numpy — no Python loops for the common case
        where all curves have the same CV count (FollicleFX always does this).

        For each curve with N points and (N-1) spans, this produces
        (N-1)*subdivide + 1 output points per curve.
        """
        cv_count = int(orig_num_points_array[0])
        uniform = numpy.all(orig_num_points_array == cv_count)

        if not uniform or cv_count < 2:
            # Rare fallback for variable CV counts
            return self.__subdivide_curves_slow(
                positions, radii, orig_num_points_array, num_curves, subdivide)

        # === FAST VECTORIZED PATH (no Python loops) ===
        n = cv_count
        num_segs = n - 1

        # Reshape to (C, N, 3) and (C, N)
        pos = positions.reshape(num_curves, n, 3)
        rad = radii.reshape(num_curves, n)

        # Build index arrays for P0, P1, P2, P3 across all segments
        seg_idx = numpy.arange(num_segs)
        p0_idx = numpy.maximum(seg_idx - 1, 0)
        p1_idx = seg_idx
        p2_idx = seg_idx + 1
        p3_idx = numpy.minimum(seg_idx + 2, n - 1)

        # Gather control points: (C, S, 3) and radii: (C, S)
        P0 = pos[:, p0_idx, :]
        P1 = pos[:, p1_idx, :]
        P2 = pos[:, p2_idx, :]
        P3 = pos[:, p3_idx, :]
        R1 = rad[:, p1_idx]
        R2 = rad[:, p2_idx]

        # t values: (T,) where T = subdivide
        t = (numpy.arange(subdivide, dtype=numpy.float32) / subdivide)
        t2 = t * t
        t3 = t2 * t

        # Broadcast to (C, S, T, 3) for positions
        P0 = P0[:, :, numpy.newaxis, :]
        P1 = P1[:, :, numpy.newaxis, :]
        P2 = P2[:, :, numpy.newaxis, :]
        P3 = P3[:, :, numpy.newaxis, :]
        te  = t[numpy.newaxis, numpy.newaxis, :, numpy.newaxis]
        t2e = t2[numpy.newaxis, numpy.newaxis, :, numpy.newaxis]
        t3e = t3[numpy.newaxis, numpy.newaxis, :, numpy.newaxis]

        # Catmull-rom: all curves × all segments × all t-values at once
        out_pos = (0.5 * (
            2.0 * P1 +
            (-P0 + P2) * te +
            (2.0 * P0 - 5.0 * P1 + 4.0 * P2 - P3) * t2e +
            (-P0 + 3.0 * P1 - 3.0 * P2 + P3) * t3e
        )).astype(numpy.float32)

        # Linear radius: (C, S, T)
        R1 = R1[:, :, numpy.newaxis]
        R2 = R2[:, :, numpy.newaxis]
        t_rad = t[numpy.newaxis, numpy.newaxis, :]
        out_rad = (R1 + (R2 - R1) * t_rad).astype(numpy.float32)

        # Reshape: (C, S*T, 3) and (C, S*T)
        out_pos = out_pos.reshape(num_curves, num_segs * subdivide, 3)
        out_rad = out_rad.reshape(num_curves, num_segs * subdivide)

        # Append the final endpoint of each curve
        out_pos = numpy.concatenate([out_pos, pos[:, -1:, :]], axis=1)
        out_rad = numpy.concatenate([out_rad, rad[:, -1:]], axis=1)

        # Output counts
        out_cv = num_segs * subdivide + 1
        new_num_points = numpy.full(num_curves, out_cv, dtype=numpy.uint32)

        return (
            numpy.ascontiguousarray(out_pos.reshape(-1, 3)),
            numpy.ascontiguousarray(out_rad.flatten()),
            new_num_points
        )

    def __subdivide_curves_slow(self, positions, radii, orig_num_points_array,
                                num_curves, subdivide):
        """Fallback subdivision for non-uniform CV counts (rare)."""
        new_positions_list = []
        new_radii_list = []
        new_num_points = numpy.zeros(num_curves, dtype=numpy.uint32)

        offset = 0
        for ci in range(num_curves):
            n = int(orig_num_points_array[ci])
            curve_pos = positions[offset:offset + n]
            curve_rad = radii[offset:offset + n]
            offset += n

            if n < 2:
                new_positions_list.append(curve_pos)
                new_radii_list.append(curve_rad)
                new_num_points[ci] = n
                continue

            out_count = (n - 1) * subdivide + 1
            out_pos = numpy.zeros((out_count, 3), dtype=numpy.float32)
            out_rad = numpy.zeros(out_count, dtype=numpy.float32)

            idx = 0
            for seg in range(n - 1):
                P0 = curve_pos[max(seg - 1, 0)]
                P1 = curve_pos[seg]
                P2 = curve_pos[min(seg + 1, n - 1)]
                P3 = curve_pos[min(seg + 2, n - 1)]
                R1 = curve_rad[seg]
                R2 = curve_rad[min(seg + 1, n - 1)]

                steps = subdivide if seg < n - 2 else subdivide + 1
                for si in range(steps):
                    t = si / subdivide
                    t2 = t * t
                    t3 = t2 * t
                    out_pos[idx] = 0.5 * (
                        (2.0 * P1) + (-P0 + P2) * t +
                        (2.0 * P0 - 5.0 * P1 + 4.0 * P2 - P3) * t2 +
                        (-P0 + 3.0 * P1 - 3.0 * P2 + P3) * t3)
                    out_rad[idx] = R1 + (R2 - R1) * t
                    idx += 1

            new_positions_list.append(out_pos[:idx])
            new_radii_list.append(out_rad[:idx])
            new_num_points[ci] = idx

        return (
            numpy.concatenate(new_positions_list),
            numpy.concatenate(new_radii_list),
            new_num_points
        )

    def __export_surface_attachment(self, parent_mesh, num_curves):
        """Export barycentric coordinates and mesh reference for surface attachment"""
        try:
            curves_data = self.curves

            # Get the parent mesh Arnold node
            parent_node = bridge_utils.get_node_by_uuid(parent_mesh.uuid)
            if not parent_node:
                print("[CURVES] Parent mesh Arnold node not found")
                return

            # Check for curve_index attribute (maps to triangle on surface)
            if 'curve_index' in curves_data.attributes:
                # Get triangle indices
                curve_index_attr = curves_data.attributes['curve_index']
                triangle_indices = numpy.zeros(num_curves, dtype=numpy.uint32)
                curve_index_attr.data.foreach_get('value', triangle_indices)

                # Export as orientframe_index (tells Arnold which triangle each curve is on)
                orientframe_index_arnold = ArnoldArray()
                orientframe_index_arnold.convert_from_buffer(num_curves, 1, 'UINT', ctypes.c_void_p(triangle_indices.ctypes.data))
                self.set_array("orientframe_index", orientframe_index_arnold)

                print("[CURVES] Exported orientframe_index for surface attachment")

            # Get barycentric coordinates if available
            if 'surface_uv_coordinate' in curves_data.attributes:
                uv_attr = curves_data.attributes['surface_uv_coordinate']
                uv_data = numpy.zeros(num_curves * 3, dtype=numpy.float32)
                uv_attr.data.foreach_get('vector', uv_data)

                # UV coordinates can be used as barycentric coordinates (u, v, 1-u-v)
                bary_coords = uv_data.reshape(-1, 3).astype(numpy.float32)

                # Export as orientframe (barycentric coordinates on triangle)
                orientframe_arnold = ArnoldArray()
                orientframe_arnold.convert_from_buffer(num_curves, 1, 'VECTOR', ctypes.c_void_p(bary_coords.ctypes.data))
                self.set_array("orientframe", orientframe_arnold)

                print("[CURVES] Exported orientframe (barycentric coords) for surface attachment")

            # Set the parent mesh reference
            self.set_pointer("orientframe_geometry", parent_node)
            print(f"[CURVES] Linked curves to parent mesh: {parent_mesh.name}")

        except Exception as e:
            print(f"[CURVES] Error exporting surface attachment: {e}")
            import traceback
            traceback.print_exc()
