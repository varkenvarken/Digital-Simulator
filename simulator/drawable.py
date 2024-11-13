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
        self.listeners = []

    def blit(self, surface):
        rect = self.surface.get_rect()
        rect.center = self.pos
        if hasattr(self,"on") and self.on:
            surface.fill("red", rect)
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
        self.state = False

class ConnectorOverlay(Drawable):
    def __init__(self, pos):
        super().__init__(pos)
        self.connectors = []

    def create_overlay(self):
        r = self.surface.get_rect()
        self.overlay = Surface(r.size, pygame.SRCALPHA).convert_alpha()
        return r

    def draw_connectors(self):
        for hotspot in self.connectors:
            draw.circle(
                self.overlay,
                "black",
                hotspot.position + self.overlay.get_rect().center,
                hotspot.radius,
                2,
            )

    def create_connectors(self, connectors):
        r = self.create_overlay()
        self.connectors = connectors
        self.draw_connectors()

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
    def __init__(self, path, pos, size=None):
        self.surface = image.load(Path(__file__).parent / path)
        if size is not None:
            self.surface = transform.smoothscale(self.surface, size)
        self.surface = self.surface.convert_alpha()
        super().__init__(pos)


class Line(ConnectorOverlay):
    def __init__(self, start, end, color="black", linewidth=1):
        super().__init__((end + start) // 2)

        vertical = False
        v = end - start
        if abs(v[1]) > abs(v[0]):  # vertical line
            vertical = True

        # always create the horizontal version
        size = v
        if vertical:
            size = size.yx
        size[0] = max(linewidth + 15, abs(size[0])) + 10
        size[1] = max(linewidth + 15, abs(size[1]))

        self.surface = Surface(size, pygame.SRCALPHA)
        rect = self.surface.get_rect()
        delta = Vector2(5, 0)
        draw.line(
            self.surface, color, rect.midright - delta, rect.midleft + delta, linewidth
        )
        self.surface = self.surface.convert_alpha()

        r = self.surface.get_rect()
        self.create_connectors(
            [
                Hotspot(Vector2(5, r.h // 2) - r.center, 6, "bidirectional"),
                Hotspot(Vector2(r.w - 5, r.h // 2) - r.center, 6, "bidirectional"),
            ]
        )

        if vertical:
            self.rotate(90)


class Gate(Image):
    def __init__(self, path, pos, size=None):
        super().__init__(path, pos, size)

        r = self.surface.get_rect()

        self.create_connectors(
            [Hotspot(Vector2(r.w - 10, r.h // 2) - r.center, 6, "output")]
            + [
                Hotspot(Vector2(hotspot) - r.center, 6, "input")
                for hotspot in ((10, r.h // 3), (10, 2 * r.h // 3))
            ]
        )


class Input(Image):
    def __init__(self, pos, size=None):
        super().__init__("icons/INPUT.svg", pos, size)

        r = self.surface.get_rect()

        self.create_connectors(
            [
                Hotspot(
                    Vector2(r.w - 8, r.h // 2) - r.center,
                    6,
                    "output",
                )
            ]
        )

        self.on = True

    def toggle(self):
        self.on = not self.on
        

class Output(Image):
    def __init__(self, pos, size=None):
        super().__init__("icons/OUTPUT.svg", pos, size)

        r = self.surface.get_rect()

        self.create_connectors([Hotspot(Vector2(8, r.h // 2) - r.center, 6, "input")])


class AndGate(Gate):
    def __init__(self, pos, size=None):
        super().__init__("icons/AND_ANSI_Labelled.svg", pos, size)

    def eval(self):
        state = True
        for ci,c in enumerate(self.connectors):
            if c.direction == "input":
                state = state and c.state
                print(f"{c.state=} {id(c)=}")
        return state 