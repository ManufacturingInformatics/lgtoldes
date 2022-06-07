#!/usr/bin/env python
# encoding: utf-8

# import logging
import json
from importlib import resources
import numpy as np
# import os

class JTModelKinematic(object):
    # def __init__(self):
    #     with resources.path("lgtoldes.data", "piston_model_v2.json") as f_tbl_path:
    #         print(f_tbl_path)
    #         logging.info(f_tbl_path)
    #         self.__init__(f_tbl_path)
    # def __init__(self, json_filename):
    #     with open(json_filename) as f:
    #         self.jti = json.load(f)
    #     self.feNum = self.jti.tolerancechain
    def __init__(self, *args) -> None:
        # if args are more than 1 sum of args
        # print(len(args))
        if len(args) < 1:
            self.fti = resources.read_text("lgtoldes.data", "piston_model_v2.json")
            self.jti = json.loads(self.fti)
        
        if len(args) == 1:
            with open(args[0], "r") as f:
                self.jti = json.load(f)
        
        # print(self.jti, flush=True)
        self._setup_matrices_()
        self._setup_jacobian_()
        self._calculate_fe_length_()

    def _setup_matrices_(self) -> None:
        # Get number of matrices for JT model and prepare them

        self.feNum = len(self.jti["tolerancechain"])
        self.matNum = 0;
        self.jntNum = 0;
        
        for i in range(self.feNum):
            nodename = self.jti['tolerancechain'][i]['node']
            nodetype = self.jti['nodes'][nodename]['type']

            if nodetype == 'fixed':
                self.matNum = self.matNum + 1
            elif nodetype == 'joint':
                self.matNum = self.matNum + 2
                self.jntNum = self.jntNum + 1
            elif nodetype == 'doublejoint':
                self.matNum = self.matNum + 3
                self.jntNum = self.jntNum + 2
            else:
                raise Exception("Invalid node type: %s" % nodetype)
            
        self.jMat = [None] * self.matNum
        self.tMat = [None] * self.matNum

    def _setup_jacobian_(self) -> None:                    
        # Jacobian matrix
        matIndex = 0
        jntIndex = np.zeros((1, self.jntNum), np.int8)
        for i in range(self.feNum):
            nodename = self.jti['tolerancechain'][i]['node']
            refpoint = self.jti['frrefpoint']
            dTemp = np.array(self.jti['nodes'][nodename]['coord']) - np.array(self.jti['nodes'][refpoint]['coord'])
            # print(dTemp)
            x,y,z = dTemp
            # print(x,y,z)
            jMatTemp = np.array([
                [1, 0, 0, 0, z, -y],
                [0, 1, 0, -z, 0, x],
                [0, 0, 1, y, -x, 0],
                [0, 0, 0, 1, 0, 0,],
                [0, 0, 0, 0, 1, 0,],
                [0, 0, 0, 0, 0, 1,]])
                
            nodename = self.jti['tolerancechain'][i]['node']
            nodetype = self.jti['nodes'][nodename]['type']

            if nodetype == 'fixed':
                self.jMat[matIndex] = jMatTemp
            elif nodetype == 'joint':
                self.jMat[matIndex] = jMatTemp
                self.jMat[matIndex + 1] = jMatTemp
                matIndex = matIndex + 2
            elif nodetype == 'doublejoint':
                self.jMat[matIndex] = jMatTemp
                self.jMat[matIndex + 1] = jMatTemp
                self.jMat[matIndex + 2] = jMatTemp
                matIndex = matIndex + 3
            else:
                raise Exception("Invalid node type: %s" % nodetype)
            
    def _calculate_fe_length_(self) -> None:
        # self.feLength = [None] *self.feNum
        self.feLength = np.zeros((self.feNum, 1), dtype=np.float)
        for i in range(self.feNum):
            nodename = self.jti['tolerancechain'][i]['node']
            coord = self.jti['nodes'][nodename]['coord']
            nextnodename = self.jti['tolerancechain'][i]['nextnode']
            nextcoord = self.jti['nodes'][nextnodename]['coord']
            self.feLength[i] = np.linalg.norm(np.array(coord) - np.array(nextcoord))
    
    def _torsor_simulation(self, *args, **kwargs):
        pass