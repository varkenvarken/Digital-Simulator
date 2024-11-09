"""
Tests for simulator.gate
"""

import pytest

from simulator import gate    # The code to test


def test_gate():
    """gate is an abstract base class and we should not be able to instantiate it."""
    with pytest.raises(TypeError):
        g = gate.Gate([])


def test_value():
    v = gate.Value()
    assert v is not None
    assert v.output() is False
    v.set(True)
    assert v.output() is True
    v.set(False)
    assert v.output() is False
    with pytest.raises(TypeError):
        v.set(0.0)


def test_unconnected_connector():
    c = gate.Connector([])
    assert c is not None
    assert c.output() is None


def test_overconnected_connector():
    with pytest.raises(gate.ConfigurationException):
        c = gate.Connector([gate.Value(), gate.Value()])


def test_connector_init_nosequence():
    with pytest.raises(TypeError):
        c = gate.Connector(gate.Value())


def test_connector():
    c = gate.Connector([gate.Value()])
    assert c is not None
    assert c.output() is False
