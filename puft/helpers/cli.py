import os
import argparse
import importlib.util
from typing import get_args

from warepy import format_message, join_paths, logger, match_enum_containing_value

from .assembler import Assembler
from ..constants.hints import CLIModeEnumUnion
from ..constants.lists import (
    CLI_MODE_ENUM_VALUES, CLI_CONSTRUCT_ENUM_VALUES, CLI_DATABASE_ENUM_VALUES, CLI_RUN_ENUM_VALUES
)
from ..constants.enums import (
    CLIRunEnum, CLIDatabaseEnum, CLIConstructEnum
)


def main() -> int:
    args = parse_input()
    mode = args.mode

    # Find enum where mode assigned.
    mode_enum_class = match_enum_containing_value(mode, *get_args(CLIModeEnumUnion))

    # Create according enum with mode value.
    mode_enum = mode_enum_class(mode)

    # Invoke Puft according to chosen mode.
    if mode_enum_class is CLIRunEnum:
        invoke_run(
            mode_enum=mode_enum,
            host=args.host,
            port=int(args.port),
            root_dir=args.root_dir,
            source_file=args.source_file,
        )

    return 0


def invoke_run(
    mode_enum: CLIModeEnumUnion, host: str, port: int, root_dir: str, source_file: str
) -> None:
    """Run puft with given mode and run parameters."""
    # Load target module spec from location, where cli were called.
    module_spec = importlib.util.spec_from_file_location(source_file, os.path.join(root_dir, source_file))
    if module_spec and module_spec.loader:
        main_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(main_module)
        build = main_module.build
        assembler = Assembler(
            build=build,
            mode_enum=mode_enum,
            host=host,
            port=port
        )
        assembler.run()


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    # TODO: Add help descriptions to args.
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=CLI_MODE_ENUM_VALUES)
    parser.add_argument("-a", dest="host", default="127.0.0.1")
    parser.add_argument("-p", dest="port", default="5000")  # TODO: Add check if given port is integer.
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    parser.add_argument("-src", dest="source_file", default="main")
    return parser.parse_args()


if __name__ == "__main__":
    main()
