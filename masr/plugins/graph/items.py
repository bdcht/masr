# -*- coding: utf-8 -*-
# Copyright (C) 2009 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license


import gtk
import math
from numpy import array

from crcanvas import *

# connectors CX are embedded inside node views. These objects are drawn on
# the node's surface and exists only as sub-objects of their node. CX are used
# as 'ports' for edges connected with a node. A node can have several such CX
# and can register or unregister its edges on such CX.
class CX(Rectangle):
    def __init__(self,e=None):
        Rectangle.__init__(self,width=3,height=3)
        self.props.line_width=1
        self.props.fill_color='red'
        #self.props.visible=False
        # list of edges connected to this CX:
        self.registered = []
        if e!=None: self.register(e)
        #self.connect('event',CX.eventhandler)

    def set_wh(self,wh):
        self.props.width = wh[0]
        self.props.height = wh[1]
    def get_wh(self):
        return (self.props.width,self.props.height)
    wh = property(get_wh,set_wh)

    # manage Edge_basic that are using this CX:
    def register(self,item):
        self.registered.append(item)
    def unregister(self,item):
        self.registered.remove(item)

    def eventhandler(*args):
        print "CX eventhandler on",args

#------------------------------------------------------------------------------
# decorators for eventhandlers: this sets the 'clicked' field to the mouse
# button id, and moves the object along with mouse-1 movements.
def mouse1moves(h):
    def wrapper(self,e,cr,pick_item):
        self.last_msec = [0]
        if e.type is gtk.gdk.BUTTON_PRESS:
            self.clicked = e.button
            self.oldx,self.oldy = e.get_coords()
            self.last_msec[0] = 0.
        elif e.type is gtk.gdk.BUTTON_RELEASE:
            self.clicked = 0
        elif e.type is gtk.gdk.MOTION_NOTIFY:
            if abs(e.time - self.last_msec[0])<10: return False
            self.last_msec[0]=e.time
            if self.clicked==1:
                newx,newy = e.get_coords()
                m = self.props.matrix
                m.translate(newx-self.oldx, newy-self.oldy)
                self.props.matrix = m
        return h(self,e,cr,pick_item)
    return wrapper

#------------------------------------------------------------------------------
# This is a 'circle' shaped view for nodes. 
class Node_basic(Ellipse):
    #prop:
    def set_r(self,r):
        self._r = r
        self.props.width = self.props.height = 2*r
    def get_r(self):
        return self._r
    r = property(get_r,set_r)

    def set_wh(self,wh): pass
    def get_wh(self):
        bb = Bounds()
        self.calculate_bounds(bb,DeviceBounds())
        return (bb.x2-bb.x1,bb.y2-bb.y1)
    wh = property(get_wh,set_wh)

    # put the cx pt at the intersection between the circle shape of Node_basic
    # and the radius from centre to pt 'topt'. 
    def intersect(self,topt,cx):
        assert cx in self.items
        x1,y1 = self.props.x,self.props.y
        x2,y2 = topt
        theta = math.atan2(y2-y1,x2-x1)
        cx.props.x = int(math.cos(theta)*self._r)
        cx.props.y = int(math.sin(theta)*self._r)
        self._angle = theta

    def set_alpha(self,a):
        color = self.props.fill_color_rgba & 0xffffff00
        self.props.fill_color_rgba = color+(int(a*255.)&0xff)
    def get_alpha(self):
        return (self.props.fill_color_rgba&0xff)/255.
    alpha = property(get_alpha,set_alpha)

    def __init__(self,r=10):
        Ellipse.__init__(self)
        self.props.fill_color = 'white'
        self.props.outline_color = 'black'
        self.props.line_width = 1.0
        self.props.test_fill = True
        # extra:
        self.alpha = 1.
        self.r = r
        self.label = Text(text='[?]',
                          font="monospace, bold, 8",
                          fill_color='blue',
                          anchor=gtk.ANCHOR_CENTER)
        self.label.props.visible = False
        # edges connectors:
        self.cx = []
        # add label item in local surface:
        self.add(self.label)
        # events:
        self.connect("event",Node_basic.eventhandler)
        # clicked: 1=mouse1, 2=mouse2, 3=mouse3
        self.clicked=0
        self.connect('notify',Node_basic.notifyhandler)

    @mouse1moves
    def eventhandler(self,e,cr,pick_item):
        #print e.type,'on',pick_item
        if e.type is gtk.gdk.ENTER_NOTIFY:
            self.set(line_width=2.0)
        elif e.type is gtk.gdk.LEAVE_NOTIFY:
            self.set(line_width=1.0)
        return False

    def notifyhandler(self,prop):
        #print "notify %s on "%prop.name,self
        if prop.name in ('matrix','x','y'):
            for cx in self.cx:
                for e in cx.registered: e.update_points()

