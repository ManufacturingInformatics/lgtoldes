#!/usr/bin/env python
# encoding: utf-8

import logging
import json
from importlib import resources
import os

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
            # self.f_json_path = resources.path("lgtoldes.data", "piston_model_v2.json")
            # self.f_json_path = resources.path("lgtoldes.data", "piston_model_v2.json")
            self.fti = resources.read_text("lgtoldes.data", "piston_model_v2.json")
            self.jti = json.loads(self.fti)
        
        if len(args) == 1:
            print(os.getcwd())
            # self.f_json_path = args[0]
            # self.fti = resources.read_text(args[0])
            with open(args[0], "r") as f:
                self.jti = json.load(f)
        
        print(self.jti, flush=True)

        self.feNum = len(self.jti["tolerancechain"])
                
            