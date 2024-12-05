# Copyright 2024 - 2024, Michel Anders and the Digital Simulator contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
import pygame
import pygame_gui
from pygame_gui.windows import ui_file_dialog
from pygame import image, time, draw, Vector2, locals, font, Rect
import pygame_gui.windows.ui_message_window

# note: we need all inputs here because we are going to create components dynamically based on their name
from simulator.component import (
    ComponentDecoder,
    Line,
    Image,
    Gate,
    ComponentEncoder,
    Input,
    Output,
    AndGate,
    NandGate,
)
from simulator.simulation import Simulation

EXT = ".dsim"


def grid(value, dp=10):
    return int(((value / dp) + 0.5))*dp                 # 14 -> 10, 15 -> 20


class Display:
    FPS = 60

    def __init__(
        self,
        width=800,
        height=600,
        title="Drawable test",
        iconpath="icons/AND_ANSI_Labelled.svg",  # TODO replace by a more distinct logo
    ):
        self.title = title
        pygame.init()
        pygame.display.set_icon(image.load(Path(__file__).parent / iconpath))

        self.clock = time.Clock()

        self.screen = pygame.display.set_mode(
            (width, height), flags=pygame.RESIZABLE)
        pygame.display.set_caption(self.title)
        self.screen.fill("white")

        self.drawables = []
        self.library = []

        self.font = font.Font(None, 16)

        self.mode = "Edit"

        self.manager = pygame_gui.UIManager(
            self.screen.get_rect().size, theme_path=Path(__file__).parent / "theme.json"
        )

        self.create_menu()

        self.filename = "new_file.dsim"
        self.changed = False

        self.current_files = None

    def create_menu(self):
        left = 1
        toplevel = (
            ("File", self.show_filemenu),
            ("Edit", self.show_editmenu),
            ("Help", self.show_helpmenu),
        )
        self.menu = []
        for label, callback in toplevel:
            width = len(label) * 10
            self.menu.append(
                (
                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((left, 1), (width, 30)),
                        text=label,
                        manager=self.manager,
                    ),
                    callback,
                )
            )
            left += width

        fileoptions = [
            ("Open ...", self.show_opendialog),
            ("Save", self.save),
            ("Save as ...", self.show_savedialog),
            ("Quit", self.show_quitdialog),
        ]
        self.filemenu = []
        width = max(len(label) for label, _ in fileoptions) * 10 + 10
        height = 30
        for label, callback in fileoptions:
            self.filemenu.append(
                (
                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((4, height), (width, 30)),
                        text=label,
                        manager=self.manager,
                        visible=0,
                    ),
                    callback,
                )
            )
            height += 30

    def process_menu_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for button, callback in self.menu + self.filemenu:
                if event.ui_element == button:
                    callback(event)
        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            print(event)
            if event.ui_object_id == "#saveas_file_dialog":
                self.saveas(event.text)
            elif event.ui_object_id == "#open_file_dialog":
                self.open(event.text)
        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            print(event)
            if event.ui_object_id == "#overwrite_existing_file_confirmation_dialog":
                self.do_saveas()
            if event.ui_object_id == "#discard_changed_file_confirmation_dialog":
                self.do_open()

    def show_filemenu(self, event):
        for b, callback in self.filemenu:
            b.visible = 1

    def hide_filemenu(self):
        for b, callback in self.filemenu:
            b.visible = 0

    def save(self, event):
        print("save")

    def show_opendialog(self, event):
        self.current_files = pygame_gui.windows.ui_file_dialog.UIFileDialog(
            rect=pygame.Rect(50, 50, 400, 400),
            manager=self.manager,
            window_title="Open file",
            object_id="#open_file_dialog",
        )
        self.hide_filemenu()

    def show_savedialog(self, event):
        self.current_files = pygame_gui.windows.ui_file_dialog.UIFileDialog(
            rect=pygame.Rect(50, 50, 400, 400),
            manager=self.manager,
            window_title="Save file as",
            object_id="#saveas_file_dialog",
        )
        self.hide_filemenu()

    def show_quitdialog(self, event):
        print("quit")

    def show_editmenu(self, event):
        print("edit")

    def show_helpmenu(self, event):
        print("help")

    def saveas(self, filename):
        f = Path(filename)
        if f.suffix == "":
            f = f.with_suffix(EXT)
        self.new_filename = f
        if f.exists() and not f.is_file():
            pygame_gui.windows.ui_message_window.UIMessageWindow(
                rect=pygame.Rect(50, 50, 400, 400),
                manager=self.manager,
                window_title="Error selecting file",
                html_message=f"{filename}<br>is not a file",
            )
            return
        elif f.exists():
            pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(
                rect=pygame.Rect(50, 50, 400, 400),
                manager=self.manager,
                window_title="Confirm overwrite",
                action_long_desc=f"File {
                    filename} already exists. Do you want to replace it?",
                action_short_name="Overwrite",
                object_id="#overwrite_existing_file_confirmation_dialog",
            )
            return
        else:
            self.do_saveas()

    def do_saveas(self):
        f: Path = self.new_filename
        # TODO save pretty printed
        # TODO add HMAC signature
        print(f"saving as {f}")
        s = json.dumps(
            {"drawables": self.drawables, "library": self.library}, cls=ComponentEncoder
        )
        print(s)
        with open(f, "w") as output:
            json.dump(
                {"drawables": self.drawables, "library": self.library},
                output,
                cls=ComponentEncoder,
                indent=4,
            )
        self.changed = False
        self.filename = str(f)

    def open(self, filename):
        f = Path(filename)
        self.new_filename = f
        if not f.exists() or not f.is_file() or f.suffix != EXT:
            pygame_gui.windows.ui_message_window.UIMessageWindow(
                rect=pygame.Rect(50, 50, 400, 400),
                manager=self.manager,
                window_title="Error selecting file",
                html_message=f"{filename}<br>is not a Digital Simulator file",
            )
            return
        elif self.changed:
            pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(
                rect=pygame.Rect(50, 50, 400, 400),
                manager=self.manager,
                window_title="Confirm discarding changes",
                action_long_desc=f"File {
                    self.filename} has changed. Do you want to discard the changes?",
                action_short_name="Discard",
                object_id="#discard_changed_file_confirmation_dialog",
            )
            return
        else:
            self.do_open()

    def do_open(self):
        with open(self.new_filename) as input:
            obj = json.load(input)
        cd = ComponentDecoder(obj)
        self.drawables = cd.d_objs
        self.library = cd.l_objs

        self.filename = self.new_filename
        self.changed = False

    def flip(self):
        self.time_delta = self.clock.tick(self.FPS) / 1000.0
        self.manager.update(self.time_delta)
        self.manager.draw_ui(self.screen)
        pygame.display.flip()

    @staticmethod
    def quit():
        pygame.quit()

    def status(self):
        fg = "black"
        bg = "grey90"
        text = self.mode
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

    def redraw_library(self):
        r = self.screen.get_rect()
        y = r.h - 80
        x = 60
        for d in self.library:
            d.pos = Vector2(x, y + 25)
            x += 120
            d.blit(self.screen)
        draw.line(self.screen, "black", (0, y), (r.w, y))

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
            yield
            for event in pygame.event.get():
                # if event.type != pygame.MOUSEMOTION: print(event)
                if event.type == pygame.QUIT:
                    running = False
                    self.mode = "Quit"
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if drawing:
                        line_end = Vector2(
                            (grid(line_end.x), grid(line_end.y)))
                        self.drawables.append(
                            Line(line_start, line_end,
                                 color="blue", linewidth=3)
                        )
                        print(line_start, line_end)
                        line_start = line_end
                        self.changed = True
                        continue
                    else:
                        for i, r in enumerate(self.drawables):
                            click, connector_position = r.collideconnector(
                                event.pos)
                            if click:
                                print(
                                    f"click on object {
                                        i} output at {event.pos}"
                                )
                                drawing = True
                                line_start = Vector2(connector_position)
                                line_end = Vector2(connector_position)
                                break
                            if r.collidepoint(event.pos):
                                active_object = r
                                dragging = True
                                dragged_rect_index = r
                                # Calculate offset to maintain position relative to click
                                offset = r.pos - event.pos
                                for d2 in self.drawables:
                                    d2.active = False
                                for d2 in self.library:
                                    d2.active = False
                                r.active = True
                                break
                        else:  # only executed if the loop did not break
                            # check for library click
                            for i, r in enumerate(self.library):
                                if r.collidepoint(event.pos):
                                    # duplicate
                                    r = type(r)
                                    pos = Vector2(pygame.mouse.get_pos())
                                    pos.y -= 0
                                    r = r(pos)
                                    self.drawables.append(r)
                                    self.changed = True
                                    # drag (duplicate code from regular drag!)
                                    active_object = r
                                    dragging = True
                                    dragged_rect_index = r
                                    # Calculate offset to maintain position relative to click
                                    offset = r.pos - event.pos
                                    for d2 in self.drawables:
                                        d2.active = False
                                    for d2 in self.library:
                                        d2.active = False
                                    r.active = True
                                    break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        # Stop dragging when the mouse button is released
                        dragging = False
                        dragged_rect_index = None
                        self.changed = True
                    elif drawing:
                        if event.button == 3:
                            drawing = False
                elif event.type == pygame.MOUSEMOTION:
                    # Update the position of the drawable while dragging
                    if dragging and dragged_rect_index is not None:
                        dragged_rect_index.pos = event.pos + offset
                        self.changed = True
                    elif drawing:
                        line_end = Vector2(event.pos)
                elif event.type == pygame.KEYUP:
                    print(event)
                    if event.key == locals.K_r and active_object is not None:
                        active_object.rotate(90)
                        self.changed = True
                    elif event.key == locals.K_s:
                        running = False
                        reason = "Start simulation"
                        self.mode = reason
                        return
                    elif (
                        event.key == locals.K_c
                        and (event.mod & locals.KMOD_CTRL)
                        and active_object is not None
                        and isinstance(active_object, Image)
                    ):
                        copy_drawable = active_object
                    elif (
                        event.key == locals.K_v
                        and (event.mod & locals.KMOD_CTRL)
                        and copy_drawable is not None
                    ):
                        t = type(copy_drawable)
                        pos = pygame.mouse.get_pos()
                        print(t)
                        d = t(pos)
                        print(d)
                        self.drawables.append(d)
                        self.changed = True
                self.process_menu_events(event)
                self.manager.process_events(event)

            self.redraw()
            self.redraw_library()

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

            pygame.display.set_caption(
                f"{'*' if self.changed else ' '} {
                    self.title} [{self.filename}]"
            )  # TODO ellide very long names  ...ery/long/file.dsim

            self.flip()

        self.screen.fill("white")
        self.flip()
        return reason

    def simulate(self):
        self.mode = "Simulate"
        self.reset()

        simulation = Simulation(self.drawables)
        simulation.connect()
        simulation.update_inputs()

        simulation._dump()
        
        n = 1
        while simulation.simulate_np():
            n += 1
        print(f"{n} steps of simulation at the start")
        simulation.update_components()

        running = True
        reason = None
        while running:
            yield
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    reason = "Quit"
                    self.mode = reason
                    return
                elif event.type == pygame.MOUSEBUTTONUP:
                    for i, r in enumerate(self.drawables):
                        if r.collidepoint(event.pos):
                            if hasattr(r, "toggle"):
                                r.toggle()
                                simulation.update_inputs()
                                n = 1
                                while simulation.simulate_np():
                                    n += 1
                                print(f"{n} steps of simulation after click")
                                simulation.update_components()

                elif event.type == pygame.KEYUP:
                    print(event)
                    if event.key == locals.K_s:
                        running = False
                        reason = "Stop simulation"
                        self.mode = reason
                        return
            self.redraw()
            self.flip()

        self.screen.fill("white")
        self.flip()
        return reason
