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
Mouse gesture send over ZMK
"""

import time
from pynput.mouse import Button, Controller
import host_io.zmqKeyboard as kbd # keyboard control of record enable/disable
import data.communicator as cm
comm = cm.Communicator([cm.SENSOR_PUSH])
from utils.constants import GESTURE_SAMPLING_FREQUENCY

mouse = Controller()
index = 0
while True:
    msg = [mouse.position[0]*(1/2000.0), mouse.position[1]*(1/1000.0)] # normalize mouse data and send
    print('\r'+str(msg),end='')
    comm.SENSOR_PUSH_SEND(msg)
    time.sleep(1.0/GESTURE_SAMPLING_FREQUENCY)
