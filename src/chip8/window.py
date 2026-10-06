import sys

import pygame

from chip8.chip8 import WIDTH, HEIGHT, Chip8

SCALE = 10 # pixel size in chip-8 display
FPS = 60
INSTRUCTIONS_PER_SECOND = 700 # the number of instructions executed on a real Chip-8 per second
INSTRUCTIONS_PER_FRAME = INSTRUCTIONS_PER_SECOND // FPS


GREY_BACKGROUND = (20, 20, 20) # grey color in RGB
WHITE = (230, 230, 230) # white color in RGB

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
        ch8.run(steps=INSTRUCTIONS_PER_FRAME)
        draw(screen, ch8.display)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()