#!/usr/bin/python
# -*- coding: latin-1 -*-
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
ØMK client test with mouse/trackpad
"""

import zmq
from random import randrange
import time
from pynput.mouse import Button, Controller

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:8802")

mouse = Controller()

while True:
  msg = "mouse "
  msg += str(mouse.position[0]*(1/2000.0)) + " " # normalize mouse data and send
  msg += str(mouse.position[1]*(1/1000.0)) # normalize mouse data and send
  print(msg)
  socket.send_string(msg)
  #time.sleep(1.0/25)
