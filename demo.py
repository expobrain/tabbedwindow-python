# -*- coding: utf-8 -*-
"""
Copyright (c) 2013, Daniele Esposti <expo@expobrain.net>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * The name of the contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import division, print_function, unicode_literals
from tabbedwindow import TabbedWindow
import sys
from PyQt4 import QtGui, QtCore


class Demo(TabbedWindow):

    def __init__(self):
        # Call superclass
        super(Demo, self).__init__()

        # Create child windows
        red = QtGui.QMainWindow()
        blue = QtGui.QMainWindow()
        green = QtGui.QMainWindow()

        # Set window's styles
        red.setStyleSheet("QMainWindow { background-color: red; }")
        blue.setStyleSheet("QMainWindow { background-color: blue; }")
        green.setStyleSheet("QMainWindow { background-color: green; }")

        self.addView(red, "Red View")
        self.addView(blue, "Blue view")
        self.addView(green, "Green view")

        # Add test toolbar
        toolbar = red.addToolBar("red_toolbar")
        toolbar.addAction("Red Action")

        # Add test menubar
        action = QtGui.QAction("Green Action", green)
        menu = green.menuBar().addMenu("File")
        menu.addAction(action)

        # Set size and show
        self.resize(400, 400)

        if sys.platform == "darwin":
            QtCore.QTimer.singleShot(0, self.raise_)


if __name__ == "__main__":
    app = QtGui.QApplication([])
    wnd = Demo()
    wnd.show()
    app.exec_()
