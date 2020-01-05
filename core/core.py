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

import multiprocessing as mp
import pickle
import warnings

import zmq
import numpy as np
from tensorflow.keras.models import load_model

from models import GestureClassifier, Mapper
import communicator as cm

GESTURE = 'gesture'
MAP = 'mapping'

LEARN_READY = 'learn_ready'
PREDICT_READY = 'predict_ready'

def learn(output_dim):
    comm = cm.Communicator([cm.LEARN_PULL, cm.MODEL_PUSH, cm.READY_REQ])

    gesture_model = None
    map_model = None

    comm.ready_req.send_pyobj(LEARN_READY)
    comm.ready_req.recv_pyobj()

    for _, novelty in next(comm):

        # A gesture to be learned
        if type(novelty) is np.ndarray:

            input_dim = novelty.shape[1]
            
            if gesture_model is None:
                print('Gesture classifier created')
                gesture_model = GestureClassifier(input_dim, output_dim)
                gesture_model.add_datapoint(novelty)
            else:
                gesture_model.add_datapoint(novelty)
                gesture_model.train()

                # Threading bug somewhere in python, cannot pickle keras models. Once pickling is possible,
                # send the entire object.
                model_file = '{}_model.h5'.format(input_dim)
                gesture_model.model.save(model_file)

                embedding_file = '{}_embeddings.h5'.format(input_dim)
                gesture_model.embedding.save(embedding_file)

                comm.model_push.send_pyobj([ GESTURE, model_file, embedding_file ])

        # A mapping to be learned, i.e. the novelty is a list of x,y pairs.
        else:

            x,y = novelty
            input_dim = len(x) 
            
            if map_model is None:
                print('Map model created')
                
                map_model = Mapper(input_dim, output_dim)
                map_model.add_datapoint(novelty)
            else:
                map_model.add_datapoint(novelty)
                map_model.train()

                map_file = '{}_mapper.h5'.format(input_dim)
                map_model.model.save(map_file)

                comm.model_push.send_pyobj([ MAP, map_file ])
            
    print('Learning process exit')

    
def predict(output_dim):
    comm = cm.Communicator([cm.MODEL_PULL, cm.PREDICT_REP, cm.READY_REQ])

    comm.ready_req.send_pyobj(PREDICT_READY)
    comm.ready_req.recv_pyobj()
    
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
                # The embedding will also include synth sound analysis.
                prediction, embedding = gesture_model(signal[np.newaxis,:])
                mapping = map_model(embedding)
                comm.predict_rep.send_pyobj([ prediction, embedding, mapping, signal ])
            except Exception as e:
                warnings.warn('Models are not trained yet')
                comm.predict_rep.send_pyobj([ False, False, False, False ])
                
    print('Prediction process exit')
