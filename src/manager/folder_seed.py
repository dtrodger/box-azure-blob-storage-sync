from __future__ import annotations
import datetime
import logging
from typing import Optional, Dict

import boxsdk

from src import utils
from src import box


log = logging.getLogger(__name__)


DATETIME_FOLDER_INDEX_SCORES = {"days": 1, "hours": 2, "minutes": 3, "seconds": 4}
DATETIME_FOLDER_INDEXS = ["days", "hours", "minutes", "seconds"]
DATETIME_STR_FORMAT = "%Y-%m-%dT%H:%M:%S"


def create_and_cache_folder(
    box_client: boxsdk.Client,
    folder_path_map: dict,
    parent_folder_id: str,
    folder_name: str,
    folder_map_key: str,
    box_user: Optional[boxsdk.object.user.User],
) -> Dict[str, boxsdk.object.folder.Folder]:
    if box_user:
        folder = (
            box_client.as_user(box_user)
            .folder(parent_folder_id)
            .create_subfolder(folder_name)
        )
    else:
        folder = box_client.folder(parent_folder_id).create_subfolder(folder_name)

    log.info(f"created new Box folder {folder} at path {folder_map_key}")
    folder_path_map[folder_map_key] = folder

    return folder_path_map


def seed_datetime_folders(env: str) -> None:
    config = utils.load_configuration(env)
    utils.configure_logging(config)
    log.info("starting Box Consulting Agent")
    box_client = box.configure_box_client(config)
    box_user = box.get_as_user(box_client, config)
    seed_folder_id = config["box"]["seed_folder_id"]
    seed_instant = datetime.datetime.strptime(
        config["box"]["seed_datetime_since"], DATETIME_STR_FORMAT
    )
    seed_until = datetime.datetime.strptime(
        config["box"]["seed_datetime_until"], DATETIME_STR_FORMAT
    )
    folder_path_map = box.fill_folder_path_map(
        box_client, seed_folder_id, seed_folder_id, box_user, None, None
    )
    log.info(f"built Box folder path id map {folder_path_map}")
    seed_datetime_folder_index = config["box"]["seed_datetime_folder_index"]
    folder_index_score = DATETIME_FOLDER_INDEX_SCORES[seed_datetime_folder_index]
    while seed_instant <= seed_until:
        (
            year_folder_name,
            month_folder_name,
            day_folder_name,
            hour_folder_name,
            minute_folder_name,
            second_folder_name,
        ) = utils.datetime_to_strings(seed_instant)
        year_folder_map_key = year_folder_name
        month_folder_map_key = f"{year_folder_map_key}|{month_folder_name}"
        day_folder_map_key = f"{month_folder_map_key}|{day_folder_name}"
        hour_folder_map_key = f"{day_folder_map_key}|{hour_folder_name}"
        minute_folder_map_key = f"{hour_folder_map_key}|{minute_folder_name}"
        second_folder_map_key = f"{minute_folder_map_key}|{second_folder_name}"
        if year_folder_map_key not in folder_path_map.keys():
            folder_path_map = create_and_cache_folder(
                box_client,
                folder_path_map,
                seed_folder_id,
                year_folder_name,
                year_folder_map_key,
                box_user,
            )

        if month_folder_map_key not in folder_path_map.keys():
            year_folder = folder_path_map[year_folder_map_key]
            year_folder_id = year_folder.response_object["id"]
            folder_path_map = create_and_cache_folder(
                box_client,
                folder_path_map,
                year_folder_id,
                month_folder_name,
                month_folder_map_key,
                box_user,
            )

        if day_folder_map_key not in folder_path_map.keys():
            month_folder = folder_path_map[month_folder_map_key]
            month_folder_id = month_folder.response_object["id"]
            folder_path_map = create_and_cache_folder(
                box_client,
                folder_path_map,
                month_folder_id,
                day_folder_name,
                day_folder_map_key,
                box_user,
            )

        if folder_index_score > 1 and hour_folder_map_key not in folder_path_map.keys():
            day_folder = folder_path_map[day_folder_map_key]
            day_folder_id = day_folder.response_object["id"]
            folder_path_map = create_and_cache_folder(
                box_client,
                folder_path_map,
                day_folder_id,
                hour_folder_name,
                hour_folder_map_key,
                box_user,
            )
        if folder_index_score > 2 and minute_folder_map_key not in folder_path_map.keys():
            hour_folder = folder_path_map[hour_folder_map_key]
            hour_folder_id = hour_folder.response_object["id"]
            folder_path_map = create_and_cache_folder(
                box_client,
                folder_path_map,
                hour_folder_id,
                minute_folder_name,
                minute_folder_map_key,
                box_user,
            )

        if folder_index_score > 3 and second_folder_map_key not in folder_path_map.keys():
            minute_folder = folder_path_map[minute_folder_map_key]
            minute_folder_id = minute_folder.response_object["id"]
            folder_path_map = create_and_cache_folder(
                box_client,
                folder_path_map,
                minute_folder_id,
                second_folder_name,
                second_folder_map_key,
                box_user,
            )

        seed_instant = seed_instant + datetime.timedelta(
            **{seed_datetime_folder_index: 1}
        )
