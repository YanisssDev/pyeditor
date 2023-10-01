import sys
import os
import subprocess
from PyQt5.QtWidgets import QInputDialog, QApplication, QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QTabWidget, QPushButton, QStyleFactory
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QTextCursor, QFont, QIcon
from PyQt5.QtCore import Qt, QRegExp

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)
        self.parent = parent

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.darkBlue)
        keyword_format.setFontWeight(QFont.Bold)

        keywords = ["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]

        self.keyword_patterns = [r'\b' + keyword + r'\b' for keyword in keywords]

        self.highlighting_rules = [(QRegExp(pattern), keyword_format) for pattern in self.keyword_patterns]

        string_format = QTextCharFormat()
        string_format.setForeground(Qt.red)
        string_format.setFontWeight(QFont.Normal)

        self.highlighting_rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class PythonEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Éditeur de Code Python')
        self.setWindowIcon(QIcon('icon.png'))

        self.setup_editor_tabs()
        self.setup_menu_bar()
        self.setup_tool_bar()
        self.setup_status_bar()

    def setup_editor_tabs(self):
        self.editor_tabs = QTabWidget(self)
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.editor_tabs.currentChanged.connect(self.editor_tab_changed)
        self.editor_tabs.setMovable(True)
        self.setCentralWidget(self.editor_tabs)

        self.new_editor()

    def setup_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Fichier')

        new_action = QAction('Nouveau', self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction('Ouvrir', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Enregistrer', self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction('Enregistrer sous...', self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        exit_action = QAction('Quitter', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_tool_bar(self):
        toolbar = self.addToolBar('Toolbar')

        run_action = QAction('Exécuter', self)
        run_action.triggered.connect(self.run_code)
        toolbar.addAction(run_action)

        pip_install_action = QAction('pip install', self)
        pip_install_action.triggered.connect(self.pip_install)
        toolbar.addAction(pip_install_action)

    def setup_status_bar(self):
        statusbar = self.statusBar()
        statusbar.showMessage('Prêt')

    def new_editor(self):
        editor = CodeEditor()

        editor_tab = QWidget()
        layout = QVBoxLayout(editor_tab)
        layout.addWidget(editor)

        self.editor_tabs.addTab(editor_tab, "Nouveau fichier")
        self.editor_tabs.setCurrentWidget(editor_tab)

    def new_file(self):
        self.new_editor()

    def open_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName()
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.new_editor()
                current_editor = self.editor_tabs.currentWidget()
                current_editor.layout().itemAt(0).widget().setPlainText(content)

    def save_file(self):
        current_editor = self.editor_tabs.currentWidget()
        editor_widget = current_editor.layout().itemAt(0).widget()
        if hasattr(editor_widget, 'file_path'):
            with open(editor_widget.file_path, 'w') as file:
                file.write(editor_widget.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        current_editor = self.editor_tabs.currentWidget()
        editor_widget = current_editor.layout().itemAt(0).widget()
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName()
        if file_path:
            editor_widget.file_path = file_path
            self.setWindowTitle(f'Éditeur de Code Python - {file_path}')
            self.save_file()

    def run_code(self):
        current_editor = self.editor_tabs.currentWidget()
        editor_widget = current_editor.layout().itemAt(0).widget()
        code = editor_widget.toPlainText()

        temp_script_path = os.path.join(os.getcwd(), "temp_script.py")
        with open(temp_script_path, "w") as temp_script_file:
            temp_script_file.write(code)

        os.system(f"python {temp_script_path}")

    def pip_install(self):
        module_name, ok = QInputDialog.getText(self, 'Installer un module', 'Nom du module :')
        if ok and module_name:
            subprocess.Popen(f'cmd.exe /K pip install {module_name}', shell=True)

    def close_editor_tab(self, index):
        editor_to_close = self.editor_tabs.widget(index)
        self.editor_tabs.removeTab(index)
        editor_to_close.deleteLater()

    def editor_tab_changed(self, index):
        if index != -1:
            current_editor = self.editor_tabs.widget(index)
            current_editor_widget = current_editor.layout().itemAt(0).widget()
            self.setWindowTitle(f'Éditeur de Code Python - {current_editor_widget.file_path if hasattr(current_editor_widget, "file_path") else "Nouveau fichier"}')

class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.setStyleSheet("font-family: 'Courier New', monospace; font-size: 18px; background-color: #1e1e1e; color: #d4d4d4;")
        self.setTabStopWidth(20)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setPlainText("Enter your Python code here...")

        self.highlighter = PythonHighlighter(self)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    editor = PythonEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
