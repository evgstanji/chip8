# chip8

<одно-два предложения: что это и зачем ты его писал>

![demo](docs/demo.gif)

## What works
- <все инструкции; что проходят тестовые ROM corax+ и flags>
- <какие игры идут; Space Invaders — с --chip48>

## Run
```
uv run chip8-window path/to/game.ch8
uv run chip8-window --chip48 path/to/game.ch8
```

## Keys
<таблица: клавиши ПК 1234/QWER/ASDF/ZXCV → кнопки CHIP-8>

## How it works
<2–3 строки: fetch → decode → execute, 60 кадров в секунду, ~700 инструкций в секунду, таймеры 60 Гц>

ROMs are not included.