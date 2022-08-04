# -*- coding: utf-8 -*-

from sys import exit
from math import sqrt, hypot, sin, cos, tan

from cgprm import *
from gprm import *
from rndm import *

import g


# ------------------------------------------------------------------------------
#        data input and setup
# ------------------------------------------------------------------------------
def INIT():

    INIT1()  # read from files
    INIT2()  # objects
    INIT3()  # adjacency
    INIT4()  # UTM coordinates -> latitude and longitude


# ------------------------------------------------------------------------------
#        read from files
# ------------------------------------------------------------------------------
def INIT1():

    # --------------------------------------------
    #        outline
    # --------------------------------------------
    with open("./data/o.csv") as f:
        g.nOBJ, g.IGN, *_ = f.readline().strip().split(",")
        g.nOBJ, g.IGN = int(g.nOBJ), int(g.IGN)  # total number of objects, fire origin
        g.TT0, *_ = f.readline().strip().split(",")
        g.TT0 = int(g.TT0)  # ambient temperature
        g.UU0, g.VW[0], g.VW[1], *_ = f.readline().strip().split(",")
        g.UU0, g.VW[0], g.VW[1] = int(g.UU0), int(g.VW[0]), int(g.VW[1])  # wind velocity, wind vector (2)
        for line in f.readlines():
            i, val, *_ = line.strip().split(",")
            i, val = int(i), float(val)  # object id, fuel load
            g.OO[i - 1].FW = val

    g.RR0 = 353.0 / g.TT0
    if g.UU0 > 0.0:
        h = hypot(g.VW[0], g.VW[1])
        g.VW = g.VW[0] / h, g.VW[1] / h

    # initialization
    g.Tsec = 0.0  # time (s)
    g.Tmin = 0.0  # time (min)
    g.nSTP = 0  # number of time step
    for x in g.OO:
        x.FW0 = x.FW  # total fuel load (initial)
        x.iFC = 0  # flag for status of computation
        x.iFB = 0  # flag for status of combustion
        x.Tig = 0.0  # ignition time
        x.QBa = 0.0  # cumulative heat release
        x.TTa = g.TT0  # ambient temperature
        g.nFB[:] = [0]  # number of objects at each combustion status
        g.nFB_r[:, :] = 0  # record of nFB
    for x in g.OO:
        for y in x.WW:
            y.eQX = 0.0  # heat flux from external fire sources
            y.eQXX = 0.0  # external heat fulx
            y.QWi = 0.0  # cumulative heat received per unit area
        for y in x.ADJ:
            y.iAO = -1  # heat receiving object
            y.iAW = -1  # heat receiving surface

    # fire origin
    RNDMi(iSEED)  # pseudo-random number
    if iSEED < 0:
        RNNu = random.random()
        IGN = min(g.nOBJ, (max(1, int(g.nOBJ * RNNu))))

    g.OO[g.IGN - 1].iFC = 1
    g.OO[g.IGN - 1].iFB = 1
    g.OO[g.IGN - 1].Tig = -dTsec

    # --------------------------------------------
    #        vertices
    # --------------------------------------------
    with open("./data/v.csv") as f:
        for line in f.readlines():
            lss = line.strip().split(",")
            ii, jj = int(lss[0]), int(lss[2])  # object id, vertex id
            g.OO[ii - 1].nVRTX = int(lss[1])  # number of vertices
            g.OO[ii - 1].VV[jj - 1].CC[:] = [int(x) for x in lss[3:6]]  # coordinates(x, y, z)
    for x in g.OO:
        x.VV = x.VV[:x.nVRTX]

    # --------------------------------------------
    #        surfaces
    # --------------------------------------------
    with open("./data/p.csv") as f:
        for line in f.readlines():
            lss = line.strip().split(",")
            ii, jj = int(lss[0]), int(lss[2])  # object id, surface id
            g.OO[ii - 1].nPOLY = int(lss[1])  # number of surfaces
            g.OO[ii - 1].WW[jj - 1].iWS = int(lss[3])  # type of surface
            g.OO[ii - 1].WW[jj - 1].iWN[:] = [int(x) for x in lss[4:8]]  # component vertices
    for x in g.OO:
        x.WW = x.WW[:x.nPOLY]


