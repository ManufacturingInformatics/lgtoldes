#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
import numpy as np
from importlib import resources

def getStdTolVal(normSize, ITGrd, ITGrdDF):
    StdTolVal = ITGrdDF[(normSize > ITGrdDF.lowerBound) & (normSize <= ITGrdDF.upperBound)].loc[:, ITGrd]
    return float(StdTolVal)

class ITGrd:
    def __init__(self):
        with resources.path("lgtoldes.data", "ITGradeTable.csv") as f_tbl_path:
            self.ITGrdDF = pd.read_csv(f_tbl_path)
    
    def getStdTolVal(self, normSize, ITGrd):
        StdTolVal = self.ITGrdDF[(normSize > self.ITGrdDF.lowerBound) & (normSize <= self.ITGrdDF.upperBound)].loc[:, ITGrd]
        return float(StdTolVal)

    def getJntErr(self, normSize, ITGrd):
        stdTolVal = self.getStdTolVal(normSize, ITGrd)
        jntAngErr = (stdTolVal / normSize) * np.pi / 10.0
        jntCl = stdTolVal / normSize
        return (jntAngErr, jntCl)

class JTModel(object):
    def __init__(self, json_val):
        self.val = json_val
        self.feNum = self.val.tolerancechain