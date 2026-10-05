from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


def calculate_age(born: date) -> int:
    today = datetime.now().astimezone().date()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
