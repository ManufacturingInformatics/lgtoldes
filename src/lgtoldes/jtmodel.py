#!/usr/bin/env python
# encoding: utf-8

# import logging
import json
import warnings
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
        self._torsor_simulation_()

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
            
        # self.jMat = [None] * self.matNum
        # self.tMat = [None] * self.matNum
        self.jMat = np.zeros((self.matNum, 6, 6), dtype=np.float32)
        self.tMat = np.zeros((self.matNum, 6), dtype=np.float32)

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
                # self.jMat[matIndex] = jMatTemp
                self.jMat[matIndex,:,:] = jMatTemp
            elif nodetype == 'joint':
                # self.jMat[matIndex] = jMatTemp
                # self.jMat[matIndex + 1] = jMatTemp
                self.jMat[matIndex, :, :] = jMatTemp
                self.jMat[matIndex + 1, :, :] = jMatTemp
                matIndex = matIndex + 2
            elif nodetype == 'doublejoint':
                # self.jMat[matIndex] = jMatTemp
                # self.jMat[matIndex + 1] = jMatTemp
                # self.jMat[matIndex + 2] = jMatTemp
                self.jMat[matIndex, :, :] = jMatTemp
                self.jMat[matIndex + 1, :, :] = jMatTemp
                self.jMat[matIndex + 2, :, :] = jMatTemp
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
    
    def _torsor_simulation_(self):
        self.feStore = np.zeros((self.matNum, 6, self.jti['simtime']), dtype=np.float) # note 3D array
        self.frStore = np.zeros((6, self.jti['simtime']), dtype=np.float)
        
        for i in range(self.jti['simtime']): # check start value
            if self.jti['errgeneration'] == 'auto':
                # lots of code
                pass
            elif self.jti['errgeneration'] == 'manual':
                warnings.warn("Warning: error generation type %s currently unsupported" % self.jti['errgeneration'])
            else:
                raise Exception("Invalid error generation type: %s" % self.jti['errgeneration'])
            
            for j in range(self.matNum): # check start value
                self.feStore[j, : ,i] = np.matmul(self.jMat[j,:,:], self.tMat[j,:])
                self.frStore[:, i] = self.frStore[:, i] + self.feStore[j, :, i]
            

    def _one_simulation_run_(self):
        matIndex = 0
        for i in range(self.feNum):
            nodename = self.jti['tolerancechain'][i]['node']
            nodetype = self.jti['nodes'][nodename]['type']

            if nodetype == 'fixed':
                # This is the MATLAB code for this section
                # d = normrnd(0, getStdTolVal(feLength(j), val.itgrade, ITGradeTable) / 3);
                # tMat{matIndex} = [d * abs(val.nodes.(val.tolerancechain(j).node).coord - val.nodes.(val.tolerancechain(j).nextnode).coord) / feLength(j); 0; 0; 0];
                # matIndex = matIndex + 1;
                pass
            elif nodetype == 'joint':
                # This is the MATLAB code for this section
                # [jntAngErr, jntCl] = getJntErr(feLength(j - 1), val.itgrade, ITGradeTable); % check this function file "getJntErr.m"
                # dJntCl = normrnd(jntCl, jntCl / 10 / 3); % TBD
                # % jntAngErr should be smaller. try jntAngErr / 30
                # dJntAng = normrnd(0, jntAngErr / 3, [3, 1]); % Joint angular error and clearance.
                # tMat{matIndex} = [dJntCl * abs(val.nodes.(val.tolerancechain(j).node).coord - val.nodes.(val.tolerancechain(j).nextnode).coord) / feLength(j); dJntAng];
                #    
                # d = normrnd(0, getStdTolVal(feLength(j), val.itgrade, ITGradeTable) / 3);
                # tMat{matIndex + 1} = [d * abs(val.nodes.(val.tolerancechain(j).node).coord - val.nodes.(val.tolerancechain(j).nextnode).coord) / feLength(j); 0; 0; 0];
                #   
                # matIndex = matIndex + 2;
                pass
            elif nodetype == 'doublejoint':
                # This is the MATLAB code for this section
                # [jntAngErr, jntCl] = getJntErr(feLength(j - 1), val.itgrade, ITGradeTable);
                # dJntCl = normrnd(jntCl, jntCl / 10 / 3); % TBD
                # % jntAngErr should be smaller. try jntAngErr / 30
                # dJntAng = normrnd(0, jntAngErr / 3, [3, 1]); % Joint angular error and clearance.
                # tMat{matIndex} = [dJntCl * abs(val.nodes.(val.tolerancechain(j - 1).node).coord - val.nodes.(val.tolerancechain(j - 1).nextnode).coord) / feLength(j - 1); dJntAng];
                #    
                # [jntAngErr, jntCl] = getJntErr(feLength(j), val.itgrade, ITGradeTable);
                # dJntCl = normrnd(jntCl, jntCl / 10 / 3); % TBD
                # % jntAngErr should be smaller. try jntAngErr / 30
                # dJntAng = normrnd(0, jntAngErr / 3, [3, 1]); % Joint angular error and clearance.
                # tMat{matIndex + 1} = [dJntCl * abs(val.nodes.(val.tolerancechain(j).node).coord - val.nodes.(val.tolerancechain(j).nextnode).coord) / feLength(j); dJntAng];
                #    
                # d = normrnd(0, getStdTolVal(feLength(j), val.itgrade, ITGradeTable) / 3);
                # tMat{matIndex + 2} = [d * abs(val.nodes.(val.tolerancechain(j).node).coord - val.nodes.(val.tolerancechain(j).nextnode).coord) / feLength(j);0;0;0];
                #    
                # matIndex = matIndex + 3;
                pass
            else:
                raise Exception("Invalid node type: %s" % nodetype)
                
    def data_analysis(self):
        # feMaxDiff = zeros(6, matNum);
        # feErrDist = zeros(6, matNum);
        # frErrDist = zeros(1, matNum);
        # for i = 1:6
        #     for j = 1:matNum
        #         feMaxDiff(i, j) = max(feStore{j}(i, :)) - min(feStore{j}(i, :));
        #     end
        # end

        # for i = 1:6
        #     feErrDist(i, :) = feMaxDiff(i, :) / sum(feMaxDiff(i, :));
        # end

        # switch val.frtype
        #     case 'point'
        #         for i = 1:3
        #             frErrDist = frErrDist + feErrDist(i, :);
        #         end
        #         frErrDist = frErrDist / 3;
        #     case 'plane'
        #         for i = 1:6
        #             frErrDist = frErrDist + feErrDist(i, :);
        #         end
        #         frErrDist = frErrDist / 6;
        # end
        pass