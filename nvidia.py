#!/usr/bin/python

import subprocess
import re

# simple function to run nv-control-dpy
def nv_control_dpy(args):
    return subprocess.check_output(["/home/wilsonp/opt/bin/nv-control-dpy"]+args)

### DISPLAYS & DEVICES ####

# probe the GPU for the currently attached displays
def probe_displays():
    return nv_control_dpy(["--probe-dpys"])

# invoke twinview
def dynamic_twinview():
    return nv_control_dpy(["--dynamic-twinview"])

# update the state for manipulating multi-head system
def update_displays():
    probe_displays()
    try:
        dynamic_twinview()
    except subprocess.CalledProcessError:
        print "Twinview already invoked"
        pass

# build a database of modes for each display
def build_modeDB():

    nv_mode_stdout = nv_control_dpy(["--print-modelines"]).splitlines()

    modeDB = {}

    for line in nv_mode_stdout:
        if "0x000" in line:
            # process port:device line
            tokens  = line.split()
            device = ''.join(tokens[2:])
            #print "Adding device: " + device
            modeDB[device] = {}
            modeDB[device]['port'] = tokens[0]
            modeDB[device]['mask'] = tokens[1]
            modeDB[device]['modelist'] = {}
            modeDB[device]['maxWmode'] = "0x0"
            modeDB[device]['maxHmode'] = "0x0"
            modeDB[device]['maxW'] = 0
            modeDB[device]['maxH'] = 0
        if "Modelines for" in line:
            # process device header
            tokens = line.split()
            # device may have white space (?) and strip trailing colon
            device = ''.join(tokens[2:])[:-1]
            #print "Processing mode lines for device: " + device
        if "::" in line:
            # process modeline
            [metadata,modeline]=line.split(" :: ")
            modedata = modeline.split()
            # strip quotation marks
            mode = modedata[0][1:-1]
            modeDB[device]['modelist'][mode] = modedata[1:]
            if 'nvidia-auto-select' not in mode:
                modeW = int(modedata[2])
                if modeW > modeDB[device]['maxW']:
                    modeDB[device]['maxW'] = modeW
                    modeDB[device]['maxWmode'] = mode
                modeH = int(modedata[6])
                if modeH > modeDB[device]['maxH']:
                    modeDB[device]['maxH'] = modeH
                    modeDB[device]['maxHmode'] = mode

    return modeDB

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
def get_all_metamodes():
    
    # get the list from nv-control-dpy
    metamode_list = nv_control_dpy(["--print-metamodes"]).splitlines()

    # set regexp to match
    mode_id_RE = re.compile(r".*id=(\d+).*:: (.*)")
    
    # initialize metamode dictionary
    metamode = {}

    # for each mode that matches, add it to the dictionary
    for mode in metamode_list:
        if "::" in mode:
            [nv_info,modeString] = mode.split(" :: ")
            nv_info_list = nv_info.split(", ")

            [k,mode_id] = nv_info_list[0].split("=")
            metamode[mode_id] = {}

            [k,v] = nv_info_list[1].split("=")
            metamode[mode_id][k] = v
            [k,v] = nv_info_list[2].split("=")
            metamode[mode_id][k] = v

            metamode[mode_id]['details'] = metamode_string2dict(modeString)

    return metamode

# get the current metamode
def get_current_metamode():
    
    # get the list from nv-control-dpy
    nv_metamode_list = nv_control_dpy(["--print-current-metamode"]).splitlines()

    # set the regexp to match
    mode_id_RE = re.compile(r".*id=(\d+).*:: (.*)")
    
    mode_id = -1

    # for each mode that matches, add it to t
    for metamode in nv_metamode_list:
        print metamode
        if (mode_id_RE.match(metamode)):
            mode_id = mode_id_RE.match(metamode).group(1)
            print mode_id

    # return 
    return mode_id

def add_metamode(modeString):
    
    add_response = nv_control_dpy(["--add-metamode","'"+modeString+"'"])
    
    # extract mode id from add_response
    mode_id_RE = re.compile(r'.*id=(\d+).*')

    mode_id = -1

    if (mode_id_RE.match(add_response)):
        mode_id = mode_id_RE.match(add_response).group(1)

    return mode_id

