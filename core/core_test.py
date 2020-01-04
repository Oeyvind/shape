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
Unittest class for shape:core
"""

import unittest
import multiprocessing as mp
import time

import numpy as np
import zmq

import core
import communicator as cm
from faux_gestures import circle, spiral, sine

class CoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.comm = cm.Communicator([cm.LEARN_PUSH, cm.PREDICT_REQ, cm.DEATH_PUB, cm.READY_REP])
        
        cls.processes = []
        cls.output_dim = 10

        cls.processes.append(mp.Process(target=core.learn, args=(cls.output_dim,)))
        cls.processes.append(mp.Process(target=core.predict, args=(cls.output_dim,)))

        cls.test_trajectories = [ circle, spiral ]

        for p in cls.processes:
            p.start()

        # Wait for the processes to be ready.
        waiting = [ core.LEARN_READY, core.PREDICT_READY ]
        for _, ready_process in next(cls.comm):
            waiting.remove(ready_process)
            cls.comm.ready_rep.send_pyobj(None) # Dummy reply

            if len(waiting) == 0:
                break


    def test_learn(self):
        for signal in self.test_trajectories:
            self.comm.learn_push.send_pyobj(signal)

            
    def test_predict(self):
        # Testing for what happens when the predict-endpoint has no model whilst waiting
        # for the model to train.
        prediction = False
        while not prediction:
            self.comm.predict_req.send_pyobj(circle)
            prediction, embedding, mapping, signal = self.comm.predict_req.recv_pyobj()
            prediction = type(prediction) is np.ndarray
            time.sleep(1)

        # Test that the model has learned these two trajectories, as well as the predict
        # function in itself.
        for i, signal in enumerate(self.test_trajectories):
            self.comm.predict_req.send_pyobj(signal)
            prediction, _, _, _ = self.comm.predict_req.recv_pyobj()
            self.assertEqual(np.argmax(prediction, axis=1), i)

        # Model sees new gesture, must learn new mapping. For the time being, this is specified.
        # Long-term: auto-discover this.
        self.comm.predict_req.send_pyobj(sine)
        prediction, _, mapping, signal = self.comm.predict_req.recv_pyobj()
        # Unhappy with prediction, requires another mapping. Attempted by adding noise.
        mapping *= np.random.random(mapping.shape)
        # This was satisfactory, added to the training datapoints of the mapping neural model.
        self.comm.learn_push.send_pyobj([signal, mapping])
            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        
        for p in cls.processes:
            p.join()

if __name__ == '__main__':
    unittest.main()
