=======
Segpy 2
=======

Status
======

Build status: rewrite branch:

.. image:: https://travis-ci.org/rob-smallshire/segpy.svg?branch=rewrite
    :target: https://travis-ci.org/rob-smallshire/segpy

What is Segpy?
==============

The SEG Y file format is one of several standards developed by the Society of Exploration Geophysicists for storing
geophysical seismic data. It is an open standard, and is controlled by the SEG Technical Standards Committee, a
non-profit organization.

This project aims to implement an open SEG Y module in Python for transporting seismic data between SEG Y files and
Python data structures in pure Python.

Segpy Versions
==============

Segpy 2.0 is a complete re-imagining of a SEG Y reader in Python and represents a complete break from Segpy 1.0 in terms
of the interface it presents to clients and the implementation behind those interfaces.   Segpy 1.0 should be considered
unmaintained legacy software. The present and future of Segpy is Segpy 2.