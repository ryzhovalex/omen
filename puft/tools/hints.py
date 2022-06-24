from core.cli.cli_db_enum import CLIDbEnum
from core.cli.cli_run_enum import CLIRunEnum
from core.cli.cli_helper_enum import CLIHelperEnum

CLIModeEnumUnion = CLIDbEnum | CLIRunEnum | CLIHelperEnum
