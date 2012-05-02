#!/usr/bin/python

NV_DEFAULT_RESOLUTION="1028x768"

import subprocess
import re

def get_metamodes():
    
    nv_metamode_list = subprocess.check_output(["/home/wilsonp/opt/bin/nv-control-dpy",
                                                "--print-metamodes"]).splitlines()

    mode_id_RE = re.compile(r".*id=(\d+).*:: (.*)")
    
    nv_metamode = dict()

    for metamode in nv_metamode_list:
        if (mode_id_RE.match(metamode)):
            mode_id   = mode_id_RE.match(metamode).group(1)
            mode_desc = mode_id_RE.match(metamode).group(2)
            nv_metamode[mode_id] = mode_desc

    return nv_metamode

def get_current_metamode():
    
    nv_metamode_list = subprocess.check_output(["/home/wilsonp/opt/bin/nv-control-dpy",
                                                "--print-current-metamode"]).splitlines()

    mode_id_RE = re.compile(r".*id=(\d+).*:: (.*)")
    
    for metamode in nv_metamode_list:
        if (mode_id_RE.match(metamode)):
            mode_id   = mode_id_RE.match(metamode).group(1)

    return mode_id

def get_displays():
    
    nv_display_list = subprocess.check_output(["/home/wilsonp/opt/bin/nv-control-dpy",
                                               "--get-associated-dpys"]).splitlines()
    
    dpy_id_RE = re.compile(r" +([A-Za-z0-9-]+) \(0x[0-9a-f]+\)")

    dpy_list = []

    for display in nv_display_list:
        if (dpy_id_RE.match(display)):
            dpy_list.append(dpy_id_RE.match(display).group(1))

    return dpy_list


def create_metamode_string(display_states):

    metamode = ""

    # for each display
    for display,state in display_states.iteritems():
        metamode += ", " + display + ": "
        if state['enabled']:
            metamode += state['resolution'] + " @" + state['resolution'] + " "
        else:
            metamode += "NULL"

    return metamode[2:]

print create_metamode_string({'CRT-0':{'enabled':True,'resolution':"1920x1200"},
                              'DFP-3':{'enabled':True,'resolution':"1600x900"}})

def enable_displays(display_resolution_map):
    
    # get list of displays
    nvidia_displays=get_displays()

    # get list of metamodes
    nvidia_metamodes=get_metamodes()

    # loop through list of available displays
    # to create array of display states
    display_states = {}
    for display in nvidia_displays:
        if display not in display_resolution_map:
            display_states[display] = {'enabled':False}
    
    for display, resolution in display_resolution_map.iteritems():
        display_states[display] = {'enabled':True,'resolution':resolution}

    # build metamode string for desired state
    
    # get the metamode ID for that state

    # invoke this metamode
    return display_states


def enable_single_display(display_name,resolution):
    return enable_displays({display_name:resolution})

print get_displays()
