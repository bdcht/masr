# -*- coding: utf-8 -*-
# Copyright (C) 2008 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license

import pygtk
pygtk.require('2.0')
import gtk

#------------------------------------------------------------------------------
class gtkgui(object):
    def __init__(self,app,conf=None):
        self.app = app
        self.make_Menubar(conf)
        self.make_Statusbar()

    def make_Menubar(self,uidef=None):
        """
        <ui>
          <menubar>
            <menu action="File">
              <menuitem action="Open" />
              <menuitem action="New" />
              <menuitem action="Save" />
              <menuitem action="Quit" />
            </menu>
            <menu action="View">
              <menu action="Canvas">
                <menuitem action="Panner" />
                <menuitem action="ZoomIn" />
                <menuitem action="ZoomOut" />
                <menuitem action="ZoomFit" />
                <menuitem action="Zoom100" />
              </menu>
              <menuitem action="Status" />
            </menu>
            <menu action="Tools">
              <menuitem action="Server" />
            </menu>
          </menubar>
        </ui>
        """
        self.ui = gtk.UIManager()
        if not isinstance(uidef,str): uidef = self.make_Menubar.func_doc
        self.ui.add_ui_from_string(uidef)
        # make menubar action group:
        ag = gtk.ActionGroup('menubar')
        ag.add_actions(
          [ ('File', None, '_File'),
              ('Open', gtk.STOCK_OPEN, '_Open File...', None, '', FileOpen),
              ('New' , gtk.STOCK_NEW, '_New File...', None, '', FileNew),
              ('Save', gtk.STOCK_SAVE, '_Save File', None, '', FileSave),
              ('Quit', gtk.STOCK_QUIT, '_Quit', None, '', gtk.main_quit),
            ('View', None, '_View'),
              ('Canvas' , None, '_Canvas'),
              ('ZoomIn' , gtk.STOCK_ZOOM_IN, 'Zoom In', None, '', Zoom),
              ('ZoomOut', gtk.STOCK_ZOOM_OUT, 'Zoom Out', None, '', Zoom),
              ('ZoomFit', gtk.STOCK_ZOOM_FIT, 'Zoom Fit', None, '', Zoom),
              ('Zoom100', gtk.STOCK_ZOOM_100, 'Zoom 1:1', None, '', Zoom),
            ('Tools', None, '_Tools'),
          ], user_data=self.app)
        ag.add_toggle_actions(
          [
            ('Panner', None, 'Mouse _Panner', '<Control>p', ''),
            ('Status' , None, 'Status Bar', '', ''),
            ('Server' , None, 'Python server', '', ''),
          ], user_data=self.app)
        self.ui.insert_action_group(ag,0)
        # the Info menu item is only active when a session is opened:
        self.ui.get_widget('/ui/menubar/Tools/Server').set_sensitive(False)
        # create MenuBar widget:
        self.menubar = gtk.HBox()
        self.menubar.pack_start(self.ui.get_widget('/ui/menubar'))
        q = gtk.Entry(max=24)
        c = gtk.EntryCompletion()
        q.set_completion(c)
        # FIX: completion widget should be prepared with a Liststore (see doc)
        q.set_has_frame(True)
        q.set_width_chars(24)
        self.menubar.pack_end(q,expand=False,padding=2)
        def query(w):
            print 'last query was: ',w.get_text()
            self.last_query = w.get_text()
            w.set_position(0)
        q.connect("activate",query)
        # setup the panner activate/deactivate on mouse 2 button:
        def pannertoggle(cmi):
            if cmi.get_active():
                self.app.screen.canvas.panner.props.button = 2
            else:
                self.app.screen.canvas.panner.props.button = 0

        q=self.ui.get_widget('/ui/menubar/View/Canvas/Panner')
        q.set_active(True)
        q.connect("toggled",pannertoggle)
        # add accel group to the main window:
        self.app.screen.window.add_accel_group(self.ui.get_accel_group())

    def make_Statusbar(self):
        self.statusbar = gtk.Statusbar()
        self.statusbar.set_has_resize_grip(0)
        self.statusbar.push(self.statusbar.get_context_id("general"),
                            "statusbar created")
        def showhide(cmi):
            if cmi.get_active():
                self.statusbar.show_all()
            else:
                self.statusbar.hide_all()
        _Status = self.ui.get_widget('/ui/menubar/View/Status')
        _Status.set_active(True)
        _Status.connect("toggled",showhide)
        self.progressbar = gtk.ProgressBar()
        self.statusbar.pack_end(self.progressbar,False,padding=2)

    def message(self,line):
        self.statusbar.push(self.statusbar.get_context_id("general"),line)
#------------------------------------------------------------------------------

def FileOpen(action, app):
      filew = gtk.FileChooserDialog("Choose a file to open...",
                                    app.screen.window,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    buttons=(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN,
                                             gtk.RESPONSE_OK)
                                   )
      resp = filew.run()
      if resp == gtk.RESPONSE_OK:
          fn = filew.get_filename()
          app.screen.gui.message( 'file %s selected'%fn )
          filew.destroy()
          if app.session:
              alert = gtk.MessageDialog(app.screen.window,
                                        gtk.DIALOG_MODAL,
                                        gtk.MESSAGE_WARNING,
                                        gtk.BUTTONS_YES_NO,
                                        'Cancel current session ?'
                                        )
              resp2 = alert.run()
              if resp2 == gtk.RESPONSE_YES:
                  app.session.clean()
                  app.session=None
              alert.destroy()
          if app.session is None:
              for p in app.plugins:
                  if hasattr(p,'Session') and fn.endswith(p.Session.filetype):
                      app.session = p.Session(fn,app)
      elif resp == gtk.RESPONSE_CANCEL:
          app.screen.gui.message( 'dialog closed, no files selected' )
          filew.destroy()

def FileNew(action,app):
    app.screen.gui.message('New File is not supported yet !')

def FileSave(action,app):
    filew = gtk.FileChooserDialog("Choose a file name...",
                                  app.screen.window,
                                  gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_SAVE,
                                           gtk.RESPONSE_OK)
                                 )
    resp = filew.run()
    if resp == gtk.RESPONSE_OK:
        fn = filew.get_filename()
        app.screen.gui.message('Save File (%s) not supported yet !'%fn)
    elif resp == gtk.RESPONSE_CANCEL:
        app.screen.gui.message( 'dialog closed, file not saved' )
    filew.destroy()

#------------------------------------------------------------------------------

def Zoom(action,app):
    canvas = app.screen.canvas
    if isinstance(action,gtk.Action):
        action = action.get_name()
    if   action == 'ZoomIn':  canvas.zoom(1.2,1.2)
    elif action == 'ZoomOut': canvas.zoom(.8,.8)
    elif action == 'ZoomFit': canvas.zoom_world()
    elif action == 'Zoom100':
        m = canvas.root.get_simple_transform()
        # TODO: use cairo Matrix :
        #coef_x,coef_y = m.transform_distance(1,1)
        #canvas.zoom(1./coef_x,1./coef_y)

#------------------------------------------------------------------------------

