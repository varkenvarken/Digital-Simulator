from typing import Sequence
from abc import abstractmethod, ABCMeta

class ConfigurationException(Exception):
    ...

class Producer(metaclass=ABCMeta):
    ...

class Gate(Producer):
    def __init__(self, inputs:Sequence[Producer]):
        self.inputs = inputs

    @abstractmethod
    def output(self) -> bool:
        ... # pragma: no cover

    def sample_input(self, index:int) -> bool | None:
        if index >= len(self.inputs) or self.inputs[index] is None:
            return None
        return self.inputs[index].output()

class Value(Producer):
    def __init__(self, value=False):
        self.inputs = [value]
    
    def output(self) -> bool:
        return self.inputs[0]
    
    def set(self, value:bool):
        if type(value) is not bool:
            raise TypeError("values can be booleans only")
        self.inputs[0] = value

class Connector(Gate):
    def __init__(self, inputs:Sequence[Producer]):
        if len(inputs) > 1:
            raise ConfigurationException("Connector can have at most 1 input")
        super().__init__(inputs)

    def output(self) -> bool:
        return self.sample_input(0)
