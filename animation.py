'''
Author: Kellie McGuire   kellie@kelliejensen.com

This program runs a pixel sensor animation widget from the command line and saves the data to a file.
Use in conjuction with util.py and sensorpixels.kv

'''

import os
import re
import serial
import sys
from util import DataSimulator, DataReader
from color_util import create_colorlist
from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
import random
import math
from colour import Color
import matplotlib.pyplot as plt


DEFAULT_MIN_VALUE = 0#34.0
DEFAULT_MAX_VALUE = 4#36.3
USE_DATA_MIN_MAX = False
RESOLUTION = 0.05

class SensorPixelsGame(Widget):
    sensors = ObjectProperty(None)

    def my_init(self):
        self.find_min_max()
        self.setup_color_map()
        self.is_setup = True



    def setup_color_map(self):
        self.color_steps = int((self.max_v-self.min_v)/RESOLUTION)
        #self.color_map = create_colorlist(Color("#43ff00"), Color("#ff0b00"),self.color_steps)
        #self.color_map = create_colorlist(Color("#00a6dd"), Color("#ff0b00"),self.color_steps)
        self.color_map = create_colorlist(Color("#1c1414"), Color("#ff0000"),self.color_steps)
        #self.color_map = create_colorlist(Color("#000000"), Color("#00ff00"),self.color_steps)



    def find_min_max(self):
        if isinstance(ser, DataReader) or not USE_DATA_MIN_MAX:
            self.min_v = DEFAULT_MIN_VALUE
            self.max_v = DEFAULT_MAX_VALUE
        else:
            self.min_v = ser.min
            self.max_v = ser.max
        print("min/max: ", self.min_v, self.max_v)

    def update(self, dt):
        data = ser.readline()
        if not hasattr(self, 'is_setup'):
            self.my_init()
        for i, sensor in enumerate(self.sensors):
            if i >= len(data):
                break

            normalize = (data[i]-self.min_v) / (self.max_v-self.min_v)

            try:
                index = int(math.floor(normalize*self.color_steps))
                color = self.color_map[index]
            except ValueError:
                color = self.color_map[0]
            except IndexError:
                color = self.color_map[0]

            sensor.color = (color[0],color[1],color[2],1)

            # grey = (data[i]-min) / (max-min)
            # sensor.color = (grey, grey, grey, 1)

s = SensorPixelsGame()



class SensorPixel(Widget):
    color = ListProperty([0, 0, 0, 1])

class SensorPixelsApp(App):
    def build(self):
        game = SensorPixelsGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

    def on_stop(self):
        global ser
        ser.close()

if __name__ == "__main__":
    global ser
    if len(sys.argv) < 2:
        print("Error: First argument must specify the COM port or test file to read from")
        exit(1)
    if re.match("COM[0-9]$",sys.argv[1]):
        if len(sys.argv)==3:
            datafile = sys.argv[2]
        else:
            datafile = None
        ser = DataReader(sys.argv[1], datafile = datafile)
    else:
        try:
            directory, filename = os.path.split(sys.argv[1])
            if len(directory)==0 or len(filename)==0:
                raise ValueError
            ser = DataSimulator(directory, filename)
        except ValueError, e:
            print(e)
            print ("Error: Must specify data file like: directory/file_name.txt")
            exit(1)
    SensorPixelsApp().run()
