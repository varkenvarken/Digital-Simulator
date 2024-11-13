from simulator.component import AndGate, Input, Output

from simulator.display import Display

display = Display()

drawables = [AndGate((x, 300)) for x in (200,)]
drawables.extend([Input((100, y)) for y in (200, 400)])
drawables.extend([Output((700, y)) for y in (300, )])

display.drawables += drawables

while True:
    reason = display.edit()
    print(f"command {reason}")
    if reason == "Quit":
        break
    elif reason == "Start simulation":
        reason = display.simulate()
        print(f"command {reason}")
        if reason == "Quit":
            break
        elif reason == "Stop simulation":
            continue
    
display.quit()
