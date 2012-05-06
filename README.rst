===================
Python NVidia tools
===================

by Paul Wilson (paul@nagus-wilson.net)

Based on PHP5 tools by redmoskito (http://ubuntuforums.org/showthread.php?t=922956)

*Requires* NVidia-supplied nv-control-dpy tool.  See instructions at: http://ubuntuforums.org/showthread.php?p=5809670

Python Module: pynvidia
------------------------

This module provides a number of python functions that populate
dictionaries of information about the diplay devices, device
modelines, and NVidia metamodes, but calling the nv-control-dpy tool
and parsing the results.

A dictionary of display ports and devices is generated with
get_displays(), returning a dictionary in which each key is the name
of a port (e.g. DFP-1, CRT-0, etc) and the value is the name of the
device connected at that port.

A dictionary of fundamental display modes is generated with
build_modeDB(), returning a dictionary in which each key is the name
of a connected device and the value is another dictionary with the
following information:

::

   'port' => string describing the port to which this device is attached
   'mask' => hex string returned by NVidia tools
   'maxResMode' => string referring to the video mode with maximum # of pixels
   'maxW' => integer width of maxResMode
   'maxH' => integer heigher of maxResMode
   'modelist' =>
        <mode> string identifying mode => list of mode data
                                          modeData[2] = width
					  modeData[6] = height

A dictionary of metamodes is generated with get_all_metamodes(),
returning a dictionary in which each key is an integer mode ID, and
each value is a dictionary of the following data:

::

    <key> => <value> : a variety of key/value pairs are parsed as is and stored
    'details' =>
         <port> string identifying port =>
                'enabled'    : Boolean indicating whether this port is active
                'mode'       : string resolution of viewable window
		'resolution' : string resolution of pannable mode
		'offset'     : string offset of this display



