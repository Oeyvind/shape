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
Creates candidate for mapping of gestures to synth parameters. 
The trajectory is assumed to be in the range of [-1,1] on all axes.
"""

import random

import numpy as np

def scale_and_separate(trajectory):
    scaled = (trajectory + 1)/2

    return scaled.T

def create(trajectory, n_parameters):
    X,Y = scale_and_separate(trajectory)
    
    root = np.random.rand( 1, n_parameters )
    root = np.repeat(root, len(X), axis=0)

    for _param in root.T:
        _param += random.choice([X,Y])*np.random.rand()

    root = np.clip(root, 0, 1)

    return root
