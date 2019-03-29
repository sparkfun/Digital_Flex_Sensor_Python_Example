#! /usr/bin/env python3
"""
This script reads info from a 2-Axis, 4in BendLabs Digital Flex Sensor Found here

https://www.sparkfun.com/products/15245

The script modles the data using matplotlib to show a simple 3d graphic

Requirements:
- pyserial
- matplotlib
- numpy
"""

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import serial
import serial.tools.list_ports as list_ports
import threading
import time


__author__ = 'Cameron Lemmon'
__copyright__ = 'Copyright 2019, SparkFun Electronics'
__license__ = 'MIT'
__version__ = '0.0.1'
__maintainer__ = 'Cameron Lemmon'


# Attaching 3D axis to the frigure
fig = plt.figure()
ax = p3.Axes3D(fig)

# Grab the COM port for our serial device
devices = list_ports.comports()
port = None
for dev in devices:
    # The SparkFun BlackBoard has CH340 in the description
    # So, I'm using that to find the right device
    if 'CH340' in dev.description:
        port = dev.device
        break
else:
    raise RuntimeError("Cannot find correct COM port")
#port = list_ports.comports()[-1].device
print('Connecting to port: ', port)
ser = serial.Serial(port)

ang1 = 0
ang2 = 0
tstop = False

# Arc length, or sensor length
s = 4.125
arc_segments = 10


def reader():
    """Thread for reading sensor data"""
    # Threading this makes it feal much more real-time
    global ang1, ang2
    # There's header data, so toss the first line
    ser.readline()
    while True:
        ang1, ang2 = [float(x) for x in ser.readline().strip().decode().split(',')]
        #print(ang1, ang2)
        if tstop:
            print('Stopping...')
            break
    

def animate(i):
    """Update our frames"""
    zline = np.linspace(0, 5, arc_segments)
    xline = build_points(ang1)
    yline = build_points(-ang2)
    ax.clear()
    # Since we cleared the axis, we have to reset the values
    ax.set_xlim3d([-4.5, 4.5])
    ax.set_xlabel('X')
    ax.set_ylim3d([-4.5, 4.5])
    ax.set_ylabel('Y')
    ax.set_zlim3d([0, 5])
    ax.set_zlabel('Z')
    ax.set_aspect('equal')
    ax.plot3D(xline, yline, zline, 'red')


def build_points(ang):
    """
    Generate the points we need
    :param ang: the angle from our sensor that we should use
    """
    is_pos = True if ang > 0 else False
    if ang == 0:
        ang = 0.0001
    radius = np.absolute((180*s)/(np.pi*ang))
    # Compute how far we need to draw
    s_point = radius * np.sin(np.deg2rad(ang))
    #print(s_point)

    # Build our domain line
    dline = np.linspace(0, s_point, arc_segments)
    
    if is_pos:
        return -(np.sqrt(np.square(radius) - np.square(dline))) + radius
    else:
        return (np.sqrt(np.square(radius) - np.square(dline))) - radius


tread = threading.Thread(target=reader)
tread.start()
# Let the reader thread start up
time.sleep(1)

ax.set_xlim3d([-4.5, 4.5])
ax.set_xlabel('X')

ax.set_ylim3d([-4.5, 4.5])
ax.set_ylabel('Y')

ax.set_zlim3d([0, 5])
ax.set_zlabel('Z')

ax.set_aspect('equal')

ani = animation.FuncAnimation(fig, animate, interval=20)

# Show the graph
plt.show()
tstop = True
# Let the reader thread stop
time.sleep(1)
