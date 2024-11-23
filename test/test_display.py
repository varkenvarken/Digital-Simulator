import pygame
import pygame.locals

from simulator.display import Display

class TestDisplay:

    def test_create(self):
        display = Display(title="test")
        display.quit()
    
    def test_editmode(self):
        display = Display(title="test")
        pygame.event.post(pygame.Event(pygame.QUIT,{}))    
        reason = display.edit()
        assert reason == "Quit"

    def test_simulationmode(self):
        display = Display(title="test")
        pygame.event.post(pygame.Event(pygame.KEYUP,{"key": pygame.locals.K_s}))    
        reason = display.edit()
        assert reason == "Start simulation"
        pygame.event.post(pygame.Event(pygame.QUIT,{}))    
        reason = display.simulate()
        assert reason == "Quit"