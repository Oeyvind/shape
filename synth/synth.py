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
Synth

Run Csound synthesizer
"""

import ctcsound, sys, os, re
import numpy as np
#sys.path.append(os.path.abspath('../core'))
#import faux_gestures as fg
# temporary hack to run locallyy before I can install cosund on docker
x = np.linspace(-.7, .7, 30)
line = np.c_[x,x]
theta = np.linspace(0, 2*np.pi, 70)
y = np.sin(theta)
sine = np.c_[ np.linspace(-1, 1, 70), y ]
gestures = [line, sine]

# settings
instrument = 'submono' #'sine' or submono'
num_sensors = 1
num_parms = 10

# test gestures
gesture_duration = 1 #just set to smth for now
#gestures = [fg.trajectories[2], fg.trajectories[4]]
gesture_names = ['line', 'sine']
gesture = gestures[0]
gesture_name = gesture_names[0]

# modify csound orc according to number of sensor inputs etc
newparms = '''; auto rewrite from Python
ginum_parms = {}
ginum_sensors = {}
; auto rewrite end'''.format(num_parms,num_sensors)

orcname = 'shape.orc'
f = open(orcname, 'r+')
text = f.read()
text = re.sub(r"(?s); auto rewrite from Python.*; auto rewrite end", newparms, text)
f.seek(0)
f.write(text)
f.truncate()
f.close()
    
#set up csound
cs = ctcsound.Csound()
cs.setOption('-o'+gesture_name+'.wav')
orcfile = open(orcname, 'r')
orc = orcfile.read()
cs.compileOrc(orc)
cs.start()
control_rate = cs.kr() # get from Csound
num_frames = int(control_rate*gesture_duration)
instruments = ['sine', 'submono', 'vst']
synthinstr = instruments.index(instrument) + 20
print(instrument)
print(synthinstr)
cs.inputMessage('''i{} 0 {}'''.format(synthinstr, gesture_duration))#run synth
gesture_index = 0
parmtable = int(cs.controlChannel("parmvalue_table")[0])
print(parmtable,len(gesture),len(gesture)/float(num_frames))
while (gesture_index < len(gesture)):
  data = gesture[int(gesture_index)]
  amp = 1
  value = (data[1]+1)*0.5 #normalize
  #print(value)
  cs.tableSet(parmtable, 0, amp)
  cs.tableSet(parmtable, 1, value)  
  cs.performKsmps() #synthesize one audio frame
  gesture_index += len(gesture)/float(num_frames)
cs.cleanup()
del cs
