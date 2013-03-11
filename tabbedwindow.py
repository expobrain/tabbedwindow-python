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
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt


class GhostWindow(QtGui.QWidget):
    """
    This widget is a static screenshot of the original tab view.

    It will be created during the Drag&Drop action as a visual feedback for the
    user.

    When moving this widget on the screen use
    :py:class:`.tabbedwindow.moveWithOffest()` instead of QWidget.move() so
    the mouse cursor will maintain the current offset from the upper left
    corner of the window as when the D&D operation has started.
    """

    OPACITY = 0.5

    def __init__(self, tabbar, pos):
        """
        Constructor accepts the reference to the tab bar widget and the
        position of the cursor local to the tab bar itself

        :param tabbar: The tab bar where the D&D action is generated
        :param pos: The screen coordinates of the mouse pointer

        :type tabbar: :py:class:`.tabbedwindow.TabBar`
        :type pos: QPoint
        """
        # Call superclass
        super(GhostWindow, self).__init__()

        # Calculate palette using original window as brush
        palette = QtGui.QPalette()
        wnd = tabbar.window()

        if QtCore.QT_VERSION >= 0x050000:
            brush = wnd.grab()
        else:
            brush = QtGui.QPixmap.grabWidget(wnd)

        palette.setBrush(self.backgroundRole(), QtGui.QBrush(brush))

        # Setup widget appearance
        self.setPalette(palette)
        self.setGeometry(wnd.geometry())
        self.setWindowOpacity(self.OPACITY)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Protected attributes
        self._offset = tabbar.mapToGlobal(pos) - wnd.pos()
        self._index = tabbar.tabAt(pos)
        self._origin = tabbar.mapToGlobal(pos)

    def offset(self):
        """
        Offset between the position of the cursor on the tab bar and the upper
        left position of the tab bar's window.

        :rtype: QPoint
        """
        return self._offset

    def index(self):
        """
        Index of the original tab in the tab bar

        :rtype: int
        """
        return self._index

    def moveWithOffset(self, pos):
        """
        Move the widget into the given position taking in account the current
        :py:attr:`.tabbedwindow.GhostWindow.offest()` value

        :param pos: The final position of the window
        :type pos: QPoint
        """
        self.move(pos - self._offset)

        if self.isHidden():
            distance = (self._origin - pos).manhattanLength()

            if distance >= QtGui.QApplication.startDragDistance():
                self.show()

    def dragStarted(self, pos):
        """
        Return *True* if the difference between the position of the original
        widget and given point is greater than the
        QApplication.startDragDistance() value

        :param pos: The current cursor position
        :type post: QPoint
        :rtype: bool
        """
        length = (pos - self._origin).manhattanLength()

        return length >= QtGui.QApplication.startDragDistance()


