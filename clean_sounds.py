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
Clear out the contents of the ./sounds folder
"""

import os
import glob

files = glob.glob('./sounds/*.wav')
files.extend(glob.glob('./sounds/*.png'))
files.extend(glob.glob('./sounds/*.html'))
files.extend(glob.glob('./sounds/*.reapeaks'))
for f in files:
    os.remove(f)
print('contents of /sounds now deleted')
