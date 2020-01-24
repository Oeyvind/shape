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

To run it, be in the root folder and type

python -m core.core_test
"""

import unittest
import multiprocessing as mp
import time

import numpy as np
import zmq
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error as mse

from core import core
from core import faux_gestures as fg
import data.communicator as cm

class CoreTrainTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):

        cls.comm = cm.Communicator([cm.TRAIN_PUSH, cm.MODEL_PULL, cm.DEATH_PUB, cm.READY_REP])
        
        cls.processes = []
        cls.n_classes = 5
        cls.synth_parameters_dim = 7
        cls.audio_features_dim = 10

        cls.processes.append(mp.Process(target=core.train, args=(cls.n_classes, cls.synth_parameters_dim,
                                                                 cls.audio_features_dim,)))

        cls.test_gestures = [ (fg.circle,
                               np.random.rand(cls.synth_parameters_dim),
                               np.random.rand(cls.audio_features_dim)),
                               (fg.spiral,
                                np.random.rand(cls.synth_parameters_dim),
                                np.random.rand(cls.audio_features_dim)) ]

        for p in cls.processes:
            p.start()

        # waiting = [ core.TRAIN_READY ]
        # cm.Waiter(cls.comm, waiting)


    def test_train_and_predict(self):
        for novelty in self.test_gestures:
            self.comm.TRAIN_PUSH_SEND(novelty)
            
        model_file = self.comm.MODEL_PULL_RECV()
        model = load_model(model_file)

        for i, (x_gesture, target_synth_prms, target_audio_ftrs) in enumerate(self.test_gestures):
            y_gesture, y_synth_prms, y_audio_ftrs = model.predict(x_gesture[np.newaxis,:])
            self.assertEqual(np.argmax(y_gesture, axis=1), i)
            print('Synth parameters MSE:', mse(target_synth_prms, np.squeeze(y_synth_prms)))
            print('Audio features MSE:', mse(target_audio_ftrs, np.squeeze(y_audio_ftrs)))

            
    @classmethod
    def tearDownClass(cls):
        cls.comm.kill()
        
        for p in cls.processes:
            p.join()


if __name__ == '__main__':
    unittest.main()
