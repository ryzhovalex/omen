import os
import sys
import pytest
import argparse
from typing import get_args

from warepy import (
    format_message, join_paths, match_enum_containing_value,
    get_enum_values, get_union_enum_values
)
from puft.tools.log import log
from dotenv import load_dotenv

from puft import __version__ as puft_version
from puft.core.assembler.assembler import Assembler
from puft.tools.hints import CLIModeEnumUnion
from .cli_run_enum import CLIRunEnum
from .cli_db_enum import CLIDbEnum
from .cli_helper_enum import CLIHelperEnum


def main() -> None:
    # Envrons should be loaded from app's root directory
    load_dotenv(os.path.join(os.getcwd(), '.env'))

    args = parse_input()

    if args.check_version:
        print(f"Puft {puft_version}")
        return
    elif args.mode[0] in get_union_enum_values(CLIModeEnumUnion):
        mode = args.mode[0] 

        # Find enum where mode assigned.
        mode_enum_class = match_enum_containing_value(
            mode, *get_args(CLIModeEnumUnion))

        # Create according enum with mode value.
        mode_enum = mode_enum_class(mode)
    else:
        raise NotImplementedError(f"Command {args.mode[0]} is not supported")
        # Mode is probably targeted to custom command.
        # mode_enum = CLIHelperEnum.CUSTOM_CMD
        #!! custom_cmd = 

    # Create and build assembler.
    assembler = Assembler(
        mode_enum=mode_enum,
        host=args.host,
        port=int(args.port),
        root_dir=args.root_dir,
        source_filename=args.source_filename)

    # Make decision about proper run option
    if type(mode_enum) in get_args(CLIModeEnumUnion):
        # Call appropriate actions depend on chosen mode.
        if type(mode_enum) is CLIRunEnum:
            invoke_run(assembler)
        elif type(mode_enum) is CLIDbEnum:
            with assembler.get_puft().get_native_app().app_context():
                invoke_db_change(assembler, mode_enum)
        elif type(mode_enum) is CLIHelperEnum:
            if mode_enum is CLIHelperEnum.SHELL:
                invoke_shell(assembler)
            elif mode_enum is CLIHelperEnum.CUSTOM_CMD: 
                # TODO: Custom cmds after assembler build operations.
                pass
            elif mode_enum is CLIHelperEnum.DEPLOY:
                # TODO: Implement deploy operation.
                pass

def invoke_shell(assembler: Assembler):
    """Invoke Puft interactive shell."""
    assembler.get_puft().run_shell()


def invoke_run(
        assembler: Assembler) -> None:
    if assembler.mode_enum is CLIRunEnum.TEST:
        log.info('Run pytest')
        # TODO: Move this logic to Assembler or Puft
        pytest.main([
            assembler.root_dir,
            f"--rootdir={assembler.root_dir}"
        ])
    else:
        assembler.run_app()


def invoke_db_change(
    assembler: Assembler,
    mode_enum: CLIDbEnum
) -> None:
    db = assembler.get_db()

    if mode_enum is CLIDbEnum.INIT:
        db.init_migration()
    elif mode_enum is CLIDbEnum.MIGRATE:
        db.migrate_migration()
    elif mode_enum is CLIDbEnum.UPGRADE:
        db.upgrade_migration()


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    # TODO: Add help descriptions to args.
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="*")
    parser.add_argument("-a", dest="host", default="127.0.0.1")
    parser.add_argument("-p", dest="port", default="5000")
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    parser.add_argument("-src", dest="source_filename", default="build")
    parser.add_argument(
        "-v", "--version", action="store_true", dest="check_version")
    return parser.parse_args()


if __name__ == "__main__":
    main()
