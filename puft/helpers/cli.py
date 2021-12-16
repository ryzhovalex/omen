import os
import argparse
import subprocess
from typing import Tuple, Literal

from warepy import format_message, join_paths, logger

# Attempt relative import, and it its failed, use absolute import.
try:
    from .constants import Modes, MODES
except ImportError:
    from constants import Modes, MODES


def main() -> int:
    args = parse_input()

    mode = args.mode
    root_dir = args.root_dir
    user_environs_file_path = args.user_environs_file_path
    host, port = parse_hostname(args.hostname)
    python_bin = parse_python_bin(args.python_bin)
    is_verbose = args.is_verbose

    # Generate and run flask-related command.
    action = resolve_flask_action(mode)
    cmd = f"{python_bin} -m flask {action}"

    # Add additional arguments only if command not targeted to database changes.
    if "db" not in action:
        cmd += f" -h {host} -p {port}"

    base_environs = generate_environs(args)
    user_environs = parse_user_environs_from_file(caller_root_dir=root_dir, user_environs_file_path=user_environs_file_path)
    subprocess_environs = {**base_environs, **user_environs}
    for x in subprocess_environs.values():
        if type(x) != str:
            raise ValueError("Heh", x)
    if is_verbose:
        logger.info(f"Apply environs: {subprocess_environs}.")
        logger.info(f"Run command: {cmd}.")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, text=True, env=subprocess_environs, shell=True) as process:
        for line in process.stdout:
            print(line, end="")
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, process.args)

    return 0


def resolve_flask_action(mode: Modes) -> str:
    """Resolve appropriate action for Flask cli depending on given mode and return this action name."""
    if mode in ["init", "migrate", "upgrade"]:
        action = f"db {mode}"
    else:
        action = "run"
    return action


def generate_environs(args: argparse.Namespace) -> dict:
    """Generate environs from given namespace and return them in mapping.
    
    Also generate special environs required by Flask itself."""
    environs = {}
    for name, value in args.__dict__.items():
        environs[f"PUFT_{name.upper()}"] = str(value)

    # Generate Flask-related environs.
    environs["FLASK_APP"] = args.source_file
    environs["FLASK_ENV"] = args.mode

    return environs


def parse_hostname(hostname: str) -> Tuple[str, str]:
    """Parse given hostname into host and port and return tuple with host and port."""
    splitted = hostname.split(":")
    if len(splitted) != 2:
        raise ValueError(format_message("Given hostname {} should contain host and port, e.g. `127.0.0.1:5000`.", hostname))
    # TODO: Add regex checking for host and maybe port.
    else:
        return (splitted[0], splitted[1])


def parse_python_bin(python_bin: str) -> str:
    """Parse given python bin path and return appropriate implementation.
    
    Look for virtual environment environs, if `python_bin = "python3"`."""
    if python_bin == "python3":
        virtual_env = os.environ.get("VIRTUAL_ENV", None)
        if virtual_env:
            return f"{virtual_env}/bin/python3"
        else:
            return "python3"


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
        formatted_line = line.replace("\n", "").split("=")
        if len(formatted_line) != 2:
            raise ValueError(format_message("Wrong format of given file environ: {}.", line))
        else:
            values_by_environ[formatted_line[0]] = formatted_line[1]
    return values_by_environ


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    # TODO: Add descriptions to args.
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="dev", choices=MODES)
    parser.add_argument("source_file", nargs="?", default="main")
    parser.add_argument("hostname", nargs="?", default="127.0.0.1:5000")
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    parser.add_argument("-py", dest="python_bin", default="python3", help="Python bin path. If default, look also for $VIRTUAL_ENV environ.")
    parser.add_argument(
        "-envsfile", 
        dest="user_environs_file_path", 
        default=None, 
        help="Path to file with user environs in format `ENVIRON_NAME=VALUE\\n`. Defaults to file `./environs` in given directory (calling directory by default)."
    )
    parser.add_argument("-v", dest="is_verbose", action="store_true", help="Enable verbose mode.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
