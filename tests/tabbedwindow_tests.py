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
from mock import patch
from tabbedwindow import TabbedWindow, GhostWindow
import gc
import sys
import unittest
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt


class MouseEvent(QtGui.QMouseEvent):

    def __init__(self, pos):
        super(MouseEvent, self).__init__(
            QtCore.QEvent.MouseButtonPress, pos,
            Qt.LeftButton, Qt.NoButton, Qt.NoModifier
        )

    # Returns global's fake mouse position
    def globalPos(self):
        return self.pos()

    def globalX(self):
        return self.globalPos().x()

    def globalY(self):
        return self.globalPos().y()


class WidgetTestsMixin(object):
    """
    GUI control tests mixin
    """

    app = (QtGui.QApplication.instance()
           if QtGui.QApplication.instance()
           else QtGui.QApplication(sys.argv))

    @classmethod
    def tearDownClass(cls):
        # Check for memory leaks
        try:
            assert(len(gc.garbage) == 0)
        except AssertionError:
            raise AssertionError(gc.get_referrers(*gc.garbage))


class TabbedWindowTests(WidgetTestsMixin, unittest.TestCase):
    """
    TabbedWindow test cases
    """

    def setUp(self):
        # Call superclass
        super(TabbedWindowTests, self).setUp()

        # Set up
        self.window = TabbedWindow()

    def test_add_view(self):
        # Add view
        view = QtGui.QWidget()
        title = "title"

        index = self.window.addView(view, title)

        # Check
        self.assertEqual(index, 0)
        self.assertEqual(self.window.tabs.tabText(index), title)
        self.assertEqual(self.window.tabs.widget(index), view)

    def test_insert_view(self):
        # Add view
        view1 = QtGui.QWidget()
        title1 = "title1"

        index = self.window.addView(view1, title1)

        self.assertEqual(index, 0)

        # Insert another view
        view2 = QtGui.QWidget()
        title2 = "title2"

        index = self.window.insertView(QtCore.QPoint(), view2, title2)

        # Check
        self.assertEqual(index, 0)
        self.assertEqual(self.window.tabs.tabText(index), title2)
        self.assertEqual(self.window.tabs.widget(index), view2)
        self.assertEqual(self.window.tabs.tabText(index + 1), title1)
        self.assertEqual(self.window.tabs.widget(index + 1), view1)

    def test_current_view(self):
        # Add view
        view1 = QtGui.QWidget()
        view2 = QtGui.QWidget()
        title1 = "title1"
        title2 = "title2"

        index1 = self.window.addView(view1, title1)
        index2 = self.window.addView(view2, title2)

        # Check set current view
        self.window.setCurrentView(index1)
        self.assertEqual(self.window.currentView(), view1)

        self.window.setCurrentView(index2)
        self.assertEqual(self.window.currentView(), view2)

    def test_remove_view(self):
        # Add view
        view = QtGui.QWidget()
        title = "title"

        index = self.window.addView(view, title)

        self.assertEqual(self.window.tabs.widget(index), view)

        # Remove view
        self.window.removeView(index)

        self.assertIsNone(self.window.tabs.widget(index))


class GhostWindowTests(WidgetTestsMixin, unittest.TestCase):
    """
    GhostWindow test cases
    """

    def setUp(self):
        # Call superclass
        super(GhostWindowTests, self).setUp()

        # Set up
        self.window = TabbedWindow()
        self.window.addView(QtGui.QWidget(), "test")

        self.tabbar = self.window.tabs.tabBar()

        # Check if first tab has geometry and save top left corner
        self.assertFalse(self.tabbar.tabRect(0).isNull())

        self.tab_pos = self.tabbar.tabRect(0).topLeft()

        # Create ghost window
        self.ghost = GhostWindow(self.tabbar, self.tab_pos)

    def test_constructor(self):
        self.assertEqual(self.window.geometry(), self.ghost.geometry())
        self.assertLess(self.ghost.windowOpacity(), 1)
        self.assertTrue(
            self.ghost.testAttribute(Qt.WA_TransparentForMouseEvents))
        self.assertEqual(self.ghost.index(), 0)
        self.assertEqual(
            self.ghost.offset(),
            self.tabbar.mapToGlobal(self.tab_pos) - self.window.pos()
        )

    def test_move_with_offset(self):
        pos = self.ghost.pos()
        movement = QtCore.QPoint(10, 10)

        self.ghost.moveWithOffset(movement)

        self.assertEqual(self.ghost.pos() - pos, movement)

    def test_drag_started(self):
        # No drag
        origin = self.ghost.pos()
        drag_distance = QtGui.QApplication.startDragDistance()
        pos = origin + QtCore.QPoint(drag_distance / 4, drag_distance / 4)

        self.assertFalse(self.ghost.dragStarted(pos))

        # Is dragging
        pos = origin + QtCore.QPoint(drag_distance, drag_distance)

        self.assertTrue(self.ghost.dragStarted(pos))


