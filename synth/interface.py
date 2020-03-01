#!/usr/bin/python
# -*- coding: latin-1 -*-
#
#    Copyright 2018 Oeyvind Brandtsegg and Axel Tidemann
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
shape:synth ØMQ wrapper
"""

from functools import partial
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error as mse

import data.communicator as cm
from synth.synth import Synth
from utils.constants import GESTURE_SAMPLING_FREQUENCY

SYNTH_READY = 'Synth interface process ready'

def play_and_analyze(parameters, instrument, X, Y, plot):
    
    duration = parameters.shape[0]/GESTURE_SAMPLING_FREQUENCY
    my_synth = Synth(duration, instrument, None, GESTURE_SAMPLING_FREQUENCY)
        
    output_analysis = []

    for step_parameters in parameters:
        my_synth.set_synthesis_parms(step_parameters)
        errcode = my_synth.step_synth()
        output_analysis.append(my_synth.get_analysis_values())

    output_analysis = np.stack(output_analysis)
    my_synth.cleanup()

    if plot:
        x = np.arange(len(X))

        fig, axs = plt.subplots(5, 2, sharex=True, sharey=True)

        # Find the most similar
        X_sim = [ mse(X, feature) for feature in output_analysis.T ]
        Y_sim = [ mse(Y, feature) for feature in output_analysis.T ]

        X_most_similar = np.argmin(X_sim)
        Y_most_similar = np.argmin(Y_sim)

        X_color = 'r'
        Y_color = 'g'
        axs[0,0].plot(x, X, label='gesture X', color=X_color)
        axs[0,0].legend(loc='upper right')
        axs[0,1].plot(x, Y, label='gesture Y', color=Y_color)
        axs[0,1].legend(loc='upper right')

        iv, jv = np.meshgrid(np.arange(1,5), np.arange(2), indexing='ij')
        plot_coords = list(zip(np.ndarray.flatten(iv), np.ndarray.flatten(jv)))

        for k, feature in enumerate(output_analysis.T):
            color = 'b'
            if k == X_most_similar:
                color = X_color
            if k == Y_most_similar:
                color = Y_color
            if k == X_most_similar == Y_most_similar:
                color = 'm'

            i,j = plot_coords[k]
            audio_features = ['amp', 'env_crest', 'pitch', 'centroid',
                              'flatness', 's_crest', 'flux', 'mfcc_diff']
            axs[i,j].plot(x, feature, color=color, label=audio_features[k])
            axs[i,j].legend(loc='upper right')
            axs[i,j].set_ylim(0,1)

        similarity = np.min(X_sim) + np.min(Y_sim)
        plt.savefig('/shape/sounds/{}.png'.format(my_synth.filename), dpi=300)
        plt.close()

    return (my_synth.filename, similarity)

def listen(sync=False):

    comm = cm.Communicator([ cm.SYNTH_REP, cm.READY_REQ ])

    if sync:
        comm.READY_REQ_SEND(SYNTH_READY)
        comm.READY_REQ_RECV()

    pool = mp.Pool()
    for _, (parameters, instrument, X, Y, plot) in next(comm):
        func = partial(play_and_analyze, instrument=instrument, X=X, Y=Y, plot=plot)
        outputs = pool.map(func, parameters)
        comm.SYNTH_REP_SEND(outputs)

    print('Synth interface process exit')
