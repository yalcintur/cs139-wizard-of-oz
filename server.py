from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os

app = FastAPI()

connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            message = await websocket.receive_text()
            for client in connected_clients:
                if client != websocket:
                    await client.send_text(message)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
