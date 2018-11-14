"""
Simulate random walk of two particles connected by a spring subject to two different diffusivities D1 and D2
"""

try:
    bl_has_run

except Exception:
    %matplotlib
    %load_ext autoreload
    %autoreload 2
    bl_has_run = True

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm, trange

from stopwatch import stopwatch

# matplotlib.use('TkAgg')

# % Constants
D1 = 0.4  # um^2/s; 0.4
D2 = 5 * D1  # um^2/s
k1 = k2 = 0 * 1e-6 / 1e3   # spring constant, N/m = kg/s^2; 1e-6
k12 = 0 * k1   # spring constant, N/m = kg/s^2; 2e-3, 3e-3; 1.5e-3
kB = 1.38e-11  # kg*um^2/s^2/K
gamma = 1e-8  # viscous drag, in kg/s; 4e-8
L12 = 2  # um
dt = 1e-4  # seconds
# substeps = 100
N = 1 + int(1e5)  # time step
x10 = -L12 / 2
x20 = L12 / 2
file = './trajectory.dat'
D1 * gamma / kB

# % Initialize
x1 = np.ones(N) * np.nan
x2 = np.ones(N) * np.nan
dx1 = np.zeros(N)
dx2 = np.zeros(N)
dx1[N - 1] = dx2[N - 1] = np.nan
t = np.arange(N) * dt


# % Calculation
A = np.array(
    [[-(k1 + k12), k12],
     [k12, -(k2 + k12)]]) / gamma
a = np.array([k1 * x10 - k12 * L12, k2 * x20 + k12 * L12]) / gamma
b = np.sqrt(2 * np.array([D1, D2]))
x0 = np.array([x10, x20])

# noise
np.random.seed()
dW = np.random.randn(2, N)
dW[0, :] = dW[0, :] * np.sqrt(dt)
dW[1, :] = dW[1, :] * np.sqrt(dt)


def mat_exp(M):
    """Calculate matrix exponent
    """
    lambdas, U = np.linalg.eig(M)
    Um1 = np.linalg.inv(U)
    return U @ np.diag(np.exp(lambdas)) @ Um1


# Iterative calculations
X = np.zeros((2, N))
X[:, 0] = x0
A_exponent = mat_exp(A * dt)
with stopwatch():
    for i in trange(N - 1):
        X[:, i + 1] = A_exponent @ (X[:, i] + a * dt + b * dW[:, i])

np.mean(X, axis=1)

fig = plt.figure(1, clear=True)
plt.plot(t, X[0, :])
plt.plot(t, X[1, :])
plt.xlabel('t, s')
plt.ylabel('$x, \mu$m')

plt.show()
plt.savefig('simulated_trajectories.png')

# % Save
dX = X[:, 1:] - X[:, 0:-1]
dX = np.concatenate([dX, [[np.nan], [np.nan]]], axis=1)
output = np.stack([t, X[0, :], dX[0, :], X[1, :], dX[1, :]], axis=1)
output = pd.DataFrame(data=output, columns=['t', 'x', 'dx', 'x2', 'dx2'])
# output = pd.DataFrame(data=output, columns=['t', 'x2', 'dx2', 'x', 'dx'])
output.to_csv(file, sep=';', index=False)
#
# %% Tests of scales
np.var(dX[:, :-1], axis=1, ddof=1) / 2 / dt
[D1, D2]
# np.var(dx1[:N - 1]) / 2 / dt
# np.sqrt(2 * dt) / L12
# np.sqrt(2 * dt) / 0.05
# np.sqrt(2 * dt_sim) / L12
# k12 * L12 / 4 / gamma * dt_sim
# np.sqrt(2 * D1 * dt_sim) * noise[0, 0]
# D1 * gamma / kB
# k12 * np.sqrt(2 * D1) * dt**(3 / 2) / gamma
