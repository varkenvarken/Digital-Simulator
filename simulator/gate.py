from typing import Sequence
from abc import abstractmethod

class Producer:
    ...

class Gate(Producer):
    def __init__(self, inputs:Sequence[Producer]):
        self.inputs = inputs

    @abstractmethod
    def output(self) -> bool:
        ...
