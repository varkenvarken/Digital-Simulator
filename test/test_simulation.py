import json
import pytest
import numpy as np

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

three_lines = """
{
    "drawables": [
        {
            "type": "Input",
            "dict": {
                "pos": [
                    100.0,
                    200.0
                ],
                "angle": 0,
                "label": "input"
            }
        },
        {
            "type": "Output",
            "dict": {
                "pos": [
                    700.0,
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
                    119.0,
                    200.0
                ],
                "end": [
                    426.0,
                    200.0
                ],
                "angle": 0,
                "label": ""
            }
        },
        {
            "type": "Line",
            "dict": {
                "start": [
                    426.0,
                    200.0
                ],
                "end": [
                    426.0,
                    299.0
                ],
                "angle": 90,
                "label": ""
            }
        },
        {
            "type": "Line",
            "dict": {
                "start": [
                    426.0,
                    299.0
                ],
                "end": [
                    681.0,
                    299.0
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
}
"""


class TestSimulation:

    def test_single_and_gate_connect(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
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
        # verify that the array mapping is correct
        assert np.all(simulation.operation == [0, 0, 0, 0, 0, 0, 0])
        assert np.all(simulation.inputmap1 == [4, 1, 2, 6, 1, 2, 0])
        assert np.all(simulation.inputmap2 == [5, 1, 2, 6, 1, 2, 0])

    @pytest.mark.timeout(3)
    def test_single_and_gate_simulate_np(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        obj = json.loads(single_and_gate)
        cd = ComponentDecoder(obj)
        components = cd.d_objs
        simulation = Simulation(components)
        simulation.connect()
        simulation.update_inputs()
        simulation.simulate_np()
        assert np.all(simulation.output == [0, 0, 0, 0, 0, 0, 0])
        simulation.simulate_np()
        assert np.all(simulation.output == [0, 0, 0, 0, 0, 0, 0])

        components[1].state = True
        components[2].state = True
        simulation.update_inputs()
        simulation.simulate_np()
        # first iteration propagates input -> output for the Input components
        assert np.all(simulation.output == [0, 1, 1, 0, 0, 0, 0])
        simulation.simulate_np()
        # this moves on to the Line components connected to the Input componenta
        assert np.all(simulation.output == [0, 1, 1, 0, 1, 1, 0])
        simulation.simulate_np()
        # next the AndGate is evaluate 1 and 1 -> 1
        assert np.all(simulation.output == [1, 1, 1, 0, 1, 1, 0])
        simulation.simulate_np()
        # AndGate output propagates to last Line component
        assert np.all(simulation.output == [1, 1, 1, 0, 1, 1, 1])
        changed = simulation.simulate_np()
        # and then to the Output component
        assert np.all(simulation.output == [1, 1, 1, 1, 1, 1, 1])
        assert changed  # assert that is indeed flagged as changed
        changed = simulation.simulate_np()
        # and then it should be stable
        assert np.all(simulation.output == [1, 1, 1, 1, 1, 1, 1])
        assert not changed

    def test_three_lines_connect(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        obj = json.loads(three_lines)
        cd = ComponentDecoder(obj)
        components = cd.d_objs
        simulation = Simulation(components)
        simulation.connect()

        # verify that the right components are loaded
        assert type(components[0]) == Input
        assert type(components[1]) == Output
        assert type(components[2]) == Line
        assert type(components[3]) == Line
        assert type(components[4]) == Line
        # verify that the array mapping is correct
        assert np.all(simulation.operation == [0, 0, 0, 0, 0])
        assert np.all(simulation.inputmap1 == [0, 4, 0, 0, 0])
        assert np.all(simulation.inputmap2 == [0, 4, 0, 0, 0])

    @pytest.mark.timeout(3)
    def test_three_lines_simulate_np(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        obj = json.loads(three_lines)
        cd = ComponentDecoder(obj)
        components = cd.d_objs
        simulation = Simulation(components)
        simulation.connect()
        simulation.update_inputs()
        simulation.simulate_np()
        assert np.all(simulation.output == [0, 0, 0, 0, 0])
        simulation.simulate_np()
        assert np.all(simulation.output == [0, 0, 0, 0, 0])

        components[0].state = True
        simulation.update_inputs()
        changed = simulation.simulate_np()
        # first iteration propagates input -> output for the Input components
        assert np.all(simulation.output == [1, 0, 0, 0, 0])
        assert changed
        changed = simulation.simulate_np()
        # second iteration propagates input to all lines directly or indirectly connected
        assert np.all(simulation.output == [1, 0, 1, 1, 1])
        assert changed
        # final iteration reaches output
        changed = simulation.simulate_np()
        assert np.all(simulation.output == [1, 1, 1, 1, 1])
        assert changed
        # and then it should stay stable
        changed = simulation.simulate_np()
        assert np.all(simulation.output == [1, 1, 1, 1, 1])
        assert not changed

    @pytest.mark.parametrize("n", (1000, 2000, 3000, 4000))
    def test_simulate_np_benchmark(
        self,
        _init_pygame,
        default_ui_manager,
        _display_surface_return_none,
        benchmark,
        n,
    ):
        components = [AndGate((100, 100)) for i in range(n)]
        simulation = Simulation(components)
        simulation.connect()
        benchmark(simulation.simulate_np)
