from .electrical_units import U, R, I, P, Factor, Usq, Isq
from lark import Lark, Transformer, v_args, UnexpectedInput

# with open('./eecalpy/eecalpy_grammar.lark', 'r') as grammar_definition:
#     eecalpy_grammar = grammar_definition.read()

eecalpy_grammar = r'''
?start: sum
        | name "=" sum    -> assign_var

?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub

?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> truediv
    | product "|" atom  -> or_
    | product "//" atom -> floordiv
    | atom "^2"         -> squared

?atom: eeinput
        | name             -> var
        | "(" sum ")"

// eecalpy
?eeinput: resistance
        | eeclass

value: SIGNED_NUMBER
prefix: /[pfnµmkGM]/
unit: /[VAWf]/
name: /[a-zA-Z][a-zA-Z_0-9]*/

tolerance: value "%"
tempcoeff: value "ppm"

eevalue: value prefix?

resistance: eevalue
            | resistance tolerance            -> r_tol
            | resistance tempcoeff            -> r_tmp
            | resistance tolerance tempcoeff  -> r_tol_tmp

eeclass: eevalue unit
        | eeclass tolerance                  -> ee_tol

%import common.SIGNED_NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
'''

@v_args(inline=True)
class EecalpyScriptTransformer(Transformer):
    from operator import add, sub, mul, truediv, floordiv , or_

    def __init__(self):
        self.vars = {}

    def name(self, name):
        return str(name)

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        var = str(name)
        if var not in self.vars:
            raise KeyError(f'unknown variable {var}')
        
        return self.vars[var]
    
    def value(self, signed_number):
        return float(signed_number)

    def unit(self, symbol):
        return {
            'V': U,
            'A': I,
            'W': P,
            'f': Factor
        }[symbol]

    def tolerance(self, percentage):
        return percentage / 100.0
    
    def tempcoeff(self, tempcoeff):
        return int(tempcoeff)

    def prefix(self, prefix):
        return {
            'p': 1e-12,
            'n': 1e-9,
            'µ': 1e-6,
            'm': 1e-3,
            'k': 1e3,
            'M': 1e6,
            'G': 1e9
        }[prefix]
    
    def eevalue(self, value, prefix=None):
        if prefix is None:
            return value
        return value * prefix

    def resistance(self, eevalue):
        return R(eevalue)
    
    def r_tol(self, resistance, tolerance):
        return R(resistance.value, tolerance=tolerance)
    
    def r_tmp(self, resistance, tempcoeff):
        return R(resistance.value, 0.0, tempcoeff)
    
    def r_tol_tmp(self, resistance, tolerance, tempcoeff):
        return R(resistance.value, tolerance, tempcoeff)

    def eeclass(self, eevalue, unit):
        return unit(eevalue)
    
    def ee_tol(self, eeclass, tolerance):
        return type(eeclass)(eeclass.value, tolerance)

    def squared(self, eevalue):
        return eevalue**2

eecalpy_script_parser = Lark(
    eecalpy_grammar,
    parser='lalr',
    transformer=EecalpyScriptTransformer()
)
eecal = eecalpy_script_parser.parse

def _parse_line(line):
    if line == '' or line.startswith('#'):
        return None
    if line.startswith("exit"):
        raise EOFError

    try:
        return eecal(line)
    except KeyError as e:
        print(e)
    except UnexpectedInput as u:
        print(line)
        print(' '*(u.pos_in_stream-1), '↧')
        print(' '*(u.pos_in_stream-1), 'unexpedted symbol')
        print(u)

def console():
    while True:
        try:
            print(_parse_line(input('» ')))
        except EOFError:
            break

def script(script_file):
    with open(script_file, 'r') as script:
        out = [_parse_line(l.strip()) for l in script.readlines()]
    
    return '\n'.join([str(o) for o in filter(lambda x: x, out)])