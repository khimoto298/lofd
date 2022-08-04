# -*- coding: utf-8 -*-

from math import sqrt, hypot, exp
from math import log10 as log
import numpy as np

from cgprm import *
from gprm import *
import g
from rndm import *


# ------------------------------------------------------------------------------
#        fire spread
# ------------------------------------------------------------------------------
def SPRD():

    XRAD()  # flames

    # windy condition
    if g.UU0 > 0.0:
        FPLM()  # wind-blown fire plumes
        SPOT()  # firebrands


# ------------------------------------------------------------------------------
#        flames
# ------------------------------------------------------------------------------
def XRAD():

    # initialization
    for x in g.OO:
        for y in x.WW:
            y.eQX = 0.0

    for x in g.OO:
        if x.iFB == 1:

            # --------------------------------------------
            #        flame geometry
            # --------------------------------------------
            DDf = sqrt(x.Afp)  # representative length of fire source

            # no-wind condition (Zukoski model)
            if g.UU0 < 1.0e-1:

                # flame length (flame height)
                QQ = x.QX / (353.0 * sqrt(GG) * (DDf ** 2.5))  # Qw*
                rLF = (3.3 * min(QQ ** 0.67, QQ ** 0.4)) * DDf
                rHF = rLF

            # windy condition (Thomas model)
            else:

                # flame length
                MM1 = (x.rMF / x.Afp) / (g.RR0 * sqrt(GG * DDf))  # Mw*
                UU1 = g.UU0 / sqrt(GG * DDf)  # Uw*
                rLF = (70.0 * (MM1 ** 0.86) * (UU1 ** (-0.22))) * DDf  # flame length

                # flame height
                if x.rMF < 1.0e-6:
                    UU2 = 1.0
                else:
                    UU2 = g.UU0 / (x.rMF * GG * DDf / g.RR0) ** (1.0 / 3.0)  # Uf*
                if UU2 < 1.0:
                    cosT = 1
                else:
                    cosT = 0.7 * (UU2 ** (-0.49))
                rHF = rLF * cosT

            # --------------------------------------------
            #        radiative heat flux
            # --------------------------------------------
            for y in x.ADJ:
                ii = y.iAO  # heat receiving object
                jj = y.iAW  # heat receiving surface
                yy = g.OO[ii].WW[jj]

                # base of radiating surface
                VS = [x.GO[k] - yy.GW[k] for k in range(3)]  # relative vector (x, y, z)
                rT = max(1.0e-1, hypot(VS[0], VS[1]))  # separation between foots of fire source and heat receiving surface
                rTp = rT - 0.5 * DDf  # separation between foots of radiating surface and heat receiving surface
                GX = [
                    (rTp / rT) * x.GO[0] + ((rT - rTp) / rT) * yy.GW[0],  # X
                    (rTp / rT) * x.GO[1] + ((rT - rTp) / rT) * yy.GW[1],  # Y
                    0.0,  # Z
                ]

                # point heat source (windy condition)
                if g.UU0 >= 1.0e-1:

                    # tilt angle
                    if rLF < 1.0e-2:
                        sinT = 1.0
                    else:
                        sinT = sqrt(rLF ** 2 - rHF ** 2) / rLF

                    # coordinates
                    GX[0] = GX[0] + 0.5 * rLF * sinT * g.VW[0]  # x
                    GX[1] = GX[1] + 0.5 * rLF * sinT * g.VW[1]  # y
                    GX[2] = GX[2] + 0.5 * rHF  # z

                # distance from point source to heat receiving surface
                for k in range(3):
                    VS[k] = GX[k] - yy.GW[k]  # relative vector (x, y, z)
                SS = max(1.0e-1, abs(sum([a * b for (a, b) in zip(yy.VE, VS)])))

                # incident heat flux
                deQX = EE * (0.3 * x.QX) / (4.0 * PI * SS * SS)
                yy.eQX = yy.eQX + deQX  # sum of incident heat flux


# ------------------------------------------------------------------------------
#        fire plumes
# ------------------------------------------------------------------------------
def FPLM():

    # initialization
    dTTa = np.zeros(nO, dtype=int)

    # --------------------------------------------
    #        individual effect
    # --------------------------------------------
    for x in g.OO:
        DDf = sqrt(x.Afp)  # representative length of fire source

        if x.iFB == 1 and x.QX > 1.0e1:
            for y in x.ADJ:

                # heat receiving object
                ii = y.iAO
                VQ = [g.OO[ii].GO[k] - x.GO[k] for k in range(3)]  # relatvie velocity (target relative to fire source)
                sOF = VQ[0] * g.VW[0] + VQ[1] * g.VW[1]  # length of OF

                if sOF > 0.0:
                    QQ = x.QX / (353.0 * sqrt(GG) * (DDf ** 2.5))  # Qw*
                    UU = g.UU0 / sqrt(GG * DDf)  # Uw*

                    # positional relationship
                    sSF = DDf * 0.59 * (QQ ** (1.0 / 3.0)) * (UU ** (-1)) * (sOF / DDf) ** (2.0 / 3.0)  # length of SF
                    sQF = sqrt(VQ[0] ** 2 + VQ[1] ** 2 + VQ[2] ** 2 - sOF ** 2)  # length of QF
                    sOS = sqrt(sOF ** 2 + sSF ** 2)  # length of OS (approximate length along trajectory)
                    sSQ = sqrt(sSF ** 2 + sQF ** 2)  # length of SQ

                    # temperature rise
                    QQ = x.QX / (353.0 * sqrt(GG) * (sOS ** 2.5))  # Qs*
                    dTTs = g.TT0 * 2.08 * QQ ** (2.0 / 3.0)  # dT along trajectory
                    dTTa[ii] = max(dTTa[ii], dTTs * exp(-((sSQ / (0.315 * sOS)) ** 2)))  # dT around target

    # --------------------------------------------
    #        overall effect
    # --------------------------------------------
    for x, d in zip(g.OO, dTTa):
        x.TTa = g.TT0 + d ** 1.5

    for x in g.OO:
        x.TTa = x.TTa ** (2.0 / 3.0)


