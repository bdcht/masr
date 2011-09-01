#  -*- coding: utf-8 -*-
#  Copyright (C) 2008 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license

from  goocanvas import Canvas as GooCanvas
from  goocanvas import polyline_new_line,Grid
import gtk

#------------------------------------------------------------------------------
#  just a wrapper above GooCanvas class, with texture dict added.
#  we just wrap it so that introspection/debug is easy...
class  Canvas(GooCanvas):
    textures = {}

    def __init__(self,**args):
        GooCanvas.__init__(self,**args)
        self.scroll_to(0,0)
        # infinite world should replace scroll_region
        self.props.automatic_bounds=True

        self.root = self.get_root_item()

        polyline_new_line(self.root,-5,0,5,0,stroke_color='gray66')
        polyline_new_line(self.root,0,-5,0,5,stroke_color='gray66')

        self.zoom = False
        self.pan  = False
        self._grid = None
        self.grid()

        # GooCanvas will transmit all keyboard events to
        # its parent unless one of its item has focus.
        self.parent.connect_object("key_press_event",
                                   Canvas.eventhandler,self)
        self.parent.connect_object("key_release_event",
                                   Canvas.eventhandler,self)
        self.connect("event",Canvas.eventhandler)

    def eventhandler(self,e):
        print e.type
        if e.type == gtk.gdk.KEY_PRESS:
            kvn = gtk.gdk.keyval_name(e.keyval)
            if kvn == 'a':
                self.scroll_to(0,0)
            if kvn == 'Control_L':
                if not self.zoom:
                    print 'zoom on'
                    self.zoom = True
            elif kvn == 'plus' and self.zoom:
                self.props.scale *= 1.2
            elif kvn == 'minus' and self.zoom:
                self.props.scale *= 0.8
            return False
        elif e.type == gtk.gdk.KEY_RELEASE:
            if gtk.gdk.keyval_name(e.keyval) == 'Control_L':
                print 'zoom off'
                self.zoom = False
                return True
        elif e.type == gtk.gdk.SCROLL and self.zoom:
            if e.direction == gtk.gdk.SCROLL_UP:
                self.props.scale *= 1.2
            elif e.direction == gtk.gdk.SCROLL_DOWN:
                self.props.scale *= 0.8
            return True
        elif e.type == gtk.gdk.BUTTON_PRESS:
            print "click:(%d,%d)"%e.get_coords()
        return False

    def grid(self,dx=100,dy=100):
        if self._grid:
            pass
        else:
            self._grid=Grid(parent=self.root,
                    x=0,y=0,width=2000,height=2000,
                    x_step=dx,y_step=dy,
                    line_width=1,
                    stroke_color='gray88')


    # textures are shared by all engine objects with a classmethod :
    @classmethod
    def loadTexture(Canvas, path):
        if Canvas.textures.has_key(path) :
            surface = Canvas.textures[path]
        else:
            surface = self.image_load(path)
            Canvas.textures[path] = surface
        return surface

    # engine dependent method, should be overwritten:
    def image_load(self,path):
            raise NotImplementedError

