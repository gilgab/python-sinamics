# python-sinamics
Python codes to work with Siemens Sinamics inverters via Snap7 library.

This project contains a class definition for control/monitoring of
SINAMICS inverters via TCP/Ip using application layer S7 protocol.
For this, it utilizes the python-snap7 library.

The python-snap7 library has a python wrapper for
s7 communication/read/write functions of snap7 library.

The codes in "Main" folder are:
- sinamics.py: Class definition to work with Sinamics inverters.
- sinamics_graph.py: A function definition built upon the class Sinamics to obtain traces from the inverter.

# How to use
This code can be executed as a module (using import),
placing the desired "Main" folder files in your python lib packages folder.
For Unix, usually /usr/lib/pythonX.X/site-packages.
For Windowns, probably lib/site-packages in your Program Files
Python folder. If you are using virtualenv, should be something similar.

# Documentation
Complete information regarding snap7 and python-snap7
can be seen in the docs bellow:

https://github.com/gijzelaerr/python-snap7
https://python-snap7.readthedocs.io
snap7.sourceforge.net/home.html

More information regarding the s7 protocol, can be seen in:

gmiru.com/article/s7comm/
gmiru.com/article/s7comm-part2/
snap7.sourceforge.net/home.html

# Installation of snap7 library
For installation of snap7 library, see:

https://python-snap7.readthedocs.io/en/latest/installation.html
snap7.sourceforge.net/home.html

# Other info
The read/write request of SINAMICS inverter are
based in the article of number (Entry ID) 97550333
in the SIOS website (Siemens Industry Online Support).

For use with G120, inverter FW must be >= 4.7,
as article of item 50037141 in SIOS describe.

So far, inverters that I sucessfully tested with this code are:
- G120 (FW 4.7 SP10)
- V90 (FW 1.02.01)
