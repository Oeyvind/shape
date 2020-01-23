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
import time

from core.faux_gestures import trajectories
import data.communicator as cm
import shape

class ShapeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.comm = cm.Communicator([ cm.LEARN_PUSH, cm.PLAY_PUSH, cm.DEATH_PUB, cm.PREFERENCES_REP ])
        
        cls.processes = []
        cls.processes.append(mp.Process(target=shape.run))

        for p in cls.processes:
            p.start()


    def test_learn(self):
        for gesture in trajectories:
            self.comm.LEARN_PUSH_SEND(gesture)

            self.comm.PREFERENCES_REP_RECV()
            time.sleep(5) # To emulate listening to a 3 second sound, and providing feedback
            self.comm.PREFERENCES_REP_SEND(True)
            
            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        
        for p in cls.processes:
            p.join()
        

if __name__ == '__main__':
    unittest.main()
