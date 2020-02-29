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
Unittest class for models.

To run it, be in the root folder and type

python -m core.models_test
"""

import unittest
import copy

import numpy as np
import matplotlib.pyplot as plt

from core.models import GestureMapper
from core.faux_gestures import trajectories
from utils.constants import ADDITIVE, MASK_VALUE
from core.candidate import create

class GestureMapperTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        input_dim = trajectories[0].shape[1]
        n_classes = len(trajectories)
        synth_parameters_dim = ADDITIVE.n_parameters
        cls.model = GestureMapper(input_dim, n_classes, synth_parameters_dim)
        
        for x in trajectories:
            cls.model.add_datapoint(x, create(x, synth_parameters_dim))

    def test_add_datapoint(self):
        self.assertWarns(UserWarning, self.model.add_datapoint, np.random.random(5), None)


    def test_train_predict(self):
        self.model.train()

        Y = [ np.ones(len(x))*i for i,x in enumerate(trajectories) ]
        Y = np.concatenate(Y)
        
        gesture_predictions, _ = self.model.predict(self.model._roll(trajectories))

        result = np.mean(np.argmax(gesture_predictions, axis=1) == Y)
        print('Prediction result:', result)
        # Test that we are correct with trajectory classificaiton at least 95% of the time.
        self.assertTrue(result > .95)


    def test_roll(self):
        x = np.zeros((10,2))
        x[:,0] = np.arange(len(x))

        rolled = self.model._roll([x])

        for i, _rld in enumerate(rolled):
            
            if i < self.model.history_length - 1:
                mask_end = self.model.history_length - 1 - i
                # Check that the maskings are correct.
                self.assertTrue(np.all(_rld[:mask_end] == MASK_VALUE))

                x_start = 0
                x_end = i+1
            else:
                mask_end = 0
                x_start = i - self.model.history_length + 1
                x_end = x_start + self.model.history_length

            # Check that the rolls are correct.                
            self.assertTrue(np.all(_rld[mask_end:] == x[x_start:x_end]))

        
    # def test_data_augmentation(self):
    #     noised = self.model._data_augmentation()

    #     for i, (original, corruptions) in enumerate(zip(self.model.data,
    #                                                     np.split(noised, len(self.model.data)))):
    #         plt.clf()

    #         for signal in corruptions:

    #             x, y = signal.T

    #             x = x[ x != MASK_VALUE ]
    #             y = y[ y != MASK_VALUE ]
                
    #             plt.plot(x, y, alpha=.1)

    #         x, y = original.T
    #         plt.plot(x, y, linewidth=3, label='original')

    #         plt.xlim(-1.1, 1.1)
    #         plt.ylim(-1.1, 1.1)

    #         plt.legend()
    #         plt.gca().set_aspect('equal')
    #         plt.tight_layout()
    #         plt.savefig('./plots/canonical_shape_{}.png'.format(i), dpi=300)

    #     print('VISUAL INSPECTION NEEDED: check ./plots/canonical_shape*png')

        
if __name__ == '__main__':
    unittest.main()
