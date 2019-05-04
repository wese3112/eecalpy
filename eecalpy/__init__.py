# -*- coding: UTF-8 -*-

# everything is defined in this single file because I could not figure out
# how to deal with cyclic importing when splitting the classes into separate
# files (U must know about R and I when an opearation U / R = I is called)

def min_max_to_nom_tol(min_value, max_value):
    '''Returns the value in the middle of the given min and max value pair
    (named as nominal value) and the +/- tolerance in respect to this nominal
    value as a tuple.
    '''
    nominal = (min_value + max_value) / 2
    tolerance = (max_value - nominal) / nominal
    return nominal, tolerance

def unit_factor_and_prefix(value):
    '''Returns a factor as float and unit prefix as string for a given value.

    Example: value = 0.000001 --> factor = 1e-6, prefix = 'µ'
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
    ]

    for factor, prefix in factors_prefixes:
        # abs(value) is used to handle negative values
        if abs(value) < factor * 1e3:
            return factor, prefix


class ElectricalUnit:
    '''This is the base class for all electrical units'''
    
    def __init__(self, value, tolerance=0.0, unit=''):
        self.value = value
        self.tolerance = tolerance
        
        self._unit = unit
        limits = (  # create to pick min/max value (value might be negative)
            value * (1 - tolerance),
            value * (1 + tolerance)
        )
        self._min, self._max = min(limits), max(limits)
        # self._temp = 20  # inital temperature (only applies to resistors)

    @property
    def min(self):
        return self._min
    
    @property
    def max(self):
        return self._max

    @property
    def unit(self):
        return self._unit

    def __repr__(self):
        # the return string repr_str is build as a list of strings and joined
        # into the to a single sting when returning it.

        # don't use unit prefixes (k, m, µ, ..) when what shall be printed is a
        # Factor. Factors sould be printed as a normal floats.
        if isinstance(self, Factor):
            factor, prefix = 1, ''
        else:
            factor, prefix = unit_factor_and_prefix(self.value)
        
        # example for comments: R(1e3, 0.01, 100)
        repr_str = [
            f'{round(self.value/factor, 2)}{prefix}{self.unit}'
        ]  # e.g. 1.00kΩ

        if float(self.tolerance) != 0.0:
            repr_str.append(
                f'± {round(self.tolerance * 100, 2)}%'
              )  # e.g. '± 1.00%'

            if not isinstance(self, Factor):
                # variation here is the ± value distance from the max/min value
                # to the nominal value (there might be a better name for it...)
                variation = (self.max - self.min) / 2
                v_factor, v_prefix = unit_factor_and_prefix(variation) 
                repr_str.append(
                    f'(± {abs(round(variation/v_factor, 2))}{v_prefix}{self.unit})'
                )  # e.g. '(± 10.0Ω)'

            # this tuple is created to call min()/max() on it below in order to
            # always print the value range as [<lower value> .. <upper value>]
            # (a value might be negative)
            limits = self.min/factor, self.max/factor
            repr_str.append(
                f'[{min(limits):.4f} .. {max(limits):.4f}]{prefix}{self.unit}'
            )  # e.g. '[0.9900 .. 1.0100]kΩ'

        if isinstance(self, R):
            repr_str.append(f'@ {self._temp:d}°C')  # e.g. '@ 20°C'

            if self.alpha_ppm is not None:
                repr_str.append(f'α={self.alpha_ppm}ppm')  # e.g. 'α=100ppm'

        return ' '.join(repr_str)

    def __len__(self):
        return 2  # lower and upper value

    def __getitem__(self, ii):
        return [self.min, self.max][ii]
    

class Factor(ElectricalUnit):
    '''A factor is used for unit-less results of calculations using U, R, I, etc.
    It might come form e.g. U/U or a voltage divider calculation. As all other
    units, a Factor might also have a tolerance range.
    '''

    def __init__(self, factor, tolerance=0.0):
        super(Factor, self).__init__(factor, tolerance, '')
    
    @classmethod
    def from_min_max(cls, f_min, f_max):
        f_nom, f_tol = min_max_to_nom_tol(f_min, f_max)
        return cls(f_nom, f_tol)
    
    # def __mul__(self, other):
    #     if isinstance(other, U):
    #         cls
    #         return U.from_min_max(
    #             self.min * other
    #         )


class R(ElectricalUnit):

    def __init__(self, resistance, tolerance=0.0, alpha_ppm=None):
        assert resistance > 0, 'resistance must be > 0'
        super(R, self).__init__(resistance, tolerance, 'Ω')
        
        self._alpha_ppm = alpha_ppm  # temperature coefficient in ppm
        self._temp = 20  # 20°C is the initial temperature for all resistors
        self._r_t20 = resistance  # resistance at 20°C
    
    @classmethod
    def from_min_max(cls, r_min, r_max, alpha_ppm=None):
        r_nom, r_tol = min_max_to_nom_tol(r_min, r_max)
        return cls(r_nom, r_tol, alpha_ppm)
    
    @property
    def temperature(self):
        return self._temp
    
    @property
    def alpha_ppm(self):
        return self._alpha_ppm

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
        temp_err_msg = 'The resistors must be at the same temperature'
        assert self.temperature == other.temperature, temp_err_msg

        r_min, r_max = (
            a + b
            for a, b
            in zip([self.min, self.max], [other.min, other.max])
        )
        r = R.from_min_max(r_min, r_max)
        r._temp = self.temperature
        return r

    def __or__(self, other):
        temp_err_msg = 'The resistors must be at the same temperature'
        assert self.temperature == other.temperature, temp_err_msg

        r_min, r_max = (
            a * b / (a + b)
            for a, b
            in zip([self.min, self.max], [other.min, other.max])
        )
        r = R.from_min_max(r_min, r_max)
        r._temp = self.temperature
        return r
    
    def __truediv__(self, other):
        if isinstance(other, R):  # R / R = Factor
            temp_err_msg = 'The resistors must be at the same temperature'
            assert self.temperature == other.temperature, temp_err_msg

            return Factor.from_min_max(
                self.min / other.max,  # min. value
                self.max / other.min  # max. value
            )

        return (self.min / other, self.max / other)
    
    def __mul__(self, other):
        if isinstance(other, I):  # R * I = U
            return U.from_min_max(
                self.min * other.min,  # min. voltage
                self.max * other.max  # max. voltage
            )
        
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

    def __init__(self, voltage, tolerance=0.0):
        super(U, self).__init__(voltage, tolerance, 'V')
    
    @classmethod
    def from_min_max(cls, v_min, v_max):
        v_nom, v_tol = min_max_to_nom_tol(v_min, v_max)
        return cls(v_nom, v_tol)
    
    def __add__(self, other):
        if isinstance(other, U):
            return U.from_min_max(
                self.min + other.min,
                self.max + other.max
            )
        
        return (self.min + other, self.max + other,)
    
    def __sub__(self, other):
        if isinstance(other, U):
            return U.from_min_max(
                self.min - other.max,
                self.max - other.min
            )
        
        return (self.min - other, self.max - other,)

    def __truediv__(self, other):
        v_min = self.min / other.max  # min. value
        v_max = self.max / other.min  # max. value

        if isinstance(other, R):  # U / R = I
            return I.from_min_max(v_min, v_max)
        
        if isinstance(other, I):  # U / I = R
            return R.from_min_max(v_min, v_max)
        
        if isinstance(other, U):  # U / U = Factor
            return Factor.from_min_max(v_min, v_max)
        
        if isinstance(other, Factor):  # U / Factor = U
            return U.from_min_max(v_min, v_max)
        
        return (self.min / other, self.max / other,)

    def __mul__(self, other):
        v_min = self.min * other.min  # min. value
        v_max = self.max * other.max  # max. value

        if isinstance(other, I):
            return P.from_min_max(v_min, v_max)
        
        if isinstance(other, Factor):
            return U.from_min_max(v_min, v_max)
        
        return (self.min / other, self.max / other,)


class I(ElectricalUnit):

    def __init__(self, current, tolerance=0.0):
        super(I, self).__init__(current, tolerance, 'A')
    
    @classmethod
    def from_min_max(cls, i_min, i_max):
        i_nom, i_tol = min_max_to_nom_tol(i_min, i_max)
        return cls(i_nom, i_tol)
    
    def __add__(self, other):
        return I.from_min_max(  # I + I = I
            self.min + other.min,
            self.max + other.max
        )

    def __mul__(self, other):
        v_min = self.min * other.min
        v_max = self.max * other.max

        if isinstance(other, R):  # I * R = U
            return U.from_min_max(v_min, v_max)
        
        if isinstance(other, U):  # I * U = P
            return P.from_min_max(v_min, v_max)
    
    def __truediv__(self, other):
        if isinstance(other, I):  # I / I = Factor
            return Factor.from_min_max(
                self.min / other.max,
                self.max / other.min
            )

        return (self.min / other, self.max / other)


class P(ElectricalUnit):

    def __init__(self, current, tolerance=0.0):
        super(P, self).__init__(current, tolerance, 'W')
    
    @classmethod
    def from_min_max(cls, p_min, p_max):
        p_nom, p_tol = min_max_to_nom_tol(p_min, p_max)
        return cls(p_nom, p_tol)

    def __truediv__(self, other):
        v_min = self.min / other.max
        v_max = self.max / other.min

        if isinstance(other, U):  # P / U = I
            return I.from_min_max(v_min, v_max)
        
        if isinstance(other, I):  # P / I = U
            return U.from_min_max(v_min, v_max)
        
        if isinstance(other, P):  # P / P = Factor
            return Factor.from_min_max(v_min, v_max)
        
        return self.min / other, self.max / other