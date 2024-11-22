from simulator.component import Gate, AndGate, NandGate, Input, Output, Line

import numpy as np

# TODO not all Line connections simulate correctly: some lead to infite repetitions


class Simulation:
    def __init__(self, components):
        self.components = components

        self.n = len(self.components)
        # gate inputs, maximum 2
        self.input1 = np.zeros(self.n, dtype=bool)
        self.input2 = np.zeros(self.n, dtype=bool)
        # input mappings, i.e. which output will this input gets its new value from
        self.inputmap1 = np.zeros(self.n, dtype=np.int32)
        self.inputmap2 = np.zeros(self.n, dtype=np.int32)
        # the result
        self.output = np.ndarray(self.n, dtype=bool)
        # the logical operation. inputs, outputs and lines have 0 too (i.e. perform an and operation)
        self.operation = np.zeros(self.n, dtype=np.int8)

        # generate the lookup map
        self.lookup = np.zeros(256, dtype=np.int8)
        self.functions = {0: lambda a, b: a and b, 4: lambda a, b: not (a or b)}
        self.functionsmap = {AndGate: 0, NandGate: 4, Line: 0, Input: 0, Output: 0}

        for index, function in self.functions.items():
            for a in (True, False):
                for b in (True, False):
                    offset = a + b * 2 + index
                    self.lookup[offset] = function(a, b)

    def _find_connections(self):
        for component_index, component in enumerate(self.components):
            if not isinstance(component, Line):
                for connector_index, connector in enumerate(component.connectors):
                    if connector.direction == "input":
                        # if this connector may depend on the output of another drawable ...
                        component.connected = False
                        # check all other drawables to see if may produce output
                        for other_component_index, other_component in enumerate(
                            self.components
                        ):
                            if (
                                component is not other_component
                            ):  # no connections to self are allowed
                                for (
                                    other_component_connector
                                ) in other_component.connectors:
                                    if other_component_connector.direction in (
                                        "output",
                                        "bidirectional",
                                    ):
                                        # if there is overlap between the connectors we add a listener to the drawable that produces output
                                        if self.overlap(
                                            component,
                                            connector,
                                            other_component,
                                            other_component_connector,
                                        ):
                                            other_component.listeners.append(
                                                (component, connector)
                                            )
                                            component.connected = True
                                            component.inputmap.append(
                                                other_component_index
                                            )
            else:  # Line objects are special
                other_component_index = self._find_connected_output(component)
                if other_component_index is not None:
                    component.connected = True
                    component.inputmap.append(other_component_index)

    def _find_connected_output(self, component):
        visisted = set()
        queue = [component]
        while len(queue):
            component = queue.pop(0)

            if component in visisted:
                break
            visisted.add(component)

            for other_component_index, other_component in enumerate(self.components):
                if (
                    component is not other_component
                ):  # no connections to self are allowed

                    # if one of the connectors overlaps with an output connector we are done
                    for connector_index, connector in enumerate(component.connectors):
                        for other_component_connector in other_component.connectors:
                            if other_component_connector.direction == "output":
                                # if there is overlap between the connectors we add a listener to the drawable that produces output
                                if self.overlap(
                                    component,
                                    connector,
                                    other_component,
                                    other_component_connector,
                                ):
                                    return other_component_index
                    # if not, and the other component is a Line, we will follow that Line to see if it is connected to an output
                    queue.append(other_component)
        return None

    def connect(self):
        # TODO detect circular dependencies
        for component in self.components:
            component.listeners = []
            component.inputmap = []

        self._find_connections()

        for component_index, component in enumerate(self.components):
            self.operation[component_index] = self.functionsmap[type(component)]

            if type(component) in (
                Input,
            ):  # may be extended with other inputs like Clock
                # we map its output back to both its own inputs and because function associated with an input is 'and' , this input then stays the same for the duration of the simulation
                self.inputmap1[component_index] = self.inputmap2[component_index] = (
                    component_index
                )
            elif type(component) in (Output,):
                self.input1[component_index] = self.input2[component_index] = 0
                for connector_index, other_component_index in enumerate(
                    component.inputmap
                ):
                    if connector_index == 0:
                        self.inputmap1[component_index] = other_component_index
                        self.inputmap2[component_index] = other_component_index
                    else:
                        raise IndexError("Output objects can have only 1 input")
            elif type(component) in (Line,):
                self.input1[component_index] = self.input2[component_index] = 0
                for connector_index, other_component_index in enumerate(
                    component.inputmap
                ):
                    if connector_index == 0:
                        self.inputmap1[component_index] = other_component_index
                        self.inputmap2[component_index] = other_component_index
                    else:
                        print(f"{component_index=} {other_component_index=}")
                        raise IndexError("Line objects can have only 1 input")
            else:
                for connector_index, other_component_index in enumerate(
                    component.inputmap
                ):
                    if connector_index == 0:
                        self.inputmap1[component_index] = other_component_index
                    else:
                        self.inputmap2[component_index] = other_component_index

    def _dump(self):  # pragma: no cover
        print([f"{i}:{type(c).__name__}" for i, c in enumerate(self.components)])
        print(f"{self.input1=}")
        print(f"{self.input2=}")
        print(f"{self.inputmap1=}")
        print(f"{self.inputmap2=}")
        print(f"{self.output=}")

    def simulate_np(self) -> bool:
        # print("simulate")
        # self._dump()
        # print("-"*20)

        state = self.input1 + 2 * self.input2 + self.operation
        previous_output = self.output
        self.output = self.lookup[state]
        # TODO these could be done in-place, i.e. put into the input array directly, to save allocating a new array
        self.input1 = self.output[self.inputmap1]
        self.input2 = self.output[self.inputmap2]

        # self._dump()
        # print("-"*20)

        return np.any(previous_output != self.output)

    def update_components(self):
        for component, output in zip(self.components, self.output):
            component.state = bool(output)

    def update_inputs(self):
        for component_index, component in enumerate(self.components):
            if type(component) in (
                Input,
            ):  # may be extended with other inputs like Clock
                self.input1[component_index] = self.input2[component_index] = (
                    component.state
                )

    @staticmethod
    def overlap(a, c1, b, c2) -> bool:
        """
        Check if hotspot c1 of component a overlaps with hotspot c2 of component b.
        """
        ap = a.pos + c1.position
        bp = b.pos + c2.position
        return (ap - bp).length() <= (c1.radius + c2.radius)
