# -*- coding: UTF-8 -*-
import pytest
from eecalpy.electrical_units import *
from eecalpy.parser import _parse_line, console, script
from lark import UnexpectedInput

@pytest.mark.parametrize(
    "text_to_parse,expected",
    [
        # U
        ("12V", U(12)),
        ("3mV", U(3e-3)),
        ("10µV 10%", U(10e-6, 0.1)),
        ("345kV 6.2176%", U(345e3, 0.062176)),

        # R
        ("12k", R(12e3)),
        ("521.23", R(521.23)),
        ("20m", R(20e-3)),
        ("1k 1%", R(1e3, 0.01)),
        ("15k 0.124%", R(15e3, 0.00124)),
        ("351 5.5% 200ppm", R(351, 0.055, 200)),

        # I
        ("22A", I(22)),
        ("75nA", I(75e-9)),

        # P
        ("86W", P(86)),
        ("5GW 2%", P(5e9, 0.02)),
    ]
)
def test_value_expression(text_to_parse, expected):
    assert str(_parse_line(text_to_parse)) == str(expected)

@pytest.mark.parametrize(
    "operation,expected",
    [
        ("12k + 24k", R(12e3) + R(24e3)),
        ("12k | 24k", R(12e3) | R(24e3)),
        ("12k 2% + 24k 0.1%", R(12e3, 0.02) + R(24e3, 0.001)),
        ("12k 2% | 24k 0.1%", R(12e3, 0.02) | R(24e3, 0.001)),
        ("12k 2% 100ppm + 24k 0.1% 300ppm", R(12e3, 0.02) + R(24e3, 0.001)),
        ("12k 2% 100ppm | 24k 0.1% 300ppm", R(12e3, 0.02) | R(24e3, 0.001)),
        ("(12k + 43k) | 24k", (R(12e3) + R(43e3)) | R(24e3)),
        ("12k * 1µA", R(12e3) * I(1e-6)),
        ("12mV / 200k", U(12e-3) / R(200e3)),
        ("2V * 1A", U(2) * I(1)),
        ("2V 3% * 1A", U(2, 0.03) * I(1)),
    ]
)
def test_operations(operation, expected):
    assert str(_parse_line(operation)) == str(expected)

@pytest.mark.parametrize(
    "var,value,expected",
    [
        ("a", "12k", R(12e3)),
        ("R34", "12k 12%", R(12e3, 0.12)),
        ("affe_34x_310", "52k 12%", R(52e3, 0.12)),
        ("3_", "3k", None),
    ]
)
def test_assignments(var, value, expected):
    _parse_line(var + ' = ' + value)
    assert str(_parse_line(var)) == str(expected)

def test_script():
    scr = 'a = 12k\nb = 31k\n\na + b\na | b'
    a = R(12e3)
    b = R(31e3)

    with open('tmp.ee', 'w') as tmp:
        tmp.write(scr)
    
    out = script('tmp.ee')
    expected = '\n'.join([str(x) for x in [a, b, a+b, a|b]])
    
    assert out == expected