# -*- coding: UTF-8 -*-

import unittest
from eecalpy import *


class TestElectricalUnit(unittest.TestCase):
    
    def test_classmethod_fmm(self):
        for unit in (U, R, I, P, Factor):
            eu = unit.from_min_max(1, 3)
            self.assertIsInstance(eu, unit)
            self.assertEqual(eu.min, 1)
            self.assertEqual(eu.value, 2)
            self.assertEqual(eu.max, 3)
        
        r = R.from_min_max(1, 3, 200)
        self.assertEqual(r.alpha_ppm, 200)

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
    
    def test_operators(self):
        selected_examples = [
            (U(2.5) + U(2.5), 5.0),
            (U(10) - U(5), 5.0),
            (I(2.5) + I(2.5), 5.0),
            (I(10) - I(5), 5.0),
            (P(2.5) + P(2.5), 5.0),
            (P(10) - P(5), 5.0),
        ]

        for U_op, expected in selected_examples:
            self.assertEqual(U_op.value, expected)

    def test_repr(self):
        r = R(1e3, 0.01, 200).at_T(100) + R(2e3, 0.01, 150)
        selected_examples = [
            (U(3), '3.0V'),
            (U(-12.3), '-12.3V'),
            (U(818e3), '818.0kV'),
            (U(200e-3, 0.1), '200.0mV ± 10.0% (± 20.0mV) [180.0000 .. 220.0000]mV'),
            (r, '3.02kΩ ± 1.0% (± 30.16Ω) [2.9858 .. 3.0462]kΩ @ mixed temp.')
        ]

        for _repr, expected in selected_examples:
            self.assertEqual(str(_repr), expected)


class TestResistors(unittest.TestCase):
    r1 = R(1e3, 0.01, 200)
    r2 = R(2e3, 0.01, 150)

    def test_same_temperatures(self):
        r = self.r1 + self.r2
        self.assertEqual(r.temperature, 20.0)

        r = self.r1 | self.r2
        self.assertEqual(r.temperature, 20.0)

        r = self.r1.at_T(100) + self.r2.at_T(100)
        self.assertEqual(r.temperature, 100.0)

        r = self.r1.at_T(100) | self.r2.at_T(100)
        self.assertEqual(r.temperature, 100.0)

    def test_temp_and_factors(self):
        r = self.r1.at_T(100) * Factor(2.0)
        self.assertEqual(r.temperature, 100.0)

        r = Factor(2.0) * self.r1.at_T(100)
        self.assertEqual(r.temperature, 100.0)

        r = self.r1 * Factor(2.0)
        self.assertEqual(r.temperature, 20.0)

        r = Factor(2.0) * self.r1
        self.assertEqual(r.temperature, 20.0)

        r = self.r1.at_T(100) * Factor(2.0)
        self.assertEqual(r.temperature, 100.0)

        r = Factor(2.0) * self.r1.at_T(100)
        self.assertEqual(r.temperature, 100.0)

    def test_different_temperatures(self):
        r = self.r1 + self.r2.at_T(100)
        self.assertIsNone(r.temperature)

        r = self.r1 | self.r2.at_T(100)
        self.assertIsNone(r.temperature)

        r = self.r1.at_T(100) + self.r2.at_T(60)
        self.assertIsNone(r.temperature)

        r = self.r1.at_T(60) | self.r2.at_T(100)
        self.assertIsNone(r.temperature)


class TestTypeConversions(unittest.TestCase):

    def test_operations_mul(self):
        # U = R * I
        self.assertIsInstance(R(1) * I(1), U)
        self.assertIsInstance(I(1) * R(1), U)

        # P = U * I
        self.assertIsInstance(U(1) * I(1), P)
        self.assertIsInstance(I(1) * U(1), P)

        # factors
        self.assertIsInstance(Factor(1) * Factor(1), Factor)
        self.assertIsInstance(U(1) * Factor(1), U)
        self.assertIsInstance(R(1) * Factor(1), R)
        self.assertIsInstance(I(1) * Factor(1), I)
        self.assertIsInstance(P(1) * Factor(1), P)
        self.assertIsInstance(Factor(1) * U(1), U)
        self.assertIsInstance(Factor(1) * R(1), R)
        self.assertIsInstance(Factor(1) * I(1), I)
        self.assertIsInstance(Factor(1) * P(1), P)

    def test_operations_div(self):
        self.assertIsInstance(U(1) / R(1), I)  # U / R = I
        self.assertIsInstance(U(1) / I(1), R)  # U / I = R
        self.assertIsInstance(P(1) / U(1), I)  # P / U = I
        self.assertIsInstance(P(1) / I(1), U)  # P / I = U
        self.assertIsInstance(R(1) / R(1), Factor)  # R / R = f
        self.assertIsInstance(U(1) / U(1), Factor)  # U / U = f
        self.assertIsInstance(I(1) / I(1), Factor)  # I / I = f
        self.assertIsInstance(P(1) / P(1), Factor)  # P / P = f
        self.assertIsInstance(Factor(1) / Factor(1), Factor)  # f / f = f


if __name__ == '__main__':
    unittest.main()