class TabBarTests(WidgetTestsMixin, unittest.TestCase):
    """
    TabBar test cases
    """

    def setUp(self):
        # Call superclass
        super(TabBarTests, self).setUp()

        # Set up
        self.window = TabbedWindow()
        self.window.addView(QtGui.QWidget(), "test")
        self.window.show()

        # Move the window just away from the screen's origin to avoid problems
        # with top/right toolbars
        self.window.move(QtCore.QPoint(100, 100))

        # Create ghost window
        tabbar = self.window.tabs.tabBar()
        local_pos = tabbar.tabRect(0).topLeft()

        self.tabbar = tabbar
        self.tab_pos = tabbar.mapToGlobal(local_pos)
        self.ghost = GhostWindow(tabbar, local_pos)

    def test_create_new_window(self):
        index = self.ghost.index()
        view = self.window.tabs.widget(index)
        text = self.window.tabs.tabText(index)

        # pylint: disable=W0212
        window = self.tabbar._create_new_window(self.ghost)
        # pylint: enable=W0212

        self.assertEqual(window.geometry(), self.ghost.geometry())
        self.assertFalse(self.tabbar.count())
        self.assertEqual(window.tabs.count(), 1)
        self.assertEqual(window.tabs.widget(0), view)
        self.assertEqual(window.tabs.tabText(0), text)

    def test_move_to_window(self):
        # Create destination window with one tab
        dest = TabbedWindow()
        dest.addView(QtGui.QWidget(), "test")

        # Get reference of the view to be moved
        index = self.ghost.index()
        view = self.window.tabs.widget(index)
        text = self.window.tabs.tabText(index)

        # Move tab into new window
        self.tabbar._move_to_window(  # pylint: disable=W0212
            dest, dest.tabs.tabBar().tabRect(0).topLeft(), self.ghost)

        # Check
        self.assertFalse(self.window.tabs.count())
        self.assertEqual(dest.tabs.count(), 2)
        self.assertEqual(dest.tabs.widget(0), view)
        self.assertEqual(dest.tabs.tabText(0), text)
        self.assertEqual(dest.currentView(), view)

    @patch.object(TabbedWindow, "close")
    def test_tab_removed(self, mock_close):
        """
        Close the window when the last tab is removed
        """
        # Remove tabs
        for i in xrange(self.window.tabs.count()):  # pylint: disable=W0612
            self.window.removeView(0)

        # Check
        mock_close.assert_called_once_with()

    def test_mouse_press_event(self):
        # Default state
        self.assertIsNone(self.tabbar._ghost)  # pylint: disable=W0212

        # Simulate mouse press event
        self.tabbar.mousePressEvent(MouseEvent(self.tab_pos))

        # Check
        # pylint: disable=W0212
        self.assertIsInstance(self.tabbar._ghost, GhostWindow)
        self.assertTrue(self.tabbar._ghost.isVisible())
        # pylint: enable=W0212

    def test_mouse_move_event(self):
        # Default state
        self.tabbar.mousePressEvent(MouseEvent(self.tab_pos))

        # pylint: disable=W0212
        self.assertIsInstance(self.tabbar._ghost, GhostWindow)
        # pylint: enable=W0212

        # Simulate mouse move
        pos = self.tab_pos + QtCore.QPoint(
            QtGui.QApplication.startDragDistance(),
            QtGui.QApplication.startDragDistance()
        )

        self.tabbar.mouseMoveEvent(MouseEvent(pos))

        # Check
        # pylint: disable=W0212
        self.assertEqual(self.tabbar._ghost.pos(), pos)
        # pylint: enable=W0212

    def test_mouse_release_new_window(self):
        """
        Release mouse create new window
        """
        # Add extra tab
        self.window.addView(QtGui.QWidget(), "test")

        self.assertGreater(self.window.tabs.count(), 1)

        # Simulate mouse press and move outside the window area
        pos = self.window.geometry().topRight()
        pos = self.window.mapToGlobal(pos)
        pos += QtCore.QPoint(10,10)

        self.assertIsNone(QtGui.QApplication.widgetAt(pos))

        self.tabbar.mousePressEvent(MouseEvent(self.tab_pos))
        self.tabbar.mouseMoveEvent(MouseEvent(pos))

        with patch.object(self.tabbar, "_create_new_window") as mock_create:
            # Simulate mouse release
            self.tabbar.mouseReleaseEvent(MouseEvent(pos))

            # Check
            # pylint: disable=W0212
            mock_create.assert_called_once_with(self.tabbar._ghost)
            # pylint: enable=W0212

    def test_mouse_release_move_tab(self):
        """
        Release mouse moving a tab into another window
        """
        # Add extra window
        dest = TabbedWindow()
        dest.addView(QtGui.QWidget(), "test")
        dest.move(self.window.geometry().topRight())
        dest.show()

        # Simulate mouse press and move outside the window area
        pos = dest.tabs.tabBar().tabRect(0).topLeft()
        pos = dest.tabs.tabBar().mapToGlobal(pos)

        self.tabbar.mousePressEvent(MouseEvent(self.tab_pos))
        self.tabbar.mouseMoveEvent(MouseEvent(pos))

        with patch.object(self.tabbar, "_move_to_window") as mock_create:
            # Simulate mouse release
            event = MouseEvent(pos)
            ghost = self.tabbar._ghost

            self.tabbar.mouseReleaseEvent(event)

            # Check
            mock_create.assert_called_once_with(  # pylint: disable=W0212
                dest, event.globalPos(), ghost)
