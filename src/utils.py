"""
utils
"""

from __future__ import annotations
import logging.config
import logging
import os

import yaml


log = logging.getLogger(__name__)


CONFIG_DIR_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "env", "{env_alias}.yml",
)


def configure_logging(configuration: dict) -> None:
    log_dict_config = configuration["log"]
    for handler_alias, handler_config in log_dict_config["handlers"].items():
        if "filename" in handler_config.keys():
            log_file_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "data",
                "log",
                handler_config["filename"],
            )
            if not os.path.exists(log_file_path):
                with open(log_file_path, "w"):
                    pass

            handler_config["filename"] = log_file_path

    logging.config.dictConfig(log_dict_config)
    log.debug(f"configured logging")


def datetime_to_strings(datetime):
    return (
        f"_{datetime.year}",
        f"_{datetime.month}",
        f"_{datetime.day}",
        f"_{datetime.hour}",
        f"_{datetime.minute}",
        f"_{datetime.second}",
    )


def load_configuration(env_alias: str) -> dict:
    config_file_path = CONFIG_DIR_FILE_PATH.format(env_alias=env_alias)
    with open(config_file_path) as fh:
        return yaml.load(fh, Loader=yaml.FullLoader)


def write_configuration(file_path: str, config_dict: dict) -> None:
    with open(file_path, "w") as fh:
        yaml.dump(config_dict, fh, default_flow_style=False)
