eecalpy Python module
=====================

The *Electrical Engineering Calculations for Python* module is a
collection of classes for simple to complex electrical calculations, with a
special focus on handling tolerances.

Installation
------------

The ``eecalpy`` package is available on the Python Package Index (PyPI):

[![pypi package](https://badge.fury.io/py/eecalpy.svg)](https://badge.fury.io/py/eecalpy)

The package needs Python 3+, you can install it with:

    $ pip install eecalpy

Introduction
------------

The available units are:

* Voltage `U(voltage, tolerance=0.0)`
* Resistance `R(resistance, tolerance=0.0, alpha_ppm=None)`
* Current `I(current, tolerance=0.0)`
* Power `P(power, tolerance=0.0)`
* Factor `Factor(factor, tolerance)` (unitless factor, example below)

A very simple start would be a perfect 5V voltage:

    >>> U(5)
    5.0V

A 3.3mA current with a 1% tolerance is defined and printed like this:

    >>> I(3.3e-6, 0.01)
    3.3µA ± 1.0% (± 33.0nA) [3.2670 .. 3.3330]µA

Resistors have an optional parameter `alpha_ppm` which is the temperature 
coefficient α in parts per million (ppm). If it is defined, you can get the
resistors' resistance at a different temperature:

    >>> r1 = R(1e3, 0.01, 200)
    >>> r1
    1.0kΩ ± 1.0% (± 10.0Ω) [0.9900 .. 1.0100]kΩ @ 20°C α=200ppm
    >>> r1.at_temperature(250)  # short cut is r1.at_T(250)
    1.05kΩ ± 1.0% (± 10.46Ω) [1.0355 .. 1.0565]kΩ @ 250°C α=200ppm

The series or parallel resistance of two or more resistors can be calculated
using `+` and `|`:

    >>> r1 + r2
    3.7kΩ @ 20°C
    >>> r1 | r2
    729.73Ω @ 20°C
    >>> r3 = R(1e3, 0.01, 150)
    >>> r4 = R(47e3, 0.02, 200)
    >>> r3 | r4
    979.16Ω ± 1.02% (± 10.0Ω) [969.1690 .. 989.1604]Ω @ 20°C
    >>> R(12e3) | (r1 + r2) | r1
    738.77Ω @ 20°C
    >>> r3.at_T(200) | r4.at_T(200)
    1.01kΩ ± 1.02% (± 10.27Ω) [0.9955 .. 1.0160]kΩ @ 200°C

The result of a voltage divider
`R(resistance, tolerance=0.0, alpha_ppm=None).voltage_divider(other_resistor)`
is a unitless factor (`Factor`):

    >>> r1.voltage_divider(r2)
    0.27
    >>> r3.voltage_divider(r4)
    0.02 ± 2.94% [0.0202 .. 0.0215]
    >>> r3 // r4  # short-cut for voltage divider
    0.02 ± 2.94% [0.0202 .. 0.0215]
    >>> U(24) * (r3 // r4)  # output voltage, when input voltage is 24V
    500.28mV ± 2.94% (± 14.69mV) [485.5917 .. 514.9777]mV

Factors are also the result when dividing two variables of the same unit

    >>> f = I(1) / I(2)
    >>> type(f)
    <class '__main__.Factor'>
    >>> I(100e-3, 0.01) / I(22e-6, 0.2)
    4744.32 ± 20.96% [3750.0000 .. 5738.6364]

And of course all the standard *U = R * I* stuff works:

    >>> R(12e3, 0.01) * I(1e-6, 0.02)
    12.0mV ± 3.0% (± 360.0µV) [11.6424 .. 12.3624]mV
    >>> U(5.0) / I(1e-3)
    5.0kΩ @ 20°C
    >>> U(3.3) * I(10e-3)
    33.0mW