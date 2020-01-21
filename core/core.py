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
shape:core

Receives gestural inputs, audio analysis inputs, as well as user happiness. 
"""

import warnings

import zmq
import numpy as np
from tensorflow.keras.models import load_model

from core.models import GestureClassifier, Mapper
import data.communicator as cm

GESTURE = 'gesture'
MAP = 'mapping'

LEARN_READY = 'Learn process ready'
PREDICT_READY = 'Predict process ready'

def learn(output_dim): # Codes for maximum size of gestures that can be learned.
    comm = cm.Communicator([cm.LEARN_REP, cm.MODEL_PUSH, cm.READY_REQ])

    gesture_model = None
    map_model = None

    comm.READY_REQ_SEND(LEARN_READY)
    comm.READY_REQ_RECV()

    for socket, novelty in next(comm):

        # A gesture to be learned
        if type(novelty) is np.ndarray:

            input_dim = novelty.shape[1]
            
            if gesture_model is None:
                print('Gesture classifier created')
                gesture_model = GestureClassifier(input_dim, output_dim)
                gesture_model.add_datapoint(novelty)
                
                socket.send_pyobj('Gesture classifier created, knows only one class')
            else:
                gesture_model.add_datapoint(novelty)
                gesture_model.train()

                # Threading bug somewhere in python, cannot pickle keras models. Once pickling is possible,
                # send the entire object.
                model_file = '{}_model.h5'.format(input_dim)
                gesture_model.model.save(model_file)

                embedding_file = '{}_embeddings.h5'.format(input_dim)
                gesture_model.embedding.save(embedding_file)

                comm.MODEL_PUSH_SEND([ GESTURE, model_file, embedding_file ])

                socket.send_pyobj('Gesture classifier trained, knows {} classes'.format(len(gesture_model.data)))
                
        # A mapping to be learned, i.e. the novelty is a list of x,y pairs.
        else:

            x,(synth_prms, audio_ftrs) = novelty
            input_dim = len(x)
            synth_prms_output_dim = len(synth_prms)
            audio_ftrs_output_dim = len(audio_ftrs)
            
            if map_model is None:
                map_model = Mapper(input_dim, synth_prms_output_dim, audio_ftrs_output_dim)
                map_model.add_datapoint(novelty)

                socket.send_pyobj('Mapper created, knows only one class')
            else:
                map_model.add_datapoint(novelty)
                map_model.train()

                map_file = '{}_mapper.h5'.format(input_dim)
                map_model.model.save(map_file)
                
                comm.MODEL_PUSH_SEND([ MAP, map_file ])
                
                socket.send_pyobj('Mapper created, knows only one class')


    print('Learning process exit')

    
def predict():
    comm = cm.Communicator([cm.MODEL_PULL, cm.PREDICT_REP, cm.READY_REQ])

    comm.READY_REQ_SEND(PREDICT_READY)
    comm.READY_REQ_RECV()
    
    gesture_model = None
    mapping_model = None

    for socket, msg in next(comm):
        
        if socket == cm.MODEL_PULL:
            
            if msg[0] == GESTURE:
                _, model_file, embedding_file = msg
                new_model = load_model(model_file)
                new_embedding = load_model(embedding_file)

                gesture_model = lambda x: [ new_model.predict(x), new_embedding.predict(x) ]
                
                print('New gesture model loaded:', gesture_model)
                
            if msg[0] == MAP:
                
                map_file = msg[1]

                new_map = load_model(map_file)
                map_model = lambda x: new_map.predict(x)
                
                print('New mapping model loaded:', map_model)

        if socket == cm.PREDICT_REP:
            signal = msg

            try:
                prediction, embedding = gesture_model(signal[np.newaxis,:])
                synth_prms, audio_ftrs = map_model(embedding)
                comm.PREDICT_REP_SEND([ prediction, embedding, synth_prms, audio_ftrs, signal ])
            except Exception as e:
                warnings.warn('Models are not trained yet')
                comm.PREDICT_REP_SEND([ False, False, False, False, False ])
                
    print('Prediction process exit')
