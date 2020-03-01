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
shape:main
"""

import multiprocessing as mp
import time

import numpy as np
from tensorflow.keras.models import load_model

from core import core
import data.communicator as cm
import data.inputs as ins
import synth.interface
from utils.constants import N_CLASSES


def run(n_classes=10, noise_std=.1):
    comm = cm.Communicator([ cm.READY_REP, cm.TRAIN_PUSH, cm.SYNTH_REQ,
                             cm.PLAY_REP, cm.MODEL_PULL, cm.LEARN_REP ])

    processes = []
    processes.append(mp.Process(target=core.train, args=(N_CLASSES, False,)))
    processes.append(mp.Process(target=synth.interface.listen))

    for p in processes:
        p.start()

    model = None

    for socket, msg in next(comm):
        if socket == cm.MODEL_PULL:
            print('Loading', msg)
            t0 = time.time()
            model = load_model(msg)
            print('Model loaded in', np.around(time.time()-t0, decimals=2), 'seconds')

        if socket == cm.PLAY_REP:
            try:
                gesture = msg[np.newaxis,:]
                t0 = time.time()
                gesture_prediction, synth_prms_prediction = model.predict(gesture)
                print(time.time() - t0)
                comm.PLAY_REP_SEND([ gesture_prediction, synth_prms_prediction ])
            except AttributeError as e:
                print('Model not ready')
                comm.PLAY_REP_SEND(None)

        if socket == cm.LEARN_REP:
            comm.TRAIN_PUSH_SEND(msg)
            comm.LEARN_REP_SEND(True)

    for p in processes:
        p.join()

    print('Shape exit')


if __name__ == "__main__":
    run()
