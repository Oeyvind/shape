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
Shape

Self-learning instrument. Take gestural input, learn how to map gestural sensor data (control channels) to synthesis parameters by evoling a modulation matrix.
Audio output is analyzed, and the modmatrix optimization function is to make the audio analysis have the same gestural shapes as the gesture sensor data.
When actual realtime sensor data is fed through the system, we assume that variations from the learned state will provide musical variation of the output.
"""


import ctcsound
import numpy as np
import re

num_sensors = 3
num_parms = 10

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

gesture_duration = 1 #just set to smth for now

#set up csound
cs = ctcsound.Csound()
cs.setOption('-n')
orcfile = open(orcname, 'r')
orc = orcfile.read()
cs.compileOrc(orc)
cs.start()
control_rate = cs.kr() # get from Csound
num_frames = int(control_rate*gesture_duration)

# names of the audio analysis vectors and the gesture (sensor) vectors
analysis_vect = ['amplitude', 'pitch', 'centroid', 'envelopecrest', 'spectralflatness', 'spectralcrest', 'spectralflux']
gesture_vect = ['x', 'y', 'z']

# test data, gestural shapes
ramp = np.array(range(num_frames))/float(num_frames)
t1=range((num_frames/2)+1)
t2=range(num_frames/2)
t2.reverse()
t1.extend(t2)
triangle = np.array(t1)/float(num_frames/2)
sine=np.sin(np.array(ramp)*np.pi*2)

gesture_data = np.zeros((num_frames,num_sensors))
# copy in test data
np.copyto(gesture_data[(np.arange(num_frames),0)], ramp)
np.copyto(gesture_data[(np.arange(num_frames),1)], sine)
np.copyto(gesture_data[(np.arange(num_frames),2)], triangle)

gesture_index = 0
audio_analysis = np.zeros((num_frames,(len(analysis_vect))))
while gesture_index<num_frames:
    dataframe = gesture_data[gesture_index]
    for i in range(len(gesture_vect)-1):
        cs.setControlChannel(gesture_vect[i],dataframe[i])
    cs.performKsmps() #synthesize one audio frame
    for i in range(len(analysis_vect)-1):
        audio_analysis[(gesture_index,i)] = cs.controlChannel(analysis_vect[i])[0]
    if gesture_index%100==0: 
        print gesture_index
    gesture_index += 1

def do_magic_thing(gesture_data, audio_analysis):
    #...optimize modulation matrix...
    modmatrixfile = open('modmatrix.txt', 'w')
    for i in range(num_parms*num_sensors):
        modmatrixfile.write('1.0, ')

do_magic_thing(gesture_data, audio_analysis)
