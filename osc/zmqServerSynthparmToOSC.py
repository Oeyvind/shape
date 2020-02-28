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
ZMK server, receive synth parameters and send them over OSC to synth
"""

import sys
import zmq
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

#  Socket to get synth parms over ZMK
context = zmq.Context()
socket = context.socket(zmq.SUB)
print("Getting synthesis parameters")
socket.connect("tcp://localhost:8803")
socket.setsockopt_string(zmq.SUBSCRIBE, "synthparm")

# OSC client
send_port = 8903
osc_client = udp_client.SimpleUDPClient("127.0.0.1", send_port)  # OSC Client for sending messages.

def send_to_synth(parameters):
    print(parameters)
    osc_client.send_message("/shapesynth", parameters)

while True:
    data = socket.recv_string()
    parameters = data.split()[1:]
    for i in range(len(parameters)):
        parameters[i] = float(parameters[i])
    send_to_synth(parameters)
