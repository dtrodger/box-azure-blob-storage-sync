from __future__ import annotations
import logging
import click

import src.manager.box_to_azure as box_to_azure_manager
import src.manager.folder_seed as folder_seed_manager


log = logging.getLogger(__name__)


@click.command()
@click.option(
    "-e", "--env", default="dev", help="env environment alias", type=str,
)
def box_to_azure(env: str) -> None:
    box_to_azure_manager.box_to_azure_blob_storage(env)


@click.command()
@click.option(
    "-e", "--env", default="dev", help="env environment alias", type=str,
)
def seed_folders(env: str) -> None:
    folder_seed_manager.seed_datetime_folders(env)


@click.group()
def cli() -> None:
    pass


def main() -> None:
    commands = [
        box_to_azure,
        seed_folders
    ]
    for command in commands:
        cli.add_command(command)

    cli()


if __name__ == "__main__":
    main()
