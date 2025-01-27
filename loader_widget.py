import os
import json
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets

ICONPATH = os.path.join(os.path.dirname(__file__), "icons")

def set_icon(widget, name=None, size=None):
    """
    Sets icon for a widget. Looks in ICONPATH for icon.
    @args:
        widget: QWidget
        name: string icon name
        size: tuple height width
    @return
    """
    icon = os.path.join(ICONPATH, name)

    widget.setIcon(QtGui.QIcon(icon))
    if size:
        widget.setIconSize(QtCore.QSize(size[0], size[1]))
         
class SearchLine(QtWidgets.QWidget):
    nameChanged = QtCore.Signal(tuple)
    patternChanged = QtCore.Signal(tuple)
    btnCklicked = QtCore.Signal(int)
    reorderCklicked = QtCore.Signal(tuple)

    def __init__(self, _id, value):
        super(SearchLine, self).__init__()
        self.__id = _id
        self.name, self.pattern = value
        self.label = QtWidgets.QLabel(self.name)
        self.label.setFixedWidth(120)
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setFixedWidth(120)
        self.line_edit.setHidden(True)

        self.led_pattern = QtWidgets.QLineEdit(self.pattern)

        delete_btn = QtWidgets.QPushButton()
        set_icon(delete_btn, "delete.svg", (16, 16))
        
        self.up_btn = QtWidgets.QPushButton()
        set_icon(self.up_btn, "caret-up.svg", (16, 8))
        self.down_btn = QtWidgets.QPushButton()
        set_icon(self.down_btn, "caret-down.svg", (16, 8))
        
        self.layout = QtWidgets.QHBoxLayout(self)
        
        self.name_lyt = QtWidgets.QVBoxLayout()
        self.name_lyt.addWidget(self.label)
        self.name_lyt.addWidget(self.line_edit)

        self.caret_lyt = QtWidgets.QVBoxLayout()
        self.caret_lyt.setSpacing(0)
        self.caret_lyt.addWidget(self.up_btn)
        self.caret_lyt.addWidget(self.down_btn)
        
        self.layout.addLayout(self.name_lyt)
        self.layout.addWidget(self.led_pattern)
        self.layout.addWidget(delete_btn)
        self.layout.addLayout(self.caret_lyt)

        self.label.mousePressEvent = self.enable_editing
        self.line_edit.editingFinished.connect(self.disable_editing)

        self.led_pattern.editingFinished.connect(self.emmit_pattern)
        self.led_pattern.returnPressed.connect(self.emmit_pattern)

        delete_btn.clicked.connect(self.emmit_click)
        
        self.up_btn.clicked.connect(partial(self.emmit_reorder, -1))
        self.down_btn.clicked.connect(partial(self.emmit_reorder, 1))

    def emmit_reorder(self, step):
        self.reorderCklicked.emit((self.__id, step))

    def emmit_click(self):
        self.btnCklicked.emit(self.__id)

    def emmit_pattern(self):
        value_to_send = self.led_pattern.text()
        self.patternChanged.emit((self.__id, value_to_send))

    def enable_editing(self, event):
        self.label.setHidden(True)
        self.line_edit.setHidden(False)
        self.line_edit.setText(self.label.text())
        self.line_edit.setFocus()
        self.line_edit.selectAll()

    def disable_editing(self):
        self.label.setHidden(False)
        self.line_edit.setHidden(True)
        label_text = self.line_edit.text()
        self.label.setText(label_text)
        self.nameChanged.emit((self.__id, label_text))

    def updateValue(self):
        return
        
    def makeUI(self):
        return self

class QueryWidget(QtWidgets.QWidget):
    def __init__(self, node, storage):
        super(QueryWidget, self).__init__()

        self.__node = node
        self.__storage = self.__node.knob(storage)

        self.load_values()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.populate()

    @staticmethod
    def spacer(type='horizontal'):
        """Makes horizontal or vertical QtWidgets.QSpacerItem."""
        if type == 'vertical':
            return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        elif type == 'horizontal':
            return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        else:
            return None

    def load_values(self):
        storage = self.__storage.getText()
        if storage == "":
            storage = "[]"

        self.__values = json.loads(storage)

    def update_values(self):
        self.__storage.setValue(json.dumps(self.__values))

    def create_widgets(self):
        self.add_line_btn = QtWidgets.QPushButton()
        set_icon(self.add_line_btn, "add.svg", (16, 16))

    def create_layout(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.search_layout = QtWidgets.QVBoxLayout()
        self.search_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_layout.addWidget(self.add_line_btn)
        self.btn_layout.addItem(self.spacer())
        self.layout.addLayout(self.btn_layout)
        self.layout.addLayout(self.search_layout)

    def create_connections(self):
        self.add_line_btn.clicked.connect(self.add_line)

    def populate(self):
        self.load_values()
        self.clear_layout(self.search_layout)
        for n, line in enumerate(self.__values):
            srch_line = SearchLine(n, line)
            srch_line.nameChanged.connect(self.update_name)
            srch_line.patternChanged.connect(self.update_pattern)
            srch_line.btnCklicked.connect(self.delete_line)
            srch_line.reorderCklicked.connect(self.reorder_line)
            self.search_layout.addWidget(srch_line)
        self.search_layout.addItem(self.spacer("vertical"))
        
    def add_line(self):
        self.__values.append(["search", ""])
        self.update_values()

    def update_name(self, value):
        _id, name = value
        self.__values[_id][0] = name
        self.update_values()

    def update_pattern(self, value):
        _id, pattern = value
        self.__values[_id][1] = pattern
        self.update_values()

    def delete_line(self, _id):
        del self.__values[_id]
        self.update_values()

    def reorder_line(self, value):
        index, step = value
        
        new_index = index+step
        if new_index>=0 and new_index<len(self.__values):
            self.__values.insert(new_index, self.__values.pop(index))
            self.update_values()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self.clear_layout(sub_layout)

    def updateValue(self):
        return

    def makeUI(self):
        return self

class ExecutionBtns(QtWidgets.QWidget):
    def __init__(self, node):
        super(ExecutionBtns, self).__init__()
        self.__node = node
        layout = QtWidgets.QVBoxLayout(self)
        self.exec_btn = QtWidgets.QPushButton("Execute")
        self.valid_btn = QtWidgets.QPushButton("Validate")
        layout.addWidget(self.exec_btn)
        layout.addWidget(self.valid_btn)

        self.exec_btn.clicked.connect(self.execute)
        self.valid_btn.clicked.connect(self.validate)

    def validate(self):
        self.__node["_validate"].execute()

    def execute(self):
        self.__node["_execute"].execute()

    def updateValue(self):
        return

    def makeUI(self):
        return self
    
def main():
    pass

if __name__ == '__main__':
    main()
