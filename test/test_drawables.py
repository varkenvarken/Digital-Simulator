import pygame

from simulator.component import AndGate

class TestDrawables:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        g = AndGate((100,100))
        assert g.pos == pygame.math.Vector2(100,100)
