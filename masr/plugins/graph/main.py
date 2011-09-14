# -*- coding: utf-8 -*-

# Copyright (C) 2010 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license



import pygtk
import gtk
import gobject

from grandalf.graphs import Vertex,Edge,Graph
from grandalf.layouts import SugiyamaLayout,DigcoLayout
from grandalf.routing import *
from grandalf.utils import median_wh,Dot

from items import *

# start is called when Masr is 'run', to modify GUI/Canvas elements
# with plugin-specific menus, keybindings, canvas options, etc. 
def start(pfunc,app,**kargs):
    if app.session: return
    app.screen.gui.message("plugin graph started by %s"%pfunc)
    al = kargs['args']
    sg = comp = 0
    gclass = CGraph
    N = None
    for i,arg in enumerate(al):
        if arg.endswith(Session.filetype):
            if not app.session:
                app.session = Session(arg,app)
        elif arg == '-sg':
            sg = int(al[i+1])
        elif arg == '-c':
            comp = int(al[i+1])
        elif arg == '-digco':
            gclass = DGraph
        elif arg == '-N':
            N = int(al[i+1])
    if app.session:
        assert sg<len(app.session.L)
        app.session.g = ast2Graph(app.session.L[sg])
        assert comp<len(app.session.g.C)
        app.session.cg = gclass(app.screen.canvas,app.session.g.C[comp])
        if N>0:
            app.session.cg.Draw(N)
        else:
            app.session.cg.Draw()

def end(pfunc,app,**kargs):
    pass

# Session class allows Masr GUIs' File menu to Open a file with matching
# extensions for a new plugin session on this file's data.
class Session(object):
    filetype = ('.dot',)
    def __init__(self,filename,app):
        self.app = app
        self.filename = filename
        self.dot = Dot()
        self.L = self.dot.read(filename)
        self.scene = None

    def info(self):
        for s in self.L:
            print s

def ast2Graph(ast):
    V={}
    E=[]
    # create Vertex and Vertex.view for each node in ast :
    for k,x in ast.nodes.iteritems():
        try:
            label = x.attr['label']
        except (KeyError,AttributeError):
            label = x.name
        v = dotnode(label)
        V[x.name] = v
    edgelist = []
    # create Edge and Edge_basic for each edge in ast:
    for e in ast.edges: edgelist.append(e)
    for edot in edgelist:
        v1 = V[edot.n1.name]
        v2 = V[edot.n2.name]
        e = Edge(v1,v2)
        e.view = Edge_basic(v1.view,v2.view,head=ast.direct)
        e.view.props.line_width = 2
        E.append(e)
    return Graph(V.values(),E,directed=ast.direct)

def dotnode(seq):
    _start = Vertex(seq)
    _start.view = Node(_start)
    return _start

#------------------------------------------------------------------------------
# SceneBasic is a VertexViewer for Graph and a Node_basic for the canvas:
class Node(Node_codeblock):
    def __init__(self,o):
        self.o = o
        label = o.data
        Node_codeblock.__init__(self,label.replace('\l','\n'))
        #self.codebox.props.fill_color = 'blue'
        self.w,self.h = self.get_wh()

    def get_xy(self):
        return (self.props.x,self.props.y)
    def set_xy(self,xy):
        self.props.x,self.props.y = xy
        self.props.matrix = self.matrix
        #self.cx.props.matrix = self.matrix
    xy = property(get_xy,set_xy)

