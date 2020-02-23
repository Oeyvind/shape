#!/usr/bin/python
# -*- coding: latin-1 -*-
#
#    Copyright 2020 Oeyvind Brandtsegg and Axel Tidemann
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
OSC server test
"""
import OSC
import time, threading

receive_address = '127.0.0.1', 8902

s = OSC.OSCServer(receive_address) # basic
#s = OSC.ThreadingOSCServer(receive_address) # threading
#s = OSC.ForkingOSCServer(receive_address) # forking
s.addDefaultHandlers()

def data_handler(addr, tags, data, source):
    #print "control_handler", addr, tags, data, source
    value = data[0]
    if addr == "/myo-data":
        print(data)
    if addr == "/mouse":
        print(data)

s.addMsgHandler("/myo-data", data_handler)
s.addMsgHandler("/mouse", data_handler)

# just checking which handlers we have added
print "Registered Callback-functions are :"
for addr in s.getOSCAddressSpace():
    print addr

# Start OSCServer
print "\nStarting Myo OSCServer. Use ctrl-C to quit."
st = threading.Thread( target = s.serve_forever )
st.start()

try :
    while 1 :
        time.sleep(5)

except KeyboardInterrupt :
    print "\nClosing OSCServer."
    s.close()
    print "Waiting for Server-thread to finish"
    st.join()
    print "Done"