def delete_metamode(mode_id):

    nv_metamode_list = get_all_metamodes()

    if mode_id in nv_metamode_list:
        nv_control_dpy(["--delete-metamode",nv_metamode_list[mode_id]])


def delete_all_metamodes_except(mode_id_list):

    nv_metamode_list = get_all_metamodes()

    for key in nv_metamode_list:
        if key not in mode_id_list:
            nv_control_dpy(["--delete-metamode",nv_metamode_list[key]])

### TRANSLATE MODE INFO ###
# ensure metamode dictionary has entry for every display
def rationalize_metamode_dict(dpy_modes):
    
    dpy_modes_new = {}

    # get list of displays
    probe_displays()
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
def metamode_string2dict(modeStr):
    
    # initialize dictionary
    dpy_modes = {}

    # split modelist into individual display modes
    modeList = modeStr.split(", ")

    # add dictionary entry for each display in metamode
    for dpyMode in modeList:
        [display,data] = dpyMode.split(':')
        tokens = data.split()
        if len(tokens)>1:
            [mode,resolution,offset] = tokens
            [offsetX,offsetY] = offset[1:].split('+')
            dpy_modes[display] = {'enabled':True,
                                  'mode':mode,
                                  'resolution':resolution[1:],
                                  'offset':offset,
                                  'offsetX':offsetX,
                                  'offsetY':offsetY}
        else:
            mode = tokens[0]
            offset = ''
            resolution = ''
            dpy_modes[display] = {'enabled':False},

    dpy_modes = rationalize_metamode_dict(dpy_modes)

    # return dictionary
    return dpy_modes

# turn dictionary of display modes into a metamode string
def metamode_dict2string(dpy_modes):

    # initialize lists
    modeStr    = ""
    modeStrOff = ""

    # for each display
    for display,modeDetails in dpy_modes['details'].iteritems():
        if modeDetails['enabled']:
            # Add to list of turned on modes
            modeStr    += ", " + display + ": " + modeDetails['mode'] + " @" + modeDetails['resolution'] + " " + modeDetails['offset']
        else:
            # Add to list of turned off modes
            modeStrOff += ", " + display + ": NULL"
    
    # concatenate list of modes
    modeStr += modeStrOff

    return modeStr[2:]

### Modify state ###
def switch_mode(mode_id):

    # get the metamode infor for mode_id

    # delete all metamodes except for the current and the new

    # calculate total width & height based on resolution and offsets
    #  (check for 0)

    # call xrandr to select mode

    # delete old mode
    pass

def enable_displays(display_resolution_map):
    
    # get list of displays
    probe_displays()
    displays=get_displays()

    # get list of metamodes
    metamodes=get_all_metamodes()

    # loop through list of available displays
    # to create array of display states
    dpy_modes = {}
    for display in displays:
        if display not in display_resolution_map:
            dpy_modes[display] = {'enabled':False}
    
    for display, resolution in display_resolution_map.iteritems():
        dpy_modes[display] = {'enabled':True,'resolution':resolution}

    # build metamode string for desired state
    metaModeStr = metamode_dict2string(dpy_modes)

    # get the metamode ID for that state
    mode_id = [k for k, v in metamodes.iteritems() if v == metaModeStr]

    # invoke this metamode
    return mode_id

# short cut to enable a single display
def enable_single_display(display_name,resolution):
    return enable_displays({display_name:resolution})


metamodeDB = get_all_metamodes()
mode126 = metamodeDB['126']
print mode126
mode126tst = metamode_dict2string(mode126)
print mode126tst

newMode = {}
newMode['details'] = {}
newMode['details']['CRT-0'] = {'enabled':False}
newMode['details']['DFP-3'] = {'enabled':True,
                               'mode':"1600x900",
                               'resolution':"1600x900",
                               'offset':"+0+0",
                               'offsetX':0,
                               'offsetY':0}
print metamode_dict2string(newMode)
