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
ØMQ server test,
with mockup mapping of gesture to synthesis parameters,
then send synthesis parms back.
"""
import time
import numpy as np
import zmq

#  Socket to talk to server
context = zmq.Context()
recv_socket = context.socket(zmq.SUB)
recv_socket.connect("tcp://localhost:8802")
print("Getting data from mouse server")
recv_socket.setsockopt_string(zmq.SUBSCRIBE, "mouse")

#  Socket to talk back
send_socket = context.socket(zmq.PUB)
send_socket.bind("tcp://*:8803")


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
    msg = "synthparms "
    for p in parameters:
        msg += str(p) + " "
    print(msg)
    send_socket.send_string(msg)

def data_handler(addr, *args):
    #print "control_handler", addr, tags, data, source
    if addr == "/mouse":
        output = mapping(np.asarray(args))
        send_to_synth(output)

def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

while True:
    data = recv_socket.recv_string()
    address, x, y = data.split()
    if address == "mouse":
        send_to_synth(mapping([float(x),float(y)]))
    else:
        print(data)
