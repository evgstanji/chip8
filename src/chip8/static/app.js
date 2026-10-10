const WIDTH = 64;
const HEIGHT = 32;
const BACKGROUND = "#141414";
const PIXEL = "#e6e6e6";

const ctx = document.getElementById("screen").getContext("2d");

function draw(pixels) {
  ctx.fillStyle = BACKGROUND;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = PIXEL;
  pixels.forEach((on, i) => {
    if (on) ctx.fillRect(i % WIDTH, Math.floor(i / WIDTH), 1, 1);
  });
}

const socket = new WebSocket(`ws://${location.host}/ws`);
socket.binaryType = "arraybuffer";
socket.onmessage = (event) => draw(new Uint8Array(event.data));

const KEYMAP = {
  Digit1: 0x1, Digit2: 0x2, Digit3: 0x3, Digit4: 0xC,
  KeyQ: 0x4, KeyW: 0x5, KeyE: 0x6, KeyR: 0xD,
  KeyA: 0x7, KeyS: 0x8, KeyD: 0x9, KeyF: 0xE,
  KeyZ: 0xA, KeyX: 0x0, KeyC: 0xB, KeyV: 0xF,
};

function sendKey(event, pressed) {
  const key = KEYMAP[event.code];
  if (key === undefined || event.repeat) return;
  socket.send(JSON.stringify({ key, pressed }));
}

document.addEventListener("keydown", (event) => sendKey(event, true));
document.addEventListener("keyup", (event) => sendKey(event, false));
