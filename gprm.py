# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from cgprm import nV, nW, nA

# --------------------------------------------
#        Polygons
# --------------------------------------------
@dataclass
class Polygon:

    # spatial attribute
    iWS: int = 0  # type of surface (0: base, 1: others)
    SW: float = 0.0  # surface area
    GW: list[float] = field(default_factory=(lambda: 3 * [0.0]))  # gravitational point of a surface (x, y, z)
    VE: list[float] = field(default_factory=lambda: 3 * [0.0])  # normal vector of a surface (x, y, z)
    VA: list[float] = field(default_factory=lambda: 3 * [0.0])  # edge vector of a surface - A
    VB: list[float] = field(default_factory=lambda: 3 * [0.0])  # edge vector of a surface - B
    iWN: list[int] = field(default_factory=lambda: 4 * [-1])  # component vertices of a surface

    # heat transfer to surfaces
    eQX: float = 0.0  # heat flux from external fire sources
    eQXX: float = 0.0  # external heat flux
    QWi: float = 0.0  # cumulative heat received per unit area


# --------------------------------------------
#        Vertices
# --------------------------------------------
@dataclass
class Vertex:

    CC: list[float] = field(default_factory=lambda: 3 * [0.0])  # coordinates of a vertex (x, y, z)
    BB: float = 0.0  # Node coordinate (x) : longitude
    LL: float = 0.0  # Node coordinate (y) : latitude


# --------------------------------------------
#        Adjacent objects
# --------------------------------------------
@dataclass
class Adjacent:
    
    iAO: int = 0  # heat receiving object
    iAW: int = 0  # heat receiving surface


# --------------------------------------------
#        Objects
# --------------------------------------------
@dataclass
class Object:

    WW: list[Polygon] = field(default_factory=lambda: [Polygon() for _ in range(nW)])
    VV: list[Vertex] = field(default_factory=lambda: [Vertex() for _ in range(nV)])
    ADJ: list[Adjacent] = field(default_factory=lambda: [Adjacent() for _ in range(nA)])

    # outline
    nVRTX: int = 0  # number of vertices
    nPOLY: int = 0  # number of surfaces

    # fuel combustion
    iFC: int = 0  # status of computation (0: inactive, 1: active, 2: ended)
    iFB: int = 0  # status of combustion (0: inactive, 1: active, 2: ended)
    Tig: float = 0  # ignition time
    FW: float = 0  # total fuel load
    FW0: float = 0  # total fuel load (initial)
    rMF: float = 0  # mass loss rate (MLR)
    QX: float = 0  # heat release rate (HRR)

    # fire spread between objects
    nADJ: int = 0  # number of adjacent objects
    HO: float = 0  # height of an object
    Afp: float = 0  # base area of an object
    QBa: float = 0  # cumulative heat release
    TTa: float = 0  # ambient temperature
    GO: list[float] = field(default_factory=lambda: 3 * [0.0])  # gravitational point of an object (x, y, z)
