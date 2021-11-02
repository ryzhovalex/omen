"""Module with various decorators.
NOTE: It's extremely important to not set return typehint in decorators with wraps 
if you want save your wrapped function's docstring (occurred in VsCode's Pylance Python Language Server)."""
from functools import wraps
from os import error
from typing import Any, List, Dict, Union, Callable

from warepy import logger, format_message
from flask import g, redirect, url_for



def login_required(allowed_types: List[str] = None, endpoint_if_not_logged: str = "auth.login", endpoint_if_not_allowed: str = "home.basic"):
    """Check if user logged in before giving access to wrapped view.
    
    If user is not logged in, redirect him to the login page.
    If user doesn't have access to the view (i.e. his type is not in `allowed_types`), redirect him to backup page.

    Args:
        allowed_types: Types of users that should have access to the view. Defaults to None, i.e. all logged users have access.
        endpoint_if_not_logged: Endpoint to redirect to if user is not logged in. Defaults to `auth.login`.
        endpoint_if_not_allowed: Endpoint to redirect to if user not in allowed types to access wrapped view. Defaults to `home.basic`.
    """
    def decorator(view: Callable):
        @wraps(view)
        def inner(**kwargs):
            result = None
            error_message = None

            if g.user is None:
                error_message = format_message("Reject request of unauthorized user to view: {}", view.__name__)
                result = redirect(url_for(endpoint_if_not_logged))
            elif allowed_types is not None:
                if g.user.type not in allowed_types:
                    error_message = format_message("Reject request of user {} with type {} to view {}.", [g.user.username, g.user.type, view.__name__])
                    result = redirect(url_for(endpoint_if_not_allowed))
            
            # Check if error occured, else normally call view. Finally return result with error or view output.
            if error_message is not None:
                logger.warning(error_message)
            else:
                result = view(**kwargs)
            return result
        return inner
    return decorator