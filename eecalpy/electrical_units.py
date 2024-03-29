# -*- coding: UTF-8 -*-
from decimal import Decimal
from typing import Optional, Tuple


def mean_and_tolerance(lower_lim: float, upper_lim: float) -> Tuple[float, Optional[float]]:
    '''Calculate mean value and tolerance of a value range

    The mean value here is the value in the middle of the given min/max float
    value pair. The tolerance here is the percentual deviation of the min/max
    values in respect to this mean value.

    Args:
        lower_lim: lower limit of the value range as float
        upper_lim: upper limit of the value range as float
    
    Returns:
        A tuple returning the mean value and tolerance of the given values.
    '''
    if lower_lim == upper_lim == 0.0:
        return 0.0, 0.0

    if lower_lim == -upper_lim:
        return 0.0, None

    mean = (lower_lim + upper_lim) / 2
    tol = abs((upper_lim - mean) / mean)
    
    return mean, None if tol > 1.0 or lower_lim == upper_lim else tol


def unit_factor_and_prefix(value: float) -> Tuple[float, str]:
    '''Returns a factor as float and unit prefix as string for a given value.

    Example: value = 0.000002 --> factor = 1e-6, prefix = 'µ' --> 2µ
    '''
    factors_prefixes = [
        (1e-12, 'p'),
        (1e-9, 'n'),
        (1e-6, 'µ'),
        (1e-3, 'm'),
        (1, ''),
        (1e3, 'k'),
        (1e6, 'M'),
        (1e9, 'G'),
        (1e12, 'T')
    ]

    ranges = list(zip(factors_prefixes[:-1], factors_prefixes[1:]))

    for rr in ranges:
        a, b = rr
        lower, prefix = a
        upper, _ = b
    
        if lower <= abs(value) < upper:
            return lower, prefix
    else:
        if abs(value) < factors_prefixes[0][0]:
            return factors_prefixes[0]
        else:
            return factors_prefixes[-1]


class ElectricalUnit:
    '''This is the base class for all electrical units'''
    
    def __init__(self, value, tolerance=0.0, unit='', limits=None):
        self.value = value
        self.tolerance = 0.0 if tolerance is None else float(tolerance)
        
        self._unit = unit
        if limits is None:
            limits = (  # create to pick min/max value (value might be negative)
                float(Decimal(str(value)) * Decimal(str(1 - self.tolerance))),
                float(Decimal(str(value)) * Decimal(str(1 + self.tolerance)))
            )

        self._min, self._max = min(limits), max(limits)
        

    @classmethod
    def from_min_max(cls, _min, _max):
        mean, tol = mean_and_tolerance(_min, _max)
        return cls(mean, tol, limits=(_min, _max) if tol is None else None)

    @property
    def min(self):
        return self._min
    
    @property
    def max(self):
        return self._max

    @property
    def unit(self):
        return self._unit

    def _value_repr(self):
        factor, prefix = unit_factor_and_prefix(self.value)

        return f'{round(self.value/factor, 2)}{prefix}{self.unit}'
    
    def _tolerance_repr(self):
        return f'± {round(self.tolerance*100, 2)}%' if self.tolerance != 0.0 else ''

    def _variation_repr(self):
        # variation here is the ± value distance from the max/min value
        # to the mean value (there might be a better name for it...)
        variation = float(Decimal(str(self.max)) - Decimal(str(self.min))) / 2
        factor, prefix = unit_factor_and_prefix(variation) 

        return f'(± {abs(round(variation/factor, 2))}{prefix}{self.unit})'

    def _vrange_repr(self):
        factor, prefix = unit_factor_and_prefix(self.value)

        if self.min < self.max:
            _min, _max = self.min/factor, self.max/factor
        else:
            _min, _max = self.max/factor, self.min/factor

        return f'[{_min:.4f} .. {_max:.4f}]{prefix}{self.unit}'
    
    def pretty(self, value=True, tolerance=True, variation=True, vrange=True, temperature=True):
        parts = list()

        if value:
            parts.append(self._value_repr())

        if tolerance and self.tolerance != 0.0:
            parts.append(self._tolerance_repr())

            if variation and not isinstance(self, Factor):
                parts.append(self._variation_repr())

            if vrange:
                parts.append(self._vrange_repr())
        
        if temperature and isinstance(self, R):
            parts.append(self._temperature_repr())
        
        return ' '.join(parts)

    def __repr__(self):
        return self.pretty()

    def __len__(self):
        return 2  # lower and upper value

    def __getitem__(self, ii):
        return [self.min, self.max][ii]
    
    def __add__(self, other):
        if isinstance(other, type(self)):
            return type(self).from_min_max(
                self.min + other.min,
                self.max + other.max
            )
        
        return self.min + other, self.max + other
    
    def __sub__(self, other):
        if isinstance(other, type(self)):
            return type(self).from_min_max(
                self.min - other.max,
                self.max - other.min
            )

        return self.min - other, self.max - other

    def __mul__(self, other):
        if type(other) not in self.mul_conversions:
            return self.min * other, self.max * other
        
        return self.mul_conversions[type(other)].from_min_max(
            self.min * other.min,
            self.max * other.max
        )
    
    def __truediv__(self, other):
        if type(other) not in self.div_conversions:
            return self.min / other, self.max / other
        
        return self.div_conversions[type(other)].from_min_max(
            self.min / other.max,
            self.max / other.min
        )
    

