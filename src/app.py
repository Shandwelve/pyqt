import os
import time

from openpyxl import Workbook
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.services.processor import ProcessorService


class ProcessingThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, files: list[str]) -> None:
        super().__init__()
        self.files = files
        self.processor = ProcessorService(files, debug=os.environ.get("DEBUG", False))

    def run(self) -> None:
        # Simulate long processing (e.g. extract data from PDFs)
        result = self.processor.run()
        # Here you could modify or extract data from self.files
        self.finished.emit(self.files)


class LoadingDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Processing...")
        self.setModal(True)
        self.setFixedSize(300, 70)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout()
        label = QLabel("Processing files, please wait...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        progress = QProgressBar()
        progress.setRange(0, 0)  # infinite loading
        layout.addWidget(progress)

        self.setLayout(layout)


class PDFSelectorApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Selector")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("No files selected")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.select_button = QPushButton("Select PDF files")
        self.select_button.clicked.connect(self.select_pdfs)
        layout.addWidget(self.select_button)

        self.setLayout(layout)

    def select_pdfs(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF files", "", "PDF Files (*.pdf)"
        )
        if files:
            self.label.setText("Selected files:")
            self.file_list.clear()
            self.file_list.addItems(files)

            # Show loading dialog and run processing thread
            self.loading_dialog = LoadingDialog()
            self.thread = ProcessingThread(files)
            self.thread.finished.connect(self.processing_finished)
            self.thread.start()
            self.loading_dialog.exec()

    def processing_finished(self, processed_files: list[str]) -> None:
        self.loading_dialog.close()

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File As", "output.xlsx", "Excel Files (*.xlsx)"
        )

        if save_path:
            self.create_excel_file(processed_files, save_path)
            QMessageBox.information(
                self, "Success", f"Excel file saved to:\n{save_path}"
            )
        else:
            QMessageBox.warning(self, "Canceled", "File save canceled.")

    def create_excel_file(self, file_paths: list[str], output_path: str) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "PDF Files"

        ws.append(["Filename", "Full Path"])
        for path in file_paths:
            filename = path.split("/")[-1]
            ws.append([filename, path])

        wb.save(output_path)

