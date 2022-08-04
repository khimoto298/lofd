# -*- coding: utf-8 -*-

import random


# uniform random number
def RNDMi(iSEED):

    if iSEED >= 0:
        random.seed(iSEED)
    else:
        random.seed()


# normal random number
def RNDMg():

    RNNg = -6.0
    for _ in range(12):
        RNNu = random.random()
        RNNg = RNNg + RNNu
    return RNNg
