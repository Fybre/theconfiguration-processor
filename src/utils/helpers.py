"""Utility functions for the configuration processor."""

import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any
from datetime import datetime


def get_text_from_tstr(element: Optional[ET.Element], lang_code: int = 1033) -> str:
    """
    Extract text from a TStr (translatable string) element.

    The TStr format is:
    <TStr>
        <T>
            <L>1033</L>  <!-- Language code -->
            <S>Text</S>   <!-- String value -->
        </T>
    </TStr>

    Args:
        element: The TStr element or its parent containing TStr
        lang_code: The language code to extract (default: 1033 for English)

    Returns:
        The text string, or empty string if not found
    """
    if element is None:
        return ""

    # If element itself is TStr, use it directly
    if element.tag == "TStr":
        tstr = element
    else:
        # Look for TStr child
        tstr = element.find("TStr")

    if tstr is None:
        # Try to get direct text content
        if element.text:
            return element.text.strip()
        return ""

    # Look for translation with matching language code
    for t_elem in tstr.findall("T"):
        l_elem = t_elem.find("L")
        s_elem = t_elem.find("S")
        if l_elem is not None and s_elem is not None:
            if l_elem.text == str(lang_code):
                return s_elem.text or ""

    # If specific language not found, return first available
    first_t = tstr.find("T")
    if first_t is not None:
        s_elem = first_t.find("S")
        if s_elem is not None:
            return s_elem.text or ""

    return ""


def get_element_text(element: Optional[ET.Element], default: str = "") -> str:
    """Get text content from an element, returning default if None."""
    if element is None:
        return default
    return element.text or default


def get_element_int(element: Optional[ET.Element], default: int = 0) -> int:
    """Get integer content from an element, returning default if None."""
    if element is None:
        return default
    try:
        return int(element.text or default)
    except (ValueError, TypeError):
        return default


def get_element_bool(element: Optional[ET.Element], default: bool = False) -> bool:
    """Get boolean content from an element, returning default if None."""
    if element is None:
        return default
    text = (element.text or "").strip().lower()
    if text in ("1", "true", "yes"):
        return True
    if text in ("0", "false", "no"):
        return False
    return default


def decode_flags(flag_table: Dict[int, str], value: int) -> List[str]:
    """
    Decode a bitmask value into a list of flag names.

    Args:
        flag_table: Dictionary mapping flag values to names
        value: The bitmask value to decode

    Returns:
        List of flag names that are set
    """
    flags = []
    for flag_value, flag_name in sorted(flag_table.items()):
        if value & flag_value:
            flags.append(flag_name)
    return flags


def format_date(date_str: str) -> str:
    """
    Format a Therefore date string into a readable format.

    Therefore dates are typically in format: YYYYMMDDHHMMSSMMM
    or YYYYMMDD

    Args:
        date_str: The date string from Therefore

    Returns:
        Formatted date string
    """
    if not date_str or date_str == "0":
        return ""

    try:
        # Try full datetime format: YYYYMMDDHHMMSSMMM
        if len(date_str) >= 14:
            dt = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        # Try date only format: YYYYMMDD
        elif len(date_str) >= 8:
            dt = datetime.strptime(date_str[:8], "%Y%m%d")
            return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    return date_str


def format_permission(permission: int) -> str:
    """Format a permission value as hex and decimal."""
    return f"0x{permission:X} ({permission})"


def escape_html(text: str) -> str:
    """Escape special HTML characters in text."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length, adding suffix if truncated."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    import re
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(" ", "-")
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    # Remove leading/trailing hyphens
    return slug.strip("-")


def build_tree_structure(items: List[Any], parent_attr: str = "parent_no",
                         id_attr: str = "folder_no") -> List[Any]:
    """
    Build a tree structure from a flat list of items.

    Args:
        items: List of items with parent reference attribute
        parent_attr: Name of the attribute containing parent ID
        id_attr: Name of the attribute containing item ID

    Returns:
        List of root items with children populated
    """
    # Create lookup by ID
    item_map = {}
    for item in items:
        item_id = getattr(item, id_attr)
        item_map[item_id] = item
        # Ensure children list exists
        if not hasattr(item, "children"):
            item.children = []
        else:
            item.children = []

    # Build tree
    roots = []
    for item in items:
        parent_id = getattr(item, parent_attr)
        if parent_id is None or parent_id not in item_map:
            roots.append(item)
        else:
            parent = item_map[parent_id]
            parent.children.append(item)

    return roots


def format_file_size(size_bytes: int) -> str:
    """Format a file size in bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def get_nested_element_text(element: ET.Element, path: str, default: str = "") -> str:
    """
    Get text from a nested element using a path.

    Args:
        element: The root element
        path: Path to the element (e.g., "Name/TStr/T/S")
        default: Default value if not found

    Returns:
        The text content or default
    """
    current = element
    for part in path.split("/"):
        if current is None:
            return default
        current = current.find(part)

    if current is not None and current.text:
        return current.text
    return default
