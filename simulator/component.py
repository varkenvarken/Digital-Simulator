# Copyright 2024 - 2024, Michel Anders and the Digital Simulator contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import abstractmethod, ABCMeta
from typing import Tuple, Sequence
from pathlib import Path
import json

import pygame
from pygame import Surface, draw, Rect, transform, Vector2, image, time

unknown = Surface((16, 16), pygame.SRCALPHA)
r = unknown.get_rect()
draw.line(unknown, "black", r.bottomleft, r.topright)
draw.line(unknown, "black", r.topleft, r.bottomright)


class Drawable:

    def __init__(self, pos, angle=0, label="unknown"):
        self.selected = False
        self.active = False
        self.pos = Vector2(pos)
        self.angle = angle
        self.listeners = []
        self.state = False
        self.label = label

    def blit(self, surface):
        if self.state:
            rect = self.surface.get_rect()
            rect.center = self.pos
            surface.blit(self.surface_on, rect)
        else:
            rect = self.surface_on.get_rect()
            rect.center = self.pos
            surface.blit(self.surface, rect)
        if self.active:
            draw.rect(surface, "orange", rect, 2)
        if self.selected:
            draw.rect(surface, "red", rect, 1)

    def rotate(self, angle):
        self.surface = transform.rotate(self.surface, angle)
        self.surface_on = transform.rotate(self.surface_on, angle)
        self.angle = angle

    def collidepoint(self, pos):
        rect = self.surface.get_rect()
        rect.center = self.pos
        return rect.collidepoint(*pos)


class Hotspot:
    def __init__(self, position, radius, direction, label=""):
        self.position = position
        self.radius = radius
        self.direction = direction
        self.state = False
        self.label = label


class ConnectorOverlay(Drawable):
    # TODO add hotspot labels
    # TODO make connectors reflect on-state

    def __init__(self, pos, angle=0, label="unknown"):
        super().__init__(pos, angle, label)
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
    def __init__(self, path, path_on, pos, angle=0, label="unknown", size=None):
        self.surface = image.load(Path(__file__).parent / path)
        self.surface_on = image.load(Path(__file__).parent / path_on)
        if size is not None:
            self.surface = transform.smoothscale(self.surface, size)
            self.surface_on = transform.smoothscale(self.surface_on, size)
        self.surface = self.surface.convert_alpha()
        self.surface_on = self.surface_on.convert_alpha()
        super().__init__(pos, angle, label)


class Line(ConnectorOverlay):
    def __init__(
        self,
        start,
        end,
        angle=0,
        label="",
        color="black",
        color_on="green",
        linewidth=1,
    ):
        start = Vector2(start)
        end = Vector2(end)

        super().__init__((end + start) // 2, angle, label)

        # we need to save this too, if we want to be able to serialize it.
        self.start = start
        self.end = end

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
        self.surface_on = Surface(size, pygame.SRCALPHA)
        rect = self.surface.get_rect()
        delta = Vector2(5, 0)
        draw.line(
            self.surface, color, rect.midright - delta, rect.midleft + delta, linewidth
        )
        draw.line(
            self.surface_on,
            color_on,
            rect.midright - delta,
            rect.midleft + delta,
            linewidth,
        )
        self.surface = self.surface.convert_alpha()
        self.surface_on = self.surface_on.convert_alpha()

        r = self.surface.get_rect()
        self.create_connectors(
            [
                Hotspot(Vector2(5, r.h // 2) - r.center, 6, "bidirectional"),
                Hotspot(Vector2(r.w - 5, r.h // 2) -
                        r.center, 6, "bidirectional"),
            ]
        )

        if vertical:
            self.rotate(90)


class Gate(Image):
    def __init__(self, path, path_on, pos, angle=0, label="unknown", size=None):
        super().__init__(path, path_on, pos, angle, label, size)

        r = self.surface.get_rect()

        self.create_connectors(
            [Hotspot(Vector2(r.w, r.h // 2) - r.center, 6, "output")]
            + [
                Hotspot(Vector2(hotspot) - r.center, 6, "input")
                for hotspot in ((0, r.h // 3), (0, 2 * r.h // 3))
            ]
        )

    def draw_connectors(self):
        ...

class Input(Image):
    def __init__(self, pos, angle=0, label="input", size=None):
        super().__init__(
            "icons/80x60/INPUT_OFF.svg", "icons/80x60/INPUT_ON.svg", pos, angle, label, size
        )

        r = self.surface.get_rect()

        self.create_connectors(
            [
                Hotspot(
                    Vector2(r.w, r.h // 2) - r.center,
                    6,
                    "output",
                )
            ]
        )

        self.on = True

    def toggle(self):
        self.state = not self.state


class Output(Image):
    def __init__(self, pos, angle=0, label="output", size=None):
        super().__init__(
            "icons/80x60/OUTPUT_OFF.svg", "icons/80x60/OUTPUT_ON.svg", pos, angle, label, size
        )

        r = self.surface.get_rect()

        self.create_connectors(
            [Hotspot(Vector2(0, r.h // 2) - r.center, 6, "input")])


class AndGate(Gate):
    def __init__(self, pos, angle=0, label="and", size=None):
        super().__init__(
            "icons/80x60/AND_OFF.svg",
            "icons/80x60/AND_ON.svg",
            pos,
            angle,
            label,
            size,
        )


class NandGate(Gate):
    def __init__(self, pos, angle=0, label="nand", size=None):
        super().__init__(
            "icons/80x60/NAND_OFF.svg",
            "icons/80x60/NAND_ON.svg",
            pos,
            angle,
            label,
            size,
        )


class ComponentEncoder(json.JSONEncoder):
    def default(self, obj):
        # Convert custom classes to dictionaries
        if isinstance(obj, Line):
            return {
                "type": obj.__class__.__name__,
                "dict": {
                    "start": obj.start,
                    "end": obj.end,
                    "angle": obj.angle,
                    "label": obj.label,
                },
            }
        elif isinstance(obj, Drawable):
            return {
                "type": obj.__class__.__name__,
                "dict": {"pos": obj.pos, "angle": obj.angle, "label": obj.label},
            }
        elif isinstance(obj, Vector2):
            return (obj.x, obj.y)
        return super().default(obj)


class ComponentDecoder:
    def __init__(self, obj):
        drawables = obj["drawables"]
        library = obj["library"]
        self.d_objs = []
        self.l_objs = []
        for d in drawables:
            t = globals()[d["type"]]
            d_obj = t(**d["dict"])
            self.d_objs.append(d_obj)
        for l in library:
            t = globals()[l["type"]]
            l_obj = t(**l["dict"])
            self.l_objs.append(l_obj)
