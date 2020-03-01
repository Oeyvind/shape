#!/usr/bin/python
# -*- coding: latin-1 -*-
# 
#    Copyright 2019 Oeyvind Brandtsegg and Axel Tidemann
#
#    This file is part of the Shape package
#
#    The Shape package is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3 
#    as published by the Free Software Foundation.
#
#    The Shape is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Shape package.  
#    If not, see <http://www.gnu.org/licenses/>.

"""
shape:inputs test
"""

import unittest
import multiprocessing as mp
import time

import numpy as np

from core.faux_gestures import trajectories
import data.communicator as cm
import data.inputs

class ShapeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comm = cm.Communicator([ cm.SENSOR_PUSH, cm.LEARNING_MODE_PUSH,
                                     cm.DEATH_PUB ])
        
        cls.processes = []
        cls.processes.append(mp.Process(target=data.inputs.run, args=(10, True)))

        for p in cls.processes:
            p.start()

            
    def test_learn_play(self):
        n = 3

        for gesture in trajectories[:n]:
            self.comm.LEARNING_MODE_PUSH_SEND(data.inputs.REC)
            time.sleep(1)
            
            for sample in gesture:
                self.comm.SENSOR_PUSH_SEND(sample)

            time.sleep(1)
            self.comm.LEARNING_MODE_PUSH_SEND(data.inputs.CHILL)
            time.sleep(10)
            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        
        for p in cls.processes:
            p.join()
        

if __name__ == '__main__':
    unittest.main()
