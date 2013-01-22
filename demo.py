# -*- coding: utf-8 -*-

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
        toolbar.addAction("Red Aaction")

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
