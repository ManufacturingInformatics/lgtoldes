#!/usr/bin/env python
# encoding: utf-8

import logging
import json
from importlib import resources

class JTModelKinematic(object):
    def __init__(self):
        with resources.path("lgtoldes.data", "piston_model_v2.json") as f_tbl_path:
            logging.info(f_tbl_path)
            self.__init__(f_tbl_path)
    def __init__(self, json_filename):
        with open(json_filename) as f:
            self.jti = json.load(f)
        self.feNum = self.jti.tolerancechain