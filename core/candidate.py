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
Trajectory is assumed to be in the range of [0,1]. The output will 
be clipped to this range anyway.
"""

import random

import numpy as np

def scale_and_separate(trajectory):
    assert False, 'This function should not be used. Inputs are supposed to be [0,1]'
    scaled = (trajectory + 1)/2

    return scaled.T

def create(trajectory, n_parameters):
    root = np.random.rand( 1, n_parameters )
    root = np.repeat(root, len(trajectory), axis=0)

    for _param in root.T:
        _param += random.choice(trajectory.T)*np.random.rand()

    root = np.clip(root, 0, 1)

    return root
