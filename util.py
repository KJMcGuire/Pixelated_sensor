import sys
import re
import time
import math
import serial
import os
import numpy as np
import datetime

project_path = os.path.dirname(os.path.abspath(__file__))  #Gives the directory of this file (util.py)

def get_path(date):
    return os.path.join(project_path,date)

def load_file(date, file):
    path = os.path.join(get_path(date),file)
    data = np.genfromtxt(path,skip_header=0)     #Import data file
    return data

def create_new_data_file(file_name):
    directory = os.path.join(project_path, datetime.datetime.now().strftime('%Y-%m-%d' ))
    if not os.path.exists(directory):
        os.mkdir(directory)
    path = os.path.join(directory, file_name)
    if os.path.exists(path):
        raise Exception('file already exists: '+path)
    print('Opened new log file: ', path)
    return open(path,'w')

class DataReader:
    def __init__(self, serial_port = 'COM9', baud_rate = 115200, datafile = None):
        if datafile != None:
            self.datafile_out = create_new_data_file(datafile)
        else:
            self.datafile_out = None

        self.ser = serial.Serial(serial_port, baud_rate)

    def readline(self):
        line = self.ser.readline()
        data = []
        for d in re.split(" *", line):
            try:
                d = float(d)
            except ValueError:
                d = 0
            if math.isnan(d):
                d = 0
            data.append(d)

        self.printline(data)
        return data

    def printline(self, data):
        time = datetime.datetime.now()
        t = time.strftime('%H/%M/%S ' )
        outputdata = t+" "+" ".join([str(x) for x in data])+"\n"
        sys.stdout.write(outputdata)
        if self.datafile_out:
            self.datafile_out.write(outputdata)

    def close(self):
        if self.datafile_out:
            self.datafile_out.close()
            print "Successfully closed file."

class DataSimulator(DataReader):
    def __init__(self, date, file_name):
        self.datafile_in = load_file(date, file_name)
        self.datafile_out = None
        self.max, self.min = np.nanmax(self.datafile_in), np.nanmin(self.datafile_in)
        print("Actual data file min/max: ", self.min, self.max)
        self.line_number = 0


    def readline(self):
        if self.line_number > len(self.datafile_in)-1:
            self.line_number = 0
        l = self.datafile_in[self.line_number][1:]
        self.line_number += 1
        time.sleep(0.01)
        self.printline(l)
        return l
