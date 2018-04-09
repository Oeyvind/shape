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

#set up csound
cs = ctcsound.Csound()
cs.setOption('-n')
orcfile = open('shape.orc', 'r')
orc = orcfile.read()
cs.compileOrc(orc)
cs.start()


gesture_duration = 1 #just set to smth for now
control_rate = cs.kr() # get from Csound
num_frames = int(control_rate*gesture_duration)
num_sensors = 3
cs.setControlChannel("num_modulators",num_sensors)
num_parms = cs.controlChannel("num_parms")[0]

# test data, gestural shapes
ramp = np.array(range(num_frames))/float(num_frames)
t1=range((num_frames/2)+1)
t2=range(num_frames/2)
t2.reverse()
t1.extend(t2)
triangle = np.array(t1)/float(num_frames/2)
sine=np.sin(np.array(ramp)*np.pi*2)

# names of the audio analysis vectors and the gesture (sensor) vectors
analysis_vect = ['amplitude', 'pitch', 'centroid', 'envelopecrest', 'spectralflatness', 'spectralcrest', 'spectralflux']
gesture_vect = ['x', 'y', 'z']

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
