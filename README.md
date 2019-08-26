# python-sinamics
Python codes to work with Siemens SINAMICS inverters via Snap7 library.

This project contains a class definition for control/monitoring of SINAMICS inverters via TCP/IP using application layer S7 protocol. For this, it utilizes the python-snap7 library.

The python-snap7 library has a python wrapper for
S7 communication/read/write functions of snap7 library.

The codes in "Main" folder are:
- sinamics.py : Class definition to work with SINAMICS inverters.
- sinamics_graph.py : A function definition built upon the class Sinamics to obtain traces from the inverter.

# How to use
This code can be executed as a module (using import), placing the desired "Main" folder files in your python lib packages folder:
- For Unix, usually /usr/lib/pythonX.X/site-packages.
- For Windowns, probably lib/site-packages in your Program Files (x86) Python folder. 
- If you are using virtualenv, should be something similar.

As documentation defines, python-snap7 library was built for python 2.7, with other versions not completely tested. The codes in this project were tested with python 2.7 only.

The needed libraries to run the codes:
- sinamics.py : snap7
- sinamics_graph.py : snap7, matplotlib, numpy, scipy.

# Installation of snap7 library
For installation of snap7 library, see:

(https://python-snap7.readthedocs.io/en/latest/installation.html)
(snap7.sourceforge.net/home.html)

# Documentation
Complete information regarding snap7 and python-snap7 can be seen in the docs bellow:

(https://github.com/gijzelaerr/python-snap7)
(https://python-snap7.readthedocs.io)
(snap7.sourceforge.net/home.html)

More information regarding the S7 protocol can be seen in:

(gmiru.com/article/s7comm/)
(gmiru.com/article/s7comm-part2/)
(snap7.sourceforge.net/home.html)
