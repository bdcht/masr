#  -*- coding: utf-8 -*-
#  Copyright (C) 2008 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license

from  crcanvas import Canvas as CrCanvas
from  crcanvas import Panner,Zoomer,Line
import  gtk

#------------------------------------------------------------------------------
#  just a wrapper above CrCanvas class, with texture dict added.
#  we just wrap it so that introspection/debug is easy...
class  Canvas(CrCanvas):
    textures = {}

    def __init__(self,**args):
        CrCanvas.__init__(self,**args)
        # finite world init:
        #self.set_scroll_region(0,0,2000,2000)
        self.scroll_to(0,0)
        # infinite world should replace scroll_region
        self.set_scroll_factor(20,20)
        self.set_max_scale_factor(16,16)
        self.set_min_scale_factor(.0125,.0125)
        self.props.maintain_center = False

        self.panner = Panner(canvas=self)
        self.zoomer = Zoomer(canvas=self,
                             fill_color_rgba=0x8888ff22,
                             outline_color_rgba=0x22)
        self.zoomer.props.corner_to_corner = True
        self.zoomer.props.maintain_aspect = False
        self.grid = None
        self.root.add(Line(points=[-5,0,5,0],outline_color='gray66'))
        self.root.add(Line(points=[0,-5,0,5],outline_color='gray66'))
        self.connect("event",Canvas.eventhandler)

    def eventhandler(self,e):
        if e.type == gtk.gdk.KEY_PRESS:
            kvn = gtk.gdk.keyval_name(e.keyval)
            if kvn == 'a':
                self.scroll_to(0,0)
            if kvn == 'Control_L':
                self.zoomer.activate()
                self.root.set_z(self.zoomer.box,-1)
            elif kvn == 'plus' and self.zoomer.props.active:
                self.zoom(1.2,1.2)
            elif kvn == 'minus' and self.zoomer.props.active:
                self.zoom(.8,.8)
            return False
        elif e.type == gtk.gdk.KEY_RELEASE:
            if gtk.gdk.keyval_name(e.keyval) == 'Control_L':
                self.zoomer.deactivate()
                return True
        elif e.type == gtk.gdk.SCROLL and self.zoomer.props.active:
            if e.direction == gtk.gdk.SCROLL_UP:
                self.zoom(1.2,1.2)
            elif e.direction == gtk.gdk.SCROLL_DOWN:
                self.zoom(.8,.8)
            return True
        elif e.type == gtk.gdk.BUTTON_PRESS:
            print "click:(%d,%d)"%e.get_coords()
        return False

    def grid(self,dx=10,dy=10):
        if self.grid:
            self.grid.props.visible= not self.grid.props.visible
        else:
            pass


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

