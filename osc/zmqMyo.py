#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright 2020 Oeyvind Brandtsegg and Axel Tidemann
#    Based on myo_to_osc by Charles Martin
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
Myo-to-ZMQ
Connects to a Myo, then sends EMG and IMU data as ZMQ messages to SHAPE
"""
from myo import *
import argparse
import math
import sys
import time
import osc.zmqKeyboard as kbd # keyboard control of record enable/disable
import data.communicator as cm
comm = cm.Communicator([cm.SENSOR_PUB])


parser = argparse.ArgumentParser(description='Connects to a Myo, then sends EMG and IMU data as OSC messages to localhost:3000.')
parser.add_argument('-l', '--log', dest='logging', action="store_true", help='Save Myo data to a log file.')
parser.add_argument('-d', '--discover', dest='discover', action='store_true', help='Search for available Myos and print their names and MAC addresses.')
parser.add_argument('-a', '--address', dest='address', help='A Myo MAC address to connect to, in format "XX:XX:XX:XX:XX:XX".')
args = parser.parse_args()

myodata = {'ori':[], 'acc':[],'gyro':[],'rpy':[],'emg':[]}

def vector_3d_magnitude(x, y, z):
    """Calculate the magnitude of a 3d vector"""
    return math.sqrt((x * x) + (y * y) + (z * z))

def toEulerAngle(w, x, y, z):
    """ Quaternion to Euler angle conversion borrowed from wikipedia.
        https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles """
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

def proc_imu(quat, acc, gyro):
    myodata['ori'] = quat
    myodata['acc'] = acc
    myodata['gyr'] = gyro
    roll, pitch, yaw = toEulerAngle(quat[0], quat[1], quat[2], quat[3])
    myodata['rpy'] = [roll / math.pi, pitch / math.pi, yaw / math.pi]

def proc_emg(emg_data):
    proc_emg = tuple(map(lambda x: x / 127.0, emg_data))  # scale EMG to be in [-1, 1]
    myodata['emg'] = proc_emg

def proc_battery(battery_level):
    # print("Battery", battery_level, end='\r')
    osc_client.send_message("/battery", battery_level)

if args.address is not None:
    print("Attempting to connect to Myo:", args.address)
else:
    print("No Myo address provided.")

# Setup Myo Connection
m = Myo()  # scan for USB bluetooth adapter and start the serial connection automatically
# m = Myo(tty="/dev/tty.usbmodem1")  # MacOS
# m = Myo(tty="/dev/ttyACM0")  # Linux
m.add_emg_handler(proc_emg)
m.add_imu_handler(proc_imu)
m.add_battery_handler(proc_battery)

m.connect(address=args.address)  # connects to specific Myo unless arg.address is none.
# Setup Myo mode, buzzes when ready.
m.sleep_mode(Sleep_Mode.never_sleep.value)
# EMG and IMU are enabled, classifier is disabled (thus, no sync gestures required, less annoying buzzing).
m.set_mode(EMG_Mode.send_emg.value, IMU_Mode.send_data.value, Classifier_Mode.disabled.value)
# Buzz to show Myo is ready.
m.vibrate(1)

def run_loop():
    m.run()
    '''
    global myodata
    rpy = myodata['rpy'] #get roll/pitch/yaw
    print('\r'+rpy,end='')
    #comm.SENSOR_PUB_SEND(rpy)
    time.sleep(1.0/25)
    '''

print("Now running...")
try:
    while True:
        run_loop()
except KeyboardInterrupt:
    pass
finally:
    m.disconnect()
    print("\nDisconnected")
