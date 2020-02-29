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
import uuid

import zmq
import numpy as np
from tensorflow.keras.models import load_model

from core.models import GestureMapper
import data.communicator as cm

TRAIN_READY = 'Train process ready'


def train(n_classes, sync=False):
    comm = cm.Communicator([cm.TRAIN_PULL, cm.MODEL_PUSH, cm.READY_REQ, cm.LEARN_COUNT_PUB])

    if sync:
        comm.READY_REQ_SEND(TRAIN_READY)
        comm.READY_REQ_RECV()

    model = None

    learn_counts = 0
    
    for socket, novelty in next(comm):
        x_gesture, y_synth_prms = novelty

        input_dim = x_gesture.shape[1]
        synth_parameters_dim = y_synth_prms.shape[1]

        if model is None:
            print('Gesture mapper created')
            model = GestureMapper(input_dim, n_classes, synth_parameters_dim)
            model.add_datapoint(x_gesture, y_synth_prms)

        else:
            model.add_datapoint(x_gesture, y_synth_prms)
            model.train()

            # Threading bug somewhere in python, cannot pickle keras models. Once pickling is possible,
            # send the entire object. This is messy, because it can't be written by being loaded.
            model_file = '/shape/trained_models/{}_gesture_mapper_{}.h5'.format(input_dim, uuid.uuid4())
            model.model.save(model_file)

            print('Training done, sending model')
            comm.MODEL_PUSH_SEND(model_file)

        learn_counts += 1
        comm.LEARN_COUNT_PUB_SEND(learn_counts)

    print('Training process exit')

