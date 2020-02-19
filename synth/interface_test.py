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

import matplotlib.pyplot as plt
import numpy as np

from synth.interface import listen, SYNTH_READY
import data.communicator as cm
from core.faux_gestures import circle

class InterfaceTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.comm = cm.Communicator([cm.SYNTH_REQ, cm.READY_REP, cm.DEATH_PUB])

        cls.listen = mp.Process(target=listen, args=(True,))
        cls.listen.start()

        cm.Waiter(cls.comm, [ SYNTH_READY ])

        
    def test_listen(self):
        x = np.arange(circle.shape[0])
        
        for _ in range(3):

            parameters = np.random.rand( circle.shape[0], 14 )
            self.comm.SYNTH_REQ_SEND(parameters)
            filename, analysis = self.comm.SYNTH_REQ_RECV()

            fig, axs = plt.subplots(5, 2, sharex=True)

            axs[0,0].plot(x, circle[:,0], label='gesture X')
            axs[0,0].legend(loc='upper right')
            axs[0,1].plot(x, circle[:,1], label='gesture Y')
            axs[0,1].legend(loc='upper right')
            
            i = 1
            j = 0
            for k, feature in enumerate(analysis.T):
                axs[i,j].plot(x, feature, label='audio feature {}'.format(k))
                axs[i,j].legend(loc='upper right')
                axs[i,j].set_ylim(0,1)

                j+=1

                if j == 2:
                    i += 1
                    j = 0

            plt.savefig('/shape/sounds/{}.png'.format(filename), dpi=300)
            plt.clf()
            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        cls.listen.join()

        
if __name__ == '__main__':
    unittest.main()
