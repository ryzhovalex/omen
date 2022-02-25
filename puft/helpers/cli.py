import os
import argparse
import subprocess
from typing import get_args

from warepy import format_message, join_paths, logger, match_enum_containing_value

from puft.constants.hints import CLIModeUnion
from puft.constants.lists import CLI_ENUM_VALUES, CLI_CONSTRUCT_ENUM_VALUES, CLI_DATABASE_ENUM_VALUES


def main() -> int:
    args = parse_input()

    mode = args.mode

    # Find enum where mode assigned.
    mode_enum = match_enum_containing_value(mode, *get_args(CLIModeUnion))
    action = resolve_action(mode_enum)

    if action in CLI_CONSTRUCT_ENUM_VALUES:
        # Do project construction related task.
        if action == "deploy":
            # TODO: Create project structure. 
            pass
    else:
        # Run Flask by command chain.
        invoke_flask(action, args)

    return 0


def invoke_flask(action: str, args: argparse.Namespace) -> None:
    """Chain actions to invoke flask.

    It might be done for common run, or for database changes.""" 
    root_dir = args.root_dir
    user_environs_file_path = args.user_environs_file_path
    host = args.host
    port = args.port
    python_bin = parse_python_bin(args.python_bin)
    is_verbose = args.is_verbose

    cmd = f"{python_bin} -m flask {action}"

    # Add additional arguments only if command not targeted to database changes.
    if "db" not in action:
        cmd += f" -h {host} -p {port}"

    base_environs = generate_environs(args)
    user_environs = parse_user_environs_from_file(caller_root_dir=root_dir, user_environs_file_path=user_environs_file_path)
    subprocess_environs = {**base_environs, **user_environs}
    if is_verbose:
        logger.info(f"Apply environs: {subprocess_environs}.")
        logger.info(f"Run command: {cmd}.")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, text=True, env=subprocess_environs, shell=True) as process:
        try:
            if process.stdout is not None:
                for line in process.stdout:
                    print(line, end="")
        except KeyboardInterrupt:
            print("Interrupted by keyboard.")
            process.kill()
            raise KeyboardInterrupt()
        
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, process.args)


def resolve_action(mode: CLIModeUnion) -> str:
    """Resolve appropriate action for Flask or Puft cli depending on given mode and return this action name."""
    if mode.value in CLI_DATABASE_ENUM_VALUES:
        action = f"db {mode}"
    else:
        action = "run"
    return action


def generate_environs(args: argparse.Namespace) -> dict:
    """Generate environs from given namespace and return them in mapping.
    
    Also generate special environs required by Flask itself."""
    environs = {}
    for name, value in args.__dict__.items():
        environs[f"CLI_{name.upper()}"] = str(value)

    # Generate Flask-related environs.
    environs["FLASK_APP"] = args.source_file

    if args.mode == "dev":
        environs["FLASK_ENV"] = "development"
    elif args.mode == "production":
        environs["FLASK_ENV"] = "production"
    elif args.mode == "test":
        environs["FLASK_ENV"] = "development"

    return environs


def parse_python_bin(python_bin: str) -> str:
    """Parse given python bin path and return appropriate implementation.
    
    Look for virtual environment environs, if `python_bin == "python3"`."""
    res_python_bin = "python3"
    if python_bin == "python3":
        virtual_env = os.environ.get("VIRTUAL_ENV", None)
        if virtual_env:
            res_python_bin = f"{virtual_env}/bin/python3"
    return res_python_bin


def parse_user_environs_from_file(caller_root_dir: str, user_environs_file_path: str) -> dict:
    """Parse environs from file by given path and return mapping with them.
    
    If `user_environs_file_path` is None or empty, look for file `environs` in given `caller_root_dir`.
    
    Raise:
        ValueError:
            If any environ within file at target path violated format `ENVIRON_NAME=VALUE\\n`"""
    # Resolve path.
    if user_environs_file_path:
        target_path = user_environs_file_path
    else:
        target_path = join_paths(caller_root_dir, "./environs")
    
    # Open target file and read all lines.
    with open(target_path, "r") as file:
        lines = file.readlines()

    # Parse received lines.
    values_by_environ = {}
    for line in lines:
        # Error that may be raised during parsing.
        wrong_format_error = ValueError(format_message("Wrong format of given file environ: {}.", line))

        # Split line into two pieces by first equal sign from the left (i.e. with lowest index).
        equal_sign_index = line.find("=")
        if equal_sign_index == -1:
            raise wrong_format_error
        formatted_line = [line[:equal_sign_index], line[equal_sign_index+1:]]
        formatted_line = line.strip().split("=")

        if len(formatted_line) != 2:
            raise wrong_format_error
        else:
            # Also perform strip to environ and value to solve cases when environ `ENVIRON = VALUE` written with spaces before and after equal sign.
            environ = formatted_line[0].strip()
            value = formatted_line[1].strip()

            values_by_environ[environ] = value
    return values_by_environ


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    # TODO: Add descriptions to args.
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=CLI_ENUM_VALUES)
    parser.add_argument("-a", dest="host", default="127.0.0.1")
    parser.add_argument("-p", dest="port", default="5000")
    parser.add_argument("-src", dest="source_file", default="main")
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    parser.add_argument("-py", dest="python_bin", default="python3", help="Python bin path. If default, looking for $VIRTUAL_ENV environ performed at first.")
    parser.add_argument(
        "-envdir", 
        dest="user_environs_file_path", 
        default=None, 
        help="Path to file with user environs in format `ENVIRON_NAME=VALUE\\n`. Defaults to file `./environs` in given directory (calling directory by default)."
    )
    parser.add_argument("-v", dest="is_verbose", action="store_true", help="Enable verbose mode.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
