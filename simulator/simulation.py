from simulator.component import Gate

# TODO not all Line connections simulate correctly: some lead to infite repetitions
class Simulation:
    def __init__(self, components):
        self.components = components

    def connect(self):
        # TODO detect circular dependencies
        for d in self.components:
            self.listeners = []
        for d in self.components:
            for i, c in enumerate(d.connectors):
                if c.direction in ("input", "bidirectional"):
                    # if this connector may depend on the output of another drawable ...
                    d.on = False
                    connected = False
                    # check all other drawable to see if may produce output
                    for od in self.components:
                        if d is not od:  # no connections to self are allowed
                            for oc in od.connectors:
                                if oc.direction in ("output", "bidirectional"):
                                    # if there is overlap between the connectors we add a listener to the drawable that produces output
                                    if self.overlap(d, c, od, oc):
                                        od.listeners.append((d, c))
                                        connected = True

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