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

MASK_VALUE = -100

class GestureClassifier:

    def __init__(self, input_dim, output_dim, n_filters=20, filter_widths=range(1,7),
                 dropout=.5, hidden_size=128, noise_std=.1, epochs=10, n_augments=100,
                 validation_split=.2):

        inputs = layers.Input(shape=(None, input_dim))

        filters = []

        for fw in filter_widths:
            x = layers.Masking(mask_value=MASK_VALUE)(inputs)
            x = layers.Conv1D(n_filters*fw, fw, activation='tanh')(x)
            x = layers.GlobalMaxPool1D()(x)
            filters.append(x)

        merge = layers.Concatenate()(filters)
        dropout = layers.Dropout(dropout)(merge)
        embedding = layers.Dense(hidden_size, activation='elu', name='embedding')(dropout)
        outputs = layers.Dense(output_dim, activation='softmax')(embedding)

        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        self.embedding = tf.keras.Model(inputs=inputs, outputs=embedding)

        self.data = []
        self.noise_std = noise_std
        self.epochs = epochs
        self.n_augments = n_augments
        self.validation_split = validation_split

        
    def add_datapoint(self, x):
        # Data: timesteps x channels.
        if len(x.shape) == 1:
            x = x.reshape(-1,1)

        if len(x) < 10:
            warnings.warn('Datapoints must have a length of at least 10')
        else:
            self.data.append(x)


    def _pad(self, X):
        max_len = max(map(len, X))

        padded = [ pad(x.T, maxlen=max_len, dtype=np.float, padding='post', value=MASK_VALUE).T for x in X ]

        return np.stack(padded)
        
            
    def _data_augmentation(self):
        padded = self._pad(self.data)
        
        repeated = np.repeat(padded, self.n_augments, axis=0)
        mask = np.where(repeated == MASK_VALUE)

        noised = repeated + np.random.normal(0, self.noise_std, size=repeated.shape)
        noised[mask] = MASK_VALUE

        return noised

    
    def training_data(self):
        x = self._data_augmentation()
        y = np.repeat(range(len(self.data)), self.n_augments)

        return shuffle(x, y)

    
    def train(self):
        x, y = self.training_data()
        self.model.fit(x, y, epochs=self.epochs, validation_split=self.validation_split)

        
    def predict(self, x):
        return self.model.predict(x), self.embedding.predict(x)

class Mapper:
    pass
