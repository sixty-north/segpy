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


import matplotlib 
matplotlib.use('GTK') 
from matplotlib.figure import Figure 
from matplotlib.axes import Subplot 
from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar 
from matplotlib.numerix import arange, sin, pi 

import Numeric as numpy

import gtk, gtk.glade

import segypy


def insert_row(model,parent,firstcolumn,secondcolumn,thirdcolumn):
		myiter=model.insert_after(parent,None)
		model.set_value(myiter,0,firstcolumn)
		model.set_value(myiter,1,secondcolumn)
		model.set_value(myiter,2,thirdcolumn)
#		print secondcolumn
#		return myiter

def update_segyplot(self):
		self.figure = Figure(figsize=(6,4), dpi=72)
		self.axis = self.figure.add_subplot(111) 
		self.axis.set_xlabel('Trace Header') 
		self.axis.set_ylabel('Time [s]') 
		self.axis.set_title(self.segy[1]['filename']) 
		self.axis.grid(True) 
		self.axis.imshow(self.segy[0])
		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea 
		self.canvas.show() 

		self.graphview = self.xml.get_widget("vbox4")
		self.graphview.pack_start(self.canvas, True, True)


def update_segyheader(self):
		import gobject

		self.treeview = self.xml.get_widget("treeview1")
		self.treemodel = gtk.TreeStore(gobject.TYPE_STRING,
											gobject.TYPE_STRING,
											gobject.TYPE_STRING)
		self.treeview.set_model(self.treemodel)
		self.treeview.set_headers_visible(True)

		# COLUMN 1
		renderer= gtk.CellRendererText()
		self.tvcolumn1 = gtk.TreeViewColumn('Name', renderer, text=0)
		self.tvcolumn1.set_resizable(True)
		self.treeview.append_column(self.tvcolumn1)

		# COLUMN 2
		renderer= gtk.CellRendererText()
		self.tvcolumn2 = gtk.TreeViewColumn('Meaning', renderer, text=1)
		self.tvcolumn2.set_resizable(True)
		self.treeview.append_column(self.tvcolumn2)

		# COLUMN 3
		renderer= gtk.CellRendererText()
		self.tvcolumn3 = gtk.TreeViewColumn('Value', renderer, text=2)
		self.tvcolumn3.set_resizable(True)
		self.treeview.append_column(self.tvcolumn3)

	
		# INSERT INTO TREEMODEL
		self.SHtree= {"init": 1}
		for key in segypy.SH_def.keys(): 
				SHkey=segypy.SH_def[key]
				if (SHkey.has_key('descr')):
						descr = segypy.SH_def[key]['descr'][0][self.segy[1][key]]
				else:
						descr = ''
				insert_row(self.treemodel,None,key,descr,self.segy[1][key])

		self.treeview.show()

def update_segytraceheader(self,itrace=1):
		import gobject

		self.treeview = self.xml.get_widget("treeview2")
		self.treemodel = gtk.TreeStore(gobject.TYPE_STRING,
											gobject.TYPE_STRING,
											gobject.TYPE_STRING)
		self.treeview.set_model(self.treemodel)
		self.treeview.set_headers_visible(True)

		# COLUMN 1
		renderer= gtk.CellRendererText()
		self.tvcolumn1 = gtk.TreeViewColumn('Name', renderer, text=0)
		self.tvcolumn1.set_resizable(True)
		self.treeview.append_column(self.tvcolumn1)

		# COLUMN 2
		renderer= gtk.CellRendererText()
		self.tvcolumn2 = gtk.TreeViewColumn('Meaning', renderer, text=1)
		self.tvcolumn2.set_resizable(True)
		self.treeview.append_column(self.tvcolumn2)

		# COLUMN 3
		renderer= gtk.CellRendererText()
		self.tvcolumn3 = gtk.TreeViewColumn('Value', renderer, text=2)
		self.tvcolumn3.set_resizable(True)
		self.treeview.append_column(self.tvcolumn3)

	
		# INSERT INTO TREEMODEL
		self.STHtree= {"init": 1}
		for key in segypy.STH_def.keys(): 
				STHkey=segypy.STH_def[key]
				if (STHkey.has_key('descr')):
						try:
							descr = segypy.STH_def[key]['descr'][0][self.segy[2][key][itrace-1]]
						except:
							descr='Not Defined'
				else:
						descr = ''
				insert_row(self.treemodel,None,key,descr,self.segy[2][key][itrace-1])

		self.treeview.show()


class SimpleTest:
	def __init__(self):
		# xml = gtk.glade.XML('test2.glade')
#		self.xml = gtk.glade.XML('test/test.glade')
		self.xml = gtk.glade.XML('segygui/segygui.glade')
		self.xml.signal_autoconnect(self)
	

	def on_open1_activate(self, button):
		dialog = gtk.FileChooserDialog("Open..",
			None,
			gtk.FILE_CHOOSER_ACTION_OPEN,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
			gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("SEG-Y files")
		filter.add_pattern("*.segy")
		filter.add_pattern("*.sgy")
		filter.add_pattern("*.seg-y")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("SU files")
		filter.add_pattern("*.su")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			print dialog.get_filename(), 'selected'
			filename  = dialog.get_filename()
			dialog.destroy()
			self.segy = segypy.readSegy(filename)
		
			update_segyheader(self)	
			update_segytraceheader(self)
			update_segyplot(self)

	def on_new1_activate(self, button):
		self.segy = segypy.readSegy('../data_4byteINT.segy')
		update_segyheader(self)
		update_segytraceheader(self,1)
		update_segyplot(self)


test = SimpleTest()

gtk.main()
