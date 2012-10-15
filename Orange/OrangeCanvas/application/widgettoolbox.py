"""
Widget Tool Box
===============


A tool box with a tool grid for each category.

"""

import logging

from PyQt4.QtGui import (
    QAbstractButton, QSizePolicy, QAction, QApplication, QDrag, QPalette,
    QBrush
)

from PyQt4.QtCore import Qt, QModelIndex, QSize

from PyQt4.QtCore import QObject, QEvent, QMimeData
from PyQt4.QtCore import  pyqtSignal as Signal, pyqtProperty as Property

from ..gui.toolbox import ToolBox, create_tab_gradient
from ..gui.toolgrid import ToolGrid

from ..registry.qt import QtWidgetRegistry

log = logging.getLogger(__name__)


def iter_item(item):
    """Iterate over child items of a `QStandardItem`.
    """
    for i in range(item.rowCount()):
        yield item.child(i)


class WidgetToolGrid(ToolGrid):
    """A Tool Grid with widget buttons. Populates the widget buttons
    from a item model. Also adds support for drag operations.

    """
    def __init__(self, *args, **kwargs):
        ToolGrid.__init__(self, *args, **kwargs)

        self.__model = None
        self.__rootIndex = None
        self.__rootItem = None
        self.__rootItem = None
        self.__actionRole = QtWidgetRegistry.WIDGET_ACTION_ROLE

        self.__dragListener = DragStartEventListener(self)
        self.__dragListener.dragStartOperationRequested.connect(
            self.__startDrag
        )

    def setModel(self, model, rootIndex=QModelIndex()):
        """Set a model (`QStandardItemModel`) for the tool grid. The
        widget actions are children of the rootIndex.

        """
        if self.__model is not None:
            self.__model.rowsInserted.disconnect(self.__on_rowsInserted)
            self.__model.rowsRemoved.disconnect(self.__on_rowsRemoved)
            self.__model = None

        self.__model = model
        self.__rootIndex = rootIndex

        if self.__model is not None:
            self.__model.rowsInserted.connect(self.__on_rowsInserted)
            self.__model.rowsRemoved.connect(self.__on_rowsRemoved)

        self.__initFromModel(model, rootIndex)

    def model(self):
        """Return the model for the tool grid.
        """
        return self.__model

    def rootIndex(self):
        return self.__rootIndex

    def setActionRole(self, role):
        """Set the action role.
        """
        if self.__actionRole != role:
            self.__actionRole = role
            if self.__model:
                self.__update()

    def actionRole(self):
        """Return the action role.
        """
        return self.__actionRole

    def insertAction(self, index, action):
        rval = ToolGrid.insertAction(self, index, action)
        button = self.buttonForAction(action)
        button.installEventFilter(self.__dragListener)
        return rval

    def removeAction(self, action):
        button = self.buttonForAction(action)
        button.removeEventFilter(self.__dragListener)
        ToolGrid.removeAction(self, action)

    def __initFromModel(self, model, rootIndex):
        """Initialize the grid from the model with rootIndex as the root.
        """
        if not rootIndex.isValid():
            rootItem = model.invisibleRootItem()
        else:
            rootItem = model.itemFromIndex(rootIndex)

        self.__rootItem = rootItem

        for i, item in enumerate(iter_item(rootItem)):
            self.__insertItem(i, item)

    def __insertItem(self, index, item):
        """Insert a widget action (from a `QStandardItem`) at index.
        """
        value = item.data(self.__actionRole)
        if value.isValid():
            action = value.toPyObject()
        else:
            action = QAction(item.text(), self)
            action.setIcon(item.icon())

        self.insertAction(index, action)

    def __update(self):
        self.clear()
        self.__initFromModel(self.__model, self.__rootIndex)

    def __on_rowsInserted(self, parent, start, end):
        """Insert items from range start:end into the grid.
        """
        item = self.__model.itemForIndex(parent)
        if item == self.__rootItem:
            for i in range(start, end + 1):
                item = self.__rootItem.child(i)
                self._insertItem(i, item)

    def __on_rowsRemoved(self, parent, start, end):
        """Remove items from range start:end from the grid.
        """
        item = self.__model.itemForIndex(parent)
        if item == self.__rootItem:
            for i in range(start - 1, end):
                action = self._gridSlots[i].action
                self.removeAction(action)

    def __startDrag(self, button):
        """Start a drag from button
        """
        action = button.defaultAction()
        desc = action.data().toPyObject()  # Widget Description
        icon = action.icon()
        drag_data = QMimeData()
        drag_data.setData(
            "application/vnv.orange-canvas.registry.qualified-name",
            desc.qualified_name
        )
        drag = QDrag(button)
        drag.setPixmap(icon.pixmap(self.iconSize))
        drag.setMimeData(drag_data)
        drag.exec_(Qt.CopyAction)