# ------------------------------------------------------------------------------
#        objects
# ------------------------------------------------------------------------------
def INIT2():

    # --------------------------------------------
    #        gravitational point (surface)
    # --------------------------------------------
    for x in g.OO:
        for y in x.WW:
            for i in range(3):
                y.GW[i] = 0.0
                for z in y.iWN:
                    y.GW[i] += x.VV[z - 1].CC[i]
                y.GW[i] *= 0.25

    # --------------------------------------------
    #        gravitational point (object)
    # --------------------------------------------
    for x in g.OO:
        tmp = [z.CC[2] for z in x.VV[: x.nVRTX]]
        x.HO = max(tmp) - min(tmp)

    for x in g.OO:
        x.GO = 3 * [0.0]

        for y in x.WW:
            if y.iWS == 0:
                x.GO[0] = y.GW[0]
                x.GO[1] = y.GW[1]
                x.GO[2] = y.GW[2] + 0.5 * x.HO

    # --------------------------------------------
    #        unit normal vector (surface)
    # --------------------------------------------
    for x in g.OO:
        for y in x.WW:
            y.VE = 3 * [0.0]

            # edge vectors of surface: VA & VB
            kk1, kk2, kk4 = y.iWN[0] - 1, y.iWN[1] - 1, y.iWN[3] - 1
            for i in range(3):
                y.VA[i] = -x.VV[kk1].CC[i] + x.VV[kk2].CC[i]
                y.VB[i] = -x.VV[kk1].CC[i] + x.VV[kk4].CC[i]

            # unit normal vector: VE
            y.VE[0] = (y.VA[1] * y.VB[2]) - (y.VA[2] * y.VB[1])  # x
            y.VE[1] = (y.VA[2] * y.VB[0]) - (y.VA[0] * y.VB[2])  # y
            y.VE[2] = (y.VA[0] * y.VB[1]) - (y.VA[1] * y.VB[0])  # z
            y.SW = sqrt(y.VE[0] ** 2 + y.VE[1] ** 2 + y.VE[2] ** 2)  # area of rectangle
            for i in range(3):
                y.VE[i] = y.VE[i] / y.SW

    # --------------------------------------------
    #        area of footprint
    # --------------------------------------------
    for x in g.OO:
        for y in x.WW:
            if y.iWS == 0:
                x.Afp = y.SW

    # --------------------------------------------
    #        mesh
    # --------------------------------------------
    # range of computational domain
    XXmax = XXmin = g.OO[0].GO[0]
    YYmax = YYmin = g.OO[0].GO[1]

    for x in g.OO[1:]:
        XXmin = min(XXmin, x.GO[0])
        XXmax = max(XXmax, x.GO[0])
        YYmin = min(YYmin, x.GO[1])
        YYmax = max(YYmax, x.GO[1])

    if XXmax - XXmin > dM * float(nXX):
        print("error : insufficient size of 'nXX'")
        exit(1)

    if YYmax - YYmin > dM * float(nYY):
        print("error : insufficient size of 'nYY'")
        exit(1)

    # subdivision of computational domain into meshes
    for i in range(nXX + 1):
        g.XX[i] = dM * float(i)

    for i in range(nYY + 1):
        g.YY[i] = dM * float(i)

    # search for relevant mesh
    k = -1
    g.nO_M[:] = k
    for i in range(1, nXX + 1):
        for j in range(1, nYY + 1):
            m = (i - 1) * nYY + j  # serial number (mesh)
            g.nO_M[m - 1] = k + 1  # start number in list
            for ii, x in enumerate(g.OO):
                if g.XX[i - 1] <= x.GO[0] < g.XX[i] and g.YY[j - 1] <= x.GO[1] < g.YY[j]:
                    g.lO_M[k] = ii  # add to list
                    k = k + 1  # serial number (object)
 
    g.nO_M[m] = k + 1


# ------------------------------------------------------------------------------
#        adjacency
# ------------------------------------------------------------------------------
def INIT3():

    # ------------------------------------------
    #        target surface
    # ------------------------------------------
    for x in g.OO:
        x.nADJ = 0

    for i, x in enumerate(g.OO):
        for j, y in enumerate(x.WW):
            if y.iWS == 1:  # all surfaces except for base

                # target object
                for ii, xx in enumerate(g.OO):
                    if i != ii:

                        # distance and incidence angle
                        VH = [xx.GO[k] - x.GO[k] for k in range(3)]
                        RO = VH[0] ** 2 + VH[1] ** 2
                        rIP = sum([a * b for (a, b) in zip(y.VE, VH)])  # inner product (same sign as cosθ)

                        # visibility
                        if RO < ROcr and rIP > 0.0:
                            for jj, yy in enumerate(xx.WW):
                                if yy.iWS == 1:  # all surfaces except for base
                                    VIEW(i, j, ii, jj)
        x.ADJ = x.ADJ[:x.nADJ]


