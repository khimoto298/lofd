# -*- coding: utf-8 -*-

import math

# computational time
Tend = 720.0  # computational time (min) 
dTsec = 1.0  # time increment (s) 
nOUT1 = 600  # output interval (1) 
nOUT2 = 600  # output interval (2) 
nSKP = 60  # skip interval 

# outline
nO = 550  # number of objects 
nW = 6  # number of surfaces per object 
nV = 8  # number of vertices per object 
nA = 30  # number of adjacent surfaces 
iSEED = 1234  # pseudo-random seed (non-repeatable when negative) 

# combustion and heat transfer
CP = 1.0  # specific heat of gas (kJ/kg/K)
GG = 9.8  # acceleration due to gravity (m/s^2)
PI = 4.0 * math.atan(1.0)  # circumference ratio
SB = 5.67e-11  # Stefan-Boltzmann's constant (kW/m^2/K^4)
EE = 1.0  # emissivity of surface
HH = 2.0e-2  # heat transfer coefficient (kW/m^2/K)
DDc = 1.0e-1  # cross-sectional width of a wood crib component (m) 
SSc = 1.35  # separation between wood crib components (m) 
FMC = 2.0e1  # moisture content of wood cribs (%) 
XA = 1.0e-2  # fire growth rate (kW/s^2)  
dHF = 16.4e3  # heat of combustion (MJ/kg)  
ROcr = 10.0 ** 2  # search rage for adjacent objects (m^2)
eQcr = 16.0  # critical heat flux of ignition (kW/m^2)
aQcr = 26000.0  # critical cumulative heat of ignition (kW^2*s/m^4)

# firebrands
RRp = 70.0  # density of firebrands (kg/m^3)
rFB = 1.e-4  # proportion of hazardous firebrands

# KML - view
v_kml_1 = 140.0683  # view focus (longitude) 
v_kml_2 = 36.1249  # view focus (latitude) 
v_kml_3 = 150.0  # distance to view focus 
v_kml_4 = 35.0  # angle between sight line and vertical axis 
v_kml_5 = 0.0  # direction of sight line (0 when north) 

# KML - coordinate conversion for output
CC_o1 = 416130.0  # reference point (x) at NILIM (in UTM zone 54N) (m) 
CC_o2 = 3998130.0  # reference point (y) at NILIM (in UTM zone 54N) (m) 
LL_o = 141.0  # origin of UTM zone 54N (longitude) 
BB_o = 0.0  # origin of UTM zone 54N (latitude) 
aa_GRS = 6378137.0  # semimajor axis of GRS80 ellipsoid (m)
ee2_GRS = 0.00669438002290079  # square of eccentricity of GRS80 ellipsoid
eed2_GRS = 0.0067394967754789573  # square of second eccentricity of GRS80 ellipsoid
rSCL = 0.9996  # scaling ratio
rKK1 = 1.005052501813147  # conversion parameter
rKK2 = 0.005063108622327  # conversion parameter
rKK3 = 0.000010627590328  # conversion parameter
rKK4 = 0.000000020820407  # conversion parameter

# computational domain
dM = 10  # mesh size (m) 
nXX = 7  # number of mesh division (x) 
nYY = 35  # number of mesh division (y) 
