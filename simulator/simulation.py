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
        self.functions = {0: lambda a, b: a and b,
                          4: lambda a, b: not (a or b)}
        self.functionsmap = {AndGate: 0, NandGate: 4,
                             Line: 0, Input: 0, Output: 0}

        for index, function in self.functions.items():
            for a in (True, False):
                for b in (True, False):
                    offset = a + b * 2 + index
                    self.lookup[offset] = function(a, b)

    def connect(self):
        # TODO detect circular dependencies
        for component in self.components:
            component.listeners = []
            component.inputmap = []

        for component_index, component in enumerate(self.components):
            for connector_index, connector in enumerate(component.connectors):
                if connector.direction in ("input", "bidirectional"):
                    # if this connector may depend on the output of another drawable ...
                    component.on = False
                    component.connected = False
                    # check all other drawable to see if may produce output
                    for other_component_index, other_component in enumerate(self.components):
                        if component is not other_component:  # no connections to self are allowed
                            for oc in other_component.connectors:
                                if oc.direction in ("output", "bidirectional"):
                                    # if there is overlap between the connectors we add a listener to the drawable that produces output
                                    if self.overlap(component, connector, other_component, oc):
                                        other_component.listeners.append((component, connector))
                                        component.connected = True
                                        component.inputmap.append(other_component_index)

        for component_index, component in enumerate(self.components):
            self.operation[component_index] = self.functionsmap[type(component)]

            if type(component) in (Input,):  # may be extended with other inputs like Clock
                self.input1[component_index] = self.input2[component_index] = component.state
                self.inputmap1[component_index] = self.inputmap2[component_index] = component_index  # we map its output back to the input and because function == and , this input stays the same for the duration of the simulation
            elif type(component) in (Output,):
                self.input1[component_index] = self.input2[component_index] = 0
                for connector_index,other_component_index in enumerate(component.inputmap):
                    if connector_index == 0:
                        self.inputmap1[component_index] = other_component_index
                        self.inputmap2[component_index] = other_component_index
                    else:
                        raise IndexError("Output objects can have only 1 input")
            elif type(component) in (Line,):
                self.input1[component_index] = self.input2[component_index] = 0
                for connector_index,other_component_index in enumerate(component.inputmap):
                    if connector_index == 0:
                        self.inputmap1[component_index] = other_component_index
                        self.inputmap2[component_index] = other_component_index
                    else:
                        raise IndexError("Line objects can have only 1 input") 
            else:
                for connector_index,other_component_index in enumerate(component.inputmap):
                    if connector_index == 0:
                        self.inputmap1[component_index] = other_component_index
                    else:
                        self.inputmap2[component_index] = other_component_index

    def simulate_np(self) -> bool:
        state = self.input1 + 2 * self.input2 + self.operation
        previous_output = self.output
        self.output = self.lookup[state]
        self.input1 = self.output[self.inputmap1]  # TODO these could be done in-place, i.e. put into the input array directly, to save allocating a new array
        self.input2 = self.output[self.inputmap2]
        return np.any(previous_output != self.output)
    
    @staticmethod
    def overlap(a, c1, b, c2) -> bool:
        """
        Check if hotspot c1 of component a overlaps with hotspot c2 of component b.
        """
        ap = a.pos + c1.position
        bp = b.pos + c2.position
        return (ap - bp).length() <= (c1.radius + c2.radius)

    def simulate(self) -> bool:
        changed = False
        for di, d in enumerate(self.components):
            for listener, connector in d.listeners:
                if isinstance(listener, Gate):
                    print(f"> {d.state=} {listener.state=} {
                          connector.state=} {id(connector)=}")
                    if connector.state != d.state:
                        changed = True
                    connector.state = d.state
                    old = listener.state
                    listener.state = listener.eval()
                    if old != listener.state:
                        changed = True
                    print(f"< {d.state=} {listener.state=} {connector.state=}")
                else:
                    if d.state != listener.state:
                        changed = True
                        listener.state = d.state
        return changed
