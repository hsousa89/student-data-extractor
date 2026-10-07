import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl

from data_extractor import StudentFileExtractor
from data_ranges import eb021_data_ranges
from data_ranges import eb030a_data_ranges
from data_ranges import eb058f_data_ranges
from data_ranges import p072_data_ranges
from data_ranges import s07a_data_ranges
from utils import extract_data_from_file_path_name

if TYPE_CHECKING:
    from datetime import date
    from datetime import datetime
    from typing import Any

    from data_extractor import DataExtractor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MissingDataRangesError(ValueError):
    def __init__(self, file_name: str) -> None:
        super().__init__(f"No data ranges defined for file: {file_name}")


class MissingExtractorError(ValueError):
    def __init_(self, file_name: str) -> None:
        super().__init__(f"No extractor implemented for file: {file_name}")


def _define_data_ranges(file_name: str) -> dict[str, str]:
    data_range_mapping = {
        re.compile(r"p\d{1,2}.xls(?:x)?"): p072_data_ranges,
        re.compile(r"pag_\d{1,2}.xls(?:x)?"): eb021_data_ranges,
        re.compile(r"s07a?.xls(?:x)?", flags=re.IGNORECASE): s07a_data_ranges,
        re.compile(r"eb058f.xls(?:x)?", flags=re.IGNORECASE): eb058f_data_ranges,
        re.compile(r"eb030a.xls(?:x)?", flags=re.IGNORECASE): eb030a_data_ranges,
    }
    for pattern, ranges in data_range_mapping.items():
        if pattern.match(file_name):
            return ranges
    raise MissingDataRangesError(file_name)


def _get_file_paths(directory: Path) -> list[Path]:
    file_paths = []
    for path in Path(directory).iterdir():
        if path.is_dir():
            for file in path.iterdir():
                if file.is_file() and file.suffix in [".xlsx", ".xls"] and not file.name.startswith("~$"):
                    file_paths.append(file)
        if path.is_file() and path.suffix in [".xlsx", ".xls"] and not path.name.startswith("~$"):
            file_paths.append(path)
    return file_paths


def _define_extractor(file_path: Path) -> DataExtractor:
    file_name = file_path.name
    if re.match(r"p(?:ag_)?\d{1,2}.xls(?:x)?", file_name):
        ranges = _define_data_ranges(file_name)
        return StudentFileExtractor(
            file_path=file_path,
            data_ranges=ranges,
        )
    raise MissingExtractorError(file_name)


def load_student_data(file_path: Path) -> dict[str, int | float | str | bool | date | datetime]:
    extractor = _define_extractor(file_path)
    return extractor.extract_data()


def aggregate_student_data(data_folder: Path) -> dict[str, list[int | float | str | bool | date | datetime]]:
    paths = _get_file_paths(data_folder)
    keys = _define_data_ranges(paths[0].name).keys()
    aggregated_data = {"level": [], "group": []}
    aggregated_data.update({key: [] for key in keys})
    for path in paths:
        level, group, _ = extract_data_from_file_path_name("/".join(path.parts))
        data = load_student_data(path)
        aggregated_data["level"].append(level)
        aggregated_data["group"].append(group)
        for key in keys:
            aggregated_data[key].append(data.get(key))
    return aggregated_data


def student_data_to_dataframe(data_folder: Path) -> pl.DataFrame:
    return pl.DataFrame(aggregate_student_data(data_folder))


def student_data_to_csv(data_folder: Path, output_path: Path, **kwargs: dict[str, Any]) -> None:
    if not output_path.name.endswith(".csv"):
        output_path.joinpath("student_data.csv")
    df = student_data_to_dataframe(data_folder)
    if kwargs.get("cast"):
        logger.info(f"Casting columns {kwargs['cast'].keys()} to {kwargs['cast'].values()}")
        df = df.with_columns([pl.col(k).cast(v) for k, v in kwargs["cast"].items()])
    if kwargs.get("sort"):
        sort_columns = kwargs["sort"]
        logger.info(f"Sorting by: {sort_columns}")
        df = df.sort(sort_columns)
    if kwargs.get("select"):
        select_columns = kwargs["select"]
        logger.info(f"Selecting columns: {select_columns}")
        df = df.select(select_columns)
    logger.info(f"Writing {df.shape[0]} rows across {df.shape[1]} columns to file: {output_path.name}")
    df.write_csv(output_path)
