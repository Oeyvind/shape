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
shape:synth �MQ wrapper
"""

from functools import partial
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error as mse
import matplotlib._color_data as mcd

import data.communicator as cm
from synth.synth import Synth
from utils.constants import GESTURE_SAMPLING_FREQUENCY

SYNTH_READY = 'Synth interface process ready'
colors = list(mcd.XKCD_COLORS.values())

def play_and_analyze(parameters, instrument_name, gesture, plot):

    duration = len(parameters)/GESTURE_SAMPLING_FREQUENCY
    my_synth = Synth(duration, instrument_name, None, GESTURE_SAMPLING_FREQUENCY)

    output_analysis = []

    for step_parameters in parameters:
        my_synth.set_synthesis_parms(step_parameters)
        errcode = my_synth.step_synth()
        output_analysis.append(my_synth.get_analysis_values())

    output_analysis = np.stack(output_analysis)
    my_synth.cleanup()

    if plot:
        x = np.arange(len(parameters))

        gesture_plot_height = int(np.ceil(gesture.shape[1]/2))
        total_plot_height = int(gesture_plot_height + 4)

        # Find the most similar
        simils = []
        for g_axis in gesture.T:
            simils.append([ mse(g_axis, feature) for feature in output_analysis.T ])

        most_simil = [ np.argmin(s) for s in simils ]

        # Plot gesture
        iv, jv = np.meshgrid(np.arange(gesture_plot_height), np.arange(2), indexing='ij')
        plot_coords = list(zip(np.ndarray.flatten(iv), np.ndarray.flatten(jv)))

        plot_shape = (total_plot_height, 2)

        for k, g_axis in enumerate(gesture.T):
            ax = plt.subplot2grid(plot_shape, plot_coords[k])
            ax.plot(x, g_axis, label='gesture axis {}'.format(k), color=colors[k])
            ax.legend(loc='upper right')
            ax.set_ylim(0,1)

        # Plot audio features
        iv, jv = np.meshgrid(np.arange(gesture_plot_height, total_plot_height),
                             np.arange(2), indexing='ij')
        plot_coords = list(zip(np.ndarray.flatten(iv), np.ndarray.flatten(jv)))

        for k, feature in enumerate(output_analysis.T):
            color = 'b'
            if k in most_simil:
                if most_simil.count(k) > 1:
                    color = 'k'
                else:
                    color = colors[most_simil.index(k)]

            audio_features = ['amp', 'env_crest', 'pitch', 'centroid',
                              'flatness', 's_crest', 'flux', 'mfcc_diff']

            ax = plt.subplot2grid(plot_shape, plot_coords[k])
            ax.plot(x, feature, color=color, label=audio_features[k])
            ax.legend(loc='upper right')
            ax.set_ylim(0,1)


        similarity = np.sum([ min(s) for s in simils ])
        plt.savefig('/shape/sounds/{}.png'.format(my_synth.filename), dpi=300)
        plt.close()

    return (my_synth.filename, similarity)

def listen(sync=False):

    comm = cm.Communicator([ cm.SYNTH_REP, cm.READY_REQ ])

    if sync:
        comm.READY_REQ_SEND(SYNTH_READY)
        comm.READY_REQ_RECV()

    pool = mp.Pool()
    for _, (parameters, instrument_name, gesture, plot) in next(comm):
        func = partial(play_and_analyze, instrument_name=instrument_name,
                       gesture=gesture, plot=plot)
        outputs = pool.map(func, parameters)
        comm.SYNTH_REP_SEND(outputs)

    print('Synth interface process exit')
