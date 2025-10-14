import sys, csv, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QLabel, QVBoxLayout, QWidget, QAction, QFileDialog, QLineEdit,
    QDialog, QTabWidget, QHBoxLayout, QMessageBox, QMenu, QTextBrowser,
    QInputDialog, QToolBar, QStatusBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QClipboard, QFont, QIcon, QPalette, QColor, QGuiApplication

CONTROL_NAMES = {
    0:"NUL",1:"SOH",2:"STH",3:"ETX",4:"EOT",5:"ENQ",6:"ACK",7:"BEL",
    8:"BS",9:"TAB",10:"LF",11:"VT",12:"FF",13:"CR",14:"SO",15:"SI",
    16:"DLE",17:"DC1",18:"DC2",19:"DC3",20:"DC4",21:"NAK",22:"SYN",23:"ETB",
    24:"CAN",25:"EM",26:"SUB",27:"ESC",28:"FS",29:"GS",30:"RS",31:"US",
    127:"DEL"
}

def hex_str(n: int) -> str:
    return f"0x{n:02X}"

def bin_str(n: int) -> str:
    return "0b" + format(n, "08b")

def c_escape(n: int) -> str:
    return f"\\x{n:02X}"

def py_escape(n: int) -> str:
    return f"\\x{n:02x}"

