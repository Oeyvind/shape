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

from core import core
import data.communicator as cm
import data.inputs as ins
import synth.interface

if __name__ == "__main__":

    
    
    comm = cm.Communicator([ cm.READY_REP, cm.DEATH_PUB, cm.GESTURE_PULL, cm.LEARNING_MODE_PULL,
                             cm.LEARN_PUSH, cm.PREFERENCES_REQ, cm.PREDICT_REQ, cm.SYNTH_REQ ])
                             
    output_dim = 10 # These should be input variables, or set during the system interface
    duration = 3
    
    processes = []
    processes.append(mp.Process(target=core.learn, args=(output_dim,)))
    processes.append(mp.Process(target=core.predict))
    processes.append(mp.Process(target=ins.gesture))
    processes.append(mp.Process(target=ins.learning_mode))
    processes.append(mp.Process(target=ins.preferences))
    processes.append(mp.Process(target=synth.interface.listen, args=(duration,)))

    for p in processes:
        p.start()

    cm.Waiter(comm, [ core.LEARN_READY, core.PREDICT_READY, ins.GESTURE_READY, ins.LEARNING_MODE_READY,
                      ins.PREFERENCES_READY, synth.interface.SYNTH_READY ])

    learning_mode = False

    for socket, msg in next(comm):

        if socket == cm.LEARNING_MODE_PULL:
            learning_mode = msg
            print('Learning mode:', learning_mode)

        if socket == cm.GESTURE_PULL:
            gesture = msg

            if learning_mode:
                print('Learning new gesture')
                comm.LEARN_PUSH_SEND(gesture)
                print('Creating new mapping for gesture')
                comm.PREDICT_REQ_SEND(gesture)
                gesture_prediction, gesture_embedding, synth_prms, audio_ftrs, signal = comm.PREDICT_REQ_RECV()

                
            else:
                print('Predicting based on gesture')
                comm.PREDICT_REQ_SEND(gesture)
                gesture_prediction, gesture_embedding, synth_prms, audio_ftrs, signal = comm.PREDICT_REQ_RECV()
        
    
    comm.kill()

    for p in processes:
        p.join()
    
