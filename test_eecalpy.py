# -*- coding: UTF-8 -*-
import pytest
from eecalpy.electrical_units import *


@pytest.mark.parametrize(
    "unit",
    [U, R, I, P, Factor, Usq, Isq]
)
def test_classmethod_fmm(unit):
    eu = unit.from_min_max(1, 3)
    assert isinstance(eu, unit)
    assert eu.min == 1
    assert eu.value == 2
    assert eu.max == 3

def test_R_temp_coeff():
    r = R(1e3)
    assert r.alpha_ppm == None

    r = R(1e3, 0.01, 200)
    assert r.alpha_ppm == 200

@pytest.mark.parametrize(
    "eu,_min,_value,_max",
    [
        (U(10, 0.1), 9.0, 10.0, 11.0),
        (R(2, 0.01), 1.98, 2.0, 2.02),
        (I(-10, 0.1), -11.0, -10.0, -9.0)
    ]
)
def test_tolerance(eu, _min, _value, _max):
    assert eu.min == _min
    assert eu.value == _value
    assert eu.max == _max

def test_tolerance_sign():
    r = R.from_min_max(3, 2)
    assert r.tolerance == 0.2

@pytest.mark.parametrize(
    "operation,expected",
    [
        (U(2.5) + U(2.5), 5.0),
        (U(10) - U(5), 5.0),
        (I(2.5) + I(2.5), 5.0),
        (I(10) - I(5), 5.0),
        (P(2.5) + P(2.5), 5.0),
        (P(10) - P(5), 5.0)
    ]
)
def test_operators(operation, expected):
    assert operation.value == expected

def test_pretty():
    i1 = I(12e-6, 0.05)
    assert str(i1) == i1.pretty()
    assert i1.pretty() == '12.0µA ± 5.0% (± 600.0nA) [11.4000 .. 12.6000]µA'
    assert i1.pretty(variation=False) == '12.0µA ± 5.0% [11.4000 .. 12.6000]µA'
    assert i1.pretty(vrange=False) == '12.0µA ± 5.0% (± 600.0nA)'
    assert i1.pretty(variation=False, vrange=False) == '12.0µA ± 5.0%'
    assert i1.pretty(tolerance=False, variation=False, vrange=False) == '12.0µA'
    assert i1.pretty(value=False, tolerance=False, variation=False, vrange=False) == ''
    assert i1.pretty(value=False, variation=False, vrange=False) == '± 5.0%'
    assert i1.pretty(value=False, variation=False) == '± 5.0% [11.4000 .. 12.6000]µA'
    assert i1.pretty(value=False) == '± 5.0% (± 600.0nA) [11.4000 .. 12.6000]µA'

    r1 = R(8.5e3, 0.01, 200)
    assert r1.pretty() == '8.5kΩ ± 1.0% (± 85.0Ω) [8.4150 .. 8.5850]kΩ @ 20°C α=200ppm'
    assert r1.pretty(temperature=False) == '8.5kΩ ± 1.0% (± 85.0Ω) [8.4150 .. 8.5850]kΩ'
    assert r1.pretty(tolerance=False, temperature=False) == '8.5kΩ'
    assert r1.pretty(value=False, temperature=False) == '± 1.0% (± 85.0Ω) [8.4150 .. 8.5850]kΩ'
    
@pytest.mark.parametrize(
    "eu,expected",
    [
        (U(3), '3.0V'),
        (U(-12.3), '-12.3V'),
        (U(818e3), '818.0kV'),
        (U(200e-3, 0.1), '200.0mV ± 10.0% (± 20.0mV) [180.0000 .. 220.0000]mV'),
        (R(1e3, 0.01, 200).at_T(100) + R(2e3, 0.01, 150), '3.02kΩ ± 1.0% (± 30.16Ω) [2.9858 .. 3.0462]kΩ @ mixed temp.'),
        (Factor(1.0, 0.01), '1.0 ± 1.0% [0.9900 .. 1.0100]'),
        (Factor.from_min_max(2, 3), '2.5 ± 20.0% [2.0000 .. 3.0000]')
    ]
)
def test_repr(eu, expected):
    assert str(eu) == expected


def test_same_temperatures():
    r1 = R(1e3, 0.01, 200)
    r2 = R(2e3, 0.01, 150)

    r = r1 + r2
    assert r.temperature == 20.0

    r = r1 | r2
    assert r.temperature == 20.0

    r = r1.at_T(100) + r2.at_T(100)
    assert r.temperature == 100.0

    r = r1.at_T(100) | r2.at_T(100)
    assert r.temperature == 100.0

def test_temp_and_factors():
    r1 = R(1e3, 0.01, 200)
    r2 = R(2e3, 0.01, 150)

    r = r1.at_T(100) * Factor(2.0)
    assert r.temperature == 100.0

    r = Factor(2.0) * r1.at_T(100)
    assert r.temperature == 100.0

    r = r1 * Factor(2.0)
    assert r.temperature == 20.0

    r = Factor(2.0) * r1
    assert r.temperature == 20.0

    r = r1.at_T(100) * Factor(2.0)
    assert r.temperature == 100.0

    r = Factor(2.0) * r1.at_T(100)
    assert r.temperature == 100.0

def test_different_temperatures():
    r1 = R(1e3, 0.01, 200)
    r2 = R(2e3, 0.01, 150)

    r = r1 + r2.at_T(100)
    assert r.temperature is None

    r = r1 | r2.at_T(100)
    assert r.temperature is None

    r = r1.at_T(100) + r2.at_T(60)
    assert r.temperature is None

    r = r1.at_T(60) | r2.at_T(100)
    assert r.temperature is None

@pytest.mark.parametrize(
    "operation,expected_type",
    [
        # U = R * I
        (R(1) * I(1), U),
        (I(1) * R(1), U),
        
        # P = U * I
        (U(1) * I(1), P),
        (I(1) * U(1), P),
        
        # factors
        (Factor(1) * Factor(1), Factor),
        (U(1) * Factor(1), U),
        (R(1) * Factor(1), R),
        (I(1) * Factor(1), I),
        (P(1) * Factor(1), P),
        (Factor(1) * U(1), U),
        (Factor(1) * R(1), R),
        (Factor(1) * I(1), I),
        (Factor(1) * P(1), P)
    ]
)
def test_operations_mul(operation, expected_type):
    assert isinstance(operation, expected_type)

@pytest.mark.parametrize(
    "operation,expected_type",
    [
        (U(1) / R(1), I),  # U / R = I
        (U(1) / I(1), R),  # U / I = R
        (P(1) / U(1), I),  # P / U = I
        (P(1) / I(1), U),  # P / I = U
        (R(1) / R(1), Factor),  # R / R = f
        (U(1) / U(1), Factor),  # U / U = f
        (I(1) / I(1), Factor),  # I / I = f
        (P(1) / P(1), Factor),  # P / P = f
        (Factor(1) / Factor(1), Factor),  # f / f = f
    ]
)
def test_operations_div(operation, expected_type):
    assert isinstance(operation, expected_type)