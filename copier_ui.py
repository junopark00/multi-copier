__author__ = "Juno Park"
__github__ = "https://github.com/junopark00/multi-copier"


import os

from PySide2 import QtWidgets, QtCore, QtGui

import qdarktheme


class DraggableListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None, dir_only=False):
        super(DraggableListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.dir_only = dir_only
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DraggableListWidget, self).dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DraggableListWidget, self).dragMoveEvent(event)
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.dir_only:
                    if os.path.isdir(file_path):
                        self.addItemWidget(file_path)
                else:
                    if os.path.isfile(file_path) or os.path.isdir(file_path):
                        self.addItemWidget(file_path)
        else:
            super(DraggableListWidget, self).dropEvent(event)
    
    def addItemWidget(self, file_path):
        item = QtWidgets.QListWidgetItem(self)
        widget = CustomListWidgetItem(file_path, self)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)

class CustomListWidgetItem(QtWidgets.QWidget):
    def __init__(self, file_path, parent_list_widget, parent=None):
        super(CustomListWidgetItem, self).__init__(parent)
        self.file_path = file_path
        self.parent_list_widget = parent_list_widget
        self.init_ui()
    
    def init_ui(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QtWidgets.QLabel(self.file_path)
        self.label.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label.setStyleSheet(
            """
            QLabel {
                padding: 3px;
                border: 1px solid rgb(70, 70, 70);
                border-radius: 5px;
            }
            """
        )
        self.layout.addWidget(self.label)
        
        self.remove_button = QtWidgets.QPushButton("X")
        self.remove_button.setFixedSize(25, 25)
        self.layout.addWidget(self.remove_button)
        
        self.remove_button.clicked.connect(self.remove_self)
    
    def remove_self(self):
        item = self.parent_list_widget.itemAt(self.pos())
        row = self.parent_list_widget.row(item)
        self.parent_list_widget.takeItem(row)


class CopierUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(CopierUI, self).__init__()
        self.set_ui()
        self.center()
        # self.test_connection()
        self.show()
        
    def set_ui(self) -> None:
        """
        Setup the UI of the application.
        """
        self.setWindowTitle("Multi Copier")
        self.setWindowIcon(QtGui.QIcon("./icon.png"))
        self.setMinimumWidth(1400)
        self.setMinimumHeight(600)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
               
        self.progress_bar_all = QtWidgets.QProgressBar()
        self.progress_bar_all.setValue(0)
        self.progress_bar_all.setTextVisible(True)
        self.progress_bar_all.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar_all.setRange(0, 100)
        self.progress_bar_all.setFixedHeight(30)
        self.main_layout.addWidget(self.progress_bar_all)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(30)
        self.main_layout.addWidget(self.progress_bar)
        
        self.hbox_1 = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.hbox_1)
        
        self.vbox_1 = QtWidgets.QVBoxLayout()
        self.label_origin = QtWidgets.QLabel("Origin")
        self.list_widget_origin = DraggableListWidget()
        self.vbox_1.addWidget(self.label_origin)
        self.vbox_1.addWidget(self.list_widget_origin)
        self.hbox_1.addLayout(self.vbox_1)
        
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(
            QtGui.QIcon(
                self.style().standardIcon(
                    QtWidgets.QStyle.SP_ArrowRight
                    )
                ).pixmap(
                    QtCore.QSize(20, 20)
                    )
            )
        self.hbox_1.addWidget(self.label)
        
        self.vbox_2 = QtWidgets.QVBoxLayout()
        self.label_destination = QtWidgets.QLabel("Destination")
        self.list_widget_destination = DraggableListWidget(None,True)
        self.vbox_2.addWidget(self.label_destination)
        self.vbox_2.addWidget(self.list_widget_destination)
        self.hbox_1.addLayout(self.vbox_2)
        
        self.hbox_2 = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.hbox_2)
        
        self.label_copying = QtWidgets.QLabel("Copying")
        self.hbox_2.addWidget(self.label_copying)
        
        self.line_edit_file = QtWidgets.QLineEdit()
        self.line_edit_file.setReadOnly(True)
        self.line_edit_file.setFocusPolicy(QtCore.Qt.NoFocus)
        self.line_edit_file.setFixedWidth(280)
        self.hbox_2.addWidget(self.line_edit_file)
        
        self.label_to = QtWidgets.QLabel("to")
        self.hbox_2.addWidget(self.label_to)
        
        self.line_edit_dst = QtWidgets.QLineEdit()
        self.line_edit_dst.setReadOnly(True)
        self.line_edit_dst.setFocusPolicy(QtCore.Qt.NoFocus)
        self.line_edit_dst.setFixedWidth(280)
        self.hbox_2.addWidget(self.line_edit_dst)
        
        self.spacer_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hbox_2.addItem(self.spacer_1)
        
        self.button_copy = QtWidgets.QPushButton("Copy")
        self.button_copy.setFixedWidth(100)
        self.hbox_2.addWidget(self.button_copy)
        
        self.button_stop = QtWidgets.QPushButton("Stop")
        self.button_stop.setFixedWidth(100)
        self.hbox_2.addWidget(self.button_stop)
        
        # Set Menu
        self.menu_bar = self.menuBar()
        self.menu_option = self.menu_bar.addMenu("Option")
        self.menu_option.setToolTipsVisible(True)
        
        self.action_email = QtWidgets.QAction("Email", self)
        self.action_email.setCheckable(True)
        self.action_email.setChecked(True)
        self.action_email.setToolTip("Send an email after the copying process.")
        self.menu_option.addAction(self.action_email)
        
        self.action_rocketchat = QtWidgets.QAction("RocketChat", self)
        self.action_rocketchat.setCheckable(True)
        self.action_rocketchat.setChecked(True)
        self.action_rocketchat.setToolTip("Send a message to RocketChat after the copying process.")
        self.menu_option.addAction(self.action_rocketchat)
        qdarktheme.setup_theme()
    
    def center(self) -> None:
        """
        Set the window to the center of the screen.
        """
        frame_geometry = self.frameGeometry()
        screen_center = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
    def test_connection(self) -> None:
        """
        Test the connection between the UI and the backend.
        """
        self.button_copy.clicked.connect(lambda: print("Copy"))
        self.button_stop.clicked.connect(lambda: print("Stop"))
        self.action_email.triggered.connect(lambda: print("Email"))
        self.action_rocketchat.triggered.connect(lambda: print("RocketChat"))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    renamer_ui = CopierUI()
    renamer_ui.show()
    app.exec_()