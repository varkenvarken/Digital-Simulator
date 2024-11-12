from pathlib import Path
import pygame
from pygame import image, time, draw, Vector2, locals, font, Rect

from simulator.drawable import Line, Image


class Display:
    FPS = 60

    def __init__(
        self,
        width=800,
        height=600,
        title="Drawable test",
        iconpath="icons/AND_ANSI_Labelled.svg",
    ):
        pygame.init()
        pygame.display.set_icon(image.load(Path(__file__).parent / iconpath))

        self.clock = time.Clock()

        self.screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.screen.fill("white")

        self.drawables = []

        self.font = font.Font(None, 16)

        self.mode = "Edit"

    def flip(self):
        pygame.display.flip()
        self.clock.tick(self.FPS)

    @staticmethod
    def quit():
        pygame.quit()

    def status(self):
        fg = "black"
        bg = "grey90"
        text = self.mode
        size = self.font.size(text)
        ren = self.font.render(text, 1, fg, bg)
        rect = self.screen.get_rect()
        y = rect.bottomleft[1] - self.font.get_linesize()
        self.screen.fill(bg, Rect(0, y - 2, rect.w, self.font.get_linesize()))
        draw.line(self.screen, fg, (0, y - 2), (rect.w, y - 2))
        self.screen.blit(ren, (rect.bottomleft[0] + 5, y))

    def redraw(self):
        self.screen.fill("white")
        for d in self.drawables:
            d.blit(self.screen)
        self.status()

    def draw_guides(self):
        x, y = pygame.mouse.get_pos()
        r = self.screen.get_rect()
        draw.line(self.screen, "black", (0, y), (r.w, y))
        draw.line(self.screen, "black", (x, 0), (x, r.h))

    def reset(self):
        for d in self.drawables:
            d.on = False
            d.selected = False
            d.active = False

    def edit(self):
        self.mode = "Edit"
        self.reset()

        # Dragging control variables
        dragging = False
        dragged_rect_index = None
        offset = Vector2(0, 0)

        active_object = None

        drawing = False
        line_start = Vector2(0, 0)
        line_end = Vector2(0, 0)

        running = True
        reason = None
        copy_drawable = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    reason = "Quit"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if drawing:
                        self.drawables.append(
                            Line(line_start, line_end, color="blue", linewidth=2)
                        )
                        line_start = line_end
                    else:
                        for i, r in enumerate(self.drawables):
                            click, connector_position = r.collideconnector(event.pos)
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
                                for d2 in self.drawables:
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
                        r = self.drawables[dragged_rect_index]
                        r.pos = event.pos + offset
                    elif drawing:
                        line_end = Vector2(event.pos)
                elif event.type == pygame.KEYUP:
                    print(event)
                    if event.key == locals.K_r and active_object is not None:
                        self.drawables[active_object].rotate(90)
                    elif event.key == locals.K_s:
                        running = False
                        reason = "Start simulation"
                    elif (
                        event.key == locals.K_c
                        and (event.mod & locals.KMOD_CTRL)
                        and active_object is not None
                        and isinstance(self.drawables[active_object], Image)
                    ):
                        copy_drawable = active_object
                    elif (
                        event.key == locals.K_v
                        and (event.mod & locals.KMOD_CTRL)
                        and copy_drawable is not None
                    ):
                        t = type(self.drawables[copy_drawable])
                        pos = pygame.mouse.get_pos()
                        print(t)
                        d = t(pos)
                        print(d)
                        self.drawables.append(d)
            self.redraw()

            if drawing:
                dl = line_end - line_start
                if dl.length() > 4:
                    if abs(dl.x) > abs(dl.y):
                        line_end.y = line_start.y
                    else:
                        line_end.x = line_start.x
                draw.line(self.screen, "green", line_start, line_end, 2)

            if True:  # TODO make this a toggle
                self.draw_guides()

            self.flip()

        self.screen.fill("white")
        self.flip()
        return reason

    def simulate(self):
        self.mode = "Simulate"
        self.reset()

        running = True
        reason = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    reason = "Quit"
                elif event.type == pygame.MOUSEBUTTONUP:
                    for i, r in enumerate(self.drawables):
                        if r.collidepoint(event.pos):
                            if hasattr(r, "toggle"):
                                r.toggle()
                elif event.type == pygame.KEYUP:
                    print(event)
                    if event.key == locals.K_s:
                        running = False
                        reason = "Stop simulation"
            self.redraw()
            self.flip()

        self.screen.fill("white")
        self.flip()
        return reason
