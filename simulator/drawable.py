from abc import abstractmethod, ABCMeta
from typing import Tuple, Sequence
from pathlib import Path

import pygame
from pygame import Surface, draw, Rect, transform, Vector2, image, time


class Drawable:
    def __init__(self, pos):
         self.selected = False
         self.active = False
         self.pos = Vector2(pos)
    
    def blit(self, surface):
        rect = self.surface.get_rect()
        rect.center = self.pos
        surface.blit(self.surface,rect)
        if self.active:
             draw.rect(surface, "orange", rect, 2)
        if self.selected:
             draw.rect(surface, "red", rect, 1)
        
    def rotate(self, angle):
         self.surface = transform.rotate(self.surface, angle)
    
    def collidepoint(self, pos):
        rect = self.surface.get_rect()
        rect.center = self.pos
        return rect.collidepoint(*pos)
   
class Image(Drawable):
    def __init__(self, path, pos, size=None):
        super().__init__(pos)
        self.surface = image.load(Path(__file__).parent / path)
        if size is not None:
            self.surface = transform.smoothscale(self.surface, size)
        self.surface = self.surface.convert_alpha()

class Circle(Drawable):
     def __init__(self, pos, radius, color="black", linewidth=1):
          super().__init__(pos)
          self.surface = Surface((2*radius,2*radius), pygame.SRCALPHA)
          draw.circle(self.surface, color, (radius,radius), radius, linewidth)
          self.surface = self.surface.convert_alpha()
  
if __name__ == "__main__":
    FPS = 60

    pygame.init()

    clock = time.Clock()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Drawable test")
    screen.fill("white")

    drawables = [Image("icons/AND_ANSI_Labelled.svg", (x, 300)) for x in (200,400,600)]

    # Dragging control variables
    dragging = False
    dragged_rect_index = None
    offset = Vector2(0,0)

    active_object = None

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(drawables):
                    if r.collidepoint(event.pos):
                        active_object = i
                        dragging = True
                        dragged_rect_index = i
                        # Calculate offset to maintain position relative to click
                        offset = r.pos - event.pos
                        for d2 in drawables:
                            d2.active = False
                        r.active = True
            elif event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging when the mouse button is released
                dragging = False
                dragged_rect_index = None
            elif event.type == pygame.MOUSEMOTION:
                # Update the position of the drawable while dragging
                if dragging and dragged_rect_index is not None:
                    r = drawables[dragged_rect_index]
                    r.pos = event.pos + offset
            elif event.type == pygame.KEYUP:
                print(event)
                if event.unicode == 'r' and active_object is not None:
                    drawables[active_object].rotate(90)

        screen.fill("white")

        for d in drawables:
            d.blit(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
