import asyncio

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from chip8.chip8 import Chip8, NUMBER_KEYS

STATIC_DIR = Path(__file__).parent / "static"

ROM_PATH = "roms/Tetris [Fran Dachille, 1991].ch8"

FPS = 60
INSTRUCTIONS_PER_SECOND = 700
INSTRUCTIONS_PER_FRAME = INSTRUCTIONS_PER_SECOND // FPS

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name='static')

async def receive_keys(websocket: WebSocket, ch8: Chip8) -> None:
    try:
        while True:
            message = await websocket.receive_json()
            key = message["key"]
            pressed = message["pressed"]
            if 0 <= key < NUMBER_KEYS:
                ch8.keys[key] = pressed
    except WebSocketDisconnect:
        pass

@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

@app.websocket("/ws")
async def stream(websocket: WebSocket) -> None:
    await websocket.accept()
    
    ch8 = Chip8(chip48_mode=True)
    ch8.load_rom(ROM_PATH)
    
    task = asyncio.create_task(receive_keys(websocket=websocket, ch8=ch8))
    
    try:
        while True:
            ch8.run(steps=INSTRUCTIONS_PER_FRAME)
            ch8.tick_timers()
            await websocket.send_bytes(bytes(ch8.display))
            await asyncio.sleep(1/FPS)
    except WebSocketDisconnect:
        pass
    finally:
        task.cancel()