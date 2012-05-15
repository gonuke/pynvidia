#!/usr/bin/python

import pynvidia
import sys


def build_dual_head_mode_list(dpy_modeDB):

    my_mode_list = []
    
    deviceData = list(dpy_modeDB.viewvalues())

    # define set of modes
    #  a) max res (width) on DPY #1
    mode_dict = {deviceData[0]['port']: {'enabled':True,
                                         'mode':deviceData[0]['maxResMode'],
                                         'resolution':deviceData[0]['maxResMode'],
                                         'offset':'0+0'} }
    mode_str = pynvidia.metamode_dict2string(pynvidia.rationalize_metamode_dict(mode_dict))
    my_mode_list.append(pynvidia.find_or_add(mode_str))

    if len(deviceData) > 1:
        #  b) max res on DPY #2 
        mode_dict = {deviceData[1]['port']: {'enabled':True,
                                             'mode':deviceData[1]['maxResMode'],
                                             'resolution':deviceData[1]['maxResMode'],
                                             'offset':'0+0'}  }
        mode_str = pynvidia.metamode_dict2string(pynvidia.rationalize_metamode_dict(mode_dict))
        my_mode_list.append(pynvidia.find_or_add(mode_str))

        #  c) max clone res on DPY #1 + DPY #2
        sharedModeList = deviceData[0]['modelist'].viewkeys() & deviceData[1]['modelist'].viewkeys()
        sharedMode = ''
        maxSharedX = 0
        
        for mode in sharedModeList:
            mode = mode.split('_')[0]
            if 'x' in mode:
                sharedX = int(mode.split('x')[0])
                if sharedX > maxSharedX:
                    maxSharedX = sharedX
                    sharedMode = mode
                
        mode_dict = {deviceData[0]['port']: {'enabled':True,
                                             'mode':sharedMode,
                                             'resolution':sharedMode,
                                             'offset':'0+0'},
                     deviceData[1]['port']: {'enabled':True,
                                             'mode':sharedMode,
                                             'resolution':sharedMode,
                                             'offset':'0+0'}   }
        mode_str = pynvidia.metamode_dict2string(mode_dict)
        my_mode_list.append(pynvidia.find_or_add(mode_str))

        #  d) max left to right extended desktop
        mode_dict = {deviceData[0]['port']: {'enabled':True,
                                             'mode':deviceData[0]['maxResMode'],
                                             'resolution':deviceData[0]['maxResMode'],
                                             'offset':'0+0'},
                     deviceData[1]['port']: {'enabled':True,
                                             'mode':deviceData[1]['maxResMode'],
                                             'resolution':deviceData[1]['maxResMode'],
                                             'offset': str(deviceData[0]['maxW']) + '+0' }  }
        
        mode_str = pynvidia.metamode_dict2string(mode_dict)
        my_mode_list.append(pynvidia.find_or_add(mode_str))
        
        #  e) (d) with swapped primary
        mode_dict = {deviceData[0]['port']: {'enabled':True,
                                             'mode':deviceData[0]['maxResMode'],
                                             'resolution':deviceData[0]['maxResMode'],
                                             'offset': str(deviceData[1]['maxW']) + '+0'},
                     deviceData[1]['port']: {'enabled':True,
                                             'mode':deviceData[1]['maxResMode'],
                                             'resolution':deviceData[1]['maxResMode'],
                                             'offset': '0+0' }  }
        
        mode_str = pynvidia.metamode_dict2string(mode_dict)
        my_mode_list.append(pynvidia.find_or_add(mode_str))
        
        #  f) max top to bottom extended desktop
        mode_dict = {deviceData[0]['port']: {'enabled':True,
                                             'mode':deviceData[0]['maxResMode'],
                                             'resolution':deviceData[0]['maxResMode'],
                                             'offset':'0+0'},
                     deviceData[1]['port']: {'enabled':True,
                                             'mode':deviceData[1]['maxResMode'],
                                             'resolution':deviceData[1]['maxResMode'],
                                             'offset': '0+' + str(deviceData[0]['maxH'])  }  }

        mode_str = pynvidia.metamode_dict2string(mode_dict)
        my_mode_list.append(pynvidia.find_or_add(mode_str))
        #  g) (f) with swapped primary
        mode_dict = {deviceData[0]['port']: {'enabled':True,
                                             'mode':deviceData[0]['maxResMode'],
                                             'resolution':deviceData[0]['maxResMode'],
                                             'offset': '0+' + str(deviceData[1]['maxH']) },
                     deviceData[1]['port']: {'enabled':True,
                                             'mode':deviceData[1]['maxResMode'],
                                             'resolution':deviceData[1]['maxResMode'],
                                             'offset': '0+0' }  }

        mode_str = pynvidia.metamode_dict2string(mode_dict)
        my_mode_list.append(pynvidia.find_or_add(mode_str))

    return my_mode_list


def cycle_modes(modeDB,custom_mode_list):

    current_mode_id = pynvidia.get_current_metamode()

    newModeIdx = 0

    if len(custom_mode_list) > 1:
        # find current mode in list
        modeIdx = 0
        foundIdx = -1
        # print custom_mode_list
        for mode_id in custom_mode_list:
            if mode_id == current_mode_id:
                foundIdx = modeIdx
                break
            else:
                modeIdx += 1
                
        if foundIdx > -1:
            # print custom_mode_list
            # print current_mode_id
            # print foundIdx
            newModeIdx = (foundIdx+1) % len(custom_mode_list)
    
    return custom_mode_list[newModeIdx]

def toggle_single_desktop_modes(modeDB):

    custom_mode_list = build_dual_head_mode_list(modeDB)

    return cycle_modes(modeDB,custom_mode_list[0:3])
        
def toggle_extended_desktop_modes(modeDB):

    custom_mode_list = build_dual_head_mode_list(modeDB)

    return cycle_modes(modeDB,custom_mode_list[0:2]+custom_mode_list[3:])


pynvidia.update_displays()
    
modeDB = pynvidia.build_modeDB()
metaModeDB = pynvidia.get_all_metamodes()

new_mode = -1

# print sys.argv

if (len(sys.argv) > 1):
    if (sys.argv[1] == '1'):
        new_mode = toggle_single_desktop_modes(modeDB)
    elif (sys.argv[1] == '2'):
        new_mode = toggle_extended_desktop_modes(modeDB)

if new_mode > 0:
    # print new_mode
    # print metaModeDB[new_mode]
    pynvidia.switch_mode(new_mode,metaModeDB[new_mode])

