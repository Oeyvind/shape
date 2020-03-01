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
Example for how to connect externally to a running container.
"""

import time

import zmq
import numpy as np

import data.communicator as cm
from core.faux_gestures import trajectories
from core.candidate import create
from utils.constants import ADDITIVE

comm = cm.Communicator([ cm.LEARN_REQ, cm.PLAY_REQ ])

n = 3

for gesture in trajectories[:n]:
    comm.LEARN_REQ_SEND([ gesture, create(gesture, ADDITIVE.n_parameters) ])
    comm.LEARN_REQ_RECV()

ready = False

while not ready:
    comm.PLAY_REQ_SEND(trajectories[0])
    reply = comm.PLAY_REQ_RECV()

    if reply is not None:
        ready = True
    else:
        print('Model not ready, waiting 5 seconds before trying again.')
        time.sleep(5)

    
for i, gesture in enumerate(trajectories[:n]):
    comm.PLAY_REQ_SEND(gesture)
    gesture_prediction, synth_prms_prediction = comm.PLAY_REQ_RECV()
    print('Predicted gesture:', np.argmax(gesture_prediction))
