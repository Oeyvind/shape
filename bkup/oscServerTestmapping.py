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
OSC server test,
with mockup mapping of gesture to synthesis parameters,
then send synthesis parms over OSC
"""
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import time
import numpy as np

ip = "127.0.0.1"
receive_port = 8902
send_port = 8903
osc_client = udp_client.SimpleUDPClient(ip, send_port)  # OSC Client for sending messages.


num_inputs = 2 # gesture sensing dimensions
input = np.zeros(num_inputs)
num_outputs = 25 # synthesis parameters
output = np.zeros(num_outputs)
xmap = np.random.uniform(0,1,num_outputs) # mock-up mapping of input 1 to all output parms
ymap = np.random.uniform(0,1,num_outputs) # mock-up mapping of input 2 to all output parms

def mapping(indata):
    global xmap, ymap
    return ((indata[0]*xmap)+(indata[1]*ymap))*np.sqrt(0.5) # replacement for smart mapping

def send_to_synth(parameters):
    print(parameters)
    osc_client.send_message("/shapesynth", parameters)

def data_handler(addr, *args):
    #print "control_handler", addr, tags, data, source
    if addr == "/mouse":
        output = mapping(np.asarray(args))
        send_to_synth(output)

def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

dispatcher = Dispatcher()
dispatcher.map("/mouse", data_handler)
dispatcher.set_default_handler(default_handler)

server = osc_server.ThreadingOSCUDPServer((ip, receive_port), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()  # Blocks forever
