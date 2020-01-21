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
Sets up all available sockets. Legibility of code gained by forcing careful 
selection of required ports - errors will be thrown if you instantiate several bind
ports, for instance. So you will know if you messed up.
"""

import sys

import zmq

pub_sub = ['PUB', 'SUB']
req_rep = ['REQ', 'REP']
push_pull = ['PUSH', 'PULL']

# All that is needed is to define name, port and socket type, and the module
# will dynamically create function handles and do all the necessary registering.
ports = {
    'PREDICT': (7000, req_rep),
    'LEARN': (7001, req_rep),
    'PREFERENCES': (7002, req_rep),
    'MODEL': (7003, push_pull),
    'READY': (7004, req_rep),
    'GESTURE': (7005, push_pull),
    'LEARNING_MODE': (7006, push_pull),
    'SYNTH': (7007, req_rep),
    'DEATH': (6666, pub_sub) }

# Enables LEARN_PUSH_SEND, LEARN_PUSH_RECV, SYNTH_REQ, SYNTH_REP, etc.
module = sys.modules[__name__]
for name, (_, socket_types) in ports.items():
    for soc_typ in socket_types:
        module_variable = '{}_{}'.format(name, soc_typ)
        value = '{} {}'.format(name, soc_typ)
        setattr(module, module_variable, value)

        
class Communicator:
    
    def __init__(self, required_sockets):
        self.context = zmq.Context()
        self.poller = zmq.Poller()

        self.sockets = {}
                                   
        if not DEATH_PUB in required_sockets:
            required_sockets.append(DEATH_SUB)

        for req_soc in required_sockets:
            name, socket_type = req_soc.split()
            port, _ = ports[name]
            getattr(self, socket_type)(req_soc, port)
            
            # Automatic function handles for sending and receiving over a socket
            setattr(self, '{}_{}_SEND'.format(name, socket_type), self.sockets[req_soc].send_pyobj)
            setattr(self, '{}_{}_RECV'.format(name, socket_type), self.sockets[req_soc].recv_pyobj)

        self.required_sockets = required_sockets

        
    def PUSH(self, soc, port):
        self.sockets[soc] = self.context.socket(zmq.PUSH)
        self.sockets[soc].bind('tcp://*:{}'.format(port))

        
    def PULL(self, soc, port):
        self.sockets[soc] = self.context.socket(zmq.PULL)
        self.sockets[soc].connect('tcp://localhost:{}'.format(port))
        self.poller.register(self.sockets[soc], zmq.POLLIN)

        
    def REQ(self, soc, port):
        self.sockets[soc] = self.context.socket(zmq.REQ)
        self.sockets[soc].connect('tcp://localhost:{}'.format(port))

        
    def REP(self, soc, port):
        self.sockets[soc] = self.context.socket(zmq.REP)
        self.sockets[soc].bind('tcp://*:{}'.format(port))
        self.poller.register(self.sockets[soc], zmq.POLLIN)

        
    def PUB(self, soc, port):
        self.sockets[soc] = self.context.socket(zmq.PUB)
        self.sockets[soc].bind('tcp://*:{}'.format(port))

        
    def SUB(self, soc, port):
        self.sockets[soc] = self.context.socket(zmq.SUB)
        self.sockets[soc].connect('tcp://localhost:{}'.format(port))
        self.sockets[soc].setsockopt(zmq.SUBSCRIBE, b'')
        self.poller.register(self.sockets[soc], zmq.POLLIN)
        
        
    def kill(self):
        self.sockets[DEATH_PUB].send(b'')

        
    def __iter__(self):
        return self

    
    def __next__(self):
        while True:
            polled_sockets = dict(self.poller.poll())

            if DEATH_SUB in self.required_sockets and polled_sockets.get(self.sockets[DEATH_SUB]) == zmq.POLLIN:
                return
            
            for name, soc in self.sockets.items():
                if soc in polled_sockets and polled_sockets.get(soc) == zmq.POLLIN:
                    yield [ name, soc.recv_pyobj() ]
            

class Waiter:
    def __init__(self, comm, wait_on):
        
        for _, ready_process in next(comm):
            print(ready_process)
            wait_on.remove(ready_process)
            comm.READY_REP_SEND(None) # Dummy reply

            if len(wait_on) == 0:
                break
