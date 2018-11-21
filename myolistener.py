# The MIT License (MIT)
#
# Copyright (c) 2017 Niklas Rosenstein
# Minor modification by Oeyvind Brandtsegg 2018, send data to OSC 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
"""
This example send Myo data to OSC.

Data is orientation, pose and RSSI as well as EMG data
if it is enabled and whether the device is locked or unlocked in the
terminal. Enable EMG streaming with double tap and disable it with finger spread.

"""

from __future__ import print_function
from myo.utils import TimeInterval
import myo, sys, OSC, threading, math



class Listener(myo.DeviceListener):

  def __init__(self):
    self.interval = TimeInterval(None, 0.05)
    self.orientation = None
    self.pose = myo.Pose.rest
    self.emg_enabled = False
    self.locked = False
    self.rssi = None
    self.emg = None
    send_address = '127.0.0.1', 9098
    print("Sending Myo data on {}".format(send_address))
    print("Ctrl+C to quit")
    self.client = OSC.OSCClient()
    self.client.connect(send_address)
    self.ypr = None
    self.orientstring = []

  def output(self):
    if not self.interval.check_and_reset():
      return

    self.orientstring = []
    parms = []
    if self.orientation:
      for q in self.orientation:
        parms.append(q)
        self.orientstring.append('{}{:.4f}'.format(' ' if q >= 0 else '', q))
      #mapping quaternions to normalized control values
      angles = self.toEulerAngle(parms)
      ypr = self.normalizeAndOffset(angles)
      self.ypr = ypr
      # send to OSC
      for i in range(len(ypr)):
        msg = OSC.OSCMessage() 
        msg.setAddress("/Myo/{}".format(i+1))
        msg.append(ypr[i]) 
        self.client.send(msg)
  
  def normalizeAndOffset(self, angles):
     # get yaw, pitch, roll of 0.5, 0.5, 0.5 when your arm is pointing straight in front of you
     # yaw increase to the right
     # pitch increase up
     # roll increase clockwise
     y,p,r = angles
     y = 1-((y/(2*math.pi)+0.5))
     p = 1-(p/(2*math.pi)+0.5) #
     r = ((r/(2*math.pi)+1.0)%1.0)
     return y,p,r
    
  def toEulerAngle(self, quats):
    """ Quaternion to Euler angle conversion borrowed from wikipedia.
        https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles """
    w,x,y,z = quats
    # roll (x-axis rotation)
    sinr = +2.0 * (w * x + y * z)
    cosr = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr, cosr)
    # pitch (y-axis rotation)
    sinp = +2.0 * (w * y - z * x)
    if (math.fabs(sinp) >= 1):
      pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
    else:
      pitch = math.asin(sinp)
    # yaw (z-axis rotation)
    siny = +2.0 * (w * z + x * y)
    cosy = +1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny, cosy)
    return roll, pitch, yaw

  def on_connected(self, event):
    event.device.request_rssi()

  def on_rssi(self, event):
    self.rssi = event.rssi
    self.output()

  def on_pose(self, event):
    self.pose = event.pose
    if self.pose == myo.Pose.double_tap:
      event.device.stream_emg(True)
      self.emg_enabled = True
    elif self.pose == myo.Pose.fingers_spread:
      event.device.stream_emg(False)
      self.emg_enabled = False
      self.emg = None
    self.output()

  def on_orientation(self, event):
    self.orientation = event.orientation
    self.output()

  def on_emg(self, event):
    self.emg = event.emg
    self.output()

  def on_unlocked(self, event):
    self.locked = False
    self.output()

  def on_locked(self, event):
    self.locked = True
    self.output()




if __name__ == '__main__':
  # Start Myo listener
  myo.init('../Myo/myo-sdk-win-0.9.0/bin/myo64.dll')
  hub = myo.Hub()
  listener = Listener()
  while hub.run(listener.on_event, 500):
    #print('Q:'+str(listener.orientstring))
    #print('YPR:'+str(listener.ypr))
    pass
