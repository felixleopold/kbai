# ANSI color reset code
RESET = '\033[0m'

# Ranges of color codes readable on dark background (#282828)
# Format: (start, end, step) - step determines how many colors to skip
# These ranges cover bright colors with good contrast on dark backgrounds
READABLE_COLOR_RANGES = [
    (9, 15, 1),      # Bright standard colors (all, step 1)
    (51, 231, 5),    # RGB color cube - skip every 3rd color for more distinct colors
    # (250, 255, 1)    # Light grayscale (all, step 1)
]

def _get_readable_color_count():
    """Calculate total number of readable colors from ranges."""
    count = 0
    for range_spec in READABLE_COLOR_RANGES:
        start, end, step = range_spec if len(range_spec) == 3 else (*range_spec, 1)
        # Count colors in range with step
        range_colors = len(range(start, end + 1, step))
        count += range_colors
    return count

def _get_readable_color_by_index(index):
    """Get a readable color code by index (0-based) from the ranges."""
    for range_spec in READABLE_COLOR_RANGES:
        start, end, step = range_spec if len(range_spec) == 3 else (*range_spec, 1)
        # Get colors in range with step
        range_colors = list(range(start, end + 1, step))
        range_size = len(range_colors)
        if index < range_size:
            return range_colors[index]
        index -= range_size
    # Fallback (shouldn't happen if index is valid)
    return 15

def get_set_color(item):
    """Get a consistent color for a set/list based on its content using readable colors on dark background."""
    # Convert to sorted tuple for consistent hashing
    if isinstance(item, (set, frozenset)):
        key = tuple(sorted(item))
    elif isinstance(item, (list, tuple)):
        key = tuple(sorted(item))
    else:
        key = tuple(sorted(str(item)))
    
    # Select color from readable color ranges
    total_colors = _get_readable_color_count()
    color_index = abs(hash(key)) % total_colors
    color_code = _get_readable_color_by_index(color_index)
    return f'\033[38;5;{color_code}m'

def colorize_sets(data, max_inline=5):
    """Colorize sets/lists in a collection, giving each unique set a consistent color.
    
    Args:
        data: The data to colorize (list, tuple, set, etc.)
        max_inline: Maximum number of items to display inline before switching to multi-line format
    """
    if not data:
        return str(data)
    
    # Handle collections of sets/lists (list of lists)
    if isinstance(data, (list, tuple)):
        result = []
        for item in data:
            if isinstance(item, (set, frozenset, list, tuple)):
                color = get_set_color(item)
                result.append(f"{color}{repr(item)}{RESET}")
            else:
                result.append(repr(item))
        
        # Format based on length: inline for small lists, multi-line for large ones
        if len(result) <= max_inline:
            return "[" + ", ".join(result) + "]"
        else:
            # Multi-line format with indentation
            items_str = ",\n    ".join(result)
            return "[\n    " + items_str + "\n]"
    
    # Handle single set/list
    elif isinstance(data, (set, frozenset, list, tuple)):
        color = get_set_color(data)
        return f"{color}{repr(data)}{RESET}"
    
    # Fallback for other types
    return str(data)

