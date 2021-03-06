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
from data.inputs import SAVE, LOAD
import data.communicator as cm
import shape
from utils.constants import ADDITIVE

class ShapeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comm = cm.Communicator([ cm.LEARN_REQ, cm.PLAY_REQ, cm.DEATH_PUB,
                                     cm.LEARN_COUNT_SUB, cm.FILE_IO_REQ ])
        
        cls.processes = []
        cls.processes.append(mp.Process(target=shape.run))

        for p in cls.processes:
            p.start()

            
    def test_learn_predict(self):
        n = 2
        
        for gesture in trajectories[:n]:
            self.comm.LEARN_REQ_SEND([ gesture, create(gesture, ADDITIVE.n_parameters) ])
            self.comm.LEARN_REQ_RECV()

        for socket, msg in next(self.comm):
            if socket == cm.LEARN_COUNT_SUB:
                if msg == n:
                    break

        for i, gesture in enumerate(trajectories[:n]):
            self.comm.PLAY_REQ_SEND(gesture)
            gesture_prediction, synth_prms_prediction = self.comm.PLAY_REQ_RECV()
            self.assertTrue(i == np.argmax(gesture_prediction))

        self.comm.FILE_IO_REQ_SEND(SAVE)
        self.assertTrue(self.comm.FILE_IO_REQ_RECV())

        self.comm.FILE_IO_REQ_SEND(LOAD)
        self.assertTrue(self.comm.FILE_IO_REQ_RECV())
        
            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        
        for p in cls.processes:
            p.join()
        

if __name__ == '__main__':
    unittest.main()
