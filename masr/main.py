# -*- coding: utf-8 -*-
# Copyright (C) 2008/2009 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license

"""  Masr : 2D pyGTK+/pyCairo graphic engine 
     (Masr is an Egyptian name for the city Cairo)
"""

try:
    import psyco
    psyco.profile(0.1)

except ImportError: pass

from plugins.utils import run_plugins

#------------------------------------------------------------------------------
class Masr(object):
    """ Main application class which contains window and engine,
            defines main events and interface to set general vars 
            on setUp and during runtime.
    """
    def __init__(self):
        import pdb
        # default configuration :
        self.title = "Masr 0.9"
        self.size = (640,480)
        self.fullScreen = 0
        self.bgColor = (200,200,200)
        self.pdb = pdb.Pdb()
        self.plugins = set()

        self.session = None

        # set initial plugin list:
        try:
            self.setup()
        except AttributeError: pass

        # create the window:
        from window import gtkWindow
        self.screen = gtkWindow(self)

        # init window, engine, events, bind events etc...
        self.screen.initWindow()

    @run_plugins
    def run(self,**kargs):
        from serv import MasrServ
        serv = MasrServ(self.__dict__)
        # main loop with start/end hooks :
        self.start()
        self.screen.mainLoop()
        self.end()

    # stubs :
    def start(self,func=None):
        if func!=None:
            return func(self)
    def end(self,func=None):
        if func!=None:
            return func(self)
    def step(self,func=None):
        if func!=None:
            return func(self)

#------------------------------------------------------------------------------
if __name__=='__main__':
    import sys
    import plugins.graph as graph
    a=Masr()
    a.plugins.add(graph)
    a.run(args=sys.argv)
