from .electrical_units import U, R, I, P, E, Time, Factor, Usq, Isq
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
     | name          -> var
     | "(" sum ")"


// eecalpy
?eeinput: resistance
        | eeclass

value: SIGNED_NUMBER
prefix: /[pfnµmkGM]/
unit: /[VAWJsf]/
name: /[a-zA-Z][a-zA-Z_0-9]*/
// temperature: "@" value "°C"

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
// %ignore "?"
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
        return name + ' = ' + str(value)

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
            'J': E,
            's': Time,
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

ee_transformer = EecalpyScriptTransformer()

eecalpy_script_parser = Lark(
    eecalpy_grammar,
    parser='lalr',
    transformer=ee_transformer
)

def _parse_line(line):
    line = line.strip()
    if line == '' or line.startswith('#'):
        return None
    if line.startswith("exit"):
        raise EOFError

    try:
        return str(eecalpy_script_parser.parse(line))
    except KeyError as e:
        print(e)
    except UnexpectedInput as u:
        print(line)
        print(' '*(u.pos_in_stream-1), '|')
        print(' '*(u.pos_in_stream-1), 'unexpedted symbol')
        print(u)

def ee_console():
    while True:
        try:
            line = _parse_line(input('» '))
            if line is not None:
                print(line)
        except EOFError:
            break

def ee_script(scr, print_output=True):
    out = [_parse_line(l.strip()) for l in scr.split('\n')]
    out = [str(o) for o in filter(lambda x: x, out)]
    
    if not print_output:
        return '\n'.join(out)
    
    for line in out:
        print(line)

def ee_script_file(scr_file):
    with open(scr_file, 'r') as script:
        out = [_parse_line(l.strip()) for l in script.readlines()]
    
    scr = '\n'.join([str(o) for o in filter(lambda x: x, out)])
    ee_script(scr)

def parse_expression(expression):
    return eecalpy_script_parser.parse(expression)
