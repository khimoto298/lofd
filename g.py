# -*- coding: utf-8 -*-

import numpy as np

from cgprm import Tend, nXX, nYY, nO
from gprm import Object

# computational time
Tsec = 0.0  # time in seconds
Tmin = 0.0  # time in minutes
nSTP = 0  # number of time steps

# outline of computation
IGN = 0  # fire origin
nOBJ = 0  # number of objects
nFB = np.zeros(3, dtype=int)  # number of objects at each combustion status (ref. iFB)
nFB_r = np.zeros((int(Tend) + 1, 3), dtype=int)  # record of nFB (ref. iFB)

# weather condition
TT0 = 0.0  # ambient temperature
RR0 = 0.0  # ambient density
UU0 = 0.0  # ambient wind
VW = 2 * [0.0]  # wind vector

# subdivition of computational domain
XX = np.zeros(nXX + 1, dtype=float)  # computational mesh (X)
YY = np.zeros(nYY + 1, dtype=float)  # computational mesh (Y)
lO_M = np.zeros(nO, dtype=int)  # list of objects contained in mesh
nO_M = np.zeros(nXX * nYY + 1, dtype=int)  # start number in the list

OO = [Object() for _ in range(nO)]