#------------------------------------------------------------------------------
class Edge_basic(Line):
    def __init__(self,n0,n1,head=False):
        self.n = [n0,n1]
        self.cx = [CX(self),CX(self)]
        n0.cx.append(self.cx[0]); n0.add(self.cx[0])
        n1.cx.append(self.cx[1]); n1.add(self.cx[1])
        Line.__init__(self,points=[0,0,1,1])
        self.props.close = False
        self.props.outline_color = 'black'
        self.props.line_width = 1
        if head:
            self.head = Arrow(point_id=-1,depth=0,fatness=6,length=6)
            self.head.connect_parent(self)
            self.add(self.head)
            self.set_z(self.head,3)
        else:
            self.head = None
        self.update_points()
        self.clicked=0

    def setpath(self,l):
        pts = []
        for xy in l: pts.extend(xy)
        self.props.points = pts

    def update_points(self):
        pts = self.props.points
        self.n[0].intersect(topt=(pts[2],pts[3]),cx=self.cx[0])
        self.n[1].intersect(topt=(pts[-4],pts[-3]),cx=self.cx[-1])
        self.cx[-1].props.fill_color='blue'
        cx = (self.cx[0].props.x,self.cx[0].props.y)
        pts[0],pts[1] = self.n[0].props.matrix.transform_point(*cx)
        cx = (self.cx[-1].props.x,self.cx[-1].props.y)
        pts[-2],pts[-1] = self.n[1].props.matrix.transform_point(*cx)
        self.props.points = pts
        if self.head:
            x1,y1 = pts[-4],pts[-3]
            x2,y2 = pts[-2],pts[-1]
            self.head.props.x,self.head.props.y = x2,y2
            self.head.props.angle = math.atan2(y2-y1,x2-x1)

#------------------------------------------------------------------------------
class Edge_curve(Path):
    __gsignals__ = {'make_path' : 'override' }
    need_path = True

    def __init__(self,n0,n1,head=True):
        self.n = [n0,n1]
        self.has_head=head
        self.cx = [CX(self),CX(self)]
        n0.cx.append(self.cx[0]); n0.add(self.cx[0])
        n1.cx.append(self.cx[1]); n1.add(self.cx[1])
        Path.__init__(self)
        self.props.outline_color = 'black'
        self.props.line_width = 1
        self.props.cap = 1
        self.props.join = 1
        self.splines = [[(n0.props.x,n0.props.y),(n1.props.x,n1.props.y)]]
        self.update_points()
        self.clicked=0

    def do_make_path(self,cr):
        if self.need_path:
            cr.new_path()
            p0 = self.splines[0][0]
            cr.move_to(*p0)
            for s in self.splines:
                if len(s)==2:
                    cr.line_to(s[1][0],s[1][1])
                else:
                    cr.curve_to(s[1][0],s[1][1],
                                s[2][0],s[2][1],
                                s[3][0],s[3][1])
                    #drawing tangents for debugging:
                    #cr.move_to(*s[0])
                    #cr.line_to(*s[1])
                    #cr.move_to(*s[2])
                    #cr.line_to(*s[3])
            if self.has_head:
                cr.rotate(self.head_angle)
                cr.rel_line_to(-5,+5)
                cr.rel_line_to(+5,-5)
                cr.rel_line_to(-5,-5)
                cr.rotate(-self.head_angle)
            return True
        return False

    def setpath(self,l):
        try:
            self.splines = self.setcurve(l)
        except:
            pass

    def update_points(self):
        try:
            spl0 = self.splines[0]
            spl1 = self.splines[-1]
            self.n[0].intersect(topt=spl0[1],cx=self.cx[0])
            self.n[1].intersect(topt=spl1[-2],cx=self.cx[1])
            cx = (self.cx[0].props.x,self.cx[0].props.y)
            spl0[0] = self.n[0].props.matrix.transform_point(*cx)
            cx = (self.cx[1].props.x,self.cx[1].props.y)
            spl1[-1] = self.n[1].props.matrix.transform_point(*cx)
            x1,y1 = spl1[-2]
            x2,y2 = spl1[-1]
            t=math.atan2(y2-y1,x2-x1)
            self.head_angle = t
            self.request_update()
        except:
            pass