class TabBar(QtGui.QTabBar):
    """
    Re-implemented the standard QTabBar widget but adds new methods to allow
    Drag&Drop operations outside the tab bar's window, like creating a new
    window with a dragged view, move a view into a different window or close
    the current window if no more tabs are available
    """

    def __init__(self, *args, **kwds):
        """
        See QTabBar
        """
        # Call superclass
        super(TabBar, self).__init__(*args, **kwds)

        # Protected attributes
        self._ghost = None

    def _create_new_window(self, ghost_wnd):
        """
        Creates and returns new window fetching geometry information from the
        given :py:class:`.tabbedwindow.GhostWindow` instance and moving the
        view at the index referenced by
        :py:meth:`.tabbedwindow.GhostWindow.index()` into the newly created
        window.

        :param ghost_wnd: The ghost windows instance from the D&D action
        :type ghost_wnd: :py:class:`.tabbedwindow.GhostWindow`
        :rtype: :py:class:`.tabbedwindow.TabbedWindow`
        """
        # Create new window
        wnd = self.window().clone(ghost_wnd.geometry())

        # Move tab into new window
        views = self.parent()
        index = ghost_wnd.index()

        view = views.widget(index)
        text = views.tabText(index)

        # Move tab
        views.removeTab(index)
        wnd.addView(view, text)

        # Show new windows
        wnd.show()

        return wnd

    def _move_to_window(self, tabbed_wnd, pos, ghost_wnd):
        """
        Move the view at the index referenced by the
        :py:meth:`.tabbedwindow.GhostWindow.index()` attribute into the given
        tabbed window and at the given current position

        :param tabbed_wnd: The target tabbed window instance
        :param pos: The global screen position where the view will be inserted
        :param ghost_wnd: The dragged ghost window

        :type tabbed_wnd: :py:class:`.tabbedwindow.TabbedWindow`
        :type pos: QPoint
        :type ghost_wnd: :py:class:`.tabbedwindow.GhostWindow`
        """
        # Get view and title to be moved
        views = self.parent()
        index = ghost_wnd.index()

        view = views.widget(index)
        text = views.tabText(index)

        # Remove view form local window
        views.removeTab(index)

        # Insert tab into remove window
        index = tabbed_wnd.insertView(pos, view, text)

        # Set it as the current tab and raise focus to the window
        tabbed_wnd.setCurrentView(index)
        tabbed_wnd.raise_()

    def _move_tab(self, pos, ghost_wnd):
        """
        Move the tab in-place by the given position

        :param pos: The global screen position where the view will be inserted
        :param ghost_wnd: The dragged ghost window

        :type pos: QPoint
        :type ghost_wnd: :py:class:`.tabbedwindow.GhostWindow`
        """
        # Move tab if more than one tab
        if self.count() > 1:
            # Get new tab index by pos
            old_index = ghost_wnd.index()
            new_index = self.tabAt(self.mapFromGlobal(pos))

            if new_index == -1:
                new_index = self.count() - 1

            # Move tab only if the indices are different
            if new_index != old_index:
                # Move tab
                self.moveTab(old_index, new_index)

                # Workaround to notify the tab widget the correct active tab
                self.emit(QtCore.SIGNAL(b"currentChanged(int)"), new_index)

    def tabRemoved(self, index):  # pylint: disable=W0613
        """
        If no tabs are left in the current tab bar closes the widget's window.

        See QTabBar.tabRemoved()

        :param index: The removed tab's index
        :type index: int
        """
        if self.count() == 0:
            self.window().close()

    def mousePressEvent(self, event):
        """
        If the left mouse button if pressed over a tab show the ghost window
        and starts the Drag&Drop operation

        See QWidget.mousePressEvent()
        """
        # Create ghost window if needed
        pos = self.mapFromGlobal(event.globalPos())

        if event.button() == Qt.LeftButton and self.tabAt(pos) > -1:
            self._ghost = GhostWindow(self, pos)

        # Call superclass
        super(TabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Update the ghost window's position during mouse move.

        See QWidget.mouseMoveEvent()
        """
        if self._ghost:
            self._ghost.moveWithOffset(event.globalPos())

    def tabDropEvent(self, event):
        """
        Drops the current dragged view and creates a new window if no tab bar
        under the event's screen position otherwise move the dragged view into
        the tab bar under the mouse event's position.

        Close the current window if no more tabs are left.

        This method can be overridden to implement custom tab drop's behaviour.

        :param event: The mouse release event
        :type: QMouseEvent
        """
        # Enter code only if drag is far enough
        pos = event.globalPos()

        if self._ghost.dragStarted(pos):
            tabs = QtGui.QApplication.widgetAt(pos)

            # Choose action by the widget under the mouse's coordinates
            if isinstance(tabs, TabBar):
                if tabs == self:
                    # Move tab in-place
                    self._move_tab(pos, self._ghost)
                else:
                    # Move the dragged tab into the window under the cursor
                    self._move_to_window(tabs.window(), pos, self._ghost)

            else:
                if self.count() == 1:
                    # Only move the current window into the new position
                    self.window().move(self._ghost.pos())
                else:
                    # Creates a new window and move the tab
                    self._create_new_window(self._ghost)

    def mouseReleaseEvent(self, event):
        """
        Analyse the mouse release event calling only the superclass if the
        released button is not the left mouse button otherwise pass the mouse
        release event to the :py:meth:`.tabbedwindow.TabBar.tabDropEvent()`
        handler.

        Finishing by destroying the ghost windows widget.

        See QWidget.mouseReleaseEvent()
        """
        # Call superclass if not a left button release mouse event
        if event.button() != Qt.LeftButton:
            super(TabBar, self).mouseReleaseEvent(event)
            return

        # Handle mouse release event
        self.tabDropEvent(event)

        # Close ghost window
        if self._ghost:
            self._ghost.close()
            self._ghost = None


class TabWidget(QtGui.QTabWidget):
    """
    Subclass of a standard QTabWidget wit a custom tab bar, to be extended to
    fit the desired view's Drag&Drop behaviour
    """

    def __init__(self, parent=None):
        """
        Constructor accepts the optional tab widget's parent

        :param parent: The optional parent widget
        :type parent: QWidget
        """
        # Call superclass
        super(TabWidget, self).__init__(parent)

        # Set up widget
        self.setTabBar(TabBar(self))

    def tabAt(self, pos):
        """
        Re-implementation of the QTabBar.tabAt() method.

        This should be exposed here because the original one is a protected
        method and in the TabbedWindow class we need to retrieve the tab's
        index by the cursor position.

        See QTabBar.tabAt()
        """
        return self.tabBar().tabAt(pos)


class TabbedWindow(QtGui.QMainWindow):
    """
    Subclass of QMainWindow, contains a tab bar to manage a per-window list of
    tabbed views and allows to add, insert or remove a view.

    Views can be standard QWidget instances or even instances of QMainWindow
    with menu bar and tool bars as well.

    These features will be displayed automatically when the view's tab will be
    activated and hidden when it'll be deactivated.
    """

    def __init__(self):
        """
        Empty constructor.

        The tabbed's window parent will be the Qt desktop widget.
        """
        # Call superclass
        super(TabbedWindow, self).__init__(QtGui.QApplication.desktop())

        # Public attributes
        self.tabs = TabWidget(self)

        # Setup window
        self.tabs.setDocumentMode(True)

        self.setCentralWidget(self.tabs)

    def addView(self, view, text):
        """
        Add the given view with the given text to this tabbed window and
        returns the position of the newly created tab

        :param view: The view to be added
        :param text: The title of the view's tab

        :type view: QWidget
        :type text: string

        :rtype: int
        """
        return self.tabs.addTab(view, text)

    def clone(self, geometry):
        """
        Clone the current window with the given geometry.

        Override this method in your subclass of TabbedWindow to return the
        instance of the subclass.

        :param geometry: The geometry of the cloned window
        :type geometry: QRect
        """
        wnd = TabbedWindow()
        wnd.setGeometry(geometry)

        return wnd

    def insertView(self, pos, view, text):
        """
        Insert the given view using the given screen's coordinates and using
        the given text as the tab's title.

        Returns -1 if the insert view operations fails otherwise returns the
        tabs's index.

        :param pos: The screen coordinates where the widget will be inserted
        :param view: The view to be inserted
        :param text: The tab's title

        :type pos: QPoint
        :type view: QWidget
        :type text: string

        :rtype: int
        """
        index = self.tabs.tabAt(self.tabs.mapFromGlobal(pos))

        return self.tabs.insertTab(index, view, text)

    def removeView(self, index):
        """
        Remove the view at the given index

        :param index: The tab's index to be removed
        :type index: int
        """
        self.tabs.removeTab(index)

    def setCurrentView(self, index):
        """
        Set the view at the given index as the current focused view

        :param index; The tab's index to be focused
        :type index: int
        """
        self.tabs.setCurrentIndex(index)

    def currentView(self):
        """
        Returns the current focused view

        :rtype: QWidget
        """
        return self.tabs.currentWidget()
