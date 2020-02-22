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

import numpy as np
from sklearn.preprocessing import minmax_scale
import matplotlib.pyplot as plt

from synth.interface import listen, SYNTH_READY
import data.communicator as cm
from core.faux_gestures import trajectories
from utils.constants import ADDITIVE, SUBMONO, SINE, PARTIKKEL

class InterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comm = cm.Communicator([cm.SYNTH_REQ, cm.READY_REP, cm.DEATH_PUB])

        cls.listen = mp.Process(target=listen, args=(True,))
        cls.listen.start()

        cm.Waiter(cls.comm, [ SYNTH_READY ])

    def evaluate(self, instrument, n_parameters):
        names = [ 'zero', 'circle', 'line', 'r_line', 'sine', 'mega_sine', 'spiral', 'tanh', 'random' ]
        for name, trajectory in zip(names, trajectories):
            # Range is -1,1 for input signals, scale it to 0,1.
            scaled = (trajectory + 1)/2
            X, Y = scaled.T

            plt.plot(X,Y)
            plt.xlim(-.1, 1.1)
            plt.ylim(-.1, 1.1)
            gesture_plot = '/shape/sounds/_{}.png'.format(name)
            plt.savefig(gesture_plot, dpi=300)
            plt.clf()

            parameters = []

            n = 8

            for _ in range(n):
                root = np.random.rand( 1, n_parameters )
                root = np.repeat(root, scaled.shape[0], axis=0)

                for _param in root.T:
                    _param += random.choice([X,Y])*np.random.rand()

                root = np.clip(root, 0, 1)

                parameters.append(root)

            self.comm.SYNTH_REQ_SEND([ parameters, instrument, X, Y, True ])

            sounds = self.comm.SYNTH_REQ_RECV()
            sounds = sorted(sounds, key=lambda L: L[1])

            title = '{}:{}'.format(instrument, name)
            html = '<html><title>{}</title><body><h1>{}</h1><img src="_{}.png" width="50%"><hr>'.format(title,
                                                                                                        title,
                                                                                                        name)
            
            for filename, similarity in sounds:
                html += '{}<audio controls> <source src="{}" type="audio/wav"> </audio>'.format(similarity, filename)
                html += '<br> <img src="{}.png" width="100%"> <hr>'.format(filename)

            html += '</body></html>'

            with open('/shape/sounds/{}_{}.html'.format(instrument, name), 'w') as out_file:
                out_file.write(html)

    def test_additive(self):
        self.evaluate(ADDITIVE.name, ADDITIVE.n_parameters)

    def test_submono(self):
        self.evaluate(SUBMONO.name, SUBMONO.n_parameters)

    def test_sine(self):
        self.evaluate(SINE.name, SINE.n_parameters)

    def test_partikkel(self):
        self.evaluate(PARTIKKEL.name, PARTIKKEL.n_parameters)
                
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        cls.listen.join()


if __name__ == '__main__':
    unittest.main()
