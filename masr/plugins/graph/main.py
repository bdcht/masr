# -*- coding: utf-8 -*-

# Copyright (C) 2010 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license



import gtk

from grandalf.graphs import Vertex,Edge,Graph
from grandalf.layouts import SugiyamaLayout
from grandalf.routing import *
from grandalf.utils import median_wh,Dot

from .items import *

# start is called when Masr is 'run', to modify GUI/Canvas elements
# with plugin-specific menus, keybindings, canvas options, etc. 
def start(pfunc,app,**kargs):
  app.screen.gui.message("plugin graph started by %s"%pfunc)
  al = kargs['args']
  sg = comp = 0
  step = False
  cons = False
  N=1
  for i,arg in enumerate(al):
    if arg.endswith(Session.filetype):
        if not app.session:
          app.session = Session(arg,app)
    if arg == '-sg':
      sg = int(al[i+1])
    if arg == '-c':
      comp = int(al[i+1])
    if arg == '-s':
      step = True
    if arg == '-N':
      N = int(al[i+1])
    if arg == '-ce':
      cons=True
  if app.session:
    assert sg<len(app.session.L)
    app.session.g = ast2Graph(app.session.L[sg])
    assert comp<len(app.session.g.C)
    app.session.cg = CGraph(app.screen.canvas,app.session.g.C[comp])
    app.session.cg.Draw(N,stepflag=step,constrained=cons)

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
    v = dotnode(label.strip('"\n'))
    V[x.name] = v
  edgelist = []
  # create Edge and Edge_basic for each edge in ast:
  for e in ast.edges: edgelist.append(e)
  for edot in edgelist:
    v1 = V[edot.n1.name]
    v2 = V[edot.n2.name]
    e = Edge(v1,v2)
    e.view = Edge_basic(v1.view,v2.view,head=True)
    e.view.set_properties(line_width = 2)
    E.append(e)
  return Graph(V.values(),E)

def dotnode(seq):
  _start = Vertex(seq)
  v = _start.view = Node_codeblock(_start.data.replace('\l','\n'))
  v.w,v.h = v.get_wh()
  return _start

#------------------------------------------------------------------------------
# CGraph is simply a SugiyamaLayout extended with adding nodes and edges views
# on the current canvas and dealing with mouse/keyboard events.
class CGraph(SugiyamaLayout):

  def __init__(self,c,g):
    self.parent = c
    SugiyamaLayout.__init__(self,g)
    self.route_edge = route_with_lines
    self.dx,self.dy = 5,5
    self.dirvh=0
    c.parent.connect_object("button-press-event",CGraph.eventhandler,self)
    c.parent.connect_object("button-release-event",CGraph.eventhandler,self)
    c.parent.connect_object("key-press-event",CGraph.eventhandler,self)
    c.parent.connect_object("key-release-event",CGraph.eventhandler,self)

  def Draw(self,N=1,stepflag=False,constrained=False):
    self.init_all(cons=constrained)
    if stepflag:
        self.drawer=self.draw_step()
        self.greens=[]
    else:
        self.draw(N)
    for e in self.alt_e: e.view.set_properties(stroke_color='red')
    for v in self.g.sV: self.connect_add(v.view)
    for e in self.g.sE:
        self.parent.root.add_child(e.view)
        # move edge start/end to CX points:
        e.view.update_points()

  def connect_add(self,item):
    self.parent.root.add_child(item)

  def disconnect(self):
    self.parent.parent.disconnect_by_func(CGraph.eventhandler)

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
  def eventhandler(self,e):
    if e.type == gtk.gdk.KEY_PRESS:
      if e.keyval == ord('p'):
        for l in self.layers:
          for v in l:
            v.view.xy = (self.grx[v].x[self.dirvh],v.view.xy[1])
        self.draw_edges()
        self.dirvh = (self.dirvh+1)%4
      if e.keyval == ord('W'):
          self.xspace += 1
          self.setxy()
          self.draw_edges()
      if e.keyval == ord('w'):
          self.xspace -= 1
          self.setxy()
          self.draw_edges()
      if e.keyval == ord('H'):
          self.yspace += 1
          self.setxy()
          self.draw_edges()
      if e.keyval == ord('h'):
          self.yspace -= 1
          self.setxy()
          self.draw_edges()
      if e.keyval == ord(' '):
        try:
          s,mvmt = self.drawer.next()
          print s,len(mvmt)
          for x in self.greens:
              x.view.shadbox.set_properties(fill_color='grey44')
          self.greens=[]
          for x in mvmt:
            if hasattr(x.view,'shadbox'):
              x.view.shadbox.set_properties(fill_color='green')
              self.greens.append(x)
        except StopIteration:
            print 'drawer terminated'
            del self.drawer
            del self.greens
        except AttributeError:
            print 'drawer created'
            self.drawer=self.draw_step()
            self.greens=[]
