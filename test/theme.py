from pathlib import Path
import pygame
import pygame_gui

FPS = 60
width, height = 800, 600

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE)
screen.fill("white")

manager = pygame_gui.UIManager(screen.get_rect().size, theme_path=Path(__file__).parent / "theme.json")

current_files = pygame_gui.windows.ui_file_dialog.UIFileDialog(
   rect=pygame.Rect(50, 50, 400, 400), manager=manager, window_title="Open file").current_file_list

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        manager.process_events(event)

    screen.fill("white")
    time_delta = clock.tick(FPS)/1000.0
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
