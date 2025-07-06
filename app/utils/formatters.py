def capitalize_first(s: str) -> str:
    """
    Capitalizes the first letter of a given string.
    Returns an empty string if the input is empty.
    """
    if not s:
        return ""
    return s[0].upper() + s[1:]