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