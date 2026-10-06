import sys

import pygame

from chip8.chip8 import WIDTH, HEIGHT, Chip8

SCALE = 10 # pixel size in chip-8 display
FPS = 60
INSTRUCTIONS_PER_SECOND = 700 # the number of instructions executed on a real Chip-8 per second
INSTRUCTIONS_PER_FRAME = INSTRUCTIONS_PER_SECOND // FPS


GREY_BACKGROUND = (20, 20, 20) # grey color in RGB
WHITE = (230, 230, 230) # white color in RGB

KEYMAP = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
}

def draw(screen: pygame.Surface, display: bytearray) -> None:
    screen.fill(GREY_BACKGROUND)
    for i, pixel in enumerate(display):
        if pixel:
            y, x = i // WIDTH, i % WIDTH 
            pygame.draw.rect(screen, WHITE, (x * SCALE, y * SCALE, SCALE, SCALE))
    
    
def main() -> None:
    ch8 = Chip8()
    ch8.load_rom(sys.argv[1])
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key in KEYMAP:
                ch8.keys[KEYMAP[event.key]] = True
            if event.type == pygame.KEYUP and event.key in KEYMAP:
                ch8.keys[KEYMAP[event.key]] = False
        ch8.run(steps=INSTRUCTIONS_PER_FRAME)
        ch8.tick_timers()
        draw(screen, ch8.display)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()