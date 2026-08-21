import bpy
node = bpy.context.object.active_material.arnold.node_tree.get_output_node().inputs["Surface"].links[0].from_node

# OpenPBR Plastic preset
node.geometry_thin_walled = False
node.caustics = False

# Base - colored plastic
node.inputs["base_weight"].default_value = 1.0
node.inputs["base_color"].default_value = (0.8, 0.2, 0.2)
node.inputs["base_metalness"].default_value = 0.0
node.inputs["base_diffuse_roughness"].default_value = 0.0

# Specular - glossy plastic
node.inputs["specular_weight"].default_value = 1.0
node.inputs["specular_color"].default_value = (1.0, 1.0, 1.0)
node.inputs["specular_roughness"].default_value = 0.2
node.inputs["specular_roughness_anisotropy"].default_value = 0.0
node.inputs["specular_ior"].default_value = 1.5

# Transmission - disabled
node.inputs["transmission_weight"].default_value = 0.0

# Subsurface - slight subsurface for plastic
node.inputs["subsurface_weight"].default_value = 0.3
node.inputs["subsurface_color"].default_value = (0.8, 0.2, 0.2)
node.inputs["subsurface_radius"].default_value = 0.5
node.inputs["subsurface_radius_scale"].default_value = (1.0, 0.5, 0.25)
node.inputs["subsurface_scatter_anisotropy"].default_value = 0.0

# Coat - disabled
node.inputs["coat_weight"].default_value = 0.0

# Fuzz - disabled
node.inputs["fuzz_weight"].default_value = 0.0

# Thin Film - disabled
node.inputs["thin_film_weight"].default_value = 0.0

# Emission - disabled
node.inputs["emission_luminance"].default_value = 0.0

# Geometry
node.inputs["geometry_opacity"].default_value = 1.0
