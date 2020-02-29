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
shape:main test
"""

import unittest
import multiprocessing as mp

import numpy as np

from core.faux_gestures import trajectories
from core.candidate import create
import data.communicator as cm
import shape
from utils.constants import ADDITIVE

class ShapeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comm = cm.Communicator([ cm.LEARN_PUSH, cm.PLAY_REQ, cm.DEATH_PUB, cm.LEARN_COUNT_SUB ])
        
        cls.processes = []
        cls.processes.append(mp.Process(target=shape.run))

        for p in cls.processes:
            p.start()

            
    def test_learn_predict(self):
        n = 3
        
        for gesture in trajectories[:n]:
            self.comm.LEARN_PUSH_SEND([ gesture, create(gesture, ADDITIVE.n_parameters) ])

        for socket, msg in next(self.comm):
            if socket == cm.LEARN_COUNT_SUB:
                if msg == n:
                    break

        for i, gesture in enumerate(trajectories[:n]):
            self.comm.PLAY_REQ_SEND(gesture)
            gesture_prediction, synth_prms_prediction = self.comm.PLAY_REQ_RECV()
            self.assertTrue(i == np.argmax(gesture_prediction))

            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        
        for p in cls.processes:
            p.join()
        

if __name__ == '__main__':
    unittest.main()
