#!/usr/bin/python

import subprocess
import re

# modeDB:
#    device:
#        port => Port string used in metamode string, e.g. CRT-0, DFP-3, DFP-1
#        mask => Hex code used for (???)
#        maxResMode => string: resolution of the mode with maximum # of pixels
#        maxRes => integer: maximum # of pixels
#        maxW => integer: width of maxResMode
#        maxH => integer: height of maxResMode
#        modelist:
#            <modeString> => list: mode data

## displayDB structure
#
#   dpy_list:
#      <port> => string: name of device

## Metamode database:
#
# metamode:
#    <mode_id>:   (integer)
#        <key> =>  <value>  : key value pairs are stored as found, but not used
#        'details':
#             <display>:   (string)
#                  enabled    => boolean
#                  mode       => string: resolution of viewable window
#                  resolution => string: resolution of underlying mode
#                  offset     => string: offset of this display in underlying mode

# simple function to run nv-control-dpy
def nv_control_dpy(args):
    return subprocess.check_output(["/home/wilsonp/opt/bin/nv-control-dpy"]+args)

### DISPLAYS & DEVICES ####

# probe the GPU for the currently attached displays
def probe_displays():
    return nv_control_dpy(["--probe-dpys"])

# invoke twinview
def dynamic_twinview():

    dyn_tview_out =''

    try:
        dyn_tview_out = nv_control_dpy(["--dynamic-twinview"])
    except subprocess.CalledProcessError:
        print "Twinview already invoked"
        pass

    return dyn_tview_out

# update the state for manipulating multi-head system
def update_displays():
    probe_displays()
    dynamic_twinview()

## Structure of modeDB:

# build a database of modes for each display
def build_modeDB():

    # get modelines from GPU
    nv_mode_stdout = nv_control_dpy(["--print-modelines"]).splitlines()

    # initialize dict
    modeDB = {}

    # parse all output
    for line in nv_mode_stdout:
        # list of devices
        if "0x000" in line:
            # process port:device line
            tokens  = line.split()
            device = ''.join(tokens[2:])
            #print "Adding device: " + device
            modeDB[device] = {}
            modeDB[device]['port'] = tokens[0]
            modeDB[device]['mask'] = tokens[1][:-1]  # strip trailing colon
            modeDB[device]['modelist'] = {}
            modeDB[device]['maxResMode'] = "0x0"
            modeDB[device]['maxRes'] = 0
            modeDB[device]['maxW'] = 0
            modeDB[device]['maxH'] = 0
        # header for each device
        if "Modelines for" in line:
            # process device header
            tokens = line.split()
            # device may have white space (?) and strip trailing colon
            device = ''.join(tokens[2:])[:-1]
            #print "Processing mode lines for device: " + device
        # modeline
        if "::" in line:
            # process modeline
            [metadata,modeline]=line.split(" :: ")
            modedata = modeline.split()
            # strip quotation marks
            mode = modedata[0][1:-1]
            modeDB[device]['modelist'][mode] = modedata[1:]
            if 'nvidia-auto-select' not in mode:
                modeW = int(modedata[2])
                modeH = int(modedata[6])
                if modeW*modeH > modeDB[device]['maxRes']:
                    modeDB[device]['maxRes'] = modeW*modeH
                    modeDB[device]['maxW'] = modeW
                    modeDB[device]['maxH'] = modeH
                    modeDB[device]['maxResMode'] = mode

    return modeDB


# get the list of the currently attached displays
def get_displays():
    
    # get the list from nv-control-dpy
    nv_display_list = nv_control_dpy(["--get-associated-dpys"]).splitlines()
    
    # initialize display list
    dpy_list = {}

    # for each RE match add an entry to the list
    for line in nv_display_list:
        if "(0x000" in line:
            # this is a display line
            tokens  = line.split()
            port = tokens[0]
            mask = tokens[1][:-1] # strip trailing colon
            device = ''.join(tokens[2:])
            dpy_list[port] = device

    # return the list of dictionaries
    return dpy_list

### GET METAMODE INFO ###

