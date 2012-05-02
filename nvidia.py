#!/usr/bin/python

NV_DEFAULT_RESOLUTION="1028x768"

import subprocess
import re

# simple function to run nv-control-dpy
def nv_control_dpy(args):
    return subprocess.check_output(["/home/wilsonp/opt/bin/nv-control-dpy"]+args)

### GET DISPLAY INFO ###

# probe the GPU for the currently attached displays
def update_displays():

    nv_control_dpy(["--probe-dpys"])

# get the list of the currently attached displays
def get_displays():
    
    # get the list from nv-control-dpy
    nv_display_list = nv_control_dpy(["--get-associated-dpys"]).splitlines()
    
    # set the regexp
    dpy_id_RE = re.compile(r" +([A-Za-z0-9-]+) \(0x[0-9a-f]+\): (.*)$")

    # initialize display list
    dpy_list = {}

    # for each RE match add an entry to the list
    for display in nv_display_list:
        if (dpy_id_RE.match(display)):
            dpy_list[dpy_id_RE.match(display).group(1)]=dpy_id_RE.match(display).group(2)

    # return the list of dictionaries
    return dpy_list

### GET METAMODE INFO ###

# get the current list of metamodes
def get_metamodes():
    
    # get the list from nv-control-dpy
    metamode_list = nv_control_dpy(["--print-metamodes"]).splitlines()

    # set regexp to match
    mode_id_RE = re.compile(r".*id=(\d+).*:: (.*)")
    
    # initialize metamode dictionary
    metamode = {}

    # for each mode that matches, add it to the dictionary
    for mode in metamode_list:
        if (mode_id_RE.match(mode)):
            metamode[mode_id_RE.match(mode).group(1)] = mode_id_RE.match(mode).group(2)

    return metamode

# get the current metamode
def get_current_metamode():
    
    # get the list from nv-control-dpy
    nv_metamode_list = nv_control_dpy(["--print-current-metamode"]).splitlines()

    # set the regexp to match
    mode_id_RE = re.compile(r".*id=(\d+).*:: (.*)")
    
    # for each mode that matches, add it to t
    for metamode in nv_metamode_list:
        if (mode_id_RE.match(metamode)):
            return mode_id_RE.match(metamode).group(1)

    # return -1 for no found mode
    return -1

### TRANSLATE MODE INFO ###
# ensure metamode dictionary has entry for every display
def rationalize_metamode_dict(dpy_modes):
    
    dpy_modes_new = {}

    # get list of displays
    dpylist = get_displays()

    # make sure there is one entry per display
    # and no entries for non-existent displays
    for dpy_key in dpylist:
        if dpy_key in dpy_modes:
            dpy_modes_new[dpy_key] = dpy_modes[dpy_key]
        else:
            dpy_modes_new[dpy_key] = {'enabled':False}
                
    # return new display=>mode list
    return dpy_modes_new

# turn metamode string into a dictionary of display modes
def parse_metamode_string(modeStr):
    
    # initialize dictionary
    dpy_modes = {}

    # setup regexp for match
    mode_info_RE = re.compile(r"([a-zA-Z0-9-]+): ([0-9]+x[0-9]+) @([0-9]+x[0-9])")

    # split modelist into individual display modes
    modeList = modeStr.split(", ")

    # add dictionary entry for each display in metamode
    for dpyMode in modeList:
        if mode_info_RE.match(dpyMode):
            reData = mode_info_RE.match(dpyMode)
            dpy_modes[reData.group(1)] = {'enabled':True,
                                          'resolution':reData.group(2)}
    # return dictionary
    return dpy_modes

# turn dictionary of display modes into a metamode string
def create_metamode_string(dpy_modes):

    # initialize lists
    modeStr    = ""
    modeStrOff = ""

    # for each display
    for display,modeInfo in dpy_modes.iteritems():
        if modeInfo['enabled']:
            # Add to list of turned on modes
            modeStr    += ", " + display + ": " + modeInfo['resolution'] + " @" + modeInfo['resolution'] + " +0+0"
        else:
            # Add to list of turned off modes
            modeStrOff += ", " + display + ": NULL"
    
    # concatenate list of modes
    modeStr += modeStrOff

    return modeStr[2:]

### Modify state ###
def enable_displays(display_resolution_map):
    
    # get list of displays
    displays=get_displays()

    # get list of metamodes
    metamodes=get_metamodes()

    # loop through list of available displays
    # to create array of display states
    dpy_modes = {}
    for display in displays:
        if display not in display_resolution_map:
            dpy_modes[display] = {'enabled':False}
    
    for display, resolution in display_resolution_map.iteritems():
        dpy_modes[display] = {'enabled':True,'resolution':resolution}

    # build metamode string for desired state
    metaModeStr = create_metamode_string(dpy_modes)

    # get the metamode ID for that state
    mode_id = [k for k, v in metamodes.iteritems() if v == metaModeStr]

    # invoke this metamode
    return mode_id

# short cut to enable a single display
def enable_single_display(display_name,resolution):
    return enable_displays({display_name:resolution})

def hide_this():
    modeList = get_metamodes()
    print modeList['114']
    print [k for k,v in modeList.iteritems() if v == modeList['114']][0]
    
    print enable_displays({'DFP-3':'400x300'})

    update_displays()
    dpylist = get_displays()
    print dpylist
    modelist = get_metamodes()
# print modelist
    tstMode = create_metamode_string({"DFP-1":{'enabled':True,"resolution":"1200x900"},
                                      "DFP-3":{'enabled':True,"resolution":"1600x900"}})
    print tstMode
    modeDict = parse_metamode_string(tstMode)
    print modeDict
    modeDictFill = rationalize_metamode_dict(modeDict)
    print modeDictFill
    tstModeFill = create_metamode_string(modeDictFill)
    print tstModeFill

def test_update():
    update_displays()
