from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from chip8.chip8 import Chip8 

STATIC_DIR = Path(__file__).parent / "static"

ROM_PATH = "roms/Space Invaders [David Winter].ch8"



app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name='static')

ch8 = Chip8(chip48_mode=True)
ch8.load_rom(ROM_PATH)
ch8.run(steps=2000)

@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/frame")
def frame() -> list[int]:
    return list(ch8.display)