# ------------------------------------------------------------------------------
#        firebrands
# ------------------------------------------------------------------------------
def SPOT():

    # --------------------------------------------
    #        firebrands
    # --------------------------------------------
    if g.nSTP % nOUT1 == 0:
        for x in g.OO:
            if x.iFB == 1:
                Nfb = (3.11e5 * ((x.rMF / x.Afp) ** 3.57)) * x.Afp * (float(nSKP) * dTsec)  # number of generated firebrands

                for _ in range(int(rFB * g.UU0 * Nfb)):

                    # W*
                    W0 = min(
                        6.83 * x.QX ** 0.2 * sqrt(x.HO / x.QX ** 0.4),
                        1.85 * x.QX ** 0.2,
                        1.08 * x.QX** 0.2 * (x.HO / x.QX ** 0.4) ** (-1.0 / 3.0),
                    )
                    UU = (g.RR0 / RRp) * (W0 ** 2 / (GG * DDc * 1.0e2))  # W*

                    # firebrand size
                    RNNg = RNDMg()
                    mu_A = 0.445 * (UU ** 1.07)  # μ_A
                    sgm_A = 1.07e-2  # σ_A
                    lmd_A = log(mu_A ** 2 / sqrt(mu_A ** 2 + sgm_A ** 2))  # λ_A
                    xi_A = sqrt(log((mu_A ** 2 + sgm_A ** 2) / (mu_A ** 2)))  # ξ_A
                    Afb = exp(lmd_A + xi_A * RNNg) * (DDc * 1.0e2) ** 2  # projected area
                    Dfb = sqrt(Afb)  # representative length

                    # B*
                    BB = (g.UU0 * W0 / (GG * sqrt(Dfb * DDc * 1.0e2))) ** 2 * (g.RR0 / RRp) * (1.0 + sqrt(1.0 + 2.0 * GG * x.HO / (W0 ** 2))) ** 2

                    # deposition (x)
                    RNNg = RNDMg()
                    mu_X = 41.0 * (BB ** 1.06)  # μ_X
                    sgm_X = 4.52  # σ_X
                    lmd_X = log(mu_X ** 2 / sqrt(mu_X ** 2 + sgm_X ** 2))  # λ_X
                    xi_X = sqrt(log((mu_X ** 2 + sgm_X ** 2) / (mu_X ** 2)))  # ξ_X
                    X_p = exp(lmd_X + xi_X * RNNg) * DDc * 1.0e2  # transport distance (x)

                    if X_p > dM * max(nXX, nYY):
                        break  # if transported beyond computational domain

                    # deposition (y)
                    RNNg = RNDMg()
                    sgm_Y = 1.0e-1 * mu_X  # σ_X
                    Y_p = sgm_Y * RNNg * DDc * 1.0e2  # transport distance (y)

                    # conversion to reference coordiate system
                    X_s = x.GO[0] + (X_p * g.VW[0] - Y_p * g.VW[1])
                    Y_s = x.GO[1] + (X_p * g.VW[1] + Y_p * g.VW[0])

                    # corresponding mesh
                    iB1 = 9999
                    iB2 = 9999
                    for m1 in range(1, nXX + 1):
                        if X_s < g.XX[m1]:
                            iB1 = m1
                            break

                    for m2 in range(1, nYY + 1):
                        if Y_s < g.YY[m2]:
                            iB2 = m2
                            break

                    if iB1 != 9999 and iB2 != 9999:
                        m = (iB1 - 1) * nYY + iB2
                    else:
                        m = 9999

                    # ignition
                    if m != 9999:

                        RNNu = random.random()
                        rA = 0.0
                        for kk in range(g.nO_M[m-1], g.nO_M[m]-1):
                            ii = g.lO_M[kk]  # object ID
                            xx = g.OO[ii]
                            rA = rA + xx.Afp / (dM * dM)  # proportion of object footprint to mesh size

                            if RNNu < rA:
                                if xx.Tig == 0.0:

                                    RNNu = random.random()
                                    pIGN = 1.0 / (1.0 + exp(-(5.2591 - 1.186e-4 * (Dfb / 1.0e2) ** (-2) - 1.5528e-1 * FMC)))  # probability of ignition

                                    if RNNu < pIGN:
                                        xx.iFC = 1  # status of computation (0: inactive, 1: active, 2: ended)
                                        xx.iFB = 1  # status of combustion (0: inactive, 1: active, 2: ended)
                                        xx.Tig = g.Tsec - dTsec  # ignition time
                                break
