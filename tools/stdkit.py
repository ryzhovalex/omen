"""Module with various tools."""
import os
import json
from typing import Any, List, Dict, Literal, Callable, Union, Tuple

import yaml
from flask import Response, make_response, redirect

from ..helpers.logger import logger
from ..helpers.constants import Path
from ..helpers.cells import Cell, ConfigCell


@logger.catch
def generate_redirect_response(url: Any, status_code: int = 302) -> Response:
    """Generate redirect response with given url and return this response."""
    response = redirect(url, code=status_code)
    return response

def generate_success_response(data: Any, is_json_enabled: bool, ok_status_code: int = 200, no_content_status_code: int = 204) -> Response:
    """Generate success response with given data and return this response.
    
    If `is_json_enabled` == True, dump data to json."""
    # Check if data should be dumped to json.
    if is_json_enabled:
        content = json.dumps(data)
    else:
        content = data

    response = make_response(content)

    # Set special status code if there is no content and OK otherwise.
    if content:
        response.status_code = ok_status_code
    else:
        response.status_code = no_content_status_code

    return response

@logger.catch
def generate_error_response(error: Exception, status_code: int = 400) -> Response:
    """Generate error response with given error and return this response."""
    data = {"error": repr(error)}
    json_data = json.dumps(data)
    response = make_response(json_data)
    response.status_code = status_code
    return response

@logger.catch
def join_paths(*args) -> str:
    """Collect given paths and return summary joined absolute path.
    
    Also calculate logic for `./` starting path, consider it as "from me" relative point."""
    summary_path = ""
    for path in args:
        # Check if path starts from slash, to remove it to avoid errors.
        if path[0] == "/": 
            path = path[1:]
        # Check if path given in logical form (starts from "./").
        elif path[:2] == "./":  
            path = path[2:]  # Remove leading "./" to perform proper paths joining.
        # Check if path ends with slash, to remove it to avoid errors.
        if path[len(path)-1] == "/":
            path = path[:len(path)-1]
        summary_path += "/" + path
    return summary_path

@logger.catch
def parse_yaml_config(
        config_path: str, 
        loader_name: Literal["base", "safe", "full"] = "full"
    ) -> Dict[str, Any]:
    """Parse YAML config and return all documents and their fields within it as dictionary."""
    loaders_by_name = {  # dict to resolve loader by given name
        "base": yaml.BaseLoader,
        "safe": yaml.SafeLoader,
        "full": yaml.FullLoader
    } 

    with open(config_path, "r") as cfg:
        content = yaml.load(cfg, Loader=loaders_by_name[loader_name])
    return content


@logger.catch
def dump_json_to_environ(environ_key: str, map_to_dump: Union[List, Dict, Tuple]) -> None:
    """Dump given map with converting to json to environment variable by given key."""
    os.environ[environ_key] = json.dumps(map_to_dump)


@logger.catch
def load_json_from_environ(environ_key: str) -> Dict[str, Any]:
    """Load json with converting to Python's map object from environment variable by given key and return data dictionary."""
    return json.loads(os.environ[environ_key])


@logger.catch
def unpack_cell(cell: Cell) -> Dict[str, Any]:
    """Unpack given cell to dictionary and return this dictionary."""
    data = cell.__dict__
    return data


@logger.catch
def generate_cells_by_name(cells: List[Cell]) -> Dict[str, Cell]:
    """Traverse through given cells names and return dict with these cells as values and their names as keys."""
    cells_by_name = {}
    for cell in cells:
        cells_by_name[cell.name] = cell
    return cells_by_name


@logger.catch
def convert_snake_to_camel_case(snake_string: str) -> str:
    """Convert given in snake_case string to CamelCase string and return it.
    
    Raise error if given string doesn't contain underscores."""
    camel_string = ""
    words = snake_string.split("_")
    if len(words) == 1:  # i.e word didn't contain underscores
        raise ValueError("Given string doesn't contain underscores.")
    for word in words:
        camel_string += word.capitalize()
    return camel_string


@logger.catch
def format_error_message(text: str, vars: Union[Any, List[Any]] = None, no_arg_phrase: str = "None") -> str:
    """Construct error message from given text with inserting given vars to it and return resulting message.
    Use 'no_arg_phrase' as phrase to insert instead of empty (Python's bool checking == False) given argument.
    Helpful when you want to format error message with variables with unknown values."""
    # Pack variable to list if given only one.
    if not isinstance(vars, list):
        vars = [vars]
        
    vars_for_format = []
    for var in vars:
        # Check var and append it to vars for formatting if it's not empty.
        if bool(var):
            vars_for_format.append(var)
        else:
            vars_for_format.append(no_arg_phrase)
    error_message = text.format(*vars_for_format)
    return error_message

@logger.catch
def get_next_dict_key(dictionary: dict) -> str:
    """Return next key in dictionary by using its iterator."""
    return next(iter(dictionary.keys()))


@logger.catch
def normalize_db_uri(cpas_module_path: str, raw_db_uri: str) -> str:
    """Normalize given db (i.e. convert rel paths to abs and check for errors) uri and return it."""
    if ":memory:" in raw_db_uri:
        return "sqlite:///:memory:"
    db_name, db_rel_path = raw_db_uri.split("://")
    if db_name == "sqlite":
        db_path = join_paths(cpas_module_path, db_rel_path)
        db_uri = db_name + ":///" + db_path  # It is necessary to set ":///" in sqlite3 abs paths
        return db_uri
    elif db_name == "postgresql":
        error_message = format_error_message("PostgreSQL database temporarily not supported.")
        raise ValueError(error_message)
    else:
        error_message = format_error_message("Couldn't recognize database name: {}", db_name)
        raise ValueError(error_message)


@logger.catch
def parse_config_cell(config_cell: ConfigCell) -> dict:
    """Parse given config cell and return configuration dictionary."""
    load_type = config_cell.load_type
    if load_type == "json":
        config = json.dump(config_cell.source)
    elif load_type == "map":
        config = config_cell.source
    return config


@logger.catch
def make_abs_path_for_config_cells(config_cells_by_name: Dict[str, ConfigCell], root_path: Path) -> Dict[str, ConfigCell]:
    """Traverse through given list of config cells and join source path with root path for those who have `load_type=json`.
    
    Return:
        Dict with names and config cells."""
    for cell in config_cells_by_name:
        if cell.load_type == "json":
            cell.source = join_paths(root_path, cell.source)
    return config_cells_by_name