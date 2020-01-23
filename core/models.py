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

class GestureMapper:

    def __init__(self, input_dim, n_classes, synth_parameters_dim, audio_features_dim,
                 n_filters=20, filter_widths=range(1,7), dropout=.5, hidden_size=128, n_hidden_layers=2,
                 noise_std=.1, epochs=10, n_augments=100, validation_split=.2):

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
        audio_ftrs = layers.Dense(audio_features_dim, name='audio_ftrs')(x)

        outputs = [ gesture, synth_prms, audio_ftrs ]
        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        losses = { 'gesture': 'sparse_categorical_crossentropy',
                   'synth_prms': tf.keras.losses.Huber(),
                   'audio_ftrs': tf.keras.losses.Huber() }
        
        metrics = { 'gesture': 'accuracy',
                    'synth_prms': 'mse',
                    'audio_ftrs': 'mse' }
                    
        self.model.compile(loss=losses, optimizer='adam', metrics=metrics)

        self.data = []
        self.noise_std = noise_std
        self.epochs = epochs
        self.n_augments = n_augments
        self.validation_split = validation_split

        
    def add_datapoint(self, x_gesture, y_synth_prms, y_audio_ftrs):
        # Data: timesteps x channels.
        if len(x_gesture.shape) == 1:
            x_gesture = x_gesture.reshape(-1,1)

        if len(x_gesture) < 10:
            warnings.warn('Datapoints must have a length of at least 10, discarding.')
        else:
            self.data.append(( x_gesture, y_synth_prms, y_audio_ftrs ))


    def _pad(self, X):
        max_len = max(map(len, X))

        padded = [ pad(x.T, maxlen=max_len, dtype=np.float, padding='post', value=MASK_VALUE).T for x in X ]

        return np.stack(padded)
        
            
    def _data_augmentation(self):

        x_gesture, y_synth_prms, y_audio_ftrs = zip(*self.data)

        y_gesture = np.arange(len(x_gesture))
        y_gesture = np.repeat(y_gesture, self.n_augments, axis=0)

        y_synth_prms = np.repeat(y_synth_prms, self.n_augments, axis=0)
        
        y_audio_ftrs = np.repeat(y_audio_ftrs, self.n_augments, axis=0)
                
        x_padded = self._pad(x_gesture)
        
        x_repeated = np.repeat(x_padded, self.n_augments, axis=0)
        mask = np.where(x_repeated == MASK_VALUE)

        x_noised = x_repeated + np.random.normal(0, self.noise_std, size=x_repeated.shape)
        x_noised[mask] = MASK_VALUE

        return shuffle(x_noised, y_gesture, y_synth_prms, y_audio_ftrs)

    
    def train(self):
        x_gesture, y_gesture, y_synth_prms, y_audio_ftrs = self._data_augmentation()

        x = x_gesture
        y = { 'gesture': y_gesture,
              'synth_prms': y_synth_prms,
              'audio_ftrs': y_audio_ftrs }

        try:
            self.model.fit(x, y, epochs=self.epochs, validation_split=self.validation_split, verbose=False)
        except Exception as e:
            print(e)
            print(x)
            print(y)

        
    def predict(self, x):
        return self.model.predict(x)


        
        

# class GestureClassifier:

#     def __init__(self, input_dim, dim, n_filters=20, filter_widths=range(1,7),
#                  dropout=.5, hidden_size=128, noise_std=.1, epochs=10, n_augments=100,
#                  validation_split=.2):

#         inputs = layers.Input(shape=(None, input_dim))

#         filters = []

#         for fw in filter_widths:
#             x = layers.Masking(mask_value=MASK_VALUE)(inputs)
#             x = layers.Conv1D(n_filters*fw, fw, activation='tanh')(x)
#             x = layers.GlobalMaxPool1D()(x)
#             filters.append(x)

