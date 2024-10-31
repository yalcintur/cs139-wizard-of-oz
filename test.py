import asyncio
import websockets

async def websocket_client():
    uri = "wss://cs139-woz-production.up.railway.app/ws" 
    async with websockets.connect(uri) as websocket:
        print("Sent message to server.")

        while True:
            message = await websocket.recv()
            print("Received message from server:", message)

asyncio.run(websocket_client())
