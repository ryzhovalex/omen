import os
import argparse
import subprocess
from typing import Tuple

from warepy import format_message


MODES = ["dev", "prod", "test", "init", "migrate", "upgrade"]


def main() -> int:
    args = parse_input()
    mode = args.mode
    source_file = args.source_file
    host, port = parse_hostname(args.hostname)
    root_dir = args.root_dir

    subprocess.run("", text=True, shell=True, capture_output=True)
    return 0


def parse_hostname(hostname) -> Tuple[str, str]:
    """Parse given hostname into host and port and return tuple with host and port."""
    splitted = hostname.split(":")
    if len(splitted) != 2:
        raise ValueError(format_message("Given hostname {} should contain host and port, e.g. `127.0.0.1:5000`.", hostname))
    # TODO: Add regex checking for host and maybe port.
    else:
        return (splitted[0], splitted[1])


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="dev", choices=MODES)
    parser.add_argument("source_file", nargs="?", default="main")
    parser.add_argument("hostname", nargs="?", default="127.0.0.1:5000")
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    return parser.parse_args()


if __name__ == "__main__":
    main()
