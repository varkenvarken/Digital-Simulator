import pygame

from simulator.component import AndGate, NandGate, Input, Output, Line


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
        p = (100, 100)
        g = AndGate(p)
        s = pygame.display.get_surface()
        s.fill("white")
        g.blit(s)
        assert s.get_at(p) == pygame.Color(255, 255, 255)

        g.state = True
        g.blit(s)
        assert s.get_at(p) == pygame.Color(0, 255, 0)
