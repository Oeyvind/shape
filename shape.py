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


def run(n_classes=10, noise_std=.1):
    comm = cm.Communicator([ cm.READY_REP, cm.TRAIN_PUSH, cm.SYNTH_REQ,
                             cm.PLAY_REP, cm.LEARN_PULL, cm.MODEL_PULL ])

    processes = []
    processes.append(mp.Process(target=core.train, args=(n_classes,False,)))
    #processes.append(mp.Process(target=synth.interface.listen))

    # These processes will be the building blocks for the play/learn push sockets.
    # processes.append(mp.Process(target=ins.gesture))
    # processes.append(mp.Process(target=ins.learning_mode))
    # processes.append(mp.Process(target=ins.preferences))

    for p in processes:
        p.start()

    model = None

    for socket, msg in next(comm):
        if socket == cm.MODEL_PULL:
            print('Loading', msg)
            t0 = time.time()
            model = load_model(msg)
            print('Model loaded in', np.around(time.time()-t0, decimals=2), 'seconds')

        if socket == cm.LEARN_PULL:
            comm.TRAIN_PUSH_SEND(msg)

        if socket == cm.PLAY_REP:
            gesture_prediction, synth_prms_prediction = model.predict(msg[np.newaxis,:])
            comm.PLAY_REP_SEND([ gesture_prediction, synth_prms_prediction ])

    for p in processes:
        p.join()

    print('Shape exit')


if __name__ == "__main__":
    run()
