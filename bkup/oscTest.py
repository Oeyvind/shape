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

import time
from pythonosc import udp_client

send_port = 8902
ip = "127.0.0.1"
osc_client = udp_client.SimpleUDPClient(ip, send_port)  # OSC Client for sending messages.

for i in range(100):
  data = (i/100.0, i/100.0)
  print("/mouse", data)
  osc_client.send_message("/mouse", data)
  time.sleep(1.0/25)
