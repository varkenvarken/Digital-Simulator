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
        self.surface = Surface((2*radius, 2*radius), pygame.SRCALPHA)
        draw.circle(self.surface, color, (radius, radius), radius, linewidth)
        self.surface = self.surface.convert_alpha()


class Line(Drawable):
    def __init__(self, start, end, color="black", linewidth=1):
        super().__init__(start)

        self.vertical = False
        self.away = False

        v = end - start
        if abs(v[1]) > abs(v[0]):  # vertical line
            self.vertical = True
            if end[1] > start[1]:  # pointing down
                self.away = True
        else:
            if end[0] < start[0]:  # pointing left
                self.away = True

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

    def blit(self, surface):
        rect = self.surface.get_rect()
        if self.vertical:
            if self.away:
                rect.midtop = self.pos
            else:
                rect.midbottom = self.pos
        else:
            if self.away:
                rect.midright = self.pos
            else:
                rect.midleft = self.pos
        surface.blit(self.surface, rect)
        if self.active:
            draw.rect(surface, "orange", rect, 2)
        if self.selected:
            draw.rect(surface, "red", rect, 1)

    def collidepoint(self, pos):
        rect = self.surface.get_rect()
        print(pos, self.pos, rect, self.vertical, self.away)
        if self.vertical:
            if self.away:
                rect.midtop = self.pos
            else:
                rect.midbottom = self.pos
        else:
            if self.away:
                rect.midright = self.pos
            else:
                rect.midleft = self.pos
        print(pos, self.pos, rect)
        return rect.collidepoint(*pos)


    def collideconnector(self, pos):
        return False, None


def rotate_rectangle(r: Rect, angle):
    angle = radians(angle)
    s = sin(angle)
    c = cos(angle)

    def rotate(p):
        return p[0] * c - p[1] * s, p[0] * s + p[1] * c

    print(r)

    center = r.center
    r.center = Vector2(0, 0)

    tl = rotate(r.topleft)
    tr = rotate(r.topright)
    bl = rotate(r.bottomleft)
    br = rotate(r.bottomright)

    r.topleft = tl
    r.bottomright = br
    r.center = center
    print(r)

    return r


class Hotspot:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius


class AndGate(Image):
    def __init__(self, pos, size=None):
        super().__init__("icons/AND_ANSI_Labelled.svg", pos, size)
        r = self.surface.get_rect()
        self.overlay = Surface(r.size, pygame.SRCALPHA).convert_alpha()
        self.output = Hotspot(Vector2(r.w-10, r.h//2) -
                              self.overlay.get_rect().center, 6)

        draw.circle(self.overlay, "black", self.output.position +
                    self.overlay.get_rect().center, self.output.radius, 2)

        self.inputs = []
        for hotspot in ((10, r.h//3), (10, 2*r.h//3)):
            draw.circle(self.overlay, "black", hotspot, 6, 2)
            self.inputs.append(
                Hotspot(Vector2(hotspot) - self.overlay.get_rect().center, 6))

        self.angle = 0

    def blit(self, surface):
        super().blit(surface)
        rect = self.overlay.get_rect()
        rect.center = self.pos
        surface.blit(self.overlay, rect)

    def rotate(self, angle):
        super().rotate(angle)
        self.overlay = transform.rotate(self.overlay, angle)

        self.output.position.rotate_ip(-angle)

        self.angle = angle

    def collideconnector(self, pos):
        p = Vector2(pos)
        rp = p - self.pos
        result = (self.output.position - rp).length() <= self.output.radius
        if result:
            return result, self.output.position + self.pos
        else:
            for hotspot in self.inputs:
                result = (hotspot.position - rp).length() <= hotspot.radius
                if result:
                    return result, hotspot.position + self.pos
        return False, None


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

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
