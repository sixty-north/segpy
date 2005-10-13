#!/usr/bin/env python
#Licence: GPLv2.0
#Copyright: Dave Aitel

import sys

try:
  import pygtk
  #tell pyGTK, if possible, that we want GTKv2
  pygtk.require("2.0")
except:
  print "You need to install pyGTK or GTKv2 or set your PYTHONPATH correctly"
  print "try: export PYTHONPATH=/usr/local/lib/python2.2/site-packages/"
  sys.exit(1)
  
import gtk
import gtk.glade
import segypy

#now we have both gtk and gtk.glade imported
#Also, we know we are running GTKv2

def insert_row(model,parent,firstcolumn,secondcolumn):
    myiter=model.insert_after(parent,None)
    model.set_value(myiter,0,firstcolumn)
    model.set_value(myiter,1,secondcolumn)
    return myiter

class appgui:
  def __init__(self):
    """
    In this init we are going to display the main serverinfo window
    """
    gladefile="project1.glade"
    windowname="serverinfo"    
    self.wTree=gtk.glade.XML (gladefile,windowname)
    #we only have one callback to register, but you could register
    #any number, or use a special class that 
    #automatically registers all callbacks
    dic = { "on_button1_clicked" : self.button1_clicked,
            "on_serverinfo_destroy" : (gtk.mainquit)}
    self.wTree.signal_autoconnect (dic)
    
    self.logwindowview=self.wTree.get_widget("textview1")
    self.logwindow=gtk.TextBuffer(None)
    self.logwindowview.set_buffer(self.logwindow)
    
    import gobject
    self.treeview=self.wTree.get_widget("treeview1")
    self.treemodel=gtk.TreeStore(gobject.TYPE_STRING,
                                 gobject.TYPE_INT,
                                 gobject.TYPE_STRING)
    self.treeview.set_model(self.treemodel)

    self.treeview.set_headers_visible(True)

    renderer=gtk.CellRendererText()
    column=gtk.TreeViewColumn("Name",renderer, text=0)
    column.set_resizable(True)
    self.treeview.append_column(column)

    renderer=gtk.CellRendererText()    
    column=gtk.TreeViewColumn("Description",renderer, text=1)
    column.set_resizable(True)
    self.treeview.append_column(column)

    self.treeview.show()

    model=self.treemodel
    treeSTH=insert_row(model,None,'Segy Trace Header', '')
    for key in segypy.STH_def.keys(): 
    	insert_row(model,treeSTH,key, 'An Empty Row')
    treeSH=insert_row(model,None,'Segy Header', 'SH')
    for key in segypy.SH_def.keys(): 
    	insert_row(model,treeSH,key, 'An Empty Row')


    
    return
  
  
  #####CALLLBACKS
  def button1_clicked(self,widget):
    print "button clicked"
    host=self.wTree.get_widget("entry1").get_text()
    port=int(self.wTree.get_widget("spinbutton1").get_value())
    if host=="":
      return
    import urllib
    page=urllib.urlopen("http://"+host+":"+str(port)+"/")
    data=page.read()
    try:
	#this changed in a revision of pyGTK2
        self.logwindow.insert_at_cursor(data,len(data))
    except:
	self.logwindow.insert_at_cursor(data)
    #print data
    return
  

app=appgui()
gtk.main()



