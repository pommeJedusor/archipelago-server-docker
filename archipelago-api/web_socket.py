import asyncio
import websockets
import json
import signal

from ArchipelagoData import ArchipelagoData

CLIENTS = set()
ARCHIPELAGO_DATA = None
PORT = 8765
ADDRESS = "0.0.0.0"
PROTOCOL = "ws"
# TODO add change queue to update data using the websocket


async def handler(websocket):
    assert type(ARCHIPELAGO_DATA) == ArchipelagoData

    CLIENTS.add(websocket)
    await websocket.send("players " + json.dumps(ARCHIPELAGO_DATA.players))
    try:
        async for message in websocket:
            assert type(message) == str
            if ARCHIPELAGO_DATA.datapackages.get(message):
                await websocket.send(
                    "datapackage " + json.dumps(ARCHIPELAGO_DATA.datapackages[message])
                )
                continue
            if message.startswith("hash ") and ARCHIPELAGO_DATA.datapackages.get(
                message[5:]
            ):
                await websocket.send(
                    "hash_datapackage "
                    + ARCHIPELAGO_DATA.datapackages[message[5:]]["hash"]
                    + " "
                    + message[5:]
                )

    except websockets.ConnectionClosed:
        pass
    finally:
        CLIENTS.discard(websocket)


async def update_data():
    assert type(ARCHIPELAGO_DATA) == ArchipelagoData

    for client in CLIENTS:
        await client.send("players " + json.dumps(ARCHIPELAGO_DATA.players))


async def web_socket_server(archipelago_data: ArchipelagoData):
    global ARCHIPELAGO_DATA
    ARCHIPELAGO_DATA = archipelago_data

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    # TODO add ways to input the address and port
    async with websockets.serve(handler, ADDRESS, PORT):
        print(f"Server running on {PROTOCOL}://{ADDRESS}:{PORT}")
        await stop  # Run until SIGTERM
