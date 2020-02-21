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
import random

import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import minmax_scale
from sklearn.metrics import mean_squared_error as mse

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

        # Note: for convenience. Do it properly when deciding on how to solve this.
        X = minmax_scale(circle[:,0])
        Y = minmax_scale(circle[:,1])
        
        parameters = []

        n = 100

        for _ in range(n):
            root = np.random.rand( 1, 14 )
            root = np.repeat(root, circle.shape[0], axis=0)
            
            for _param in root.T:
                _param += random.choice([X,Y])*np.random.rand()

            root = np.clip(root, 0, 1)
            
            parameters.append(root)
            
        self.comm.SYNTH_REQ_SEND(parameters)

        for filename, analysis in self.comm.SYNTH_REQ_RECV():

            fig, axs = plt.subplots(5, 2, sharex=True, sharey=True)
            
            # Find the most similar
            X_sim = [ mse(X, feature) for feature in analysis.T ]
            Y_sim = [ mse(Y, feature) for feature in analysis.T ]

            X_most_similar = np.argmin(X_sim)
            Y_most_similar = np.argmin(Y_sim)

            X_color = 'r'
            Y_color = 'g'
            axs[0,0].plot(x, X, label='gesture X', color=X_color)
            axs[0,0].legend(loc='upper right')
            axs[0,1].plot(x, Y, label='gesture Y', color=Y_color)
            axs[0,1].legend(loc='upper right')
            
            i = 1
            j = 0
            for k, feature in enumerate(analysis.T):
                color = 'b'
                if k == X_most_similar:
                    color = X_color
                if k == Y_most_similar:
                    color = Y_color
                if k == X_most_similar == Y_most_similar:
                    color = 'm'

                axs[i,j].plot(x, feature, color=color,
                              label='audio feature {}'.format(k))
                axs[i,j].legend(loc='upper right')
                axs[i,j].set_ylim(0,1)

                j+=1

                if j == 2:
                    i += 1
                    j = 0

            similarity = np.min(X_sim) + np.min(Y_sim)
            plt.savefig('/shape/sounds/{}_{}.png'.format(similarity, filename), dpi=300)
            plt.close()
            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        cls.listen.join()

        
if __name__ == '__main__':
    unittest.main()
