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
Example gestures to be used for unit testing.
"""

import numpy as np
from scipy.special import expit

x = np.linspace(-.5, .5, 50)
y = np.zeros(50)
zero = np.c_[x, y]

theta = np.linspace(0, 2*np.pi, 20)
x = np.cos(theta)
y = np.sin(theta)
circle = np.c_[x,y]

x = np.linspace(-.7, .7, 30)
line = np.c_[x,x]

x = np.linspace(-.5, .8, 20)
r_line = np.c_[x, -x]

theta = np.linspace(0, 2*np.pi, 70)
y = np.sin(theta)
sine = np.c_[ np.linspace(-1, 1, 70), y ]

theta = np.linspace(0, 6*np.pi, 120)
y = np.sin(theta)
mega_sine = np.c_[ np.linspace(-1, 1, 120), y ]

theta = np.linspace(0, 10*np.pi, 150)
r = theta**2
x = r*np.cos(theta)
x = x/max(abs(x))
y = r*np.sin(theta)
y = y/max(abs(y))
spiral = np.c_[x,y]

y = np.tanh(np.linspace(-5, 5, 60))
tanh = np.c_[np.linspace(-1, 1, 60), y]

x = np.linspace(-1, 1, 40)
y = np.linspace(0, 1, 40)*np.random.random(40)
random = np.c_[x,y]

trajectories = [ zero, circle, line, r_line, sine, mega_sine, spiral, tanh, random ]