class DragStartEventListener(QObject):
    """An event filter object that can be used to detect drag start
    operation on buttons which otherwise do not support it.

    """
    dragStartOperationRequested = Signal(QAbstractButton)

    def __init__(self, parent=None, **kwargs):
        QObject.__init__(self, parent, **kwargs)
        self.button = None
        self.buttonDownObj = None
        self.buttonDownPos = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.buttonDownPos = event.pos()
            self.buttonDownObj = obj
            self.button = event.button()

        elif event.type() == QEvent.MouseMove and obj is self.buttonDownObj:
            if (self.buttonDownPos - event.pos()).manhattanLength() > \
                    QApplication.startDragDistance() and \
                    not self.buttonDownObj.hitButton(event.pos()):
                # Process the widget's mouse event, before starting the
                # drag operation, so the widget can update its state.
                obj.mouseMoveEvent(event)

                self.dragStartOperationRequested.emit(obj)

                self.buttonDownObj.setDown(False)
                self.button = None
                self.buttonDownPos = None
                self.buttonDownObj = None
                return True  # Already handled

        return QObject.eventFilter(self, obj, event)


class WidgetToolBox(ToolBox):

    triggered = Signal(QAction)
    hovered = Signal(QAction)

    def __init__(self, parent=None):
        ToolBox.__init__(self, parent)
        self.__model = None
        self.__iconSize = QSize(25, 25)
        self.__buttonSize = QSize(50, 50)
        self.setSizePolicy(QSizePolicy.Fixed,
                           QSizePolicy.Expanding)

    def setIconSize(self, size):
        """Set the widget icon size.
        """
        self.__iconSize = size
        for widget in  map(self.widget, range(self.count())):
            widget.setIconSize(size)

    def iconSize(self):
        """Return the widget buttons icon size.
        """
        return self.__iconSize

    iconSize_ = Property(QSize, fget=iconSize, fset=setIconSize,
                         designable=True)

    def setButtonSize(self, size):
        """Set fixed widget button size.
        """
        self.__buttonSize = size
        for widget in map(self.widget, range(self.count())):
            widget.setButtonSize(size)

    def buttonSize(self):
        return self.__buttonSize

    buttonSize_ = Property(QSize, fget=buttonSize, fset=setButtonSize,
                           designable=True)

    def setModel(self, model):
        """Set the widget registry model for this toolbox.
        """
        if self.__model is not None:
            self.__model.itemChanged.disconnect(self.__on_itemChanged)
            self.__model.rowsInserted.disconnect(self.__on_rowsInserted)
            self.__model.rowsRemoved.disconect(self.__on_rowsRemoved)

        self.__model = model
        if self.__model is not None:
            self.__model.itemChanged.connect(self.__on_itemChanged)
            self.__model.rowsInserted.connect(self.__on_rowsInserted)
            self.__model.rowsRemoved.connect(self.__on_rowsRemoved)

        self.__initFromModel(self.__model)

    def __initFromModel(self, model):
        for cat_item in iter_item(model.invisibleRootItem()):
            self.__insertItem(cat_item, self.count())

    def __insertItem(self, item, index):
        """Insert category item at index.
        """
        grid = WidgetToolGrid()
        grid.setModel(item.model(), item.index())

        grid.actionTriggered.connect(self.triggered)
        grid.actionHovered.connect(self.hovered)

        grid.setIconSize(self.__iconSize)
        grid.setButtonSize(self.__buttonSize)

        text = item.text()
        icon = item.icon()
        tooltip = item.toolTip()

        # Set the 'tab-title' property to text.
        grid.setProperty("tab-title", text)
        grid.setObjectName("widgets-toolbox-grid")

        self.insertItem(index, grid, text, icon, tooltip)
        button = self.tabButton(index)

        # Set the 'highlight' color
        brush = item.background()

        if not brush.gradient():
            gradient = create_tab_gradient(brush.color())
            brush = QBrush(gradient)
        palette = button.palette()
        palette.setBrush(QPalette.Highlight, brush)
        button.setPalette(palette)

    def __on_itemChanged(self, item):
        """Item contents have changed.
        """
        parent = item.parent()
        if parent is self.__model.invisibleRootItem():
            button = self.tabButton(item.row())
            button.setIcon(item.icon())
            button.setText(item.text())
            button.setToolTip(item.toolTip())

    def __on_rowsInserted(self, parent, start, end):
        """Items have been inserted in the model.
        """
        # Only the top level items (categories) are handled here.
        if not parent.isValid():
            root = self.__model.invisibleRootItem()
            for i in range(start, end + 1):
                item = root.child(i)
                self.__insertItem(item, i)

    def __on_rowsRemoved(self, parent, start, end):
        """Rows have been removed from the model.
        """
        # Only the top level items (categories) are handled here.
        if not parent.isValid():
            for i in range(end, start - 1, -1):
                self.removeItem(i)
