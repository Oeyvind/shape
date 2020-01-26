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

import ctcsound, sys, os
import numpy as np

# To train one gesture, instantiate the synth and synthesize audio frames with step_synth(),
# updating synthesis parameters and retrieveing analysis values for each step

class Synth:
    def __init__(self, duration, synthesis_parms):
        self.duration = duration
        self.synthesis_parms = synthesis_parms # numpy array with size 10 for the instr submono
        # settings
        instrument = 'submono' #'sine', 'submono', 'additive'

        #set up csound
        self.cs = ctcsound.Csound()
        self.cs.setOption('-o/shape/synth/test.wav')
        orcfile = open('/shape/synth/shape.orc', 'r')
        orc = orcfile.read()
        self.cs.compileOrc(orc)
        self.cs.readScore("f0 .1")
        self.cs.start()
        instruments = ['sine', 'submono', 'additive']
        synthinstr = instruments.index(instrument) + 20

        self.cs.inputMessage('''i{} 0 {}'''.format(synthinstr, duration))#run synth
        self.cs.inputMessage('''i{} 0 {}'''.format(30, duration))#run analyzer

        self.parmtable = int(self.cs.controlChannel("parmvalue_table")[0])
        self.analysistable = int(self.cs.controlChannel("analysis_table")[0])
        self.analysis_values = self.cs.table(self.analysistable) # read analysis parameters from here

    def set_synthesis_parms(self, synthesis_parms):
        self.synthesis_parms = synthesis_parms

    def get_analysis_values(self):
        return self.analysis_values

    def run_synth(self):
        # for testing: run synth with the specified duration and the specified parameters
        while True:
          self.cs.tableCopyIn(self.parmtable, self.synthesis_parms)
          result = self.cs.performKsmps()
          self.cs.tableCopyOut(self.analysistable, self.analysis_values)
          if result != 0:
            break
        print('synthesis parms:', self.synthesis_parms)
        print('analysis parms:', self.analysis_values)
        self.cs.cleanup()
        del self.cs

    def step_synth(self):
        # Use this method for training,
        # you can set the synthesis parameters in self.synthesis_parms
        # then call this method (step_synth()) to synthesize one frame of audio
        # the retrieve the analysis frame from self.analysis_parms
        # When this method return something else than zero, the synthesis process is finished and you should call cleanup()
        self.cs.tableCopyIn(self.parmtable, self.synthesis_parms)
        errcode = self.cs.performKsmps()
        self.cs.tableCopyOut(self.analysistable, self.analysis_values)
        return errcode

    def cleanup(self):
        self.cs.cleanup()
        del self.cs

if __name__ == '__main__':
    #test_parms = np.array([0.5,.2,0,0.9,0,0.1,0.1,0.7,0.2,0.2])
    test_parms = np.array([0.5,.2,1,0,0,0,0,0,0,0,0,0,0,0])
    print(test_parms)
    s = Synth(3, test_parms)
    #s.run_synth()
    errcode = 0
    while errcode == 0:
      errcode = s.step_synth()
    print('synthesis parms:', s.synthesis_parms)
    print('analysis parms:', s.analysis_values)
    s.cleanup()