# ------------------------------------------------------------------------------
#        visibility
# ------------------------------------------------------------------------------
def VIEW(i, j, ii, jj):

    # ------------------------------------------
    #        visibility
    # ------------------------------------------
    # gravitational point of element of radiating surface - A
    kkA = g.OO[i].WW[j].iWN[0] - 1
    dGA = [g.OO[i].VV[kkA].CC[k] + 0.5 * (g.OO[i].WW[j].VA[k] + g.OO[i].WW[j].VB[k]) for k in range(3)]

    # gravitational point of element of heat receiving surface - B
    kkB = g.OO[ii].WW[jj].iWN[0] - 1
    dGB = [g.OO[ii].VV[kkB].CC[k] + 0.5 * (g.OO[ii].WW[jj].VA[k] + g.OO[ii].WW[jj].VB[k]) for k in range(3)]

    # unit direction vector
    VS = [dGB[k] - dGA[k] for k in range(3)]
    SS = hypot(VS[0], hypot(VS[1], VS[2]))  # distance between elements
    for k in range(3):
        VS[k] = VS[k] / SS  # unit direction vector

    # ------------------------------------------
    #       sight line shielding
    # ------------------------------------------
    for iii, x in enumerate(g.OO):
        VH = [x.GO[k] - g.OO[i].GO[k] for k in range(3)]
        RO = VH[0] ** 2 + VH[1] ** 2
        rIP = sum([a * b for (a, b) in zip(g.OO[i].WW[j].VE, VH)])  # inner product (unit normal of A and unit direction vector)

        if RO < ROcr and rIP > 0.0:
            for jjj, y in enumerate(x.WW):
                if (y.iWS == 1) and (iii != i or jjj != j) and (iii != ii or jjj != jj):

                    # relative vector of a vertex of shielding surface
                    kkT = y.iWN[0] - 1  # f2p
                    VT = [x.VV[kkT].CC[k] - dGA[k] for k in range(3)]

                    # distance to shielding surface
                    rIP1 = sum([a * b for (a, b) in zip(y.VE, VT)])
                    rIP2 = sum([a * b for (a, b) in zip(y.VE, VS)])
                    if rIP2 == 0.0:
                        DD = SS + 1.0  # exclude as VE is perpendicular to VS
                    else:
                        DD = rIP1 / rIP2

                    # sight line shielding
                    if SS > DD > 0.0:
                        FF = [DD * VS[k] - VT[k] for k in range(3)]
                        rU = y.VA[0] * y.VB[1] - y.VB[0] * y.VA[1]

                        if abs(rU) >= 1.0e-3:
                            rS = (FF[0] * y.VB[1] - y.VB[0] * FF[1]) / rU
                            rT = (y.VA[0] * FF[1] - FF[0] * y.VA[1]) / rU
                        else:
                            rU = y.VA[0] * y.VB[2] - y.VB[0] * y.VA[2]
                            if abs(rU) >= 1.0e-3:
                                rS = (FF[0] * y.VB[2] - y.VB[0] * FF[2]) / rU
                                rT = (y.VA[0] * FF[2] - FF[0] * y.VA[2]) / rU
                            else:
                                rU = y.VA[1] * y.VB[2] - y.VB[1] * y.VA[2]
                                rS = (FF[1] * y.VB[2] - y.VB[1] * FF[2]) / rU
                                rT = (y.VA[1] * FF[2] - FF[1] * y.VA[2]) / rU

                        if rS >= 0.0 and rS <= 1.0 and rT >= 0.0 and rT <= 1.0:
                            return  # if shielded

    # ------------------------------------------
    #       listing
    # ------------------------------------------
    for n in range(g.OO[i].nADJ + 1):
        if g.OO[i].ADJ[n].iAO == ii and g.OO[i].ADJ[n].iAW == jj:
            break
        elif g.OO[i].ADJ[n].iAO == -1 and g.OO[i].ADJ[n].iAW == -1:
            g.OO[i].nADJ += 1
            g.OO[i].ADJ[n].iAO = ii
            g.OO[i].ADJ[n].iAW = jj
            break
        elif n > nA:
            print("error : insufficient size of 'nA'")
            exit(1)


