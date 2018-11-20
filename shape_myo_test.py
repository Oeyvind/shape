#!/usr/bin/python
# -*- coding: latin-1 -*-
# 
#    Copyright 2018 Oeyvind Brandtsegg and Axel Tidemann
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
Shape Myo test

Simple setup for using the Myo armband to control some synthesis parameters.

"""


import ctcsound, re
import numpy as np
import myolistener as m
myopath = '../Myo/myo-sdk-win-0.9.0/bin/myo64.dll'
m.myo.init(myopath)
myohub = m.myo.Hub()
myolistener = m.Listener()

# settings
instrument = 'submono' #'sine' or submono'
num_sensors = 3
num_parms = 10
csdur = 86400 # run duration in seconds

orcname = 'shape.orc'
f = open(orcname, 'r+')
text = f.read()
newparms = '''; auto rewrite from Python
ginum_parms = {}
ginum_sensors = {}
; auto rewrite end'''.format(num_parms,num_sensors)
text = re.sub(r"(?s); auto rewrite from Python.*; auto rewrite end", newparms, text)
f.seek(0)
f.write(text)
f.truncate()
f.close()
        
#set up csound
cs = ctcsound.Csound()
cs.setOption('-odac')
orcfile = open(orcname, 'r')
orc = orcfile.read()
cs.compileOrc(orc)
cs.start()
control_rate = cs.kr() # get from Csound
cs.inputMessage("i5 0  {}".format(csdur))#read sensor data, write to modmatrix
cs.inputMessage("i10 0 {}".format(csdur))#run modmatrix
instruments = ['sine', 'submono', 'vst']
synthinstr = instruments.index(instrument) + 20
print instrument
print synthinstr
cs.inputMessage('''i{} 0 {}'''.format(synthinstr, csdur))#run synth


#while myohub.run(myolistener.on_event, 500):
#    if myolistener.orientation:
while True:
        #cs.setControlChannel('myo1', myolistener.parms[0])
        #cs.setControlChannel('myo2', myolistener.parms[1])
        #cs.setControlChannel('myo3', myolistener.parms[2])
        cs.performKsmps() #synthesize one audio frame
