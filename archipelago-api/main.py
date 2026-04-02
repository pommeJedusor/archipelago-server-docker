import os, asyncio
from web_socket import update_data, web_socket_server
from ArchipelagoData import ArchipelagoData, get_apsave_file_path, load_apsave


async def detect_data_update(
    apsave_file_path: str, archipelago_data: ArchipelagoData, interval: int = 1
):
    last_modified = os.path.getmtime(apsave_file_path)
    while True:
        current_modified = os.path.getmtime(apsave_file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            # TODO checks what used fields have been modified and send a websocket event for each
            archipelago_data.players = load_apsave(
                apsave_file_path, archipelago_data.players
            )
            await update_data()
        await asyncio.sleep(interval)


async def main():
    archipelago_data = ArchipelagoData()

    data_reloader_task = asyncio.create_task(
        detect_data_update(get_apsave_file_path(), archipelago_data)
    )
    websocket_server_task = asyncio.create_task(web_socket_server(archipelago_data))
    await asyncio.gather(data_reloader_task, websocket_server_task)


if __name__ == "__main__":
    asyncio.run(main())