#         merge = layers.Concatenate()(filters)
#         dropout = layers.Dropout(dropout)(merge)
#         embedding = layers.Dense(hidden_size, activation='elu', name='embedding')(dropout)
#         outputs = layers.Dense(dim, activation='softmax')(embedding)

#         self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
#         self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

#         self.embedding = tf.keras.Model(inputs=inputs, outputs=embedding)

#         self.data = []
#         self.noise_std = noise_std
#         self.epochs = epochs
#         self.n_augments = n_augments
#         self.validation_split = validation_split

        
#     def add_datapoint(self, x):
#         # Data: timesteps x channels.
#         if len(x.shape) == 1:
#             x = x.reshape(-1,1)

#         if len(x) < 10:
#             warnings.warn('Datapoints must have a length of at least 10')
#         else:
#             self.data.append(x)


#     def _pad(self, X):
#         max_len = max(map(len, X))

#         padded = [ pad(x.T, maxlen=max_len, dtype=np.float, padding='post', value=MASK_VALUE).T for x in X ]

#         return np.stack(padded)
        
            
#     def _data_augmentation(self):
#         padded = self._pad(self.data)
        
#         repeated = np.repeat(padded, self.n_augments, axis=0)
#         mask = np.where(repeated == MASK_VALUE)

#         noised = repeated + np.random.normal(0, self.noise_std, size=repeated.shape)
#         noised[mask] = MASK_VALUE

#         return noised

    
#     def training_data(self):
#         x = self._data_augmentation()
#         y = np.repeat(range(len(self.data)), self.n_augments)

#         return shuffle(x, y)

    
#     def train(self):
#         x, y = self.training_data()
#         self.model.fit(x, y, epochs=self.epochs, validation_split=self.validation_split)

        
#     def predict(self, x):
#         return self.model.predict(x), self.embedding.predict(x)

# class Mapper:

#     # Noise std is lower here, because it is assumed these kinds of mappings will be 
#     # closer in the high-dimensional feature space
#     def __init__(self, input_dim, synth_parameters_dim, audio_features_dim, n_hidden_layers=2,
#                  hidden_size=128, noise_std=.01, epochs=10, n_augments=100,
#                  validation_split=.2):

#         inputs = layers.Input(shape=(input_dim,))

#         x = inputs

#         for _ in range(n_hidden_layers):
#             x = layers.Dense(hidden_size, activation='elu')(x)

#         synth_parameters = layers.Dense(synth_parameters_dim, name='synth_prms')(x)
#         audio_features = layers.Dense(audio_features_dim, name='audio_ftrs')(x)

#         outputs = [ synth_parameters, audio_features ]
        
#         self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
#         self.model.compile(loss=tf.keras.losses.Huber(), optimizer='adam')

#         self.data = []
#         self.noise_std = noise_std
#         self.epochs = epochs
#         self.n_augments = n_augments
#         self.validation_split = validation_split

        
#     def add_datapoint(self, x_y):
#         self.data.append(x_y)

        
#     def _data_augmentation(self):
#         x, y = zip(*self.data)

#         x = np.stack(x)

#         repeated = np.repeat(x, self.n_augments, axis=0)

#         noised = repeated + np.random.normal(0, self.noise_std, size=repeated.shape)

#         return noised, y
    
    
#     def training_data(self):
#         x,y = self._data_augmentation()

#         synth_parameters, audio_features = zip(*y)

#         synth_parameters = np.stack(synth_parameters)
#         synth_parameters = np.repeat(synth_parameters, self.n_augments, axis=0)

#         audio_features = np.stack(audio_features)
#         audio_features = np.repeat(audio_features, self.n_augments, axis=0)
        
#         return shuffle(x, synth_parameters, audio_features)

    
#     def train(self):
#         x, synth_parameters, audio_features = self.training_data()
#         y = [ synth_parameters, audio_features ]
#         self.model.fit(x, y, epochs=self.epochs, validation_split=self.validation_split)

        
#     def predict(self, x):
#         return self.model.predict(x)
