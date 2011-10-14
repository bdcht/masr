#!/usr/bin/env python
# Copyright (C) 2008/2010 Axel Tillequin (bdcht3@gmail.com)
# This code is part of Masr
# published under GPLv2 license

from masr import Masr
from masr.plugins.graph.items import *

def scene(app):
    # test drawing on canvas:
    print 'make ellipse'
    el = Ellipse(parent=app.screen.canvas.root,
                 center_x=400,center_y=200,
                 radius_x=50,radius_y=40,
                 fill_color='gray88',
                 stroke_color='red',
                 line_width=2)
    # use items:
    n1 = Node_basic(r=50)
    n1.label.set_properties(text="TOTO")
    n1.set_properties(x=151,y=151)
    app.screen.canvas.root.add_child(n1)
    n2 = Node_codeblock("0x0804843c 'f3a4'    rep movsb dword [esp+0x4],0x3\n"
                        "0x0804835e '8945fc'  mov [ebp-0x4],eax")
    n2.set_properties(x=351,y=51)
    app.screen.canvas.root.add_child(n2)
    #e = Edge_basic(n1,n2,head=False)
    #self.screen.canvas.root.add_child(e)
    #e = Edge_curve(n1,n2)
    #e.props.stroke_color='DarkGreen'
    #self.screen.canvas.root.add_child(e)
    #e.update_points()

app=Masr()
app.run(start=scene)
