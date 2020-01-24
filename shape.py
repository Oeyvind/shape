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

def run(n_classes=10, synth_prms_dim=10, audio_ftrs_dim=8, duration=3, noise_std=.1):

    comm = cm.Communicator([ cm.READY_REP, cm.TRAIN_PUSH, cm.PREFERENCES_REQ, cm.SYNTH_REQ,
                             cm.PLAY_PULL, cm.LEARN_PULL, cm.MODEL_PULL ])

    processes = []
    processes.append(mp.Process(target=core.train, args=(n_classes, synth_prms_dim, audio_ftrs_dim,)))
    processes.append(mp.Process(target=synth.interface.listen, args=(duration,)))
    
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

        else:
            print('Mapping gesture to synth parameters')

            x_gesture = msg

            if model is None:
                y_synth_prms = np.random.rand(synth_prms_dim)
            else:
                _, y_synth_prms, _ = model.predict(x_gesture[np.newaxis,:])
                y_synth_prms = np.squeeze(y_synth_prms)

            happy = False
            while not happy:
                y_synth_prms = np.clip(y_synth_prms, 0, 1)

                print('Creating audio')
                comm.SYNTH_REQ_SEND(y_synth_prms)
                y_audio_ftrs = comm.SYNTH_REQ_RECV()

                if socket == cm.PLAY_PULL:
                    happy = True

                if socket == cm.LEARN_PULL:

                    print('Asking user')
                    comm.PREFERENCES_REQ_SEND('Happy with the sound?')
                    happy = comm.PREFERENCES_REQ_RECV()

                    print('User happy?', happy)

                    # Add noise to the synth parameters
                    y_synth_prms += np.random.normal(0, noise_std, size=y_synth_prms.shape)

            if socket == cm.LEARN_PULL:
                comm.TRAIN_PUSH_SEND([ x_gesture, y_synth_prms, y_audio_ftrs ])

    
    for p in processes:
        p.join()

    print('Shape exit')
    

if __name__ == "__main__":
    run()
