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

import threading
import data.communicator as cm
comm = cm.Communicator([cm.LEARNING_MODE_PUSH])
from data.inputs import REC, PLAY, CHILL, SAVE, LOAD
chill = 0

class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return

def my_callback(inp):
    if inp == ('r'):
        set_status(REC)
    elif inp == ('p'):
        set_status(PLAY)
    elif inp == ('c'):
        set_status(CHILL)
    elif inp == ('s'):
        set_status(SAVE)
    elif inp == ('l'):
        set_status(LOAD)
    else:
        print(inp, 'not in use')

def set_status(status):
    if status == CHILL:
        chill = True
    elif status == REC or status == PLAY:
        chill = False
    comm.LEARNING_MODE_PUSH_SEND(status)
    print("\nInput status:", status)

#start the Keyboard thread
kthread = KeyboardThread(my_callback)
