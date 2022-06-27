""""
Utility functions
"""

# standard imports
from pathlib import Path
import logging
import logging.config
import json

# third-party imports
import yaml

logger = logging.getLogger(__name__)

def get_map_centre(longitudes: list, latitudes: list):
    return {'lon': sum(longitudes)/len(longitudes), \
        'lat': sum(latitudes)/len(latitudes)}

def validate_path(
        path: str, 
        check_for_dir=True, 
        check_for_file=False, 
        file_types=[]):

    path = Path(path)

    if not path.exists():
        raise Exception(f"{path} does not exist!")

    if check_for_dir and not path.is_dir():
        raise Exception(f"{path} is not a directory!")

    if check_for_file and path.suffix not in file_types:
        raise Exception(f"Invalid file type passed {path} , \
            valid file types are {file_types}")

def read_file(file_path: str) -> dict:

    file_path = Path(file_path)
    logger.debug(f"Attempting to read {file_path}")

    validate_path(file_path, check_for_dir=False, check_for_file=True, \
        file_types=['.json', '.yaml'])

    # Handle JSON file read
    if file_path.suffix == '.json':
        with open(file_path, "r") as f:
            content = json.load(f)

    # Handle YAML file read
    elif file_path.suffix == '.yaml':
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)

    else:
        logger.error(f"Could not read the {file_path}, this feature is not yet implemented")
        raise Exception(f"File of type {file_path.suffix} \
            is not yet implemented for reading purpose")

    logger.debug(f"{file_path} read successfully")
    return content

def write_file(content:dict, file_path: str, **kwargs) -> None:

    file_path = Path(file_path)
    validate_path(file_path.parent)

    # Handle JSON file write
    if file_path.suffix == '.json':
        with open(file_path, "w") as f:
            json.dump(content, f, **kwargs)

    # Handle YAML file write
    elif file_path.suffix == '.yaml':
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f, **kwargs)

    else:
        raise Exception(f"File of type {file_path.suffix} \
            is not yet implemented for writing purpose")

def setup_logging(filename: str = None):

    """
    Creates log directory and sets up logging via logging.yaml
    """
    if filename is None:
        filename = Path(__file__).parents[2] / 'logging.yaml' 

    logging.config.dictConfig(read_file(filename))