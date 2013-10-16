====================================
Masr-"a simple gtk/cairo canvas gui"
====================================

 +-----------+--------------------------------------+
 | Status:   | Under Development                    |
 +-----------+--------------------------------------+
 | Location: | http://github.com/bdcht/masr         |
 +-----------+--------------------------------------+
 | Version:  | 0.1                                  |
 +-----------+--------------------------------------+

Description
===========
masr is a gtk cairo framework based on GooCanvas_.
It provides a GUI application template class (Masr) with:

- a menu bar
- the main drawing canvas (a Canvas widget)
- a status bar
- a dbus server

It provides also a dbus-based python client that allows a complete remote
control of the Masr application instance. New features can be developed as
plugins.

masr was developed initially for drawing graphs with the grandalf_ framework
The code dedicated to graph drawing is found in the plugins/graph directory.
Coordinates of nodes and edge routing points are computed by grandalf and
node/edge views (gtk widgets on the canvas) are managed by the plugin.

Installation
============
masr depends on *pygtk*, *numpy*, *dbus* and *goocanvas*.
Most _Linux_ distributions have packages for these dependencies (python-numpy,
python-dbus, python-pygoocanvas, python-gtk2, ...) so the installation is
straightforward for Linux platform.

For _Windows_, you will obviously need to install gtk/pygtk libraries from
http://www.pygtk.org/dowloads.html.
I've used /pygtk-all-in-one-2.24.2.win32-py2.7.msi/ installer
(which provides goocanvas support as well). The numpy installer is found here:
http://pypi.python.org/pypi/numpy
I have tested grandalf/masr on Windows XP SP3 with Python 2.7.

Quickstart
==========
The "raw naked" Masr template class provides a window equiped with some gtk
widgets (menu,statusbar,crcanvas,etc). Simply do:

.. sourcecode:: python

   >>> from masr import Masr
   >>> a = Masr()
   >>> a.run()

Then we can use the masrdbc script to "connect" to the Masr instance through
D-bus and control the entire app :

.. sourcecode:: python

   $ masrdbc
   Welcome to masr d-bus client.
   you are connected to the running Masr() instance: app = <masr.main.Masr ...

   >>> app.screen
   <masr.window.gtkWindow object at 0x8d6f20c>
   >>> app.screen.canvas
   <Canvas object at 0x8d7175c (GooCanvas at 0x8df6040)>


*masr/main.py*
--------------
Contains the main class:

- Masr

Masr.
~~~~~
This class is the base template for any GUI application. The main class may
inherit from Masr, and redefine the 'start' and 'end' or 'step' methods.

- start() is called just before entering the GUI mainloop, so its a good
  place to put everything needed to setup the scene,
- step() is called inside the mainloop,
- end() is called after the mainloop to clean up everything.

The run() method of Masr will also setup all loaded plugins (modules).
Such plugin is loaded if it appears in the Masr.plugins list.
The default usage is:

.. sourcecode:: python

   >>> a=Masr()
   >>> a.run()

The init of Masr instance will setup the gtk window, GUI elements, and the
crcanvas widget. (The graph plugin is loaded by default.)

*masr/window.py*
----------------
Contains the gtk window classes:

- Window
- gtkWindow(Window)

gtkWindow.
~~~~~~~~~~
The initWindow creates gtk objects Window, adds a VBox widget in it, creates
the GUI elements (menubar, VPaned widget and statusbar), and finally the canvas
(in a ScrolledWindow widget) is added to the VPaned. The show_all() method is
called later in the mainloop only. The mainLoop() method is called by
Masr.run() to handle all events on widgets by starting the main gtk event loop.
Event handlers are supposed to be set up in start() or during plugins init.

*masr/gui.py*
-------------
Contains the menubar and statusbar gtk widget definition.

- gtkgui

*masr/canvas.py*
----------------
Contains the Canvas wrapper. This branch of masr relies
on the pygoocanvas_ python wrapper
(simply do apt-get install python-pygoocanvas).
This library allows for interesting export to various formats.

- Canvas

GooCanvas
~~~~~~~~~
The canvas region is setup as an infinite scrolling area.
A 'Zoomer' provides canvas scaling through Ctrl-[+-] or Ctrl-mouse-scroll.

*masr/serv.py*
--------------
Contains the dbus 'server' socket and associated methods.

*masrdbc*
---------
Contains the dbus 'client' python interactive console.

*masr/plugins/utils.py*
-----------------------

*masr/plugins/graph/*
---------------------
See plugins/graph/README.


.. _GooCanvas:  http://live.gnome.org/GooCanvas
.. _pygoocanvas: http://live.gnome.org/PyGoocanvas
.. _grandalf: http://github.com/bdcht/grandalf
