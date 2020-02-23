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
OSC client test with mouse/trackpad
"""

import OSC
import time
from pynput.mouse import Button, Controller

send_address = '127.0.0.1', 8902

client = OSC.OSCClient()
client.connect(send_address)

mouse = Controller()
while True:
  msg = OSC.OSCMessage()
  msg.setAddress("/mouse")
  msg.append(mouse.position)
  client.send(msg)
  time.sleep(1.0/25)

print("done")
