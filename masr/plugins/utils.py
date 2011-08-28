# Copyright (C) 2008/2009 Axel Tillequin (bdcht3@gmail.com)
# This code is part of Masr
# published under GPLv2 license

def run_plugins(func):
    def wrapper(self,**kargs):
        for plugin in self.plugins:
            plugin.start(func.__name__,self,**kargs)
        ret = func(self,**kargs)
        for plugin in self.plugins:
            plugin.end(func.__name__,self,**kargs)
        return ret
    return wrapper

