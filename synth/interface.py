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

import numpy as np #remove

import data.communicator as cm
from synth.synth import Synth
from constants import GESTURE_SAMPLING_FREQUENCY

SYNTH_READY = 'Synth interface process ready'

def listen(sync=False):

    comm = cm.Communicator([ cm.SYNTH_REP , cm.READY_REQ ])

    if sync:
        comm.READY_REQ_SEND(SYNTH_READY)
        comm.READY_REQ_RECV()

    for _, parameters in next(comm):
        
        duration = parameters.shape[0]/GESTURE_SAMPLING_FREQUENCY
        # synthesis_parms = None since they are set explicitly below
        my_synth = Synth(duration, None)
        
        output_analysis = []
        
        for step_parameters in parameters:
            my_synth.set_synthesis_parms(step_parameters)
            errcode = my_synth.step_synth()
            output_analysis.append(my_synth.get_analysis_values())

        print('TERMINAL ERRCODE', errcode)
        
        output_analysis = np.stack(output_analysis)
        comm.SYNTH_REP_SEND([ my_synth.filename, output_analysis ])
        my_synth.cleanup()

    print('Synth interface process exit')
