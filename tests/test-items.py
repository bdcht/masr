#!/usr/bin/env python
# Copyright (C) 2008/2010 Axel Tillequin (bdcht3@gmail.com)
# This code is part of Masr
# published under GPLv2 license

from masr import Masr
from masr.plugins.graph.items import *

class App(Masr):
    def start(self):
        # test drawing on canvas:
        n1 = Node_basic(r=50)
        n1.props.x,n1.props.y=51,51
        self.screen.canvas.root.add(n1)
        n2 = Node_codeblock("0x0804843c 'f3a4'    rep movsb dword [esp+0x4],0x3\n"
                           "0x0804835e '8945fc'  mov [ebp-0x4],eax")
        n2.props.x,n2.props.y=351,51
        # if Node_basic is a Blit object, we set its canvas:
        if isinstance(n2,Blit): n2.set(canvas=self.screen.canvas)
        self.screen.canvas.root.add(n2)
        e = Edge_basic(n1,n2,head=True)
        self.screen.canvas.root.add(e)
        e = Edge_curve(n1,n2)
        e.props.outline_color='DarkGreen'
        self.screen.canvas.root.add(e)
        e.update_points()

App().run()
