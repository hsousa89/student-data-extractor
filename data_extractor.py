from abc import ABC
from abc import abstractmethod
from datetime import date
from datetime import datetime
from typing import TYPE_CHECKING

from python_calamine import CalamineWorkbook

if TYPE_CHECKING:
    from pathlib import Path

from dotenv import load_dotenv

from data_ranges import eb021_data_ranges
from data_ranges import eb030a_data_ranges
from index_mapper import a1_notation_to_index
from student import ASE
from student import Gender
from student import Student

load_dotenv()


def calculate_age(born: date) -> int:
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def convert_to_date_object(date_str: str) -> date:
    return datetime.strptime(date_str, "%d-%m-%Y").date()


class MissingValueError(ValueError):
    def __init__(self, key: str, cell: str, file_path: Path):
        super().__init__(f"Missing value for {key} on {cell} in file {file_path}")


class DataExtractor(ABC):
    @abstractmethod
    def extract_data(self): ...


class StudentFileExtractor(DataExtractor):
    def __init__(
        self,
        file_path: Path,
        data_ranges: dict[str, str] = eb021_data_ranges,
    ):
        self.file_path = file_path
        self.data_ranges = data_ranges

    def _load_workbook_to_python(self) -> list[list[int | float | str | bool | date | datetime]]:
        wb = CalamineWorkbook(self.file_path)
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
        return value

    def extract_data(self) -> Student:
        raw_data = self._load_workbook_to_python()
        data = {}
        for key, cell in self.data_ranges.items():
            cell_index = a1_notation_to_index(cell)
            value = raw_data[cell_index[0]][cell_index[1]]
            if not value and key not in {"bdate", "cc_emission_date", "cc_validity_date"}:
                raise MissingValueError(key, cell, self.file_path)
            value = value.split(":")[1].strip() if ":" in value else value.strip()
            value = self._convert_cell_value(key, value)
            data[key] = value
        data["age"] = calculate_age(data["bdate"])
        data.pop("school_year", None)
        return Student(**data)


""" class StudentListExtractor(DataExtractor):
    def __init__(
        self,
        file_path: Path,
        data_ranges: dict[str, str] = eb030a_data_ranges,
    ):
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
