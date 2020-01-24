#!/usr/bin/python
# -*- coding: latin-1 -*-
# 
#    Copyright 2018 Oeyvind Brandtsegg and Axel Tidemann
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
shape:synth ØMQ wrapper test file
"""

import unittest
import multiprocessing as mp
import time

import numpy as np

from synth.interface import listen, SYNTH_READY
import data.communicator as cm

class InterfaceTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.comm = cm.Communicator([cm.SYNTH_REQ, cm.READY_REP, cm.DEATH_PUB])

        duration = 3
        cls.listen = mp.Process(target=listen, args=(duration,))
        cls.listen.start()

        cm.Waiter(cls.comm, [ SYNTH_READY ])

        
    def test_listen(self):
        for _ in range(3):
            parameters = np.random.rand(10)
            print('Sending parameters:', parameters)
            self.comm.SYNTH_REQ_SEND(np.random.rand(10))
            analysis = self.comm.SYNTH_REQ_RECV()
            print('Received analysis:', analysis)

            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        cls.listen.join()

        
if __name__ == '__main__':
    unittest.main()
