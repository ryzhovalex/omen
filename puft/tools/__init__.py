"""Module with various tools."""
import os
import json
from typing import Any, List, Dict, Literal, Callable, Union, Tuple, Type

from werkzeug.wrappers.response import Response
from flask import make_response, redirect, flash, render_template

from warepy import logger, join_paths, format_message, load_yaml

from ..helpers.cells import Cell, ConfigCell


@logger.catch
def generate_redirect_response(url: Any, status_code: int = 302) -> Response:
    """Generate redirect response with given url and return this response."""
    response = redirect(url, code=status_code)
    return response

@logger.catch
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
def generate_cells_by_name(cells: List[Cell]) -> Dict[str, Cell]:
    """Traverse through given cells names and return dict with these cells as values and their names as keys."""
    cells_by_name = {}
    for cell in cells:
        cells_by_name[cell.name] = cell
    return cells_by_name


@logger.catch
def parse_config_cell(config_cell: ConfigCell, root_path: str, update_with: dict = None) -> dict:
    """Parse given config cell and return configuration dictionary.
    
    NOTE: This function performs automatic path absolutize - all paths starting with "./" within config will be joined to given root path.

    Args:
        config_cell: Configuration cell to parse from.
        root_path: Path to join config cell source with.
        update_with (optional): Dictionary to update config cell mapping with. Defaults to None.
    
    Raise:
        ValueError: If given config cell has non-relative source path.
        ValueError: If given config cell's source has unrecognized extension."""
    config = {}
    config_path = join_paths(root_path, config_cell.source)

    if config_cell.source[0] != "." and config_cell.source[1] != "/":
        error_message = format_message("Given config cell has non-relative source path {}", config_cell.source)
        raise ValueError(error_message)

    # Fetch config's extension.
    if "json" in config_path[-5:len(config_path)]:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
    elif "yaml" in config_path[-5:len(config_path)]:
        config = load_yaml(config_path)
    else:
        error_message = format_message("Unrecognized config cell source's extension.")
        raise ValueError(error_message)

    # Traverse all values and find paths required to be joined to the root path.
    for k, v in config.items():
        if type(v) == str:
            if v[0] == "." and v[1] == "/":
                config[k] = join_paths(root_path, v)

    # Update given config with extra dictionary if this dictionary given and not empty.
    if update_with:
        config.update(update_with)
    return config


@logger.catch
def make_fail_response(
    template_path: str, template_ctx: dict = {}, flash_message: str = "Error", flash_category: Literal["message", "error", "info", "warning"] = "error"
) -> Response:
    """Generate fail response with rendered template by given path with status code 422 compatible with turbo.js.
    
    Also able to flash message to template context.
    
    Args:
        template_path: Path to template to render.
        template_ctx (optional): Context to push to template. Defaults to empty dict.
        flash_message (optional): Message to flash to template context. Defaults to "Error".
        flash_category (optional): Category for flash message according to Flask's `flash` categories. Defaults to "error".
    """
    # Login errors should be flashed to user.
    flash(flash_message, category=flash_category)
    response = make_response(render_template(template_path, **template_ctx))
    # Always set status code of failed to form posts responses to 422 or turbo.js will raise an error.
    # Source: https://github.com/miguelgrinberg/turbo-flask/issues/11#issuecomment-883248949
    response.status_code = 422
    return response


@logger.catch
def do_or_flash(func: Callable, message: str = None, *args, **kwargs) -> Any:
    """Call given function with given args and kwargs and flask.flash message if the function raised an error. Return function output if there was no exception.
    
    Args:
        func: Function to execute and grab output.  
        message: Message to flash by Flask engine. Defaults to None, which means;
        - If `PUFT_MODE` is `dev`, `test`: flash error text.    
        - If `PUFT_MODE` is `prod`: flash text: "Something bad happened."  
    """
    puft_mode = os.environ["PUFT_MODE"]

    try:
        output = func(*args, **kwargs)
    except Exception as error:
        if puft_mode in ["dev", "test"] and message:
            flash(message)
        elif puft_mode in ["prod"]:
            flash("Something bad happened.")
    else:
        return output


def find_cell_by_name(cells: List[Cell], name: str) -> Cell:
    """Traverse through given list of cells and return first one with specified name."""
    for cell in cells:
        if cell.name == name:
            return cell
    raise ValueError(format_message("No cell with name {} in given cells.", name))