# 🧮 ASCIIHEX — ASCII / HEX Conversion Table Viewer  
**Version:** 1.3  
**Author:** Dr. Eric Oliver Flores  
**License:** MIT  
**Platform:** Linux / Windows / macOS  
**Framework:** Python 3 + PyQt5  
**Status:** Stable Release  

---

## 📘 Overview
**ASCIIHEX** is a graphical ASCII and hexadecimal reference viewer designed for engineers, developers, and metrologists who frequently analyze character encodings, escape sequences, and control characters.  

The application displays a fully interactive ASCII/Latin-1 table (0–127 or 0–255) with real-time conversion between **character**, **decimal**, and **hexadecimal** formats.  
It supports **searching**, **copying**, **dark mode**, **CSV export**, and a professional-grade **help and about system**.  

This release (v1.3) introduces an extended character range, enhanced dark-mode palette, smarter search, and better integration for precision-engineering and software development workflows.

---

## ⚙️ Features

### 🔍 **Core Functionalities**
- Displays ASCII (0–127) and extended Latin-1 (0–255) characters.  
- Shows **Character**, **Decimal**, and **Hexadecimal (0xNN)** values.  
- Tooltip displays both decimal and hexadecimal simultaneously.  
- Includes **control-character names** (e.g., `NUL`, `CR`, `LF`, `ESC`, `DEL`).  
- Supports **Go-To function** by decimal, hex, or single character.  

### 🖱️ **User Interface Enhancements**
- **Live search**: Type any character, dec, or hex to highlight matches instantly.  
- **Context menu**: Right-click any cell to copy:
  - Char  
  - Decimal  
  - Hexadecimal  
  - Binary (`0bXXXXXXXX`)  
  - C escape (`\xNN`)  
  - Python escape (`\xnn`)  
  - Full formatted string  
- **Toolbar controls**:
  - Copy, Export, Dark mode toggle  
  - Font zoom (A- / A+)  
  - Range toggle (ASCII ↔ Extended 255)  
- **Status bar feedback** for all copy and export operations.  
- **Search bar shortcuts**:
  - Press `Enter` to focus first hit  
  - Press `Esc` to clear search instantly  

### 🌙 **Dark Mode & Appearance**
- Palette-based dark mode (theme-safe for all platforms).  
- Adjustable font sizes: Small / Medium / Large.  
- Auto-resized cells with centered text alignment.  

### 📤 **Export & Integration**
- Export full ASCII/Latin-1 table as UTF-8 encoded **CSV file**.  
- Safe filename handling (automatically appends `.csv` extension).  
- Compatible with spreadsheet tools (Excel, LibreOffice Calc).  
- Tested under **Pop!_OS 22.04 LTS / Qt 5.15 / Python 3.10+**.

---

## 🧠 System Requirements

| Component | Minimum | Recommended |
|------------|----------|--------------|
| **Python** | 3.7+ | 3.10+ |
| **Qt Framework** | PyQt5 | PyQt5 + QtWebEngine |
| **Memory** | 128 MB | 512 MB |
| **Display** | 1024×600 | 1366×768 or higher |

---

## 🧩 Installation

### 🟢 Linux (Pop!_OS / Ubuntu)
```bash
sudo apt update
sudo apt install python3 python3-pyqt5 python3-pyqt5.qtsvg python3-pyqt5.qtwebengine
```

### 🟣 Windows / macOS
```bash
pip install PyQt5 PyQtWebEngine PyQt5-sip
```

### 📦 Clone from GitHub
```bash
git clone https://github.com/drericflores/asciihex.git
cd asciihex
python3 asciihexv1_3.py
```

---

## 🚀 Usage Guide

### Run the Application
```bash
python3 asciihexv1_3.py
```

### Start in Dark Mode
```bash
python3 asciihexv1_3.py --dark
```

### Interface Overview
| Area | Description |
|------|--------------|
| **Search Bar** | Enter text, number, or hex to locate entries dynamically |
| **Table View** | 16×8 grid showing ASCII/Latin-1 characters |
| **Output Label** | Displays selected Char, Dec, and Hex values |
| **Toolbar** | Quick access to Copy, Export, Font, Range, and Dark Mode |
| **Menu Bar** | File, Edit, View, Help menus with advanced actions |
| **Status Bar** | Displays contextual hints and operation results |

---

## 📚 Menus & Shortcuts

### **File Menu**
| Action | Description |
|--------|--------------|
| Export CSV | Save full table to `.csv` file |
| Quit | Exit application |

### **Edit Menu**
| Action | Description |
|--------|--------------|
| Copy Selection | Copies current cell info |
| Go to… | Jump directly to a specific code |
| Clear Search | Clears search box |

### **View Menu**
| Action | Description |
|--------|--------------|
| Toggle Dark Mode | Switch between light/dark themes |
| Font Small/Medium/Large | Adjust display size |
| Show Extended (0–255) | Toggle Latin-1 view |

### **Help Menu**
| Action | Description |
|--------|--------------|
| About | Displays credits and version info |
| How to Use | Opens detailed HTML user guide |

---

## 🧰 Developer Notes

### Project Structure
```
asciihex/
├── asciihexv1_3.py        # Main application
├── asciihexv1_2.py        # Previous version
├── documentation/          # Help and design notes
├── LICENSE
└── README.md
```

### Utility Functions
| Function | Description |
|-----------|--------------|
| `hex_str(n)` | Returns hex in `0xNN` uppercase format |
| `bin_str(n)` | Returns binary string (8 bits) |
| `c_escape(n)` | Returns C-style escape `\xNN` |
| `py_escape(n)` | Returns Python-style escape `\xnn` |

---

## 🧾 Version History

### **v1.3 — 2025-10-14**
- Fixed hex output format (`0xNN` uppercase).  
- Added control-character labels and tooltips.  
- Added extended range toggle (0–255).  
- Added “Go to…” dialog.  
- Improved CSV export robustness.  
- Enhanced search and highlight behavior.  
- Added binary, C-escape, and Python-escape copy options.  
- Added toolbar and status bar feedback.  
- Replaced stylesheet dark mode with palette system.  
- Updated Help/About dialogs.  
- Code modularization for maintainability.

### **v1.2 — 2025-08**
- Added dark mode toggle.  
- Basic search and CSV export.  
- Minimal toolbar and About dialog.

### **v1.1 — Initial Release**
- Basic ASCII 0–127 viewer with copy function.  

---

## 🧑‍💻 Author
**Dr. Eric Oliver Flores, D.M.**  
Precision Measurement Engineer • AI Systems Developer • Software Engineer  
📍 Pop!_OS 22.04 LTS | Python 3.10 | GTK / Qt / C++ / AI Integration  

---

## 📄 License
Licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.  

---

## 🌐 Repository
**GitHub:** [https://github.com/drericflores/asciihex](https://github.com/drericflores/asciihex)

---

> _“Precision meets clarity — ASCIIHEX bridges engineering and computation in one glance.”_  
> — *Dr. Eric O. Flores, 2025*