# get the current list of metamodes
def get_all_metamodes():
    
    # get the list from nv-control-dpy
    metamode_list = nv_control_dpy(["--print-metamodes"]).splitlines()

    # initialize metamode dictionary
    metamode = {}

    # for each mode that matches, add it to the dictionary
    for mode in metamode_list:
        if "::" in mode:
            [nv_info,modeString] = mode.split(" :: ")
            nv_info_list = nv_info.split(", ")

            [k,v] = nv_info_list[0].split("=")
            mode_id = int(v)
            metamode[mode_id] = {}

            [k,v] = nv_info_list[1].split("=")
            metamode[mode_id][k] = v
            [k,v] = nv_info_list[2].split("=")
            metamode[mode_id][k] = v

            metamode[mode_id]['details'] = metamode_string2dict(modeString)

    return metamode

# get the current metamode
# returns integer value of current metamode
def get_current_metamode():
    
    # get the list from nv-control-dpy
    nv_metamode_list = nv_control_dpy(["--print-current-metamode"]).splitlines()

    # initialize mode ID
    mode_id = -1

    # for each mode that matches, add it to t
    for line in nv_metamode_list:
        if 'current metamode: "id=' in line:
            start_id = line.find('id=')
            if start_id > -1:
                end_id = line.find(',',start_id)
                mode_id = int(line[start_id+3:end_id])

    # return 
    return mode_id

# search the metamode list by the modestring
def find_metamode(modeString):

    metamodeDB = get_all_metamodes()

    found_mode_id = -1
    for mode_id,modeData in metamodeDB.iteritems():
        if metamode_dict2string(modeData['details']) == modeString:
            found_mode_id = mode_id
            break

    return found_mode_id

# add a new metamode to the list of available modes
def add_metamode(modeString):
    
    add_response_lines = nv_control_dpy(["--add-metamode",modeString]).splitlines()
    
    # extract mode id from add_response
    mode_id_RE = re.compile(r'.*id=(\d+).*')

    mode_id = -1

    for line in add_response_lines:
        if (mode_id_RE.match(line)):
            mode_id = int(mode_id_RE.match(line).group(1))

    return mode_id

# delete a metamode based on it's integer id
def delete_metamode(mode_id):

    nv_metamode_list = get_all_metamodes()

    if mode_id in nv_metamode_list:
        print metamode_dict2string(nv_metamode_list[mode_id]['details'])
        nv_control_dpy(["--delete-metamode",metamode_dict2string(nv_metamode_list[mode_id]['details'])])

# delete all metamodes that are not in the list of integers
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
            dpy_modes[display] = {'enabled':True,
                                  'mode':mode,
                                  'resolution':resolution[1:],
                                  'offset':offset[1:]}
        else:
            mode = tokens[0]
            offset = ''
            resolution = ''
            dpy_modes[display] = {'enabled':False}

    # probably don't rationalize modes in all cases
    # dpy_modes = rationalize_metamode_dict(dpy_modes)

    # return dictionary
    return dpy_modes

# turn dictionary of display modes into a metamode string
def metamode_dict2string(dpy_modes):

    # initialize lists
    modeStr    = ""
    modeStrOff = ""

    # for each display
    for display,modeDetails in dpy_modes.iteritems():
        if modeDetails['enabled']:
            # Add to list of turned on modes
            modeStr += ", " + display + ": " + modeDetails['mode'] 
            modeStr += " @" + modeDetails['resolution'] + " +" + modeDetails['offset']
        else:
            # Add to list of turned off modes
            modeStrOff += ", " + display + ": NULL"
    
    # concatenate list of modes
    modeStr += modeStrOff

    return modeStr[2:]

# calculate xrandr mode from NV metamode
def get_xrandr_resolution(modeData):

    maxX = 0
    maxY = 0

    for k,v in modeData['details'].iteritems():
        if v['enabled']:
            [resX,resY]=v['resolution'].split('x')
            [offX,offY]=v['offset'].split('+')
            maxX = max(int(resX)+int(offX),maxX)
            maxY = max(int(resY)+int(offY),maxY)

    return str(maxX) + "x" + str(maxY)

### Modify state ###
def switch_mode(mode_id,modeData):
    # ?? delete all metamodes except for the current and the new
    # Not sure why to delete these??

    xrandr_args = ['-s',get_xrandr_resolution(modeData),'-r',str(mode_id)]
    # call xrandr to select mode
    # print xrandr_args
    subprocess.check_output(["xrandr"]+xrandr_args)

    # delete old mode
    pass

