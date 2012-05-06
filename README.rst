===================
Python NVidia tools
===================

by Paul Wilson (paul@nagus-wilson.net)

Based on PHP5 tools by redmoskito (http://ubuntuforums.org/showthread.php?t=922956)

*Requires* NVidia-supplied nv-control-dpy tool.  See instructions at:
http://ubuntuforums.org/showthread.php?p=5809670

Motivation
----------

In fall 2010, 12 years since I had last relied on Linux as my primary
OS, I returned to Linux on my brand new HP 8440p Elitebook.  It was
equipped with an NVidia graphics card to enable some of the intensive
CAD manipulation I intended to do.

I quickly found, however, that while NVidia did a good job of
delivering high performance kernel modules to support their graphics
cards, they didn't integrate well into the normal display switching
tools of the Ubuntu 10.10 system I was using.  Since I have external
displays at both by office and my home office, and I occasionally use
projectors in common conference rooms, I wanted to be able to easily
switch between the different display options.  Some of those
configurations include:

- laptop LCD only (with resolution A)
- external office LCD only (with resolution B)
- external home office LCD only (with resolution C)
- clone to extnernal project (with resolution D)
- extended desktop across office/home office LCD

and so on. Moreover, in my ideal world, the computer would detect all
these changes at various time including booting, waking from suspend,
waking from hibernation, and even hot docking/undocking in a docking
station.

I scoured the net only to find a variety of convoluted-seeming
schemes, most based on the nv-control-dpy tool that NVidia distributes
with its settings tool source code.  At the time, it seemed as though
most of these relied on my learning more about video modes and
metamodes that really wanted to.  (Given my experience with these
developments here, it probably wasn't that much to learn, but still
more than I should have needed to!)

I managed to accomplish a solution that was about 65% of what I
wanted.  I added the metamodes for all the scenarios that I most
typically experience and then used xrandr to choose between them,
binding some particular options to special key combinations.  The main
problem with this solution was that I had no ability to easily adapt
to settings not identified a priori and was forced to use the
effective but tedious NVidia settings tool.

After the most recent OS upgrade (Ubunutu 12.04), I decided it was
time to tackle this for once and for all.  Available at that time, and
still available now in the archives, was a set of PHP5 tools that
invoked the nv-control-dpy tool and parsed its results to accomplish a
variety of tasks.  I decided to build a Python module that would
provide the basic functionality necessary for this mode switching and
use that to accomplish what I wanted.

One of the key goals here is not avoid the need for hard-coded screen
resolutions or options.  The goal is to discover the available
resolutions dynamically in order to generate a set of metamodes based
on some heuristics.


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


Sample Applets
--------------

With these dictionaries fully populated, and tools to add additional
metamodes to the previous set of modes, I was able to create brief
scripts that accomplish my particular aims and include them as
samples.

*build_dual_head_mode_list()*

Given my use cases, I am interested in first being able to dynamically
identify all the attached display devices (pynvidia.probe_displays())
and include them in my metamodes (pynvidia.dynamic_twinview()),
allowing me to detect the available devices at any time despite
changes since boot-time.  Once I have build the list of modelines for
these devices (pynvida.build_modeDB()), I can use that information at
a fairly high level to build the metamodes that are interesting to me.

Since I assume that I can only have 2 devices attached at a time (this
will need to be updated if/when I ever use the HDMI to make this an
invalid assumption), I have the following 7 modes that are of interest to me:

- internal LCD only
- external LCD only (discover resolution dynamically)
- clone internal/external (discover largest common resolution dynamically)
- dual desktop (dynamically discover resolution in all cases)
   - internal left of external
   - internal right of external
   - internal above external
   - internal below external

Using the information in the modeline database, I can generate the
metamode information that describes each of these.  I then add it to
the available metamodes, if not already present (pynvidia.find_or_add()).

*cylce_modes()*

Given a list of mode IDs, it is easy to cycle through them.  First I
search for the current mode in the list, and then find the next mode
(modulus the first 3 modes) and return that, to be invoked by
pynvidia.switch_mode().

*toggle_single_desktop_modes()*

With the list of available modes in a predictable order, it is
possible to write methods that will cycle through these modes in
predictable ways.  Most laptops have some hot-key combination that
cycles through the first three modes:

- internal LCD only
- external LCD only (discover resolution dynamically)
- clone internal/external (discover largest common resolution dynamically)

By passing this sub-list to cycle_modes(), I can replicate that.

*toggle_extended_desktop_modes()*

By passing a list to cycle_modes() that includes everything except the
cloned mode, I can cycle through the extended desktop modes also.

TODO
----

- Probably should determine if/how to clean up modes that are no longer valid.

- Having bound some of these to certain key combinations, the next step is to have them invoked automatically under certain state changing situations:

   - wake from suspend
   - hot docking
   - hot undocking

