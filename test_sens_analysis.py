from eecalpy import* 
import matplotlib.pyplot as plt

sa = SensitivityAnalysis('''
i1 = 3mA
r1 = 120k
r2 = 440k
''')

sa.calculation = lambda x: (x.r1 | x.r2) * x.i1
res = sa.run()

fig, ax = plt.subplots()
ax.plot(res['tolerances'], res['r1'], label='R1')
ax.plot(res['tolerances'], res['r2'], label='R2')
ax.plot(res['tolerances'], res['i1'], label='I1')
ax.set_xticklabels([f'{tol*100.0:.2f}%' for tol in res['tolerances']])
ax.grid()
ax.legend()
plt.show()
