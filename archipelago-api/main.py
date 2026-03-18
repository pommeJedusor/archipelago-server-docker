import pickle
import zlib
import glob
import os, asyncio
from web_socket import update_data, web_socket_server
from ArchipelagoData import (
    get_players_from_apsave_data,
    get_players_from_archipelago_data,
)
import zipfile

OUTPUT_PATH = "./output"  # must not end with a '/'


def print_save_data(save_data, depth=0):
    for key, value in save_data.items():
        if type(value) == dict:
            print("  " * depth, key, ":")
            print_save_data(save_data[key], depth + 1)
        else:
            print("  " * depth, key, value)


def get_apsave_file_path():
    # TODO add ways to input the output_path/apsave path
    apsave_files = glob.glob(f"{OUTPUT_PATH}/*.apsave")
    if len(apsave_files) == 0:
        raise Exception(
            f"no .apsave file found in the output path directory {OUTPUT_PATH}"
        )
    # TODO add choosing the latest edited apsave file as default behavior while giving a warning
    if len(apsave_files) > 1:
        raise Exception(
            f"more than one .apsave file found in the output path directory {OUTPUT_PATH}"
        )

    return apsave_files[0]


def get_zip_file_path():
    # TODO add ways to input the output_path/zip path
    zip_files = glob.glob(f"{OUTPUT_PATH}/*.zip")
    if len(zip_files) == 0:
        raise Exception(
            f"no .zip file found in the output path directory {OUTPUT_PATH}"
        )
    # TODO add choosing the latest edited zip file as default behavior while giving a warning
    if len(zip_files) > 1:
        raise Exception(
            f"more than one .zip file found in the output path directory {OUTPUT_PATH}"
        )

    return zip_files[0]


def load_apsave(apsave_file_path: str, players) -> list:
    # TODO check if the file exists
    with open(apsave_file_path, "rb") as f:
        save_data = pickle.loads(zlib.decompress(f.read()))
    return get_players_from_apsave_data(save_data, players)


def load_archipelago_file(zip_file_path: str):
    with zipfile.ZipFile(zip_file_path) as zf:
        for file in zf.namelist():
            if file.endswith(".archipelago"):
                data = zf.read(file)
                break
    data = pickle.loads(zlib.decompress(data[1:]))
    return get_players_from_archipelago_data(data)


async def detect_data_update(
    apsave_file_path: str, archipelago_data: list, interval: int = 1
):
    last_modified = os.path.getmtime(apsave_file_path)
    while True:
        current_modified = os.path.getmtime(apsave_file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            # TODO checks what used fields have been modified and send a websocket event for each
            archipelago_data[0] = load_apsave(apsave_file_path, archipelago_data[0])
            await update_data()
        await asyncio.sleep(interval)


async def main():
    archipelago_data = [
        load_archipelago_file(get_zip_file_path())
    ]  # uses list as a pointer
    archipelago_data[0] = load_apsave(get_apsave_file_path(), archipelago_data[0])

    data_reloader_task = asyncio.create_task(
        detect_data_update(get_apsave_file_path(), archipelago_data)
    )
    websocket_server_task = asyncio.create_task(web_socket_server(archipelago_data))
    await asyncio.gather(data_reloader_task, websocket_server_task)


if __name__ == "__main__":
    asyncio.run(main())
