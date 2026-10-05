import os
from pathlib import Path

import pyexcel as p


def convert_xls_to_xlsx(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The file {input_file} does not exist.")

    p.save_book_as(file_name=input_file, dest_file_name=output_file)
    print(f"Converted {input_file} to {output_file}")


def convert_all_xls_in_directory_to_xlsx(directory: Path):
    for filename in os.listdir(directory):
        if filename.endswith(".xls"):
            input_path = os.path.join(directory, filename)
            output_path = os.path.join(directory, filename + "x")
            convert_xls_to_xlsx(input_path, output_path)
            os.remove(input_path)


if __name__ == "__main__":
    r2_directory = Path("./data/2R")
    a3_directory = Path("./data/3A")
    p3_directory = Path("./data/3P")
    convert_all_xls_in_directory_to_xlsx(r2_directory)
    convert_all_xls_in_directory_to_xlsx(a3_directory)
    convert_all_xls_in_directory_to_xlsx(p3_directory)
