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

SYNTH_READY = 'Synth interface process ready'

def listen(duration):

    comm = cm.Communicator([ cm.SYNTH_REP ])#, cm.READY_REQ ])

    # comm.READY_REQ_SEND(SYNTH_READY)
    # comm.READY_REQ_RECV()

    for _, parameters in next(comm):
        
        # For now: load a new synth each time, until the Synth bugs are worked out.
        my_synth = Synth(duration, parameters)
        
        errcode = 0

        while errcode == 0:
            errcode = my_synth.step_synth()
            
        print('TERMINAL ERRCODE', errcode)
        
        comm.SYNTH_REP_SEND(my_synth.analysis_values)
        my_synth.cleanup()

    print('Synth interface process exit')
