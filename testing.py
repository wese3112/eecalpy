# -*- coding: UTF-8 -*-

import unittest
from eecalpy import *


class TestElectricalUnit(unittest.TestCase):
    
    def test_tolerance(self):
        selected_examples = [
            (U(10, 0.1), 9.0, 10.0, 11.0),
            (R(2, 0.01), 1.98, 2.0, 2.02),
            (I(-10, 0.1), -11.0, -10.0, -9.0)
        ]

        for eu, v_min, v_nom, v_max in selected_examples:
            self.assertEqual(eu.min, v_min)
            self.assertEqual(eu.value, v_nom)
            self.assertEqual(eu.max, v_max)

class TestVoltages(unittest.TestCase):

    def test_repr(self):
        selected_examples = [
            (U(3), '3.0V'),
            (U(-12.3), '-12.3V'),
            (U(818e3), '818.0kV'),
            (U(200e-3, 0.1), '200.0mV ± 10.0% (± 20.0mV) [180.0000 .. 220.0000]mV')
        ]

        for U_repr, expected in selected_examples:
            self.assertEqual(str(U_repr), expected)
    
    def test_operators(self):
        selected_examples = [
            (U(2.5) + U(2.5), 5.0),
            (U(10) - U(5), 5.0)
        ]

        for U_op, expected in selected_examples:
            self.assertEqual(U_op.value, expected)


if __name__ == '__main__':
    unittest.main()