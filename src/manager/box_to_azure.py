import datetime
import logging
import time
import io

import azure.storage.blob as azure_blob_storage
import boxsdk

from src import utils
from src import box


log = logging.getLogger(__name__)


FILE_CREATED_AT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def box_to_azure_blob_storage(env: str) -> None:
    config = utils.load_configuration(env)
    utils.configure_logging(config)
    log.info("starting State of Florida Box Platform application")
    azure_blob_storage_client = azure_blob_storage.BlobServiceClient.from_connection_string(
        config["azure"]["blob_storage_connection_string"]
    )
    blob_storage_container_name = config["azure"]["blob_storage_container_name"]
    box_client = box.configure_box_client(config)
    box_user = box.get_as_user(box_client, config)
    upload_folder_id = config["box"]["monitored_folder_id"]
    if box_user:
        upload_folder = box_client.as_user(box_user).folder(upload_folder_id).get()
    else:
        upload_folder = box_client.folder(upload_folder_id).get()

    log.info(f"got upload Box folder {upload_folder}")
    final_folder_id = config["box"]["final_folder_id"]
    if box_user:
        final_folder = box_client.as_user(box_user).folder(final_folder_id).get()
    else:
        final_folder = box_client.folder(final_folder_id).get()

    log.info(f"got final Box folder {final_folder}")
    final_folder_path_map = box.fill_folder_path_map(
        box_client, final_folder_id, final_folder_id, box_user, None, None
    )
    log.info(f"built final Box folder path id map {final_folder_path_map}")
    while True:
        for upload_folder_item in upload_folder.get_items():
            try:
                if upload_folder_item.response_object["type"] == "file":
                    upload_file_id = upload_folder_item.response_object["id"]
                    if box_user:
                        upload_file = (
                            box_client.as_user(box_user).file(upload_file_id).get()
                        )
                    else:
                        upload_file = box_client.file(upload_file_id).get()
                        log.info(
                            f"got upload Box file {upload_file} and cached with ID {upload_file_id}"
                        )

                    upload_file_created_at = datetime.datetime.strptime(
                        upload_file.response_object["created_at"][0:-6],
                        FILE_CREATED_AT_DATETIME_FORMAT,
                    )
                    final_folder_path_map_key = f"_{upload_file_created_at.year}|_{upload_file_created_at.month}|_{upload_file_created_at.day}|_{upload_file_created_at.hour}"
                    final_folder = final_folder_path_map.get(final_folder_path_map_key)
                    log.debug(
                        f"found Box folder {final_folder} from key {final_folder_path_map_key}"
                    )
                    upload_file.move(final_folder)
                    log.info(f"moved Box file {upload_file} to folder {final_folder}")
                    upload_file_stream = io.BytesIO()
                    upload_file.download_to(upload_file_stream)
                    upload_file_name = upload_file.response_object["name"]
                    azure_blob_container_client = azure_blob_storage_client.get_blob_client(
                        container=blob_storage_container_name, blob=upload_file_name
                    )
                    azure_blob_container_client.upload_blob(upload_file_stream)
                    log.info(
                        f"uploaded Box file {upload_file_name} to Azure as blob with name {upload_file_name} to container {blob_storage_container_name}"
                    )
            except Exception as e:
                log.error(
                    f"failed processing Box folder {upload_folder} item {upload_folder_item} with {e}"
                )

        time.sleep(0.001)
