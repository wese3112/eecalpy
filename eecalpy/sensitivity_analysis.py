from .electrical_units import U, R, I, P, Factor, Usq, Isq
from .parser import ee_script, ee_transformer


class SensitivityAnalysis:

    def __init__(self, script=None):
        self._vars = None
        self.script = self.load_script(script) if script is not None else None
        self._calculation = None
        self.tolerances = [t/100.0 for t in [0.1, 0.5, 1, 2, 5, 10]]  # %
    
    def load_script(self, script):
        self.script = ee_script(script, print_output=False)
        self._vars = ee_transformer.vars
        for k, v in self._vars.items():
            self.__dict__[k] = v
    
    @property
    def calculation(self):
        if self._calculation is None:
            print('no calculation function set')
        else:
            print('calculation function is set')

    @calculation.setter
    def calculation(self, callback):
        self._calculation = callback
    
    def run(self):
        assert self._calculation is not None, 'no calculation function set'
        _save = self._vars.copy()
        results = {'tolerances': self.tolerances}

        for k, v in self._vars.items():
            results[k] = list()
            for tol in self.tolerances:
                self.__dict__[k] = type(v)(v.value, tol)

                res = self._calculation(self)
                results[k].append(res.tolerance)
                print(res, '-->', [v.pretty() for k, v in self._vars.items()], '-->', f'{res.tolerance*100.0:.2f}')
            
            # restore
            self.__dict__[k] = _save[k]
        
        return results
            
