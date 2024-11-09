from abc import abstractmethod, ABCMeta
from typing import Tuple
from pygame import Surface, draw, Rect


class Drawable:
    def __init__(self, color, linewidth):
        self.color = color
        self.linewidth = linewidth

    @property
    def x(self):
        return self.drawable.x

    @x.setter
    def x(self, value):
        self.drawable.x = value

    @property
    def y(self):
        return self.drawable.y

    @y.setter
    def y(self, value):
        self.drawable.y = value

    @property
    def w(self):
        return self.drawable.w

    @w.setter
    def w(self, value):
        self.drawable.w = value

    @property
    def h(self):
        return self.drawable.h

    @h.setter
    def h(self, value):
        self.drawable.h = value

    def collidepoint(self, *args, **kwargs):
        return self.drawable.collidepoint(*args, **kwargs)

    def __str__(self):
        return f"{self.drawable}"
    
class Rectangle(Drawable):
    def __init__(self, x, y, w, h, color="black", linewidth=2):
        self.drawable = pygame.Rect(x, y, w, h)
        super().__init__(color, linewidth)

    def draw(self, screen:Surface):
        pygame.draw.rect(screen, self.color, self.drawable, self.linewidth)

if __name__ == "__main__":
    import pygame
    pygame.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Drawable test")
    screen.fill("white")

    rectangles = [ Rectangle(width//2, height//2, 20, 10), Rectangle(width//4, height//4, 20, 10)]

    # Dragging control variables
    dragging = False
    dragged_rect_index = None
    offset_x, offset_y = 0, 0

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i,r in enumerate(rectangles):
                    if r.collidepoint(event.pos):
                        dragging = True
                        dragged_rect_index = i  # later we work with more than one rectangle
                        # Calculate offset to maintain position relative to click
                        offset_x = r.x - event.pos[0]
                        offset_y = r.y - event.pos[1]
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging when the mouse button is released
                dragging = False
                dragged_rect_index = None
            elif event.type == pygame.MOUSEMOTION:
                # Update the position of the rectangle while dragging
                if dragging and dragged_rect_index is not None:
                    r = rectangles[dragged_rect_index]
                    r.x = event.pos[0] + offset_x
                    r.y = event.pos[1] + offset_y

        screen.fill("white")
        
        for r in rectangles:
            r.draw(screen)
        
        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()
