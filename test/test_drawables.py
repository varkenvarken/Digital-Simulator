import json
import pygame

from simulator.component import AndGate, NandGate, Input, Output, Line, ComponentEncoder


class TestDrawables:

    def test_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        pos = pygame.math.Vector2(100, 100)
        pos2 = pygame.math.Vector2(200, 100)
        pos3 = pygame.math.Vector2(100, 200)

        gate = AndGate(pos)
        assert gate.pos == pos

        gate = NandGate(pos)
        assert gate.pos == pos

        img = Input(pos)
        assert img.pos == pos

        img = Output(pos)
        assert img.pos == pos

        line = Line(pos, pos2)
        assert line.start == pos
        assert line.end == pos2
        assert line.pos == (pos + pos2) // 2
        assert line.angle == 0

        line = Line(pos, pos3)
        assert line.start == pos
        assert line.end == pos3
        assert line.pos == (pos + pos3) // 2
        assert line.angle == 90

    def test_blit(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        pos = pygame.math.Vector2(100, 100)
        pos2 = pygame.math.Vector2(200, 100)
        center = (pos + pos2) // 2

        gate = AndGate(pos)
        surface = pygame.display.get_surface()
        surface.fill("white")

        gate.blit(surface)
        assert surface.get_at(pos) == pygame.Color(255, 255, 255)

        gate.state = True
        gate.blit(surface)
        assert surface.get_at(pos) == pygame.Color(0, 255, 0)

        line = Line(pos, pos2)
        line.blit(surface)
        assert surface.get_at(pos) == pygame.Color(0,0,0)

        line.state = True
        line.blit(surface)
        assert surface.get_at(pos) == pygame.Color(0, 255, 0)

    def test_component_encoder(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        pos = pygame.math.Vector2(100, 100)
        pos2 = pygame.math.Vector2(200, 100)
        s = json.dumps([AndGate(pos),pos,Line(pos,pos2)], cls=ComponentEncoder, indent=None)
        assert s == '[{"type": "AndGate", "dict": {"pos": [100.0, 100.0], "angle": 0, "label": "and"}}, [100.0, 100.0], {"type": "Line", "dict": {"start": [100.0, 100.0], "end": [200.0, 100.0], "angle": 0, "label": ""}}]'

    def test_collidepoint_andgate(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        pos = pygame.math.Vector2(100, 100)
        pos2 = pygame.math.Vector2(200, 100)
        
        gate = AndGate(pos)
        assert gate.collidepoint(pos)
        assert not gate.collidepoint(pos2)

    def test_collideconnector_andgate(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        pos = pygame.math.Vector2(100, 100)
        # gate icons are 50 high and 120 wide
        # they have 2 input connectors on the left, 10 pixels in, at 1/3 and 2/3 height
        # and 1 output connector on the right, 10 pixels in, at 1/2 height
        # connectors have a radius of 6 pixels
        gate = AndGate(pos)
        # the position of the gate is its nominal center, so the hotspot positions are calculated relative to that center
        # frist we check the output
        click = pos+pygame.math.Vector2(60-10,0)
        con = gate.collideconnector(click)
        assert con[1] == click
        click = pos+pygame.math.Vector2(60-10,7)
        con = gate.collideconnector(click)
        assert con[1] == None
        # then the inputs
        click = pos+pygame.math.Vector2(-60+10,-25//3)
        con = gate.collideconnector(click)
        assert con[1] == click
        click = pos+pygame.math.Vector2(-60+10,+25//3)
        con = gate.collideconnector(click)
        assert con[1] == click