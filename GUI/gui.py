#!/usr/bin/python2.4
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Small test to demonstrate glade.XML.signal_autoconnect on an instance
#

import pygtk
pygtk.require('2.0')

import gtk, gtk.glade

import segypy

class SimpleTest:
	def __init__(self):
		# xml = gtk.glade.XML('test2.glade')
		xml = gtk.glade.XML('test/test.glade')
		xml.signal_autoconnect(self)
	
	def on_new1_activate(self, button):
		print 'foo'
		self.segy = segypy.readSegy('../data_4byteINT.segy')
		print 'foo2'

test = SimpleTest()
gtk.main()
