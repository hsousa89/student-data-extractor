import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def calculate_age(born: date) -> int:
    today = datetime.now().astimezone().date()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def extract_data_from_file_path_name(file_path_name: str) -> tuple[str, str, str]:
    pattern = re.compile(r"(?:.*)([7-9]|1[0-2])(?:\-)([1-7a-z])(?:.*)(?:p(?:ag_)?)(\d{1,2})(?:\.xls(?:x)?)")
    match = pattern.match(file_path_name)
    if not match:
        logger.warning(f"Could not match pattern to {file_path_name}")
        return "", "", ""
    return match.group(1), match.group(2), match.group(3)
