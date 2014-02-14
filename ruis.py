import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as CM
import matplotlib.patches as mpatches
import numbers
import ctypes
import sys
import csv
import sqlite3
import pandas
import os
import math

class Analysis:
    def __init__(self, 
                 token_name=None,
                 rui_fname=None,
                 events_fname=None,
                 expertise=0,
                 offset=0,
                 debug=False):
        
        ##
        ## Initalize input parameters
        ##
        self.token_name   = token_name
        self.rui_fname    = rui_fname
        self.events_fname = events_fname
        self.expertise    = expertise
        self.offset       = offset

        self.data_is_good = False
        self.events       = []
        self.rui_t0=None
        self.events_t0=None

        self.cuts = []
        self.tags_times  = {}
        self.tags_colours = {}

        ##
        ## fill in the rui events and find the syncing token
        ##
        if self.fill_rui_and_sync() == True and \
           self.fill_events_and_sync() == True:
            self.data_is_good = True
        else:
            return

        self.t0_diff = (float(self.events_t0)+self.offset) - float(self.rui_t0)
        self.start_time = 0
        self.stop_time  = self.events[len(self.events)-1].time

        if(debug):
            print "Time shift: ",self.t0_diff
            print "Start time: ",self.start_time
            print "Stop time : ",self.stop_time
            print "offset: ", self.offset
        
    def fill_rui_and_sync(self):
        if self.rui_fname == '':
            return False

        print "RUI filename: ",self.rui_fname

        f = open(self.rui_fname,'r')

        self.events    = []
        for line in f:
            self.events.append( Event(line, self.offset) )

        for index, e in enumerate(self.events):
            if self.events[index+0].spt[2] == '/' and \
               self.events[index+1].spt[2] == 'l' and \
               self.events[index+2].spt[2] == 'o' and \
               self.events[index+3].spt[2] == 'g' and \
               self.events[index+4].spt[2] == "RETURN":
                self.rui_t0 = self.events[index+4].time
                break

        print "RUI log activated: ", self.rui_t0
        
        if self.rui_t0 <> None:
            return True
        else:
            return False


    def fill_events_and_sync(self):
        if self.events_fname == '':
            return False

        print "events filename: ",self.events_fname

        csv_reader = pandas.read_csv(open(self.events_fname,'r'), sep='\t');

        self.Behavior   = csv_reader['Behavior']
        self.Event_Type = csv_reader['Event_Type']
        self.Time_Relative_sf = csv_reader['Time_Relative_sf']

        for index, row in enumerate(self.Behavior):
            if row == "Activate chatlog":
                self.events_t0=self.Time_Relative_sf[index]
                break
        print "Activate chatlog: ",self.events_t0

        if self.events_t0 <> None:
            return True
        else:
            return False


    def add_tags(self, tag_name, tag_colour):
        start_times = []
        stop_times  = []
        for index, row in enumerate(self.Behavior):
            if row == tag_name:
                if self.Event_Type[index] == "State start":
                    start_times.append( float(self.Time_Relative_sf[index]) - self.t0_diff + self.offset - eps )
                elif self.Event_Type[index] == "State stop":
                    stop_times.append( float(self.Time_Relative_sf[index]) - self.t0_diff + self.offset + eps )

        if len(start_times) <> len(stop_times):
            sys.exit("tags length mismatch")

        self.tags_times[tag_name]  = zip(start_times,stop_times)
        self.tags_colours[tag_name] = tag_colour

    def add_point_tag(self, tag_name, tag_colour):
        start_times = []
        stop_times  = []
        for index, row in enumerate(self.Behavior):
            if row == tag_name:
                if self.Event_Type[index] == "Point":
                    start_times.append( float(self.Time_Relative_sf[index]) - self.t0_diff + self.offset )
                    stop_times.append( float(self.Time_Relative_sf[index]) - self.t0_diff + self.offset + 1 )

        if len(start_times) <> len(stop_times):
            sys.exit("tags length mismatch")

        self.tags_times[tag_name]  = zip(start_times,stop_times)
        self.tags_colours[tag_name] = tag_colour
        


    def add_cut( self, cut ):
        assert isinstance(cut, tuple)
        self.cuts.append( cut )

    def print_cuts( self ):
        print self.cuts

    def cut_by_tags(self, tag_name):
        tags = self.tags_times[tag_name]
        for tag in tags:
            self.cuts.append(tag)

    def cut_all_but(self,
                    tag_name,
                    start_time=None, 
                    stop_time=None):

        if start_time == None:
            start_time = self.start_time
        if stop_time  == None:
            stop_time  = self.stop_time

        tags = self.tags_times[tag_name]

        if len(tags)==0 : return

        self.cuts.append( (start_time, tags[0][0] ) )

        for index, tag in enumerate(tags):
            try:
                self.cuts.append( (tags[index][1], tags[index+1][0]) )
            except:
                self.cuts.append( (tags[index][1], stop_time) )


    def apply_cuts(self):
        for e in self.events:
            for c in self.cuts:
                if e.time>c[0] and e.time <c[1]:
                    e.cut = True

    def calc_play_time( self,
                        start_time=None,
                        stop_time=None ):
        if start_time == None:
            start_time = self.start_time
        if stop_time  == None:
            stop_time  = self.stop_time

        time = stop_time - start_time

        for cut in self.cuts:
            time = time - (cut[1] - cut[0])

        return time


    def make_keys_hist(self):

        keys={}
        for i in accepted:
            keys[i]=0

        for i in range(len(self.events)-1):
            e = self.events[i]

            if e.cut == True:
                continue

            if e.spt[1] == 'KEY':
                key = e.spt[2]

                if key not in accepted:

                    s = key.split()
                    if s[0] == 'SHIFT':
                        try:
                            keys[key] = keys[key] + 1
                        except:
                            keys[key] = 1
                        continue
                    else:
                        print "unknown: ",key
                        continue

                try:
                    keys[key] = keys[key] + 1
                except:
                    keys[key] = 1

        return keys


    def make_time_keys(self):
        x = []
        y = []
        for i in range(len(self.events)-1):
            e = self.events[i]

            if e.cut == True:
                continue

            if e.spt[1] == 'KEY':
                key = e.spt[2]

                if key not in accepted:

                    s = key.split()
                    if s[0] == 'SHIFT':
                        try:
                            y.append(accepted.index(s[2]))
                            x.append(e.time)
                        except: continue
                        continue
                    else:
                        print "unknown: ",key
                        continue

                y.append(accepted.index(key))
                x.append(e.time)

            if e.spt[1] == 'Pressed' and e.spt[2] == 'Left':
                x.append(e.time)
                y.append(accepted.index('MOUSE Left'))
            if e.spt[1] == 'Pressed' and e.spt[2] == 'Right':
                x.append(e.time)
                y.append(accepted.index('MOUSE Right'))
            if e.spt[1] == 'Moved':
                x.append(e.time)
                y.append(accepted.index('MOUSE Moved'))

        return x,y

    def make_clicks_hist(self):
        hx = []
        hy = []

        for i in range(len(self.events)-1):
            e = self.events[i]
            next_e = self.events[i+1]
            x = -1
            y = -1
            if e.spt[1] == 'Pressed' and e.spt[2] == 'Left' and next_e.spt[1] == 'Released' and next_e.spt[2] == 'Left':
                j = i - 1
                while True:
                    prev_e = self.events[j]
                    #print j, prev_e.spt
                    if prev_e.spt[1] == 'Moved':
                        x = int(prev_e.spt[2])
                        y = int(prev_e.spt[3])
                        break
                    else:
                        j = j - 1

                #apply cuts if necessary
                if e.cut == False:
                    hx.append(x)
                    hy.append(y)
        return hx,hy

class Event:
    def __init__(self):
        return

    def __init__(self, line, offset):
        self.data = line.rstrip()
        self.spt  = self.data.split('\t')
        self.time = float(self.spt[0]) + offset
        self.cut  = False
        
    def Print(self):
        if self.spt[1] == 'Pressed':
            print self.spt

accepted = ['LEFT','RIGHT','UP','DOWN','0','1','2','3','4','5','6','7','8','9','RETURN','SPACE','ESCAPE','ENTER','DELETE','TAB','.',',','-','/',';','=','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','MOUSE Moved','MOUSE Left','MOUSE Right']
accepted.reverse()

accepted_no_mouse = ['LEFT','RIGHT','UP','DOWN','0','1','2','3','4','5','6','7','8','9','RETURN','SPACE','ESCAPE','ENTER','DELETE','TAB','.',',','-','/',';','=','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

eps=5 #seconds


def get_colour(expertise):
    return {
        0 : "grey", #NA
        1 : "blue", #Novice
        2 : "red",  #Intermediate
        3 : "black" #Expert
        }[expertise]