#------------------------------------------------------------------------------
class Node_codeblock(Item):

    def __init__(self,code):
        Item.__init__(self)
        self.codebox = Rectangle()
        self.code = Text(text=code,font='monospace, 8',anchor=gtk.ANCHOR_CENTER)
        self.codebox.add(self.code)
        self.padding = 4
        bb = Bounds()
        self.code.calculate_bounds(bb,DeviceBounds())
        w  = (bb.x2-bb.x1)+self.padding
        h  = (bb.y2-bb.y1)+self.padding
        self.codebox.set(width=w,height=h)
        self.codebox.props.fill_color = 'white'
        self.codebox.props.outline_color = 'black'
        self.codebox.props.line_width = 1.0
        self.codebox.props.test_fill = True
        # shadow :
        self.shadow = s = 3
        self.codebox.set(x=-s,y=-s)
        self.shadbox = Rectangle(x=s,y=s,width=w,height=h,fill_color='grey44')
        self._wh = (w+s+s,h+s+s)
        self.cx = []
        self.add(self.shadbox)
        self.add(self.codebox)
        self.set_z(self.shadbox,0)
        self.set_z(self.codebox,2)
        # events:
        self.clicked=0
        self.connect("event",Node_codeblock.eventhandler)
        self.connect('notify',Node_codeblock.notifyhandler)

    def set_wh(self,wh): pass
    def get_wh(self):
        return self._wh
    wh = property(get_wh,set_wh)

    def intersect(self,topt,cx):
        assert cx in self.items
        x1,y1 = 0,0
        x2,y2 = topt[0]-self.props.x,topt[1]-self.props.y
        bb = Bounds()
        #bb.x2 = self._wh[0]/2
        #bb.x1 = -bb.x2
        #bb.y2 = self._wh[1]/2
        #bb.y1 = -bb.y2
        self.codebox.calculate_bounds(bb,DeviceBounds())
        # now try all 4 segments of self rectangle:
        S = [((x1,y1),(x2,y2),(bb.x1,bb.y1),(bb.x2,bb.y1)),
             ((x1,y1),(x2,y2),(bb.x2,bb.y1),(bb.x2,bb.y2)),
             ((x1,y1),(x2,y2),(bb.x1,bb.y2),(bb.x2,bb.y2)),
             ((x1,y1),(x2,y2),(bb.x1,bb.y2),(bb.x1,bb.y1))]
        for segs in S:
            xy = intersect2lines(*segs)
            if xy!=None:
                x,y = xy
                cx.props.x = x+self.codebox.props.x
                cx.props.y = y+self.codebox.props.y
                break

    def highlight_on(self,style=None):
        import re
        if style is None:
            style = {'addr': '<span foreground="blue">%s</span>',
                     'code': '<span foreground="black">%s</span>',
                     'mnem': '<span foreground="black" weight="bold">%s</span>',
                     'strg': '<span foreground="DarkRed">%s</span>',
                     'cons': '<span foreground="red">%s</span>',
                     'comm': '<span foreground="DarkGreen">%s</span>',
                    }
        lre = re.compile("(0x[0-9a-f]+ )('[0-9a-f]+' +)(.*)$")
        hcode = []
        for l in self.code.props.text.splitlines():
            if l.startswith('#'):
                hcode.append(style['comm']%l)
            else:
                m = lre.match(l)
                if m is None: return
                g = m.groups()
                s  = [style['addr']%g[0]]
                s += [style['strg']%g[1]]
                s += [style['code']%g[2]]
                hcode.append(''.join(s))
        self.code.set(text='\n'.join(hcode))
        self.code.set(use_markup=True)

    def highlight_off(self):
        import re
        lre = re.compile("<span [^>]+>(.*?)</span>")
        code = []
        for l in self.code.props.text.splitlines():
            g = lre.findall(l)
            if len(g)>0: code.append(''.join(g))
        self.code.set(text='\n'.join(code))
        self.code.set(use_markup=False)

    @mouse1moves
    def eventhandler(self,e,cr,pick_item):
        #print e.type,'on',pick_item
        if e.type is gtk.gdk.ENTER_NOTIFY:
            self.codebox.set(line_width=2.0)
        elif e.type is gtk.gdk.LEAVE_NOTIFY:
            self.codebox.set(line_width=1.0)
        return False

    def notifyhandler(self,prop):
        #print "notify %s on "%prop.name,self
        if prop.name in ('matrix','x','y'):
            for cx in self.cx:
                for e in cx.registered: e.update_points()

    def resrc(self,code):
        bb = Bounds()
        self.code.props.text = code
        self.code.calculate_bounds(bb,DeviceBounds())
        w  = (bb.x2-bb.x1)+self.padding
        h  = (bb.y2-bb.y1)+self.padding
        self.codebox.set(width=w,height=h)
        self.shadbox.set(width=w,height=h)


def intersect2lines((x1,y1),(x2,y2),(x3,y3),(x4,y4)):
    b = (x2-x1,y2-y1)
    d = (x4-x3,y4-y3)
    det = b[0]*d[1] - b[1]*d[0]
    if det==0: return None
    c = (x3-x1,y3-y1)
    t = float(c[0]*b[1] - c[1]*b[0])/(det*1.)
    if (t<0. or t>1.): return None
    t = float(c[0]*d[1] - c[1]*d[0])/(det*1.)
    if (t<0. or t>1.): return None
    x = x1 + t*b[0]
    y = y1 + t*b[1]
    return (x,y)
