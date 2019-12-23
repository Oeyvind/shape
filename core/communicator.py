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

import zmq

PREDICT = 7000
LEARN = 7001
FEEDBACK = 7002
MODEL = 7003
DEATH = 6666

DEATH_PUB = 'death_pub'
LEARN_PUSH = 'learn_push'
LEARN_PULL = 'learn_pull'
MODEL_PUSH = 'model_push'
MODEL_PULL = 'model_pull'
PREDICT_REP = 'predict_rep'
PREDICT_REQ = 'predict_req'

class Communicator:

    def __init__(self, required_sockets):
        context = zmq.Context()

        self.poller = zmq.Poller()
        
        # If you don't require the killer, you will be killed.
        if DEATH_PUB in required_sockets:
            self.death_pub = context.socket(zmq.PUB)
            self.death_pub.bind('tcp://*:{}'.format(DEATH))
        else:
            self.death_sub = context.socket(zmq.SUB)
            self.death_sub.connect('tcp://localhost:{}'.format(DEATH))
            self.death_sub.setsockopt(zmq.SUBSCRIBE, b'')
            self.poller.register(self.death_sub, zmq.POLLIN)

        if LEARN_PUSH in required_sockets:
            self.learn_push = context.socket(zmq.PUSH)
            self.learn_push.bind('tcp://*:{}'.format(LEARN))

        if LEARN_PULL in required_sockets:
            self.learn_pull = context.socket(zmq.PULL)
            self.learn_pull.connect('tcp://localhost:{}'.format(LEARN))
            self.poller.register(self.learn_pull, zmq.POLLIN)

        if MODEL_PUSH in required_sockets:
            self.model_push = context.socket(zmq.PUSH)
            self.model_push.bind('tcp://*:{}'.format(MODEL))

        if MODEL_PULL in required_sockets:
            self.model_pull = context.socket(zmq.PULL)
            self.model_pull.connect('tcp://localhost:{}'.format(MODEL))
            self.poller.register(self.model_pull, zmq.POLLIN)

        if PREDICT_REP in required_sockets:
            self.predict_rep = context.socket(zmq.REP)
            self.predict_rep.bind('tcp://*:{}'.format(PREDICT))
            self.poller.register(self.predict_rep, zmq.POLLIN)

        if PREDICT_REQ in required_sockets:
            self.predict_req = context.socket(zmq.REQ)
            self.predict_req.connect('tcp://localhost:{}'.format(PREDICT))

        self.required_sockets = required_sockets

        
    def kill(self):
        self.death_pub.send(b'')

        
    def __iter__(self):
        return self

    
    def __next__(self):
        while True:
            socks = dict(self.poller.poll())

            if not DEATH_PUB in self.required_sockets and socks.get(self.death_sub) == zmq.POLLIN:
                return

            if MODEL_PULL in self.required_sockets and socks.get(self.model_pull) == zmq.POLLIN:
                yield [ MODEL_PULL, self.model_pull.recv_pyobj() ]

            if PREDICT_REP in self.required_sockets and socks.get(self.predict_rep) == zmq.POLLIN:
                yield [ PREDICT_REP, self.predict_rep.recv_pyobj() ]

            if LEARN_PULL in self.required_sockets and socks.get(self.learn_pull) == zmq.POLLIN:
                yield [ LEARN_PULL, self.learn_pull.recv_pyobj() ]