class AsciiTable(QMainWindow):
    def __init__(self, start_dark: bool = False):
        super().__init__()
        self.setWindowTitle("ASCII Conversion Table v1.3")
        # Safe icon fallback
        icon_path = "asciihex.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(720, 560)

        self.dark_mode = False
        self.font_size = 10
        self.extended = False  # 0–127 default

        # Central UI
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Search row
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search char, dec, hex (e.g., A, 65, 0x41)…  Esc clears")
        self.search_input.textChanged.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.focus_table_first_hit)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setRowCount(16)
        self.table.setColumnCount(8)
        self._apply_headers()
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.horizontalHeader().setDefaultSectionSize(72)

        self.output_label = QLabel("Selected: None | Dec: - | Hex: -")
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 6px;")

        self.populate_table()

        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.output_label)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Menus/toolbar/status
        self.init_menu()
        self._init_toolbar()
        self.setStatusBar(QStatusBar())
        self.apply_font_size()

        # Keyboard shortcuts
        self.search_input.installEventFilter(self)

        if start_dark:
            self.toggle_dark_mode()

    # --- UI helpers ---
    def _apply_headers(self):
        self.table.setHorizontalHeaderLabels([f"C{i}" for i in range(8)])
        self.table.setVerticalHeaderLabels([f"R{i}" for i in range(16)])

    def apply_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        self.table.setFont(font)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def set_font_size(self, size):
        self.font_size = size
        self.apply_font_size()

    # --- Data population ---
    def range_max(self):
        return 256 if self.extended else 128

    def populate_table(self):
        self.table.clearContents()
        self.cells = {}
        max_code = self.range_max()
        for code in range(max_code):
            row = code // 8
            col = code % 8
            if row >= self.table.rowCount():
                self.table.insertRow(self.table.rowCount())
            if col >= self.table.columnCount():
                self.table.insertColumn(self.table.columnCount())

            # Choose display char
            if 32 <= code <= 126:
                char_display = chr(code)
            elif code in CONTROL_NAMES:
                char_display = f"[{CONTROL_NAMES[code]}]"
            else:
                # Extended Latin-1 printable range hint
                try:
                    ch = chr(code)
                    char_display = ch if ch.isprintable() else f"[{code}]"
                except Exception:
                    char_display = f"[{code}]"

            item = QTableWidgetItem(char_display)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setToolTip(f"Dec: {code} | Hex: {hex_str(code)}")
            self.table.setItem(row, col, item)
            self.cells[code] = (row, col)

        # Make sure we have exactly enough rows for the range
        needed_rows = (max_code + 7) // 8
        while self.table.rowCount() > needed_rows:
            self.table.removeRow(self.table.rowCount() - 1)
        self.table.resizeColumnsToContents()

    # --- Selection / copy ---
    def on_cell_clicked(self, row, col):
        self.show_selection(row, col)

    def code_from_rc(self, row, col):
        return row * 8 + col

    def show_selection(self, row, col):
        code = self.code_from_rc(row, col)
        if code >= self.range_max():
            return
        if 32 <= code <= 126:
            char = chr(code)
        elif code in CONTROL_NAMES:
            char = f"[{CONTROL_NAMES[code]}]"
        else:
            ch = chr(code)
            char = ch if ch.isprintable() else f"[{code}]"
        hx = hex_str(code)
        self.output_label.setText(f"Selected: {char} | Dec: {code} | Hex: {hx}")
        self.last_selection = f"{char} | Dec: {code} | Hex: {hx}"
        self.last_code = code
        self.statusBar().showMessage(f"Copied target ready: {self.last_selection}", 2000)

    def copy_selection(self):
        if hasattr(self, 'last_selection'):
            QApplication.clipboard().setText(self.last_selection)
            self.statusBar().showMessage("Copied full selection", 1500)
        else:
            QMessageBox.information(self, "Copy", "No selection to copy.")

    def copy_text(self, text):
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage("Copied", 1200)

    # --- Search ---
    def clear_highlights(self):
        pal = self.table.palette()
        base = pal.base().color()
        for code, (r, c) in self.cells.items():
            it = self.table.item(r, c)
            if it:
                it.setBackground(base)

    def perform_search(self, text):
        text = text.strip().lower()
        self.clear_highlights()
        if not text:
            return

        first = None
        for code in range(self.range_max()):
            r, c = self.cells[code]
            it = self.table.item(r, c)
            if not it:
                continue
            char_disp = it.text().lower()
            dec_str = str(code)
            hx_str = hex_str(code).lower()
            if (text in char_disp) or (text in dec_str) or (text in hx_str):
                it.setBackground(QColor(255, 255, 150))  # soft yellow
                if first is None:
                    first = (r, c)

        if first:
            self.table.setCurrentCell(first[0], first[1])
            self.table.scrollToItem(self.table.item(first[0], first[1]))

    def focus_table_first_hit(self):
        cur = self.table.currentItem()
        if cur:
            self.on_cell_clicked(cur.row(), cur.column())

    # --- Export / save ---
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export ASCII Table", "", "CSV Files (*.csv)")
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        try:
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["Dec", "Hex", "Char"])
                for code in range(self.range_max()):
                    if 32 <= code <= 126:
                        ch = chr(code)
                    elif code in CONTROL_NAMES:
                        ch = CONTROL_NAMES[code]
                    else:
                        cp = chr(code)
                        ch = cp if cp.isprintable() else f"[{code}]"
                    w.writerow([code, hex_str(code), ch])
            QMessageBox.information(self, "Export", f"Table exported successfully to:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export:\n{e}")

    # --- Dark mode ---
    def toggle_dark_mode(self):
        if not self.dark_mode:
            pal = QPalette()
            pal.setColor(QPalette.Window, QColor(43, 43, 43))
            pal.setColor(QPalette.WindowText, QColor(240, 240, 240))
            pal.setColor(QPalette.Base, QColor(60, 63, 65))
            pal.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            pal.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
            pal.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
            pal.setColor(QPalette.Text, QColor(240, 240, 240))
            pal.setColor(QPalette.Button, QColor(53, 53, 53))
            pal.setColor(QPalette.ButtonText, QColor(240, 240, 240))
            pal.setColor(QPalette.Highlight, QColor(90, 122, 185))
            pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            QApplication.setPalette(pal)
            self.dark_mode = True
        else:
            QApplication.setPalette(QApplication.style().standardPalette())
            self.dark_mode = False

    # --- Context menu ---
    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return
        row, col = item.row(), item.column()
        self.show_selection(row, col)
        code = self.code_from_rc(row, col)
        if code >= self.range_max():
            return

        # derive values for copying
        char_disp = item.text()
        try:
            true_char = chr(code) if 32 <= code <= 0x10FFFF else ''
        except Exception:
            true_char = ''

        menu = QMenu()
        menu.addAction(f"Copy Char: {char_disp}", lambda: self.copy_text(char_disp))
        menu.addAction(f"Copy Dec: {code}", lambda: self.copy_text(str(code)))
        menu.addAction(f"Copy Hex: {hex_str(code)}", lambda: self.copy_text(hex_str(code)))
        menu.addAction(f"Copy Binary: {bin_str(code)}", lambda: self.copy_text(bin_str(code)))
        menu.addSeparator()
        menu.addAction(f"Copy C escape: {c_escape(code)}", lambda: self.copy_text(c_escape(code)))
        menu.addAction(f"Copy Python escape: {py_escape(code)}", lambda: self.copy_text(py_escape(code)))
        menu.addSeparator()
        menu.addAction("Copy Full", lambda: self.copy_selection())
        menu.exec_(self.table.viewport().mapToGlobal(position))

    # --- Menus / Toolbar ---
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
        copy_action = QAction("Copy Selection", self)
        copy_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(copy_action)
        goto_action = QAction("Go to…", self)
        goto_action.triggered.connect(self.goto_dialog)
        edit_menu.addAction(goto_action)
        clear_action = QAction("Clear Search (Esc)", self)
        clear_action.triggered.connect(lambda: self.search_input.clear())
        edit_menu.addAction(clear_action)

        view_menu = menubar.addMenu("View")
        dark_action = QAction("Toggle Dark Mode", self)
        dark_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(dark_action)
        view_menu.addAction(QAction("Font Small", self, triggered=lambda: self.set_font_size(8)))
        view_menu.addAction(QAction("Font Medium", self, triggered=lambda: self.set_font_size(10)))
        view_menu.addAction(QAction("Font Large", self, triggered=lambda: self.set_font_size(14)))
        ext_action = QAction("Show Extended (0–255)", self, checkable=True)
        ext_action.triggered.connect(self.toggle_extended)
        view_menu.addAction(ext_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        help_action = QAction("How to Use ASCIIHEX", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def _init_toolbar(self):
        tb = QToolBar("Main")
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(tb)

        act_copy = QAction("Copy", self)
        act_copy.triggered.connect(self.copy_selection)
        tb.addAction(act_copy)

        act_export = QAction("Export CSV", self)
        act_export.triggered.connect(self.export_csv)
        tb.addAction(act_export)

        act_dark = QAction("Dark", self)
        act_dark.triggered.connect(self.toggle_dark_mode)
        tb.addAction(act_dark)

        tb.addSeparator()

        act_small = QAction("A-", self)
        act_small.triggered.connect(lambda: self.set_font_size(max(6, self.font_size - 1)))
        tb.addAction(act_small)

        act_large = QAction("A+", self)
        act_large.triggered.connect(lambda: self.set_font_size(min(24, self.font_size + 1)))
        tb.addAction(act_large)

        tb.addSeparator()

        act_ext = QAction("0–255", self)
        act_ext.triggered.connect(self.toggle_extended)
        tb.addAction(act_ext)

    # --- Features ---
    def toggle_extended(self):
        self.extended = not self.extended
        self.populate_table()
        self.clear_highlights()
        self.statusBar().showMessage(f"Range: 0–{self.range_max()-1}", 1500)

    def goto_dialog(self):
        text, ok = QInputDialog.getText(self, "Go to…",
            "Enter Dec (e.g., 65), Hex (e.g., 0x41), or single character (e.g., A):")
        if not ok or not text.strip():
            return
        s = text.strip()
        code = None
        # char
        if len(s) == 1:
            code = ord(s)
        # hex
        elif s.lower().startswith("0x"):
            try:
                code = int(s, 16)
            except ValueError:
                pass
        else:
            # decimal
            try:
                code = int(s)
            except ValueError:
                pass

        if code is None:
            QMessageBox.warning(self, "Go to…", "Could not parse input.")
            return

        if code < 0 or code >= self.range_max():
            QMessageBox.warning(self, "Go to…", f"Code {code} out of range for current mode.")
            return

        r, c = self.cells[code]
        self.table.setCurrentCell(r, c)
        self.table.scrollToItem(self.table.item(r, c))
        self.show_selection(r, c)

    # --- Help / About ---
    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def show_help(self):
        html_content = '''
        <h2>How to Use ASCIIHEX Table</h2>
        <p>This application displays ASCII/Latin-1 characters with their decimal and hexadecimal values.</p>
        <ul>
            <li><b>Click</b> a cell to see values in the output bar.</li>
            <li><b>Right-click</b> to copy Char/Dec/Hex/Binary or escape codes.</li>
            <li><b>Search</b> live-filters: type char, dec, or hex (e.g., <code>A</code>, <code>65</code>, <code>0x41</code>).</li>
            <li><b>Export</b> CSV via File → Export CSV.</li>
            <li><b>View</b>: change font size, dark mode, or toggle extended 0–255.</li>
            <li><b>Go to…</b> (Edit menu) jumps directly to a code.</li>
            <li><b>Esc</b> clears the search box.</li>
        </ul>
        <p>Version 1.3<br>Author: Dr. Eric Oliver Flores</p>
        '''
        dlg = QDialog(self)
        dlg.setWindowTitle("How to Use ASCIIHEX")
        dlg.setFixedSize(460, 340)
        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setHtml(html_content)
        layout.addWidget(text_browser)
        dlg.setLayout(layout)
        dlg.exec_()

    # Allow Esc to clear when focus in search
    def eventFilter(self, obj, event):
        if obj is self.search_input and event.type() == event.KeyPress and event.key() == Qt.Key_Escape:
            self.search_input.clear()
            return True
        return super().eventFilter(obj, event)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ASCII / Hex Table")
        self.setFixedSize(320, 220)

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
        layout.addWidget(QLabel("Version 1.3"))
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
    # Optional: pass "--dark" to start with dark mode
    start_dark = "--dark" in sys.argv
    app = QApplication([a for a in sys.argv if a != "--dark"])
    window = AsciiTable(start_dark=start_dark)
    window.show()
    sys.exit(app.exec_())