#------------------------------------------------------------------------------
# CGraph is simply a SugiyamaLayout extended with adding nodes and edges views
# on the current canvas and dealing with mouse/keyboard events.
# FIXME: should inherit from Blit rather than Item but this leads to segfault
class CGraph(SugiyamaLayout):

    def __init__(self,c,g):
        #Blit.__init__(self,canvas=c,scale_factor=10,test_image=False)
        self.parent = c
        #c.root.add(self)
        SugiyamaLayout.__init__(self,g)
        self.route_edge = route_with_lines
        self.xspace,self.yspace = median_wh([v.view for v in g.V()])

    def Draw(self,N=1):
        gr = self.g
        self.init_all()
        self.draw(N)
        for e in self.alt_e: e.view.props.outline_color='red'
        for v in gr.sV: self.connect_add(v.view)
        for e in gr.sE:
                self.parent.root.add(e.view)
                # Blit case do: self.add(e.view)
                #self.parent.root.set_z(e.view,1)
                # move edge start/end to CX points:
                e.view.update_points()

    def connect_add(self,item):
        item.connect_object_after("event",CGraph.eventhandler,self,item)
        #item.code.props.visible = False
        self.parent.root.add(item)
        # Blit case do: self.add(item)

    def disconnect(self,item):
        item.disconnect_by_func(CGraph.eventhandler)

    def remove(self,item):
        #import gc
        #gc.set_debug(gc.DEBUG_LEAK)
        #gc.collect()
        Blit.remove(self,item)
        for e in item.cx.registered[:]:
            for cx in e.cx: cx.unregister(e)
            self.c.root.remove(self,e)

    def clean(self):
        for v in self.g.sV:
            self.c.root.remove(v.view)

    # Scene-Wide (default) event handler on items events:
    def eventhandler(self,e,cr,pick_item,obj):
        self.selected=obj
        if e.type == gtk.gdk.KEY_PRESS:
            if e.keyval == ord('p'):
                for l in self.layers:
                    for v in l:
                        v.view.xy = (self.grx[v].x[self.x],v.view.xy[1])
                self.draw_edges()
            if e.keyval == ord(' '):
                try:
                    mvmt=self.drawer.next()
                    if mvmt!=None:
                        for x in mvmt:
                            if hasattr(x.view,'shadbox'):
                                x.view.shadbox.props.fill_color='green'
                except AttributeError:
                    self.drawer=self.draw_step()

#------------------------------------------------------------------------------
# DGraph is simply a DigcoLayout extended with adding nodes and edges views
# on the current canvas and dealing with mouse/keyboard events.
# FIXME: should inherit from Blit rather than Item but this leads to segfault
class DGraph(DigcoLayout):
    def __init__(self,c,g):
        self.parent = c
        DigcoLayout.__init__(self,g)

    def Draw(self,N=None):
        gr = self.g
        self.init_all()
        self.draw(N)
        for v in gr.sV:
            self.connect_add(v.view)
        for e in gr.sE:
            self.parent.root.add(e.view)
            # Blit case do: self.add(e.view)
            #self.parent.root.set_z(e.view,1)
            # move edge start/end to CX points:
            e.view.update_points()

    def connect_add(self,item):
        item.connect_object_after("event",DGraph.eventhandler,self,item)
        #item.code.props.visible = False
        self.parent.root.add(item)
        # Blit case do: self.add(item)

    def disconnect(self,item):
        item.disconnect_by_func(DGraph.eventhandler)

    def remove(self,item):
        #import gc
        #gc.set_debug(gc.DEBUG_LEAK)
        #gc.collect()
        Blit.remove(self,item)
        for e in item.cx.registered[:]:
            for cx in e.cx: cx.unregister(e)
            self.c.root.remove(self,e)

    def clean(self):
        for v in self.g.sV:
            self.c.root.remove(v.view)

    # Scene-Wide (default) event handler on items events:
    def eventhandler(self,e,cr,pick_item,obj):
        self.selected=obj
        if e.type == gtk.gdk.KEY_PRESS:
            if e.keyval == ord(' '):
                try:
                    mvmt=self.drawer.next()
                    if mvmt!=None:
                        for x in mvmt:
                            if hasattr(x.view,'shadbox'):
                                x.view.shadbox.props.fill_color='green'
                    else:
                        self.app.screen.gui.message("drawer terminated")
                except AttributeError:
                    self.drawer=self.draw_step()
