import os
import argparse
import subprocess
from typing import Tuple, Literal

from warepy import format_message

from constants import Modes, MODES


def main() -> int:
    args = parse_input()

    mode = args.mode
    host, port = parse_hostname(args.hostname)
    python_bin = args.python_bin

    # Generate and run flask-related command.
    action = resolve_flask_action(mode)
    cmd = f"{python_bin} -m flask {action}"

    # Add additional arguments only if command not targeted to database changes.
    if "db" not in action:
        cmd += f" -h {host} -p {port}"

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, text=True, env=generate_environs(args), shell=True) as process:
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
        environs[f"PUFT_{name.upper()}"] = value       

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


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    # TODO: Add descriptions to args.
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="dev", choices=MODES)
    parser.add_argument("source_file", nargs="?", default="main")
    parser.add_argument("hostname", nargs="?", default="127.0.0.1:5000")
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    parser.add_argument("-py", dest="python_bin", default="python3")
    return parser.parse_args()


if __name__ == "__main__":
    main()
