def prompt_yes_no(msg: str, default: bool = True) -> bool:
    """
    Prompt the user for a yes/no response.

    Args:
        msg (str): The message to display.
        default (bool): The default if user presses enter.

    Returns:
        bool: True if user says yes, False otherwise.
    """
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{msg} {suffix}: ").strip().lower()
    if not response:
        return default
    return response.startswith("y")


def prompt_input(msg: str, default: str = "") -> str:
    """
    Prompt user for string input with optional default.

    Args:
        msg (str): The message to display.
        default (str): Default value to use if no input.

    Returns:
        str: User input or default.
    """
    suffix = f" (default: {default})" if default else ""
    response = input(f"{msg}{suffix}: ").strip()
    return response or default