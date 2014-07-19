=====
Segpy
=====

The SEG Y file format is one of several standards developed by the Society of Exploration Geophysicists for storing
geophysical seismic data. It is an open standard, and is controlled by the SEG Technical Standards Committee, a
non-profit organization.

This project aims to implement an open SEG Y module in Python for transporting seismic data between SEG Y files and
Numpy arrays. Segpy is a package for reading, writing and manipulating SEG Y data in pure Python.

History
=======

Segpy is a fork of a seemingly abandoned Python SEG Y reader called `SegyPY <http://segymat.sourceforge.net/segypy/>`_
which was last updated in 2005. I couldn't get a response from the original author of SegyPY and since it the code was
under an LGPL license I took the decision in 2011 to fork and run a new project on Google Code, under a the name of
*Segpy* avoid confusion. In July 2014 the project was again migrated from a now defunct Mercurial repository on Google
Code to this Git repository on GitHub.

The aim of the revived project is to fix serious problems with the code base in the area of correctness and
performance, but also to update it to work with contemporary Python environments including Python 2.7 and Python 3.

**Pull requests, bug reports and suggestions for improvements are most welcome!**


Authors
=======

 * Robert Smallshire 2011 to date
 * Thomas Mejer Hansen 2005

The Ibm2Ieee conversion routines are developed and made availabe for SegyPY by Secchi Angelo, who thanks Howard
Lightstone and Anton Vredegoor for their help.
