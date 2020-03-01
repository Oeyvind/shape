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
Deep learning models for sequence and feature embeddings.
"""

import warnings

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import load_model
import numpy as np
from sklearn.utils import shuffle
from tensorflow.keras.preprocessing.sequence import pad_sequences as pad

from utils.constants import MASK_VALUE, HISTORY_LENGTH

class GestureMapper:

    def __init__(self, input_dim, n_classes, synth_parameters_dim, 
                 n_filters=20, filter_widths=range(1,7), dropout=.5, hidden_size=128,
                 n_hidden_layers=2, noise_std=.1, epochs=10, n_augments=10,
                 validation_split=.2):

        inputs = layers.Input(shape=(None, input_dim))

        filters = []

        for fw in filter_widths:
            x = layers.Masking(mask_value=MASK_VALUE)(inputs)
            x = layers.Conv1D(n_filters*fw, fw, activation='tanh')(x)
            x = layers.GlobalMaxPool1D()(x)
            filters.append(x)

        x = layers.Concatenate()(filters)
        
        for _ in range(n_hidden_layers):
            x = layers.Dropout(dropout)(x)
            x = layers.Dense(hidden_size, activation='elu')(x)

        gesture = layers.Dense(n_classes, activation='softmax', name='gesture')(x)
        synth_prms = layers.Dense(synth_parameters_dim, name='synth_prms')(x)

        outputs = [ gesture, synth_prms ]
        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        losses = { 'gesture': 'sparse_categorical_crossentropy',
                   'synth_prms': tf.keras.losses.Huber() }
        
        metrics = { 'gesture': 'accuracy',
                    'synth_prms': 'mse' }
                    
        self.model.compile(loss=losses, optimizer='adam', metrics=metrics)

        self.data = []
        self.noise_std = noise_std
        self.epochs = epochs
        self.n_augments = n_augments
        self.validation_split = validation_split
        self.history_length = HISTORY_LENGTH

        
    def add_datapoint(self, x_gesture, y_synth_prms):
        # Data: timesteps x channels.
        if len(x_gesture.shape) == 1:
            x_gesture = x_gesture.reshape(-1,1)

        if len(x_gesture) < 10:
            warnings.warn('Datapoints must have a length of at least 10, discarding.')
        else:
            self.data.append(( x_gesture, y_synth_prms ))


    def _pad(self, X):
        max_len = max(map(len, X))

        padded = [ pad(x.T, maxlen=max_len, dtype=np.float, padding='post',
                       value=MASK_VALUE).T for x in X ]

        return np.stack(padded)

    def _roll(self, X):
        out = []

        for x in X:
            # Pads the array with MASK_VALUE along the first axis.
            padded = np.pad(x, pad_width=((self.history_length-1, 0), (0,0)),
                            mode='constant', constant_values=MASK_VALUE)
            # Cycles over the padded array.
            for i in np.arange(len(x)):
                window = np.roll(padded, -i, axis=0)[:self.history_length]
                out.append(window)

        out = np.stack(out)

        return out

    
    def _data_augmentation(self):
        x_gesture, y_synth_prms = zip(*self.data)

        y_gesture = [ np.ones(len(x))*i for i,x in enumerate(x_gesture) ]
        y_gesture = np.concatenate(y_gesture)
        y_gesture = np.repeat(y_gesture, self.n_augments, axis=0)

        y_synth_prms = np.concatenate(y_synth_prms, axis=0)
        y_synth_prms = np.repeat(y_synth_prms, self.n_augments, axis=0)

        x_rolled = self._roll(x_gesture)
        
        x_repeated = np.repeat(x_rolled, self.n_augments, axis=0)
        mask = np.where(x_repeated == MASK_VALUE)

        x_noised = x_repeated + np.random.normal(0, self.noise_std, size=x_repeated.shape)
        x_noised[mask] = MASK_VALUE

        return shuffle(x_noised, y_gesture, y_synth_prms)

    
    def train(self):
        x_gesture, y_gesture, y_synth_prms = self._data_augmentation()

        x = x_gesture
        y = { 'gesture': y_gesture,
              'synth_prms': y_synth_prms }

        self.model.fit(x, y, epochs=self.epochs, validation_split=self.validation_split, verbose=True)

        
    def predict(self, x):
        return self.model.predict(x)

