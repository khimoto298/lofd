# -*- coding: utf-8 -*-

from math import sqrt

from cgprm import *
from gprm import *
import g


# ------------------------------------------------------------------------------
#        fire behavior
# ------------------------------------------------------------------------------
def FIRE():

    HRR()  # MLR & HRR
    HTRF()  # external heat flux & ignition time


# ------------------------------------------------------------------------------
#        MLR & HRR
# ------------------------------------------------------------------------------
def HRR():

    for x in g.OO:
        x.rMF = 0.0
        if x.iFB == 1:

            # MLR
            rAF = min(1.0, (XA * (g.Tsec - x.Tig) ** 2) / dHF)  # growth rate in mass loss
            vp = 2.2e-6 / DDc ** 0.6  # charring rate
            dMF1 = 4.0 * x.FW0 * vp / DDc * sqrt(x.FW / x.FW0)  # MLR (fuel controlled)
            dMF2 = 4.4e-4 * (SSc * x.FW0) / (x.HO * DDc)  # MLR (air supply controlled)
            x.rMF = rAF * min(dMF1, dMF2)  # MLR

            # HRR + fuel load
            x.QX = x.rMF * dHF  # HRR
            x.FW = max(0.0, x.FW - x.rMF * dTsec)  # total fuel load
            if x.FW < x.FW0 * 2.0e-1:  # if burn is in decay phase 
                x.iFB = 2


# ------------------------------------------------------------------------------
#        external heat flux & ignition time
# ------------------------------------------------------------------------------
def HTRF():

    # --------------------------------------------
    #        external heat flux
    # --------------------------------------------
    for x in g.OO:
        if x.iFC == 1:
            for y in x.WW:
                if y.iWS == 1:  # if not base surface
                    y.eQXX = y.eQX + EE * SB * (x.TTa ** 4 - g.TT0 ** 4) + HH * (x.TTa - g.TT0)

    # --------------------------------------------
    #        ignition time
    # --------------------------------------------
    #for x in g.OO:
    for i, x in enumerate(g.OO):
        if x.iFC == 1:
            
            #for y in x.WW:
            for j, y in enumerate(x.WW):
                if y.iWS == 1 and x.iFB == 0:  # if not base & still not ignited
                    if y.eQXX > 1.0:
                        y.QWi += y.eQXX ** 2 * dTsec  # cumulative heat received per unit area
                    if y.eQXX > eQcr and y.QWi > aQcr:  # if both heat flux and cumulative heat exceeds critical
                        x.iFB = 1  #  status of combustion
                        x.Tig = g.Tsec - dTsec  # ignition time