class Factor(ElectricalUnit):
    '''A factor is used for unit-less results of calculations using U, R, I, etc.
    It might come form e.g. U/U or a voltage divider calculation. As all other
    units, a Factor might also have a tolerance range.
    '''

    def __init__(self, factor, tolerance=0.0, limits=None):
        super(Factor, self).__init__(factor, tolerance, '')
    
    def __mul__(self, other):
        if not any([isinstance(other, eu) for eu in (U, R, I, P, Factor)]):
            return self.min * other, self.max * other
        
        if isinstance(other, R):
            r = R.from_min_max(
                self.min * other.min,
                self.max * other.max
            )
            r._temp = other.temperature
            return r
        else:
            return type(other).from_min_max(
                self.min * other.min,
                self.max * other.max
            )
    
    def __truediv__(self, other):
        if isinstance(other, Factor):
            return Factor.from_min_max(
                self.min / other.max,
                self.max / other.min
            )
    
    def __add__(self, other):
        # adding factors does not make sense
        pass

    def __sub__(self, other):
        # subtracting factors does not make sense
        pass


class R(ElectricalUnit):

    def __init__(self, resistance, tolerance=0.0, alpha_ppm=None, limits=None):
        assert resistance > 0, 'resistance must be > 0'
        super(R, self).__init__(resistance, tolerance, 'Ω')
        
        # temperature coefficient in ppm
        self._alpha_ppm = int(alpha_ppm) if alpha_ppm is not None else None
        self._temp = 20  # 20°C is the initial temperature for all resistors
        self._r_t20 = resistance  # resistance at 20°C
    
    @classmethod
    def from_min_max(cls, r_min, r_max, alpha_ppm=None):
        r_mean, r_tol = mean_and_tolerance(r_min, r_max)
        return cls(r_mean, r_tol, alpha_ppm)
    
    @property
    def temperature(self):
        return self._temp
    
    @property
    def alpha_ppm(self):
        return self._alpha_ppm
    
    def _temperature_repr(self):
        parts = ['@ mixed temp.' if self._temp is None else f'@ {self._temp:d}°C']

        if self.alpha_ppm is not None:
            parts.append(f'α={self.alpha_ppm}ppm')
        
        return ' '.join(parts)

    def at_temperature(self, temperature):
        err_msg = 'temperature coefficient alpha (R.alpha_ppm) not specified'
        assert self.alpha_ppm is not None, err_msg

        R0, α, T = self._r_t20, self.alpha_ppm * 10**-6, temperature

        # https://en.wikipedia.org/wiki/Temperature_coefficient#Electrical_resistance
        r = R(
            R0 * (1 + α * (T - 20)),
            self.tolerance,
            self.alpha_ppm
        )
        r._temp = T
        return r
    
    def at_T(self, temperature):
        return self.at_temperature(temperature)
    
    def __add__(self, other):
        r_min, r_max = (
            a + b
            for a, b
            in zip([self.min, self.max], [other.min, other.max])
        )
        r = R.from_min_max(r_min, r_max)
        r._temp = self._temp if self._temp == other._temp else None
        return r

    def __sub__(self, other):
        # overwrite the parent classes' subtracting method - it does not make
        # sense for resistors
        pass

    def __or__(self, other):
        r_min, r_max = (
            a * b / (a + b)
            for a, b
            in zip([self.min, self.max], [other.min, other.max])
        )
        r = R.from_min_max(r_min, r_max)
        r._temp = self._temp if self._temp == other._temp else None
        return r
    
    def __truediv__(self, other):
        if isinstance(other, R):  # R / R = Factor
            return Factor.from_min_max(
                self.min / other.max,
                self.max / other.min
            )
        
        if isinstance(other, Factor):
            # other_min = min(other)
            # other_max = max(other)
            r = R.from_min_max(
                self.min / other.max,
                self.max / other.min
            )
            r._temp = self._temp if self._temp == other._temp else None
            return r

        return self.min / other, self.max / other
    
    def __mul__(self, other):
        if isinstance(other, I):  # R * I = U
            return U.from_min_max(
                self.min * other.min,
                self.max * other.max
            )
        
        if isinstance(other, Factor):
            r = R.from_min_max(
                self.min * other.min,
                self.max * other.max
            )
            r._temp = self.temperature
            return r
        
        r = R.from_min_max(self.min * other, self.max * other, self.alpha_ppm)
        r._temp = self._temp
        return r

    def __floordiv__(self, other):
        return self.voltage_divider(other)
    
    def voltage_divider(self, other_resistor, voltage=None):
        temp_err_msg = 'The resistors must be at the same temperature'
        assert self.temperature == other_resistor.temperature, temp_err_msg

        # factors of all combinations of the voltage divider
        factors = [
            a / (a + b)
            for a in [self.min, self.max]
            for b in [other_resistor.min, other_resistor.max]
        ]

        # voltage divider factor
        f_vd = Factor.from_min_max(min(factors), max(factors))

        if voltage is None:
            return f_vd

        return voltage * f_vd


