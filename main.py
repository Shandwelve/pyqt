import sys

from PyQt6.QtWidgets import QApplication

from src.app import PDFSelectorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFSelectorApp()
    window.show()
    sys.exit(app.exec())
