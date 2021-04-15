from __future__ import annotations
import logging
import click

import src.commands.box_to_azure as box_to_azure_commands
import src.commands.seed_folders as seed_folders_commands


log = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


def main() -> None:
    commands = [
        box_to_azure_commands.box_to_azure,
        seed_folders_commands.seed_folders
    ]
    for command in commands:
        cli.add_command(command)

    cli()


if __name__ == "__main__":
    main()
