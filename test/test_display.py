import pytest
import pygame
import pygame.locals
import pygame_gui
from simulator.display import Display

class TestDisplay:

    @staticmethod
    def post_and_next_frame(event, generator):
        pygame.event.post(event)
        next(generator)

    def test_create(self):
        display = Display(title="test")
        display.quit()
    
    def test_editmode(self):
        display = Display(title="test")
        quit = pygame.Event(pygame.QUIT,{})
        generator = display.edit()
        next(generator)
        assert display.mode == "Edit"
        with pytest.raises(StopIteration):
            self.post_and_next_frame(quit, generator)
        assert display.mode == "Quit"
        
    def test_simulationmode(self):
        display = Display(title="test")
        quit = pygame.Event(pygame.QUIT,{})
        generator = display.simulate()
        next(generator)
        assert display.mode == "Simulate"
        with pytest.raises(StopIteration):
            self.post_and_next_frame(quit, generator)
        assert display.mode == "Quit"
    
    @pytest.mark.timeout(3)
    def test_open_fileopen_dialog(self):
        display = Display(title="test")
        generator = display.edit()
        next(generator)
        assert display.mode == "Edit"
        click_file = pygame.Event(pygame.MOUSEBUTTONDOWN,{"pos":(18,16), "button":1, "touch":False, "window":None})
        click_file_release = pygame.Event(pygame.MOUSEBUTTONUP,{"pos":(18,16), "button":1, "touch":False, "window":None})
        click_open = pygame.Event(pygame.MOUSEBUTTONDOWN,{"pos":(42,46), "button":1, "touch":False})
        click_open_release = pygame.Event(pygame.MOUSEBUTTONUP,{"pos":(42,46), "button":1, "touch":False})
        self.post_and_next_frame(click_file, generator)
        self.post_and_next_frame(click_file_release, generator)
        while not display.filemenu[0][0].visible:
            next(generator)
        self.post_and_next_frame(click_open, generator)
        self.post_and_next_frame(click_open_release, generator)
        while display.current_files is None or not display.current_files.alive():
            next(generator)
        