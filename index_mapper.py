import re


class InvalidA1NotationError(ValueError):
    def __init__(self, a1_notation: str) -> None:
        super().__init__(f"Invalid A1 notation: {a1_notation}")


def _separate_column_and_row(a1_notation: str) -> tuple[str, int]:
    """Separate the column and row from an Excel A1 notation."""
    a1_notation = a1_notation.strip().upper()
    match = re.match(r"([A-Z]+)([0-9]+)", a1_notation.strip().upper())
    if not match:
        raise InvalidA1NotationError(a1_notation)
    column, row = match.groups()
    return column, int(row)


def a1_notation_to_index(a1_notation: str) -> tuple[int, int]:
    """Convert an Excel A1 notation to a 1-based index."""
    column, row = _separate_column_and_row(a1_notation)
    index = 0

    for letter in column:
        index = index * 26 + (ord(letter) - ord("A") + 1)

    return row - 1, index - 1
