"""
UDIM Utilities

Helper functions for UDIM texture tile support across Arnold nodes.
"""

import re
import os
from pathlib import Path


def process_udim_filepath(filepath, use_udim=True):
    """
    Process filepath for UDIM support.
    Converts various UDIM patterns to Arnold's <UDIM> token.

    Args:
        filepath (str): The texture file path
        use_udim (bool): Whether UDIM processing should be applied

    Returns:
        str: Processed filepath with <UDIM> token if applicable

    Supported input patterns:
        - <UDIM>: Direct Arnold format (preserved)
        - <UVTILE>: Blender's alternative format (converted)
        - 1001: Numeric UDIM tile notation (converted)

    Examples:
        >>> process_udim_filepath("texture.<UDIM>.exr")
        "texture.<UDIM>.exr"

        >>> process_udim_filepath("texture.<UVTILE>.exr")
        "texture.<UDIM>.exr"

        >>> process_udim_filepath("texture.1001.exr")
        "texture.<UDIM>.exr"

        >>> process_udim_filepath("texture_1001_diffuse.png")
        "texture_<UDIM>_diffuse.png"
    """
    if not use_udim:
        return filepath

    # Replace Blender's <UVTILE> with Arnold's <UDIM>
    filepath = filepath.replace("<UVTILE>", "<UDIM>")

    # Replace 1001 pattern (e.g., texture.1001.exr -> texture.<UDIM>.exr)
    # Match patterns like .1001. or _1001. or -1001.
    filepath = re.sub(r'([._-])1001([._-])', r'\1<UDIM>\2', filepath)

    # Also handle cases where 1001 is at the end before extension
    # e.g., texture_1001.exr -> texture_<UDIM>.exr
    filepath = re.sub(r'([._-])1001(\.[a-zA-Z0-9]+)$', r'\1<UDIM>\2', filepath)

    # If no UDIM token found but use_udim is enabled, warn user
    if "<UDIM>" not in filepath:
        print(f"Warning: UDIM enabled but no <UDIM> token found in filepath: {filepath}")

    return filepath


def detect_udim_tiles(base_filepath):
    """
    Detect available UDIM tiles for a given base filepath.

    Args:
        base_filepath (str): Path with <UDIM> token

    Returns:
        list: List of tuples (tile_number, filepath) for found tiles

    Example:
        >>> detect_udim_tiles("texture.<UDIM>.exr")
        [(1001, "texture.1001.exr"), (1002, "texture.1002.exr"), ...]
    """
    if "<UDIM>" not in base_filepath:
        return []

    directory = os.path.dirname(base_filepath)
    if not directory:
        directory = "."

    if not os.path.exists(directory):
        return []

    # Create regex pattern from filepath
    pattern_str = re.escape(base_filepath)
    pattern_str = pattern_str.replace(r"\<UDIM\>", r"(\d{4})")
    pattern = re.compile(pattern_str)

    tiles = []
    try:
        for filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            match = pattern.match(full_path)
            if match:
                tile_num = int(match.group(1))
                tiles.append((tile_num, full_path))
    except OSError:
        pass

    return sorted(tiles)


def udim_to_uv(tile_number):
    """
    Convert UDIM tile number to UV coordinates.

    Args:
        tile_number (int): UDIM tile number (e.g., 1001, 1002, 1011)

    Returns:
        tuple: (U, V) coordinates

    Examples:
        >>> udim_to_uv(1001)
        (0, 0)
        >>> udim_to_uv(1002)
        (1, 0)
        >>> udim_to_uv(1011)
        (0, 1)
    """
    offset = tile_number - 1001
    u = offset % 10
    v = offset // 10
    return (u, v)


def uv_to_udim(u, v):
    """
    Convert UV coordinates to UDIM tile number.

    Args:
        u (int): U coordinate (0-9)
        v (int): V coordinate (0-9)

    Returns:
        int: UDIM tile number

    Examples:
        >>> uv_to_udim(0, 0)
        1001
        >>> uv_to_udim(1, 0)
        1002
        >>> uv_to_udim(0, 1)
        1011
    """
    return 1001 + u + (v * 10)


def validate_udim_filepath(filepath):
    """
    Validate that a filepath is properly formatted for UDIM.

    Args:
        filepath (str): The filepath to validate

    Returns:
        tuple: (is_valid, message)

    Examples:
        >>> validate_udim_filepath("texture.<UDIM>.exr")
        (True, "Valid UDIM filepath")

        >>> validate_udim_filepath("texture.exr")
        (False, "No <UDIM> token found")
    """
    if not filepath:
        return (False, "Empty filepath")

    if "<UDIM>" not in filepath:
        return (False, "No <UDIM> token found in filepath")

    # Check for valid file extension
    ext = os.path.splitext(filepath)[1]
    if not ext:
        return (False, "No file extension found")

    valid_extensions = ['.exr', '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.tx', '.tga', '.bmp']
    if ext.lower() not in valid_extensions:
        return (False, f"Unsupported file extension: {ext}")

    # Check for multiple UDIM tokens
    if filepath.count("<UDIM>") > 1:
        return (False, "Multiple <UDIM> tokens found (only one allowed)")

    return (True, "Valid UDIM filepath")


def get_udim_range(tiles):
    """
    Get the UV range covered by a list of UDIM tiles.

    Args:
        tiles (list): List of UDIM tile numbers

    Returns:
        tuple: ((min_u, max_u), (min_v, max_v))

    Example:
        >>> get_udim_range([1001, 1002, 1011, 1012])
        ((0, 1), (0, 1))
    """
    if not tiles:
        return ((0, 0), (0, 0))

    uv_coords = [udim_to_uv(tile) for tile in tiles]
    u_coords = [uv[0] for uv in uv_coords]
    v_coords = [uv[1] for uv in uv_coords]

    return ((min(u_coords), max(u_coords)), (min(v_coords), max(v_coords)))
