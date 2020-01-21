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

Handles gesture input, learning mode input and preferences input.
"""

import data.communicator as cm

GESTURE_READY = 'Gesture process ready'
LEARNING_MODE_READY = 'Learning mode process ready'
PREFERENCES_READY = 'Preferences process ready'

def gesture():
    comm = cm.Communicator([ cm.READY_REQ, cm.GESTURE_PUSH ])
    
    comm.READY_REQ_SEND(GESTURE_READY)
    comm.READY_REQ_RECV()

    print('Gesture process exit')

def learning_mode():
    comm = cm.Communicator([ cm.READY_REQ, cm.LEARNING_MODE_PUSH ])
    
    comm.READY_REQ_SEND(LEARNING_MODE_READY)
    comm.READY_REQ_RECV()

    print('Learning mode process exit')

def preferences():
    comm = cm.Communicator([ cm.READY_REQ, cm.PREFERENCES_REP ])
    
    comm.READY_REQ_SEND(PREFERENCES_READY)
    comm.READY_REQ_RECV()

    print('Preferences process exit')
