def round_floats(obj, precision=4):
    """Recursively round all float values in nested data structures.

    This ensures cross-platform consistency in regression tests,
    since floating-point results from image processing (OpenCV, etc.)
    can vary slightly across OS/architecture combinations.
    """
    if isinstance(obj, float):
        return round(obj, precision)
    elif isinstance(obj, dict):
        return {k: round_floats(v, precision) for k, v in obj.items()}
    elif hasattr(obj, '_asdict'):
        # Handle named tuples — must be checked before plain tuple
        d = obj._asdict()
        return {k: round_floats(v, precision) for k, v in d.items()}
    elif isinstance(obj, (list, tuple)):
        rounded = [round_floats(item, precision) for item in obj]
        return type(obj)(rounded) if isinstance(obj, tuple) else rounded
    return obj


def remove_points(obj):
    if isinstance(obj, dict):
        return {k: remove_points(v) for k, v in obj.items() if k != "points"}
    elif hasattr(obj, '_asdict'):
        return remove_points(obj._asdict())
    elif isinstance(obj, (list, tuple)):
        cleaned = [remove_points(item) for item in obj]
        return type(obj)(cleaned) if isinstance(obj, tuple) else cleaned
    return obj
