import os
from pathlib import Path

import polars as pl
from dotenv import load_dotenv

from data_loader import student_data_to_csv

load_dotenv()


def main() -> None:
    data_root_folder = os.getenv("DATA_ROOT_FOLDER")
    data_input_directory = Path(data_root_folder).joinpath("input")
    data_output_directory = Path(data_root_folder).joinpath("output")
    file_output_path = data_output_directory.joinpath("student_eb021_26-27_data.csv")
    sorting_cols = ["level", "group", "name"]
    casting_cols = {"level": pl.Int8}
    student_data_to_csv(data_input_directory, file_output_path, sort=sorting_cols, cast=casting_cols)


if __name__ == "__main__":
    main()
