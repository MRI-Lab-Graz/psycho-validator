"""
Modern style specification file for PyQt5 BIDS GUI components
"""

STYLE = """
/* Main window and general styling */
QMainWindow {
    background-color: #f5f5f5;
}

/* Labels styling */
QLabel {
    color: #333333;
    font-size: 11px;
    min-height: 20px;
    max-height: 20px;
}

/* Line edits and text edits */
QLineEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 6px;
    color: #333333;
    font-size: 11px;
}

QLineEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #4a7ba7;
    background-color: #fafafa;
}

/* Combo boxes */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 4px 8px;
    color: #333333;
    font-size: 11px;
    min-height: 26px;
}

QComboBox:focus {
    border: 2px solid #4a7ba7;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    width: 12px;
    height: 8px;
}

/* Push buttons - main style */
QPushButton {
    background-color: #4a7ba7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: bold;
    min-width: 70px;
    max-width: 80px;
}

QPushButton:hover {
    background-color: #5a8bb7;
}

QPushButton:pressed {
    background-color: #3a6b97;
}

/* Add/Remove buttons (smaller) */
QPushButton#addButton, QPushButton#removeButton {
    min-width: 32px;
    max-width: 32px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#addButton {
    background-color: #5cb85c;
}

QPushButton#addButton:hover {
    background-color: #6cc86c;
}

QPushButton#removeButton {
    background-color: #d9534f;
}

QPushButton#removeButton:hover {
    background-color: #e9635f;
}

/* Save button (primary action) */
QPushButton#saveButton {
    background-color: #0275d8;
    min-width: 100px;
    max-width: 100px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#saveButton:hover {
    background-color: #0366e0;
}

QPushButton#saveButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

/* Scroll area */
QScrollArea {
    border: none;
    background-color: #ffffff;
}

/* Scroll bar styling */
QScrollBar:vertical {
    border: none;
    background-color: #f5f5f5;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

/* Spacing improvements */
QWidget {
    background-color: #f5f5f5;
}
"""