# ------------------------------------------------------------------------------
#        UTM coordinates -> longitude and latitude
# ------------------------------------------------------------------------------
def INIT4():

    # --------------------------------------------
    #        preprocessing
    # --------------------------------------------
    rDG = 180.0 / PI  # conversion ratio
    LL_0 = LL_o / rDG  # origin of UTM zone 54N (longitude) (rad)
    BB_0 = BB_o / rDG  # origin of UTM zone 54N (latitude) (rad)
    DDN0 = (aa_GRS * (1.0 - ee2_GRS)) * (rKK1 * BB_0 - rKK2 / 2.0 * sin(2.0 * BB_0) + rKK3 / 4.0 * sin(4.0 * BB_0) - rKK4 / 6.0 * sin(6.0 * BB_0))

    # --------------------------------------------
    #        conversion
    # --------------------------------------------
    for x in g.OO:
        for y in x.VV:

            # latitude of perpendicular line from target point to meridian
            XXN = (y.CC[1] + CC_o2) / rSCL  # reference point (x) at NILIM
            YYE = (y.CC[0] + CC_o1 - 5.0e5) / rSCL  # reference point (y) at NILIM
            BB_1 = BB_0  # initialization of latitude
            DDN = XXN + DDN0  # solitary length of meridian + distance to target point
            PRM = 4 * [0.0]
            for _ in range(10):
                SSN = (aa_GRS * (1.0 - ee2_GRS)) * (rKK1 * BB_1 - rKK2 / 2.0 * sin(2.0 * BB_1) + rKK3 / 4.0 * sin(4.0 * BB_1) - rKK4 / 6.0 * sin(6.0 * BB_1))
                PRM[0] = 2.0 * (SSN - DDN) * sqrt((1.0 - ee2_GRS * sin(BB_1) ** 2) ** 3)
                PRM[1] = 3.0 * ee2_GRS * (SSN - DDN) * sin(BB_1) * cos(BB_1) * sqrt(1.0 - ee2_GRS * sin(BB_1) ** 2)
                PRM[2] = 2.0 * aa_GRS * (1.0 - (ee2_GRS) ** 2)
                BB_1 = BB_1 + PRM[0] / (PRM[1] - PRM[2])

            # coefficients
            R_N = aa_GRS / sqrt(1.0 - ee2_GRS * sin(BB_1) ** 2)  # curvature radius of parallel of latitude
            tbb = tan(BB_1)  # tan(BB_1)
            eta = eed2_GRS * (cos(BB_1) ** 2)  # η^2

            # latitude
            PRM[0] = (tbb * (1.0 + eta)) * (YYE ** 2) / (2.0 * (R_N ** 2))
            PRM[1] = (tbb * (5.0 + 3.0 * (tbb ** 2) + 6.0 * eta - 6.0 * (tbb ** 2) * eta - 3.0 * (eta ** 2) - 9.0 * (tbb ** 2) * (eta ** 2))) * (YYE ** 4) / (24.0 * (R_N ** 4))
            PRM[2] = (tbb * (61.0 + 90.0 * (tbb ** 2) + 45.0 * (tbb ** 4) + 107.0 * eta - 162.0 * (tbb ** 2) * eta - 45.0 * (tbb ** 4) * eta)) * (YYE ** 6) / (720.0 * (R_N ** 6))
            PRM[3] = (tbb * (1385.0 + 3633.0 * (tbb ** 2) + 4095.0 * (tbb ** 4) + 1575.0 * (tbb ** 6))) * (YYE ** 8) / (40320.0 * (R_N ** 8))
            y.BB = (BB_1 - PRM[0] + PRM[1] - PRM[2] + PRM[3]) * rDG

            # longitude
            PRM[0] = (YYE) / (R_N * cos(BB_1))
            PRM[1] = (1.0 + 2.0 * (tbb ** 2) + eta) * (YYE ** 3) / (6.0 * (R_N ** 3) * cos(BB_1))
            PRM[2] = (5.0 + 28.0 * (tbb ** 2) + 24.0 * (tbb ** 4) + 6.0 * eta - 8.0 * (tbb ** 2) * eta) * (YYE ** 5) / (120.0 * (R_N ** 5) * cos(BB_1))
            PRM[3] = (61.0 + 662.0 * (tbb ** 2) + 1320.0 * (tbb ** 4) + 720.0 * (tbb ** 6)) * (YYE ** 7) / (5040.0 * (R_N ** 7) * cos(BB_1))
            y.LL = (LL_0 + PRM[0] - PRM[1] + PRM[2] - PRM[3]) * rDG
