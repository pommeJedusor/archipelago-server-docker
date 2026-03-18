import asyncio
import websockets
import json
import signal

CLIENTS = set()
ARCHIPELAGO_DATA = []
PORT = 8765
ADDRESS = "0.0.0.0"
PROTOCOL = "ws"
# TODO add change queue to update data using the websocket


async def handler(websocket):
    CLIENTS.add(websocket)
    await websocket.send(json.dumps(ARCHIPELAGO_DATA[0]))
    try:
        async for message in websocket:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        CLIENTS.discard(websocket)


async def web_socket_server(archipelago_data: list):
    global ARCHIPELAGO_DATA
    ARCHIPELAGO_DATA = archipelago_data

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    # TODO add ways to input the address and port
    async with websockets.serve(handler, ADDRESS, PORT):
        print(f"Server running on {PROTOCOL}://{ADDRESS}:{PORT}")
        await stop  # Run until SIGTERM
