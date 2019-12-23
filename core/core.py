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

from models import GestureClassifier
import communicator as cm

GESTURE = 'gesture'
MAPPING = 'mapping'

def learn(output_dim):
    print('Learning process started')

    comm = cm.Communicator([cm.LEARN_PULL, cm.MODEL_PUSH])
     
    gesture_model = None
    mapping_model = None

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

        # A mapping to be learned
        else:
            if mapping_model is None:
                print('Mapping model created')
                mapping_model = 1
                x,y = novelty
            else:
                print('Training new mapping model')
            
            

    print('Learning process exit')

    
def predict(output_dim):
    print('Prediction process started')

    comm = cm.Communicator([cm.MODEL_PULL, cm.PREDICT_REP])
    
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
                
            if msg[0] == MAPPING:
                print('New mapping model loaded')

        if socket == cm.PREDICT_REP:
            signal = msg
            input_dim = signal.shape[1]

            try:
                prediction, embedding = gesture_model(signal[np.newaxis,:])
                mapping = np.random.random(output_dim)
                comm.predict_rep.send_pyobj([ prediction, embedding, mapping, signal ])
            except:
                warnings.warn('Models not trained yet')
                comm.predict_rep.send_pyobj([ False, False, False, False ])
                
    print('Prediction process exit')


if __name__ == '__main__':
    processes = []
    output_dim = 10
    processes.append(mp.Process(target=learn, args=(output_dim,)))
    processes.append(mp.Process(target=predict, args=(output_dim,)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()
