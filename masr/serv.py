# Copyright (C) 2010 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license

try:
    import dbus
    import dbus.service
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except ImportError:
    _has_dbus = False
else:
    _has_dbus = True

import code
import sys
from cStringIO import StringIO

#------------------------------------------------------------------------------
# MasrException should be used to internally catch all
# other exceptions (wrapper), so that in a fully functional app,
# if something goes wrong, only this exception
# is raised, eventually leading to a MasrSignal sent over dbus.
#------------------------------------------------------------------------------
class MasrException(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return repr(self.message)

# decorator to make a method hookable in a Masr object
def hookable(func):
    def wrapper(self,*args):
        self.probe(func.__name__,*args)
        ret = func(self,*args)
        self.retprobe(func.__name__,ret)
        return ret
    return wrapper

if not _has_dbus:
    class MasrServ:
        def __init__(self,app):
            print 'dbus not supported'
else:
    #------------------------------------------------------------------------------
    # MasrServ is the dbus Object provided by Masr over the SessionBus.
    #------------------------------------------------------------------------------
    class MasrServ(dbus.service.Object):
        def __init__(self,app):
            import rlcompleter
            import readline
            # provide access to the Masr object:
            self.app = app
            # declare service name "org.masr" on the Session Bus:
            self.busname = dbus.service.BusName("org.masr",dbus.SessionBus())
            # declare object "/serv" on this service:
            dbus.service.Object.__init__(self,self.busname.get_bus(),"/serv")
            # create a python interactive console with self.app as locals and org.masr/serv as filename :
            self.ic = code.InteractiveConsole(self.app,'org.masr/serv')
            readline.set_completer(rlcompleter.Completer(self.ic.locals).complete)
            self.completer = readline.get_completer()
            # create stdout/stderr streams used to receive all output from console: 
            self.io = StringIO()
            self.streams = {}
            self.streams['stdout'] = sys.stdout
            self.streams['stdin'] = sys.stdin
            self.streams['stderr'] = sys.stderr
            self.pos=0


        # declare methods of interface 'masr.rcon':
        #------------------------------------------

        # remote console push method:
        @dbus.service.method('masr.rcon')
        def push(self,message):
            #print "push called with ", message
            sys.stdout = self.io
            sys.stderr = self.io
            if self.ic.push(message)==False:
                self.io.seek(self.pos,0)
                res = self.io.read()
                self.pos = self.io.tell()
            else:
                res = None
            sys.stdout = self.streams['stdout']
            sys.stderr = self.streams['stderr']
            return res

        # remote console completer method:
        @dbus.service.method('masr.rcon')
        def complete(self,text,state):
            #print "complete called with '%s' [%d] :"%(text, state),
            res = self.completer(text,state)
            #print "->",res
            return res

if __name__ == '__main__':
    from gobject import MainLoop
    srv = MasrServ(app=globals())
    MainLoop().run()

# #python sync client should do:
# import dbus
# bus = dbus.SessionBus()
# db = bus.get_object('org.masr','/serv')
# rcon = dbus.Interface(db,"masr.rcon")
# rcon.push("1+2")  
