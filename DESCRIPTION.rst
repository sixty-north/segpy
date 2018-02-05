The SEG Y file format is one of several standards developed by the Society of Exploration Geophysicists for storing
geophysical seismic data. It is an open standard, and is controlled by the SEG Technical Standards Committee, a
non-profit organization.

This project aims to implement an open SEG Y module in Python for transporting seismic data between SEG Y files and
Python data structures in pure Python.


Status
======

*Segpy 2* is currently in alpha, so expect rough edges. That said, it seems to broadly work and is largely feature
complete.


What It Does
============

How To Get It
=============

*Segpy* is available on the Python Package index and can be installed with ``pip``::

  $ pip install segpy


Requirements
============

*Segpy 2* work with Python 3.5 and higher.  For the majority of use *Segpy 2* has no external
dependencies.  Optional modules with further dependencies such as *Numpy* are included in the ``segpy.ext`` package of
extras.