class U(ElectricalUnit):

    def __init__(self, voltage, tolerance=0.0, limits=None):
        super(U, self).__init__(voltage, tolerance, 'V')

        # unit conversions when multiplying U with other units
        self.mul_conversions = {
            I: P,  # U * I = P
            U: Usq,  # U * U = U²
            Factor: U  # U * f = U
        }
        # unit conversions when dividing U with other units
        self.div_conversions = {
            R: I,  # U / R = I
            I: R,  # U / I = R
            U: Factor,  # U / U = Factor
            Factor: U,  # U / Factor = U
        }
    
    def __pow__(self, other):
        assert other == 2, 'voltages can only be squared using U(..)**2'
        return Usq.from_min_max(self.min**2, self.max**2)


class I(ElectricalUnit):

    def __init__(self, current, tolerance=0.0, limits=None):
        super(I, self).__init__(current, tolerance, 'A')

        # unit conversions when multiplying I with other units
        self.mul_conversions = {
            R: U,  # I * R = U
            I: Isq,  # I * I = I²
            U: P,  # I * U = P
            Factor: I  # I * f = I
        }
        # unit conversions when dividing I with other units
        self.div_conversions = {
            I: Factor,  # I / I = Factor
            Factor: I,  # I / Factor = I
        }
    
    def __pow__(self, other):
        assert other == 2, 'currents can only be squared using I(..)**2'
        return Isq.from_min_max(self.min**2, self.max**2)


class P(ElectricalUnit):

    def __init__(self, current, tolerance=0.0, limits=None):
        super(P, self).__init__(current, tolerance, 'W')

        # unit conversions when multiplying U with other units
        self.mul_conversions = {
            Factor: P,  # P * f = P
            Time: E  # P * Time = E
        }
        # unit conversions when dividing P with other units
        self.div_conversions = {
            U: I,  # P / U = I
            I: U,  # P / I = U
            P: Factor,  # P / P = f
            Factor: P  # P / f = P
        }


class Time(ElectricalUnit):

    def __init__(self, time, tolerance=0.0, limits=None):
        super(Time, self).__init__(time, tolerance, 's')

        # unit conversions when multiplying U with other units
        self.mul_conversions = {
            Factor: Time  # Time * f = Time
        }
        # unit conversions when dividing P with other units
        self.div_conversions = {
            Time: Factor,  # Time / Time = f
            Factor: Time  # Time / f = Time
        }


class E(ElectricalUnit):

    def __init__(self, energy, tolerance=0.0, limits=None):
        super(E, self).__init__(energy, tolerance, 'J')

        # unit conversions when multiplying U with other units
        self.mul_conversions = {
            Factor: E  # E * f = E
        }
        # unit conversions when dividing P with other units
        self.div_conversions = {
            Time: P,  # E / Time = P
            E: Factor,  # E / E = f
            Factor: E  # E / f = E
        }


class Usq(ElectricalUnit):

    def __init__(self, current, tolerance=0.0, limits=None):
        super(Usq, self).__init__(current, tolerance, 'V²')

        # unit conversions when multiplying U with other units
        self.mul_conversions = {
            Factor: Usq  # U² * f = U²
        }
        # unit conversions when dividing P with other units
        self.div_conversions = {
            R: P,  # U² / R = P
            P: R,  # U² / I = U
            U: U,  # U² / U = U
            Usq: Factor,  # U² / U² = f
            Factor: Usq  # U² / f = U²
        }


class Isq(ElectricalUnit):

    def __init__(self, current, tolerance=0.0, limits=None):
        super(Isq, self).__init__(current, tolerance, 'A²')

        # unit conversions when multiplying U with other units
        self.mul_conversions = {
            Factor: Isq,  # I² * f = I²
            R: P  # I² * R = P
        }
        # unit conversions when dividing P with other units
        self.div_conversions = {
            I: I,  # I² / I = I
            Isq: Factor,  # I² / I² = f
            Factor: Isq  # I² / f = I²
        }
