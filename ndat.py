# -*- coding: utf-8 -*-

import numpy as np

from cgprm import *
from gprm import *
import g


# ------------------------------------------------------------------------------
#        data update and output
# ------------------------------------------------------------------------------
def NDAT():

    # --------------------------------------------
    #        status of computation
    # --------------------------------------------
    for x in g.OO:
        if x.iFC == 0 and x.FW > 1.0e1:  # if still not activated and substantial fuel load remains
            if x.TTa - g.TT0 > 50.0 or max([y.eQX for y in x.WW]) > 1.0:  # if either ambient temp. or incident heat flux exceeds critical value 
                x.iFC = 1

    # --------------------------------------------
    #        status of combustion
    # --------------------------------------------
    g.nFB[:] = 0
    for x in g.OO:
        g.nFB[x.iFB] += 1

    g.nFB_r[int(g.Tmin), :] = np.array(g.nFB, dtype=int)


# ------------------------------------------------------------------------------
#        output
# ------------------------------------------------------------------------------
def OUTP():

    # on screen
    if g.nSTP % nOUT1 == 0:
        print(f" TIME={g.Tmin:6.1f}    UU0={g.UU0:5.1f}m/s,    burning={g.nFB[1]:5}/{g.nOBJ:5}    burnt out={g.nFB[2]:5}/{g.nOBJ:5}")

    # kml files
    if g.nSTP % nOUT2 == 0:
        KML()


# ------------------------------------------------------------------------------
#        output : KML
# ------------------------------------------------------------------------------
def KML():

    # file name
    nTmin = int(g.Tmin + 0.5)
    fname = f"{nTmin:04}.kml"

    # --------------------------------------------
    #        output
    # --------------------------------------------
    with open(f"./data/{fname}", "w") as f:

        # --------------------------------------------
        #        header
        # --------------------------------------------
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(' <kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write(" <Document>\n")
        f.write(f" <name>{fname[:4]}</name>\n")

        # --------------------------------------------
        #        viewp
        # --------------------------------------------
        f.write(" <LookAt>\n")
        f.write(f"   <longitude>{v_kml_1}</longitude>\n")  # view focus (longitude)
        f.write(f"    <latitude>{v_kml_2}</latitude>\n")  # view focus (latitude)
        f.write(f"       <range>{v_kml_3}</range>\n")  # distance to view focus
        f.write(f"        <tilt>{v_kml_4}</tilt>\n")  # angle between sight line and vertical axis
        f.write(f"     <heading>{v_kml_5}</heading>\n")  # direction of sight line
        f.write(" </LookAt>\n")

        # --------------------------------------------
        #        specification of polygons
        # --------------------------------------------
        # not ignited
        f.write(' <Style id="0_0">\n')
        f.write(" <PolyStyle>\n")
        f.write(" <color>c0c5c5c5</color>\n")
        f.write(" </PolyStyle>\n")
        f.write(" <LineStyle>\n")
        f.write(" <color>ff919191</color>\n")
        f.write(" <width>1</width>\n")
        f.write(" </LineStyle>\n")
        f.write(" </Style>\n")

        # burning
        f.write(' <Style id="0_1">\n')
        f.write(" <PolyStyle>\n")
        f.write(" <color>c00000ff</color>\n")
        f.write(" </PolyStyle>\n")
        f.write(" <LineStyle>\n")
        f.write(" <color>ff0000ff</color>\n")
        f.write(" <width>1</width>\n")
        f.write(" </LineStyle>\n")
        f.write(" </Style>\n")

        # burnt out
        f.write(' <Style id="0_2">\n')
        f.write(" <PolyStyle>\n")
        f.write(" <color>c0000000</color>\n")
        f.write(" </PolyStyle>\n")
        f.write(" <LineStyle>\n")
        f.write(" <color>ff000000</color>\n")
        f.write(" <width>1</width>\n")
        f.write(" </LineStyle>\n")
        f.write(" </Style>\n")

        # --------------------------------------------
        #        polygons
        # --------------------------------------------
        for i, x in enumerate(g.OO):
            for y in x.WW:
                if y.iWS == 0:  # if surface is base

                    f.write("<Placemark>\n")
                    f.write(f"<name>{i:12} </name>\n")

                    # color
                    if x.iFB == 0:  # not ignited
                        f.write("<styleUrl>#0_0</styleUrl>\n")
                    elif x.iFB == 2:  # burnt
                        f.write("<styleUrl>#0_2</styleUrl>\n")
                    else:  # burning
                        f.write("<styleUrl>#0_1</styleUrl>\n")

                    # shape
                    f.write(" <Polygon>\n")
                    f.write(" <extrude>1</extrude>\n")
                    f.write(" <altitudeMode>relativeToGround</altitudeMode>\n")
                    f.write(" <outerBoundaryIs>\n")
                    f.write(" <LinearRing>\n")
                    f.write(" <coordinates>\n")

                    for k in range(4):
                        f.write(f"{x.VV[k].LL},{x.VV[k].BB},{x.HO}\n")

                    f.write(f"{x.VV[0].LL},{x.VV[0].BB},{x.HO}\n")

                    f.write(" </coordinates>\n")
                    f.write(" </LinearRing>\n")
                    f.write(" </outerBoundaryIs>\n")
                    f.write(" </Polygon>\n")
                    f.write(" </Placemark>\n")

        # --------------------------------------------
        #        footer
        # --------------------------------------------
        f.write(" </Document>\n")
        f.write(" </kml>\n")


# ------------------------------------------------------------------------------
#        summary
# ------------------------------------------------------------------------------
def RSLT():

    # --------------------------------------------
    #        summary
    # --------------------------------------------
    # outline
    with open("./data/mc1.csv", "a+", newline="\n") as f:
        f.write(f"{int(g.Tmin):5}, {g.UU0:12.5f}, {g.VW[0]:12.5f}, {g.VW[1]:12.5f},{g.IGN:6}, {g.nFB_r[int(g.Tmin),1] + g.nFB_r[int(g.Tmin),2]}\n")

    # burn status of each object
    with open("./data/mc2.csv", "a+", newline="\n") as f:
        f.write(f"{g.nFB_r[int(g.Tmin),1] + g.nFB_r[int(g.Tmin),2]:5},")
        for x in g.OO:
            f.write(f"{x.iFB:5},")
        f.write("\n")

    # time transition of number of burning objects
    with open("./data/mc3.csv", "a+") as f:
        for i in range(int(g.Tmin) + 1):
            f.write(f"{g.nFB_r[i,1]:5},")
        f.write("\n")

    # time transition of number of burnt out objects
    with open("./data/mc4.csv", "a+") as f:
        for i in range(int(g.Tmin) + 1):
            f.write(f"{g.nFB_r[i,2]:5},")
        f.write("\n")
