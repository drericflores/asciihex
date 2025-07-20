import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QLabel, QVBoxLayout, QWidget, QAction, QFileDialog, QLineEdit,
    QDialog, QTabWidget, QHBoxLayout, QMessageBox, QMenu, QTextBrowser,
    QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard, QFont, QIcon, QBrush, QColor
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

class AsciiTable(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Conversion Table v1.3 (Enhanced)")
        # Removed QIcon("asciihex.png") for broader compatibility.
        # You can add it back if you have the icon file.
        # self.setWindowIcon(QIcon("asciihex.png"))
        self.setGeometry(100, 100, 800, 600) # Increased size for new column

        self.dark_mode = False
        self.font_size = 10
        self.control_char_map = self._get_control_char_map() # Map for control characters

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search ASCII, Dec, Hex, Binary...")
        self.search_input.textChanged.connect(self.perform_search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setRowCount(256) # Extended to 256 for full ASCII range
        self.table.setColumnCount(4) # Dec, Hex, Char, Binary
        self.table.setHorizontalHeaderLabels(["Dec", "Hex", "Char", "Binary"])
        # Make headers stretch to fill space
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False) # Hide row headers for cleaner look
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionMode(QTableWidget.ContiguousSelection) # Allow multiple cell selection

        self.output_label = QLabel("Selected: None | Dec: - | Hex: - | Bin: -")
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
        self.apply_theme() # Apply initial theme

    def _get_control_char_map(self):
        """Returns a dictionary mapping control character codes to their mnemonics."""
        return {
            0: "NUL", 1: "SOH", 2: "STX", 3: "ETX", 4: "EOT", 5: "ENQ", 6: "ACK", 7: "BEL",
            8: "BS", 9: "HT", 10: "LF", 11: "VT", 12: "FF", 13: "CR", 14: "SO", 15: "SI",
            16: "DLE", 17: "DC1", 18: "DC2", 19: "DC3", 20: "DC4", 21: "NAK", 22: "SYN",
            23: "ETB", 24: "CAN", 25: "EM", 26: "SUB", 27: "ESC", 28: "FS", 29: "GS",
            30: "RS", 31: "US", 127: "DEL"
        }

    def populate_table(self):
        """Populates the table with ASCII, Decimal, Hex, and Binary values."""
        self.table.setSortingEnabled(False) # Disable sorting during population
        for code in range(256): # Iterate through full 256 ASCII range
            # Decimal column
            dec_item = QTableWidgetItem(str(code))
            dec_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(code, 0, dec_item)

            # Hexadecimal column
            hex_item = QTableWidgetItem(f"{code:02X}") # Always two digits for hex
            hex_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(code, 1, hex_item)

            # Character column
            char_display = self.control_char_map.get(code, chr(code) if 32 <= code <= 126 else ".")
            char_item = QTableWidgetItem(char_display)
            char_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(code, 2, char_item)

            # Binary column (new)
            bin_item = QTableWidgetItem(f"{code:08b}") # 8-bit binary
            bin_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(code, 3, bin_item)

            # Set tooltips for all items in the row
            tooltip_text = f"Dec: {code} | Hex: {code:02X} | Char: {char_display} | Bin: {code:08b}"
            dec_item.setToolTip(tooltip_text)
            hex_item.setToolTip(tooltip_text)
            char_item.setToolTip(tooltip_text)
            bin_item.setToolTip(tooltip_text)

        self.table.setSortingEnabled(True) # Re-enable sorting

    def on_cell_clicked(self, row, col):
        """Updates the output label when a cell is clicked."""
        code = row # Row number directly corresponds to ASCII code
        self.show_selection_info(code)

    def show_selection_info(self, code):
        """Displays detailed information about the selected ASCII code."""
        char_display = self.control_char_map.get(code, chr(code) if 32 <= code <= 126 else ".")
        dec_val = str(code)
        hex_val = f"{code:02X}"
        bin_val = f"{code:08b}"
        self.output_label.setText(f"Selected: {char_display} | Dec: {dec_val} | Hex: {hex_val} | Bin: {bin_val}")
        # Store last selection for single copy action
        self.last_selection_info = {
            "char": char_display,
            "dec": dec_val,
            "hex": hex_val,
            "bin": bin_val,
            "full": f"Char: {char_display} | Dec: {dec_val} | Hex: {hex_val} | Bin: {bin_val}"
        }

    def perform_search(self, text):
        """Performs a search and highlights matching cells, scrolling to the first match."""
        text = text.strip().lower()
        first_match_row = -1

        # Clear previous highlights
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(self.table.palette().base().color()) # Reset to default background

        if not text:
            return

        for code in range(self.table.rowCount()): # Iterate through all codes
            dec_str = str(code)
            hex_str = f"{code:02X}".lower()
            bin_str = f"{code:08b}"
            char_display = self.control_char_map.get(code, chr(code) if 32 <= code <= 126 else ".").lower()

            # Check if any part of the row matches the search text
            if (text == dec_str or text == hex_str or text == bin_str or text == char_display):
                for col in range(self.table.columnCount()):
                    item = self.table.item(code, col)
                    if item:
                        item.setBackground(QBrush(QColor("yellow"))) # Highlight
                if first_match_row == -1:
                    first_match_row = code # Store the first match row

        # Scroll to the first found item
        if first_match_row != -1:
            self.table.scrollToItem(self.table.item(first_match_row, 0), QTableWidget.EnsureVisible)

    def export_csv(self):
        """Exports the entire ASCII table to a CSV file."""
        path, _ = QFileDialog.getSaveFileName(self, "Export ASCII Table", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Dec", "Hex", "Char", "Binary"]) # Updated header
                    for code in range(256): # Export full range
                        char_display = self.control_char_map.get(code, chr(code) if 32 <= code <= 126 else ".")
                        writer.writerow([code, f"{code:02X}", char_display, f"{code:08b}"])
                QMessageBox.information(self, "Export", f"Table exported successfully to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export: {e}")

    def toggle_dark_mode(self):
        """Toggles between light and dark mode themes."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Applies the selected theme (light/dark) to the application."""
        if self.dark_mode:
            self.setStyleSheet(
                "QMainWindow { background-color: #2b2b2b; color: #f0f0f0; }"
                "QTableWidget { background-color: #3c3f41; color: #f0f0f0; gridline-color: #555555; }"
                "QTableWidget::item { selection-background-color: #4a4a4a; selection-color: #f0f0f0; }"
                "QHeaderView::section { background-color: #555555; color: #f0f0f0; }"
                "QLineEdit { background-color: #555555; color: #f0f0f0; border: 1px solid #777777; }"
                "QLabel { color: #f0f0f0; }"
                "QMenu { background-color: #3c3f41; color: #f0f0f0; border: 1px solid #555555; }"
                "QMenu::item:selected { background-color: #4a4a4a; }"
                "QMessageBox { background-color: #2b2b2b; color: #f0f0f0; }"
                "QDialog { background-color: #2b2b2b; color: #f0f0f0; }"
                "QTextBrowser { background-color: #3c3f41; color: #f0f0f0; }"
                "QTabWidget::pane { border: 1px solid #555555; }"
                "QTabBar::tab { background-color: #555555; color: #f0f0f0; }"
                "QTabBar::tab:selected { background-color: #3c3f41; }"
            )
        else:
            self.setStyleSheet("") # Reset to default system theme

        # Reapply font size to ensure it persists with theme changes
        self.apply_font_size()
        # Clear and re-populate table to ensure item background colors are reset correctly
        # This is a bit heavy-handed, but ensures highlight clearing works with theme changes.
        self.populate_table()


    def apply_font_size(self):
        """Applies the current font size to the table and other relevant widgets."""
        font = QFont()
        font.setPointSize(self.font_size)
        self.table.setFont(font)
        self.search_input.setFont(font)
        # Adjust output label font size slightly larger
        output_font = QFont()
        output_font.setPointSize(self.font_size + 4)
        output_font.setBold(True)
        self.output_label.setFont(output_font)

    def set_font_size(self, size):
        """Sets the font size and reapplies it."""
        self.font_size = size
        self.apply_font_size()

    def copy_selection(self):
        """Copies the information of the last clicked cell to the clipboard."""
        if hasattr(self, 'last_selection_info'):
            clipboard = QApplication.clipboard()
            clipboard.setText(self.last_selection_info["full"])
        else:
            QMessageBox.information(self, "Copy", "No selection to copy.")

    def copy_multiple_selections(self):
        """Copies data from all currently selected cells."""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            QMessageBox.information(self, "Copy", "No cells selected to copy.")
            return

        copied_data_lines = []
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                for col in range(r.leftColumn(), r.rightColumn() + 1):
                    item = self.table.item(row, col)
                    if item:
                        code = row # Row index is the ASCII code
                        char_display = self.control_char_map.get(code, chr(code) if 32 <= code <= 126 else ".")
                        dec_val = str(code)
                        hex_val = f"{code:02X}"
                        bin_val = f"{code:08b}"
                        copied_data_lines.append(f"Dec: {dec_val}, Hex: {hex_val}, Char: {char_display}, Bin: {bin_val}")

        if copied_data_lines:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(copied_data_lines))
            QMessageBox.information(self, "Copy", f"Copied {len(copied_data_lines)} entries to clipboard.")
        else:
            QMessageBox.information(self, "Copy", "No valid data found in selection.")


    def show_context_menu(self, position):
        """Displays a context menu for copying specific data from a cell."""
        item = self.table.itemAt(position)
        if item:
            row = item.row()
            # col = item.column() # Not directly used for code, as row is the code

            code = row # Row number is the ASCII code
            char_display = self.control_char_map.get(code, chr(code) if 32 <= code <= 126 else ".")
            dec_val = str(code)
            hex_val = f"{code:02X}"
            bin_val = f"{code:08b}"

            # Update the output label for the right-clicked cell
            self.show_selection_info(code)

            menu = QMenu()
            menu.addAction(f"Copy Char: {char_display}", lambda: self.copy_text(char_display))
            menu.addAction(f"Copy Dec: {dec_val}", lambda: self.copy_text(dec_val))
            menu.addAction(f"Copy Hex: {hex_val}", lambda: self.copy_text(hex_val))
            menu.addAction(f"Copy Bin: {bin_val}", lambda: self.copy_text(bin_val))
            menu.addSeparator()
            menu.addAction(f"Copy Full: {self.last_selection_info['full']}", lambda: self.copy_text(self.last_selection_info['full']))
            menu.addSeparator()
            menu.addAction("Copy All Selected Cells", self.copy_multiple_selections) # New action

            menu.exec_(self.table.viewport().mapToGlobal(position))

    def copy_text(self, text):
        """Helper function to copy arbitrary text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def init_menu(self):
        """Initializes the application's menu bar."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        export_action = QAction("Export CSV", self)
        export_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_action)

        print_action = QAction("Print Table", self) # New print action
        print_action.triggered.connect(self.print_table)
        file_menu.addAction(print_action)

        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("Edit")
        copy_single_action = QAction("Copy Selected Cell Info", self)
        copy_single_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(copy_single_action)

        copy_multiple_action = QAction("Copy All Selected Cells", self)
        copy_multiple_action.triggered.connect(self.copy_multiple_selections)
        edit_menu.addAction(copy_multiple_action)


        view_menu = menubar.addMenu("View")
        dark_action = QAction("Toggle Dark Mode", self)
        dark_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(dark_action)
        view_menu.addSeparator()
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

    def print_table(self):
        """Prints the content of the QTableWidget."""
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            # Create a QTextDocument from the table content
            document = self._create_document_from_table()
            document.print_(printer)
            QMessageBox.information(self, "Print", "Table sent to printer.")

    def _create_document_from_table(self):
        """Creates a QTextDocument from the table's content for printing."""
        document = QTextBrowser() # Use QTextBrowser to leverage its HTML rendering
        html_content = "<html><head><style>"
        html_content += "table { width: 100%; border-collapse: collapse; font-family: monospace; }"
        html_content += "th, td { border: 1px solid black; padding: 4px; text-align: center; }"
        html_content += "</style></head><body>"
        html_content += "<h1>ASCII Conversion Table</h1>"
        html_content += "<table><thead><tr>"
        for i in range(self.table.columnCount()):
            html_content += f"<th>{self.table.horizontalHeaderItem(i).text()}</th>"
        html_content += "</tr></thead><tbody>"

        for row in range(self.table.rowCount()):
            html_content += "<tr>"
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                html_content += f"<td>{item.text() if item else ''}</td>"
            html_content += "</tr>"
        html_content += "</tbody></table></body></html>"
        document.setHtml(html_content)
        return document


    def show_about(self):
        """Displays the About dialog."""
        dlg = AboutDialog(self)
        dlg.exec_()

    def show_help(self):
        """Displays the How to Use help dialog."""
        html_content = '''
        <h2>How to Use ASCIIHEX Table</h2>
        <p>This application displays ASCII characters (0-255) along with their decimal, hexadecimal, and binary values.</p>
        <ul>
            <li><b>Click</b> a cell to view its detailed information in the output pane.</li>
            <li><b>Right-click</b> a cell to copy its data in various formats.</li>
            <li><b>Select multiple cells</b> (drag or Ctrl/Shift+click) and right-click to copy all selected data.</li>
            <li>Use the <b>search bar</b> to find characters by ASCII char, decimal, hex, or binary code.</li>
            <li><b>Export</b> the table as CSV using File > Export CSV.</li>
            <li><b>Print</b> the table using File > Print Table.</li>
            <li><b>Adjust font size</b> or <b>toggle dark mode</b> using the View menu.</li>
            <li>Access this help from Help > How to Use ASCIIHEX.</li>
        </ul>
        <p>Version 1.3 (Enhanced)<br>Author: Dr. Eric Oliver Flores</p>
        '''
        dlg = QDialog(self)
        dlg.setWindowTitle("How to Use ASCIIHEX")
        dlg.setFixedSize(600, 400) # Increased size for more content
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
        self.setFixedSize(400, 250) # Increased size

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
        layout.addWidget(QLabel("Version 1.3 (Enhanced)")) # Updated version
        layout.addWidget(QLabel("by Dr. Eric Oliver Flores"))
        layout.addWidget(QLabel("September 2024")) # Added date
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tech_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Python 3.x"))
        layout.addWidget(QLabel("PyQt5"))
        layout.addWidget(QLabel("Qt Framework"))
        layout.addWidget(QLabel("CSV Module"))
        layout.addWidget(QLabel("Tested on Linux"))
        layout.addStretch()
        widget.setLayout(layout)
        return widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AsciiTable()
    window.show()
    sys.exit(app.exec_())
