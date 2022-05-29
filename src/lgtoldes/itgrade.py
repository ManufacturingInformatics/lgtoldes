#!/usr/bin/env python
# encoding: utf-8

def print_something(something):
    print(something, flush=True)
    return something

def getStdTolVal(normSize, ITGrd, ITGrdDF):
    StdTolVal = ITGrdDF[(normSize > ITGrdDF.lowerBound) & (normSize <= ITGrdDF.upperBound)].loc[:, ITGrd]
    return float(StdTolVal)

class ITGrd:
    def __init__(self):
        self.ITGrdTblZZ