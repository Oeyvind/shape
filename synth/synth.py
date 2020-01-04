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

class Synth:
    def __init__(self, duration, synthesis_parms):
        self.duration = duration
        self.synthesis_parms = synthesis_parms # numpy array with size 10 for the instr submono
        # settings
        instrument = 'submono' #'sine' or submono'

        #set up csound
        self.cs = ctcsound.Csound()
        self.cs.setOption('-otest.wav')
        orcfile = open('shape.orc', 'r')
        orc = orcfile.read()
        self.cs.compileOrc(orc)
        self.cs.readScore("f0 .1")
        self.cs.start()
        instruments = ['sine', 'submono']
        synthinstr = instruments.index(instrument) + 20
        self.cs.inputMessage('''i{} 0 {}'''.format(synthinstr, duration))#run synth
        self.cs.inputMessage('''i{} 0 {}'''.format(30, duration))#run analyzer

        self.parmtable = int(self.cs.controlChannel("parmvalue_table")[0])
        self.analysistable = int(self.cs.controlChannel("analysis_table")[0])
        self.analysis_parms = self.cs.table(self.analysistable) # read analysis parameters from here

    def run_synth(self):
        while True:
          self.cs.tableCopyIn(self.parmtable, self.synthesis_parms)
          result = self.cs.performKsmps()
          self.cs.tableCopyOut(self.analysistable, self.analysis_parms)
          if result != 0:
            break
        print('synthesis parms:', self.synthesis_parms)
        print('analysis parms:', self.analysis_parms)
        self.cs.cleanup()
        del self.cs

if __name__ == '__main__':
    test_parms = np.array([0.5,.2,0,0.9,0,0.1,0.1,0.7,0.2,0.2])
    print(test_parms)
    s = Synth(3, test_parms)
    s.run_synth()