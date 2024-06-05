""" Basic utility functions. """

from typing import List, Dict, Union
from pathlib import Path
import json
import json5
import time

import yaml

from loguru import logger


def validate_path(
    path: str,
    check_for_dir: bool = True,
    check_for_file: bool = False,
    file_types: Union[None, List[str]] = None,
) -> None:
    """Check for path validation.

    Args:
        path (str): Path for either file or folder
        check_for_dir (bool): Set to true if need to check for directory
        check_for_file (bool): Set to true if need to check of
            existence of file
        file_types (Union[None, List[str]]): List of file types against
            which file path is to be checked.

    Raises:
        Exception: If file path does not exist or folder path does
            not exist or passed file type do not match what is in
            file_types list.
    """

    if not file_types:
        file_types = []

    path = Path(path)

    if not path.exists():
        raise Exception(f"{path} does not exist!")

    if check_for_dir and not path.is_dir():
        raise Exception(f"{path} is not a directory!")

    if check_for_file and path.suffix not in file_types:
        raise Exception(
            f"Invalid file type passed {path} , \
            valid file types are {file_types}"
        )


def read_file(file_path: str, use_json5=False) -> Dict:
    """Reads a file and returns a python dictionary."""

    file_path = Path(file_path)
    logger.debug(f"Attempting to read {file_path}")

    validate_path(
        file_path, check_for_dir=False, check_for_file=True, file_types=[".json", ".yaml"]
    )

    if file_path.suffix == ".json":
        with open(file_path, "r") as f:
            content = json.load(f) if not use_json5 else json5.load(f)

    elif file_path.suffix == ".yaml":
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)

    else:
        logger.error(
            f"""Could not read the {file_path}, this feature is not yet
        implemented"""
        )
        raise Exception(
            f"File of type {file_path.suffix} \
            is not yet implemented for reading purpose"
        )

    logger.debug(f"{file_path} read successfully")
    return content


def write_file(content: dict, file_path: str, use_json5=False, **kwargs) -> None:
    """Takes a python dictionary and writes it into a file."""
    file_path = Path(file_path)
    validate_path(file_path.parent)

    if file_path.suffix == ".json":
        with open(file_path, "w") as f:
            json.dump(content, f, **kwargs) if not use_json5 else json5.dump(content, f, **kwargs)

    elif file_path.suffix == ".yaml":
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f, **kwargs)

    else:
        raise Exception(
            f"File of type {file_path.suffix} \
            is not yet implemented for writing purpose"
        )


def time_tracker(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f" '{func.__name__}' took {elapsed_time:.6f}s to execute.")
        return result

    return wrapper
