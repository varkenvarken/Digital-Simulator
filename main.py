# Digital Simulator
# Copyright (C) 2024  Michel Anders

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from simulator.component import AndGate, NandGate, Input, Output

from simulator.display import Display

display = Display()

drawables = [AndGate((x, 300)) for x in (200,)]
drawables.extend([Input((100, y)) for y in (200, 400)])
drawables.extend([Output((700, y)) for y in (300, )])

display.drawables += drawables

display.library += [AndGate((50,100)), NandGate((50,100)), Input((50,100)), Output((50,100))]

while True:
    editor = display.edit()
    for iteration in editor:
        ...
    if display.mode == "Quit":
        break
    elif display.mode == "Start simulation":
        simulation = display.simulate()
        for iteration in simulation:
            ...
        if display.mode != "Stop simulation":
            break
    
display.quit()
