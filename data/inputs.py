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
shape:io

Handles gesture input and learning mode input.
"""

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import data.communicator as cm
from core.candidate import create, scale_and_separate
from utils.constants import ADDITIVE, PROJECT_ROOT, HISTORY_LENGTH

REC = 'record'
PLAY = 'play'
CHILL = 'chill'

GESTURE_READY = 'Gesture process ready'
LEARNING_MODE_READY = 'Learning mode process ready'
PREFERENCES_READY = 'Preferences process ready'

def run(examples=10, select_lowest_mse=False):
    comm = cm.Communicator([ cm.SENSOR_PULL, cm.LEARNING_MODE_PULL,
                             cm.LEARN_REQ, cm.PLAY_REQ, cm.SYNTH_REQ,
                             cm.SYNTH_PLAY_PUSH ])
    
    status = CHILL
    recorder = []
    
    for socket, msg in next(comm):
        if socket == cm.SENSOR_PULL:
            if status == CHILL:
                continue
            
            recorder.append(msg)
            
            if status == PLAY:
                gesture = np.stack(recorder)
                gesture = gesture[-HISTORY_LENGTH:]
                print('Send to play', gesture.shape)

                comm.PLAY_REQ_SEND(gesture)
                response = comm.PLAY_REQ_RECV()

                if response is not None:
                    gesture_prediction, synth_prms_prediction = response
                    print('Predicted gesture:', np.argmax(gesture_prediction))

                    comm.SYNTH_PLAY_PUSH_SEND(synth_prms_prediction)

        if socket == cm.LEARNING_MODE_PULL:
            if len(recorder) and status == REC and msg in [PLAY, CHILL]:
                print('Recorded {} samples, making suggestions'.format(len(recorder)))
                gesture = np.stack(recorder)

                X,Y = scale_and_separate(gesture)

                plt.plot(X,Y)
                plt.xlim(-.1, 1.1)
                plt.ylim(-.1, 1.1)
                gesture_plot = '{}/sounds/_{}.png'.format(PROJECT_ROOT, ADDITIVE.name)
                plt.savefig(gesture_plot, dpi=300)
                plt.clf()
                
                parameters = [ create(gesture, ADDITIVE.n_parameters) for _ in
                               range(examples) ]

                comm.SYNTH_REQ_SEND([ parameters, ADDITIVE.name, X, Y, True ])

                sounds = comm.SYNTH_REQ_RECV()
                filenames, similarities = zip(*sounds)
                sounds = list(zip(filenames, similarities, parameters))

                sounds = sorted(sounds, key=lambda L: L[1])

                title = ADDITIVE.name
                html = ('<html><title>{}</title><body><h1>{}</h1>'
                        '<img src="_{}.png" width="50%">'
                        '<hr>').format(title, title, ADDITIVE.name)

                for i, (filename, similarity, _) in enumerate(sounds):
                    html += ('<table><tr><td><b>Candidate {}<br>'
                             'Similarity: {} </b><br><br> <audio controls>'
                             '<source src="{}" type="audio/wav"> </audio></td>'
                             '<td><img src="{}.png" width="60%"> </td></tr></table>'
                             '<hr>').format(i, similarity, filename, filename)

                html += '</body></html>'

                html_file = '{}/sounds/{}.html'.format(PROJECT_ROOT, ADDITIVE.name)
                with open(html_file, 'w') as out_file:
                    out_file.write(html)

                if not select_lowest_mse:
                    q ='Open {} and select your favourite:'.format(html_file)
                    favourite = int(input(q))
                else:
                    favourite = 0

                if favourite > -1:
                    print('You chose {}, similarity {}.'.format(favourite,
                                                                sounds[favourite][1]))

                    synth_parameters = sounds[favourite][2]

                    comm.LEARN_REQ_SEND([ gesture, synth_parameters ])
                    comm.LEARN_REQ_RECV()
                else:
                    print('None selected, continue.')

            status = msg
            print('STATUS:', status)

            recorder = []


if __name__ == '__main__':
    run()
