
import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QLabel, QVBoxLayout, QWidget, QAction, QFileDialog, QLineEdit,
    QDialog, QTabWidget, QHBoxLayout, QMessageBox, QMenu, QTextBrowser
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard, QFont, QIcon

class AsciiTable(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Conversion Table v1.2")
        self.setWindowIcon(QIcon("asciihex.png"))
        self.setGeometry(100, 100, 600, 500)

        self.dark_mode = False
        self.font_size = 10

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search ASCII, Dec, Hex...")
        self.search_input.textChanged.connect(self.perform_search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setRowCount(16)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([f"Col {i}" for i in range(8)])
        self.table.setVerticalHeaderLabels([f"Row {i}" for i in range(16)])
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.output_label = QLabel("Selected: None | Dec: - | Hex: -")
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 6px;")

        self.populate_table()

        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.output_label)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.init_menu()
        self.apply_font_size()

    def populate_table(self):
        self.cells = {}
        for code in range(128):
            row = code // 8
            col = code % 8
            char = chr(code) if 32 <= code <= 126 else f"[{code}]"
            item = QTableWidgetItem(char)
            item.setToolTip(f"Dec: {code} | Hex: {hex(code).upper()}")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, item)
            self.cells[code] = (row, col)

    def on_cell_clicked(self, row, col):
        self.show_selection(row, col)

    def show_selection(self, row, col):
        code = row * 8 + col
        char = chr(code) if 32 <= code <= 126 else f"[{code}]"
        hex_val = hex(code).upper()
        self.output_label.setText(f"Selected: {char} | Dec: {code} | Hex: {hex_val}")
        self.last_selection = f"{char} | Dec: {code} | Hex: {hex_val}"
        self.last_code = code

    def perform_search(self, text):
        text = text.strip().lower()
        for code in range(128):
            row, col = self.cells[code]
            item = self.table.item(row, col)
            if item:
                item.setBackground(Qt.white)

        if not text:
            return

        for code in range(128):
            row, col = self.cells[code]
            item = self.table.item(row, col)
            char = chr(code) if 32 <= code <= 126 else f"[{code}]".lower()
            dec_str = str(code)
            hex_str = hex(code).lower()

            if (text == char.lower() or text == dec_str or text == hex_str):
                item.setBackground(Qt.yellow)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export ASCII Table", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Dec", "Hex", "Char"])
                    for code in range(128):
                        char = chr(code) if 32 <= code <= 126 else f"[{code}]"
                        writer.writerow([code, hex(code).upper(), char])
                QMessageBox.information(self, "Export", f"Table exported successfully to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export: {e}")

    def toggle_dark_mode(self):
        if not self.dark_mode:
            self.setStyleSheet(
                "QMainWindow { background-color: #2b2b2b; color: #f0f0f0; }"
                "QTableWidget { background-color: #3c3f41; color: #f0f0f0; }"
                "QLineEdit { background-color: #555555; color: #f0f0f0; }"
                "QLabel { color: #f0f0f0; }"
            )
            self.dark_mode = True
        else:
            self.setStyleSheet("")
            self.dark_mode = False

    def apply_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        self.table.setFont(font)

    def set_font_size(self, size):
        self.font_size = size
        self.apply_font_size()

    def copy_selection(self):
        if hasattr(self, 'last_selection'):
            clipboard = QApplication.clipboard()
            clipboard.setText(self.last_selection)
        else:
            QMessageBox.information(self, "Copy", "No selection to copy.")

    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if item:
            row = item.row()
            col = item.column()
            self.show_selection(row, col)

            code = row * 8 + col
            char = chr(code) if 32 <= code <= 126 else f"[{code}]"
            hex_val = hex(code).upper()
            dec_val = str(code)

            menu = QMenu()
            menu.addAction(f"Copy Char: {char}", lambda: self.copy_text(char))
            menu.addAction(f"Copy Dec: {dec_val}", lambda: self.copy_text(dec_val))
            menu.addAction(f"Copy Hex: {hex_val}", lambda: self.copy_text(hex_val))
            menu.addAction(f"Copy Full: {char} | Dec: {dec_val} | Hex: {hex_val}", lambda: self.copy_text(f"{char} | Dec: {dec_val} | Hex: {hex_val}"))
            menu.exec_(self.table.viewport().mapToGlobal(position))

    def copy_text(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        export_action = QAction("Export CSV", self)
        export_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_action)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("Edit")
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(copy_action)

        view_menu = menubar.addMenu("View")
        dark_action = QAction("Toggle Dark Mode", self)
        dark_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(dark_action)
        view_menu.addAction(QAction("Font Small", self, triggered=lambda: self.set_font_size(8)))
        view_menu.addAction(QAction("Font Medium", self, triggered=lambda: self.set_font_size(10)))
        view_menu.addAction(QAction("Font Large", self, triggered=lambda: self.set_font_size(14)))

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        help_action = QAction("How to Use ASCIIHEX", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def show_help(self):
        html_content = '''
        <h2>How to Use ASCIIHEX Table</h2>
        <p>This application displays the standard ASCII characters along with their decimal and hexadecimal values.</p>
        <ul>
            <li><b>Click</b> a cell to view its ASCII, decimal, and hex values in the output pane.</li>
            <li><b>Right-click</b> a cell to copy its data in various formats.</li>
            <li>Use the <b>search bar</b> to find characters by char, decimal, or hex code.</li>
            <li><b>Export</b> the table as CSV using File > Export CSV.</li>
            <li><b>Adjust font size</b> or <b>toggle dark mode</b> using the View menu.</li>
            <li>Access this help from Help > How to Use ASCIIHEX.</li>
        </ul>
        <p>Version 1.2<br>Author: Dr. Eric Oliver Flores</p>
        '''
        dlg = QDialog(self)
        dlg.setWindowTitle("How to Use ASCIIHEX")
        dlg.setFixedSize(400, 300)
        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setHtml(html_content)
        layout.addWidget(text_browser)
        dlg.setLayout(layout)
        dlg.exec_()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ASCII / Hex Table")
        self.setFixedSize(300, 200)

        tabs = QTabWidget()
        tabs.addTab(self.create_about_tab(), "About")
        tabs.addTab(self.create_tech_tab(), "Technologies")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("ASCII / Hex Table"))
        layout.addWidget(QLabel("Version 1.2"))
        layout.addWidget(QLabel("by Dr. Eric Oliver Flores"))
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tech_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Python 3.x"))
        layout.addWidget(QLabel("PyQt5"))
        layout.addWidget(QLabel("Qt Framework"))
        layout.addWidget(QLabel("Tested on Linux"))
        layout.addStretch()
        widget.setLayout(layout)
        return widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AsciiTable()
    window.show()
    sys.exit(app.exec_())