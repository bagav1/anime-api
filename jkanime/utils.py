
def removeprefix(str: str, prefix: str) -> str:
    """
    Remove the prefix of a given string if it contains that
    prefix for compatability with Python >3.9

    :param _str: string to remove prefix from.
    :param episode: prefix to remove from the string.
    :rtype: str
    """

    if type(str) is type(prefix):
        if str.startswith(prefix):
            return str[len(prefix) :]
        else:
            return str[:]


def safe_strip(text: str) -> str:
    """
    Removes leading and trailing whitespace from a given string.

    :param text (str): The string to strip.

    :return (str): The stripped string, or an empty string if the input is None.
    """
    return text.strip() if text is not None else ""
