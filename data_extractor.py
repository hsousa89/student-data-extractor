import logging
from abc import ABC
from abc import abstractmethod
from datetime import date
from datetime import datetime
from typing import TYPE_CHECKING

from python_calamine import CalamineWorkbook

if TYPE_CHECKING:
    from pathlib import Path

# from data_ranges import eb030a_data_ranges
from data_ranges import eb021_data_ranges
from index_mapper import a1_notation_to_index
from student import ASE
from student import Gender
from student import Student
from utils import calculate_age

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def convert_to_date_object(date_str: str) -> date:
    day, month, year = map(int, date_str.split("-"))
    return date(year, month, day)


class MissingValueError(ValueError):
    def __init__(self, key: str, cell: str, file_path: Path) -> None:
        super().__init__(f"Missing value for {key} on {cell} in file {file_path}")


class DataExtractor(ABC):
    @abstractmethod
    def extract_data(self) -> dict[str, int | float | str | bool | date | datetime]: ...


class StudentFileExtractor(DataExtractor):
    def __init__(
        self,
        file_path: Path,
        data_ranges: dict[str, str] = eb021_data_ranges,
    ) -> None:
        self.file_path = file_path
        self.data_ranges = data_ranges

    def _load_workbook_to_python(self) -> list[list[int | float | str | bool | date | datetime]]:
        wb = CalamineWorkbook.from_path(self.file_path)
        logger.info(f"Extracting data from {self.file_path}.")
        return wb.get_sheet_by_index(0).to_python(skip_empty_area=False)

    def _convert_cell_value(self, key: str, value: str) -> int | float | str | bool | date | datetime:
        if key in {"bdate", "cc_emission_date", "cc_validity_date"}:
            return None if not value else convert_to_date_object(value)
        if key in {
            "special_education_needs",
            "computer_at_home",
            "internet_at_home",
        }:
            return value.lower() == "sim"
        if key == "gender" and value.lower() == "masculino":
            return Gender.MALE
        if key == "gender" and value.lower() == "feminino":
            return Gender.FEMALE
        if key == "ase" and value.lower() in {"a", "b", "c"}:
            return ASE(value)
        if key == "guardian_relation":
            value = value.split("-", maxsplit=1)[0].strip()
        if "address" not in key and ":" in value:
            value = value.split(":")[1].strip()
        return value.strip()

    def extract_data(self) -> dict[str, int | float | str | bool | date | datetime]:
        not_null_keys = {
            "school_year",
            "process_no",
            "name",
            "bdate",
            "gender",
            "special_education_needs",
            "guardian_relation",
            "guardian_name",
        }
        raw_data = self._load_workbook_to_python()
        max_row = len(raw_data)
        data = {}
        for key, cell in self.data_ranges.items():
            row, column = a1_notation_to_index(cell)
            try:
                value = raw_data[row][column]
            except IndexError:
                logger.warning(f"Row: {row} is not within file's range! Using row: {row - 1} instead.")
                try:
                    value = raw_data[row - 1][column]
                except IndexError:
                    logger.warning(f"Row: {row} is not within file's range! Using row: {row - 2} instead.")
                    value = raw_data[row - 2][column]
            if key.startswith("guardian") and not value and (row + 1 < max_row):
                logger.warning(f"No {key} foound on {cell}! Using row: {row + 1} instead.")
                value = raw_data[row + 1][column]
            if key.startswith("guardian") and not value and (row + 2 < max_row):
                logger.warning(f"No {key} foound on {cell}! Using row: {row + 2} instead.")
                value = raw_data[row + 2][column]
            if key.startswith("guardian") and not value:
                logger.warning(f"No {key} foound on {cell}! Using row: {row - 1} instead.")
                value = raw_data[row - 1][column]
            if key.startswith("guardian") and not value:
                logger.warning(f"No {key} foound on {cell}! Using row: {row - 2} instead.")
                value = raw_data[row - 2][column]
            if not value and key in not_null_keys:
                raise MissingValueError(key, cell, self.file_path)
            value = self._convert_cell_value(key, value)
            data[key] = value
        data["age"] = calculate_age(data["bdate"])
        return data

    def data_to_student(self, data: dict[str, int | float | str | bool | date | datetime]) -> Student:
        data = self.extract_data()
        data.pop("school_year", None)
        return Student(**data)


""" class StudentListExtractor(DataExtractor):
    def __init__(
        self,
        file_path: Path,
        data_ranges: dict[str, str] = eb030a_data_ranges,
    ) -> None:
        self.file_path = file_path
        self.data_ranges = data_ranges

    def extract_data(self) -> dict[str, list[str]]:
        wb = load_workbook(filename=self.file_path)
        ws = wb.active
        school_year = ws[self.data_ranges["school_year"]].value.strip().split("\n")[0]
        group = ws[self.data_ranges["group"]].value.strip().split("\n")[1]
        dt = ws[self.data_ranges["dt"]].value.strip()
        headers_map = {
            "Nº MATR".lower(): "student_number",
            "Nº MATRIC".lower(): "student_number",
            "Nº PROC".lower(): "process_no",
            "NOME".lower(): "name",
            "idade": "age",
            "sit": "situation",
            "ing": "english_enrollment",
            "ING1".lower(): "english_enrollment",
        }
        headers = [
            headers_map.get(
                str(cell.value).lower().replace("\n", "").replace(".", ""),
                str(cell.value).lower().replace("\n", "").replace(".", "") if cell.value else None,
            )
            for cell in ws[self.data_ranges["headers"]][0]
        ]

        data = {
            "school_year": [],
            "group": [],
            "dt": [],
        }
        for row in ws[self.data_ranges["students"]]:
            if row[0].value and row[-1].value:
                data["school_year"].append(school_year)
                data["group"].append(group)
                data["dt"].append(dt)
                for i, cell in enumerate(row):
                    if not cell.value:
                        value = None
                    elif headers[i] in ("english_enrollment", "situation") and str(cell.value).lower() == "x":
                        value = True
                    elif headers[i] == "student_number" and cell.value:
                        value = f"{int(cell.value):02d}"
                    else:
                        value = str(cell.value).strip()
                    if headers[i]:
                        if data.get(headers[i]):
                            data[headers[i]].append(value)
                        else:
                            data[headers[i]] = [value]
        return data """
