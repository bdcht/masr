# -*- coding: utf-8 -*-
# Copyright (C) 2008 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license


#------------------------------------------------------------------------------
class Window(object):
    """ main basic window class, needs an extending class providing init.
    """

    def __init__(self, app):
        self.app = app # window link back to application
        self.window = None
        self.canvas = None
        self.events = None
        self.gui    = None

    # mandatory methods, should be defined in extending classes :
    def initWindow(self):         pass
    def mainLoop(self):           pass

#------------------------------------------------------------------------------
# imports needed to let Window init Engine and Event manager:
import pygtk
pygtk.require('2.0')
import gtk

gtk.gdk.threads_init()

class gtkWindow(Window):
    """ pygtk based window, extending Window class
    """
    # called by Masr init :
    def initWindow(self):
        # we provide only the main gtk window here, not the drawing area:
        self.window = gtk.Window()
        self.window.set_title(self.app.title)
        # handler of events on the X11 window (close,kill,etc):
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(0)
        if self.app.fullScreen :
            self.window.fullscreen()
        else:
            # smallest window size allowed:
            self.window.set_size_request(*self.app.size)
        # add a vertical stacking box for menu/canvas/statusbar:
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        self.initGUI()
        self.initCanvas()

    def initGUI(self):
        from gui import gtkgui
        self.gui = gtkgui(self.app)
        self.vbox.pack_start(self.gui.menubar,0)
        self.vpan = gtk.VPaned()
        self.vbox.add(self.vpan)
        self.vbox.pack_end(self.gui.statusbar,0)

    def initCanvas(self):
        from canvas import Canvas
        # the canvas will be added to a scrollable window:
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(2)
        ## always show h,v scroll bars
        scrolled_window.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        # create canvas object which holds the layout:
        self.canvas = Canvas(parent=scrolled_window)
        #scrolled_window.add(self.canvas)
        #scrolled_window.connect_object("key_press_event",
        #        kbdhandler,self.canvas)
        # add it to vpan widget:
        if not self.vpan:
            self.vpan = gtk.VPaned()
            self.vbox.add(self.vpan)
        self.vpan.add(scrolled_window)

    def mainLoop(self):
        # create the gtk window and everything in it:
        self.window.show_all()
        # let gtk handle the event loop:
        gtk.main()
