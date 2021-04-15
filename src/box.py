from typing import Optional
import logging
from typing import Dict

import boxsdk


log = logging.getLogger(__name__)


def configure_box_client(config: dict) -> boxsdk.Client:
    box_auth = configure_jwt_auth(config)
    box_client = boxsdk.Client(box_auth)
    log.debug(f"set up Box client {box_client}")

    return box_client


def configure_jwt_auth(config: dict) -> boxsdk.JWTAuth:
    box_auth = boxsdk.JWTAuth.from_settings_dictionary(config["box"]["jwt_auth"])
    box_auth.authenticate_instance()
    log.debug(f"authenticated to Box with {box_auth}")

    return box_auth


def get_as_user(
    box_client: boxsdk.Client, config: dict
) -> Optional[boxsdk.object.user.User]:
    as_user_id = config["box"]["as_user_id"]
    box_user = None
    if as_user_id:
        box_user = box_client.user(as_user_id).get()

    if box_user:
        log.debug(f"got Box user {box_user}")

    return box_user


def fill_folder_path_map(
    box_client: boxsdk.Client,
    folder_id: str,
    seed_root_folder_id: str,
    box_user: Optional[boxsdk.object.user.User] = None,
    map_key_root: Optional[str] = None,
    folder_path_map: Optional[dict] = None,
) -> Dict[str, boxsdk.object.folder.Folder]:
    if not folder_path_map:
        folder_path_map = dict()

    if box_user:
        folder = box_client.as_user(box_user).folder(folder_id).get()
    else:
        folder = box_client.folder(folder_id).get()

    log.debug(f"got Box folder {folder}")

    if folder_id != seed_root_folder_id:
        folder_name = folder.response_object["name"]

        if map_key_root:
            map_key_root = f"{map_key_root}|{folder_name}"
        else:
            map_key_root = folder_name

        folder_path_map[map_key_root] = folder

        log.debug(
            f"added folder map key {map_key_root} with value {folder_id} to Box folder path id map"
        )

    for folder_item in folder.get_items():
        if folder_item.response_object["type"] == "folder":
            folder_path_map = {
                **folder_path_map,
                **fill_folder_path_map(
                    box_client,
                    folder_item.response_object["id"],
                    seed_root_folder_id,
                    box_user,
                    map_key_root,
                    folder_path_map,
                ),
            }

    return folder_path_map
