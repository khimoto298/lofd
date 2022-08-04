# -*- coding: utf-8 -*-

from cgprm import *
from gprm import *
import g
from rndm import *
from init import *
from ndat import *
from fire import *
from sprd import *

INIT()

while True:

    OUTP()
    NDAT()
    FIRE()
    SPRD()

    if g.Tmin > Tend or g.nFB[1] == 0:
        break

    g.nSTP += 1
    g.Tsec += dTsec
    g.Tmin = g.Tsec / 60.0
    
RSLT()
