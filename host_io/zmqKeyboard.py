#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright 2020 Oeyvind Brandtsegg and Axel Tidemann
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
Keyboard control of record enable via ZMK
"""

from pynput import keyboard
import data.communicator as cm
comm = cm.Communicator([cm.LEARNING_MODE_PUSH])
from data.inputs import REC, PLAY, CHILL

def on_press(key):
    try:
        if key.char == ('r'):
            set_status(REC)
        if key.char == ('p'):
            set_status(PLAY)
        if key.char == ('c'):
            set_status(CHILL)
    except AttributeError:
        print('Key not used {0}'.format(key))

def on_release(key):
    pass

def set_status(status):
    comm.LEARNING_MODE_PUSH_SEND(status)
    print("\nInput status:", status)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
