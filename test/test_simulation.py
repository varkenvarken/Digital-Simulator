import json
import pytest
import pygame

from simulator.component import AndGate, ComponentDecoder, NandGate, Input, Output, Line
from simulator.simulation import Simulation

single_and_gate = """
{
    "drawables": [
        {
            "type": "AndGate",
            "dict": {
                "pos": [
                    200.0,
                    300.0
                ],
                "angle": 0,
                "label": "and"
            }
        },
        {
            "type": "Input",
            "dict": {
                "pos": [
                    96.0,
                    291.0
                ],
                "angle": 0,
                "label": "input"
            }
        },
        {
            "type": "Input",
            "dict": {
                "pos": [
                    33.0,
                    305.0
                ],
                "angle": 0,
                "label": "input"
            }
        },
        {
            "type": "Output",
            "dict": {
                "pos": [
                    313.0,
                    300.0
                ],
                "angle": 0,
                "label": "output"
            }
        },
        {
            "type": "Line",
            "dict": {
                "start": [
                    115.0,
                    291.0
                ],
                "end": [
                    147.0,
                    291.0
                ],
                "angle": 0,
                "label": ""
            }
        },
        {
            "type": "Line",
            "dict": {
                "start": [
                    52.0,
                    305.0
                ],
                "end": [
                    148.0,
                    305.0
                ],
                "angle": 0,
                "label": ""
            }
        },
        {
            "type": "Line",
            "dict": {
                "start": [
                    250.0,
                    300.0
                ],
                "end": [
                    296.0,
                    300.0
                ],
                "angle": 0,
                "label": ""
            }
        }
    ],
    "library": [
        {
            "type": "AndGate",
            "dict": {
                "pos": [
                    60.0,
                    545.0
                ],
                "angle": 0,
                "label": "and"
            }
        },
        {
            "type": "NandGate",
            "dict": {
                "pos": [
                    180.0,
                    545.0
                ],
                "angle": 0,
                "label": "nand"
            }
        },
        {
            "type": "Input",
            "dict": {
                "pos": [
                    300.0,
                    545.0
                ],
                "angle": 0,
                "label": "input"
            }
        },
        {
            "type": "Output",
            "dict": {
                "pos": [
                    420.0,
                    545.0
                ],
                "angle": 0,
                "label": "output"
            }
        }
    ]
}"""


class TestSimulation:

    def test_single_and_gate_connect(self,_init_pygame, default_ui_manager, _display_surface_return_none):
        obj = json.loads(single_and_gate)
        cd = ComponentDecoder(obj)
        components = cd.d_objs
        simulation = Simulation(components)
        simulation.connect()
        # verify that the right components are loaded
        assert type(components[0]) == AndGate 
        assert type(components[1]) == Input
        assert type(components[2]) == Input 
        assert type(components[3]) == Output 
        assert type(components[4]) == Line 
        assert type(components[5]) == Line 
        assert type(components[6]) == Line
        # verify that he last Line component gets its input from the output of the AndGate
        assert components[0].listeners[0][0] is components[6]
        assert components[0].listeners[0][1] is components[6].connectors[0]
        # verify the Input elements are connected correctly
        assert components[1].listeners[0][0] is components[4]
        assert components[1].listeners[0][1] is components[4].connectors[0]
        assert components[2].listeners[0][0] is components[5]
        assert components[2].listeners[0][1] is components[5].connectors[0]
        # verify that the Line components coming from the inputs have the and gate as listener (note: connectors[0] would be the and gate output)
        assert components[4].listeners[0][0] is components[0]
        assert components[4].listeners[0][1] is components[0].connectors[1]
        assert components[5].listeners[0][0] is components[0]
        assert components[5].listeners[0][1] is components[0].connectors[2]

    @pytest.mark.timeout(3)
    def test_single_and_gate_simulate(self,_init_pygame, default_ui_manager, _display_surface_return_none):
        obj = json.loads(single_and_gate)
        cd = ComponentDecoder(obj)
        components = cd.d_objs
        simulation = Simulation(components)
        simulation.connect()
        while simulation.simulate():
            ...
        assert components[0].state == False  # andgate
        assert components[3].state == False  # output
        assert components[1].state == False  # input
        assert components[2].state == False  # input

        components[1].toggle()
        while simulation.simulate():
            ...
        assert components[0].state == False  # andgate
        assert components[3].state == False  # output
        assert components[1].state == True  # input
        assert components[2].state == False  # input

        components[2].toggle()
        while simulation.simulate():
            ...
        assert components[0].state == True  # andgate
        assert components[3].state == True  # output
        assert components[1].state == True  # input
        assert components[2].state == True  # input
        
        