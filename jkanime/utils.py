from bs4 import Tag
from animeflv.exception import AnimeFLVParseError


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


def parse_table(table: Tag):
    """
    Parse a given HTML table into a list of dictionaries.

    :param table (Tag): The HTML table to parse.

    :return (List[Dict[str, Tag]]): A list of dictionaries where each dictionary represents a row in the table.
    The dictionary keys are the column headers and the values are the corresponding table cells.
    """
    columns = list([x.string for x in table.thead.tr.find_all("th")])
    rows = []

    for row in table.tbody.find_all("tr"):
        values = row.find_all("td")

        if len(values) != len(columns):
            raise AnimeFLVParseError("Don't match values size with columns size")

        rows.append({h: x for h, x in zip(columns, values)})

    return rows
