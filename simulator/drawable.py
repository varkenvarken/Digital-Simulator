from abc import abstractmethod, ABCMeta
from typing import Tuple, Sequence
from pathlib import Path
from math import radians, sin, cos

import pygame
from pygame import Surface, draw, Rect, transform, Vector2, image, time


class Drawable:
    def __init__(self, pos):
        self.selected = False
        self.active = False
        self.pos = Vector2(pos)
        self.angle = 0

    def blit(self, surface):
        rect = self.surface.get_rect()
        rect.center = self.pos
        surface.blit(self.surface, rect)
        if self.active:
            draw.rect(surface, "orange", rect, 2)
        if self.selected:
            draw.rect(surface, "red", rect, 1)

    def rotate(self, angle):
        self.surface = transform.rotate(self.surface, angle)
        self.angle = angle

    def collidepoint(self, pos):
        rect = self.surface.get_rect()
        rect.center = self.pos
        return rect.collidepoint(*pos)


class Hotspot:
    def __init__(self, position, radius, direction):
        self.position = position
        self.radius = radius
        self.direction = direction


class ConnectorOverlay(Drawable):
    def __init__(self, pos, connectors=None):
        super().__init__(pos)
        self.connectors = connectors
        if connectors:
            self.create_overlay()
            self.draw_connectors()
        else:
            self.connectors = []

    def create_overlay(self):
        r = self.surface.get_rect()
        self.overlay = Surface(r.size, pygame.SRCALPHA).convert_alpha()
        return r

    def draw_connectors(self):
        for hotspot in self.connectors:
            draw.circle(self.overlay, "black", hotspot.position +
                        self.overlay.get_rect().center, hotspot.radius, 2)

    def blit(self, surface):
        super().blit(surface)
        rect = self.overlay.get_rect()
        rect.center = self.pos
        surface.blit(self.overlay, rect)

    def rotate(self, angle):
        super().rotate(angle)
        self.overlay = transform.rotate(self.overlay, angle)
        for hotspot in self.connectors:
            hotspot.position.rotate_ip(-angle)

    def collideconnector(self, pos):
        p = Vector2(pos)
        rect = self.surface.get_rect()
        rect.center = self.pos
        rp = p - rect.center
        for hotspot in self.connectors:
            result = (hotspot.position - rp).length() <= hotspot.radius
            if result:
                return result, hotspot.position + rect.center
        return False, None

class Image(ConnectorOverlay):
    def __init__(self, path, pos, connectors=None, size=None):
        self.surface = image.load(Path(__file__).parent / path)
        if size is not None:
            self.surface = transform.smoothscale(self.surface, size)
        self.surface = self.surface.convert_alpha()
        super().__init__(pos, connectors)
        

class Line(ConnectorOverlay):
    def __init__(self, start, end, color="black", linewidth=1):
        super().__init__((end + start)//2)

        self.vertical = False
        v = end - start
        if abs(v[1]) > abs(v[0]):  # vertical line
            self.vertical = True
        size = v
        size[0] = max(linewidth+15, abs(size[0]))
        size[1] = max(linewidth+15, abs(size[1]))
        self.surface = Surface(size, pygame.SRCALPHA)
        rect = self.surface.get_rect()
        if self.vertical:
            draw.line(self.surface, color, rect.midtop,
                      rect.midbottom, linewidth)
        else:
            draw.line(self.surface, color, rect.midright,
                      rect.midleft, linewidth)
        self.surface = self.surface.convert_alpha()

        r = self.create_overlay()

        if self.vertical:
            self.connectors.append(Hotspot(Vector2(r.w//2, 0) -
                                  self.overlay.get_rect().center, 6, "output"))
            self.connectors.append(Hotspot(Vector2(r.w//2, r.h) -
                                       self.overlay.get_rect().center, 6, "input"))
        else:
            self.connectors.append(Hotspot(Vector2(0, r.h//2) -
                                  self.overlay.get_rect().center, 6, "output"))
            self.connectors.append(Hotspot(Vector2(r.w, r.h//2) -
                                       self.overlay.get_rect().center, 6, "input"))

        self.draw_connectors()




class Gate(Image):
    def __init__(self, path, pos, size=None):
        super().__init__(path, pos, size)
        
        r = self.create_overlay()

        self.connectors.append(Hotspot(Vector2(r.w-10, r.h//2) -
                              self.overlay.get_rect().center, 6, "output"))
        for hotspot in ((10, r.h//3), (10, 2*r.h//3)):
            draw.circle(self.overlay, "black", hotspot, 6, 2)
            self.connectors.append(
                Hotspot(Vector2(hotspot) - self.overlay.get_rect().center, 6, "input"))

        self.draw_connectors()

class AndGate(Gate):
    def __init__(self, pos, size=None):
        super().__init__("icons/AND_ANSI_Labelled.svg", pos, size)

if __name__ == "__main__":
    FPS = 60

    pygame.init()
    pygame.display.set_icon(image.load(
        Path(__file__).parent / "icons/AND_ANSI_Labelled.svg"))

    clock = time.Clock()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Drawable test")
    screen.fill("white")

    drawables = [AndGate((x, 300)) for x in (200, 400, 600)]

    # Dragging control variables
    dragging = False
    dragged_rect_index = None
    offset = Vector2(0, 0)

    active_object = None

    drawing = False
    line_start = Vector2(0, 0)
    line_end = Vector2(0, 0)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if drawing:
                    drawables.append(
                        Line(line_start, line_end, color="blue", linewidth=2))
                    line_start = line_end
                else:
                    for i, r in enumerate(drawables):
                        click, connector_position = r.collideconnector(
                            event.pos)
                        if click:
                            print(f"click on object {i} output at {event.pos}")
                            drawing = True
                            line_start = Vector2(connector_position)
                            line_end = Vector2(connector_position)
                            break
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
                if dragging:
                    # Stop dragging when the mouse button is released
                    dragging = False
                    dragged_rect_index = None
                elif drawing:
                    if event.button == 3:
                        drawing = False
            elif event.type == pygame.MOUSEMOTION:
                # Update the position of the drawable while dragging
                if dragging and dragged_rect_index is not None:
                    r = drawables[dragged_rect_index]
                    r.pos = event.pos + offset
                elif drawing:
                    line_end = Vector2(event.pos)

            elif event.type == pygame.KEYUP:
                print(event)
                if event.unicode == 'r' and active_object is not None:
                    drawables[active_object].rotate(90)

        screen.fill("white")

        for d in drawables:
            d.blit(screen)

        if drawing:
            dl = line_end - line_start
            if dl.length() > 4:
                if abs(dl.x) > abs(dl.y):
                    line_end.y = line_start.y
                else:
                    line_end.x = line_start.x
            draw.line(screen, "green", line_start, line_end, 2)

        if True:  # TODO make this a toggle
            x, y = pygame.mouse.get_pos()
            r = screen.get_rect()
            draw.line(screen, "black", (0, y), (r.w, y))
            draw.line(screen, "black", (x, 0), (x, r.h))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
