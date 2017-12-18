=======
Segpy 2
=======

Segpy is open source software created by Sixty North and licensed under the GNU Affero General Public License.

Alternative commercial license terms are available from Sixty North AS if you wish to redistribute Segpy as
part of a proprietary closed source product or deliver software software-as-a-service (SaaS) using Segpy as part
of a proprietary closed source service.

Status
======

Build status:

.. image:: https://travis-ci.org/sixty-north/segpy.svg?branch=master
    :target: https://travis-ci.org/sixty-north/segpy

.. image:: https://readthedocs.org/projects/segpy/badge/?version=latest
    :target: http://segpy.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/sixty-north/segpy/badge.svg?branch=master
    :target: https://coveralls.io/github/sixty-north/segpy?branch=master


What is Segpy?
==============

The SEG-Y file format is one of several standards developed by the Society of Exploration Geophysicists for storing
geophysical seismic data. It is an open standard, and is controlled by the SEG Technical Standards Committee, a
non-profit organization.

This project aims to implement an open SEG-Y module in Python 3 for transporting seismic data between SEG-Y files and
Python data structures in pure Python.


Contributing
============

The easiest way to contribute is to use Segpy submit reports for defects or any other issues you come across. Please
see `CONTRIBUTING.rst <https://github.com/sixty-north/segpy/blob/master/CONTRIBUTING.rst>`_ for more details.


Development
===========

Segpy was created by – and to meet the needs of – Sixty North.  If you require additional features, improved
performance, portability to earlier versions of Python, or specific defects fixed (such defects are marked 'unfunded'
in the GitHub issue tracker) Sixty North's experienced *Segpy* maintainers may be available to perform
funded development work.  Enquire with Sixty North at http://sixty-north.com.


Segpy Versions
==============

Segpy 2.0 is a complete re-imagining of a SEG-Y reader in Python 3 and represents a complete break from any and all older
versions of Segpy.  No attempt has been made to maintain API compatibility with earlier versions of Segpy and no code is
shared across versions.  Although earlier versions of Segpy were open source, they were never 'released' as such.
Earlier versions of Segpy are deprecated and completely unsupported.
