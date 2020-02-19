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

class GestureMapperTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        input_dim = 2
        n_classes = 10
        synth_parameters_dim = 10
        audio_features_dim = 12
        cls.model = GestureMapper(input_dim, n_classes, synth_parameters_dim, audio_features_dim)
        
        for x in trajectories:
            cls.model.add_datapoint(x, np.random.rand(synth_parameters_dim), np.random.rand(audio_features_dim))

    def test_add_datapoint(self):
        self.assertWarns(UserWarning, self.model.add_datapoint, np.random.random(5), None, None)


    def test_train_predict(self):
        self.model.train()

        gesture_predictions, _, _ = self.model.predict(self.model._pad(trajectories))
        self.assertTrue(all(np.argmax(gesture_predictions, axis=1) == range(len(trajectories))))


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
