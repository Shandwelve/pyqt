import os
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
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

from src.schema import BillPosition
from src.services.excel import ExcelService
from src.services.processor import ProcessorService


class ProcessingThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, files: list[str]) -> None:
        super().__init__()
        self.files = files
        self.processor = ProcessorService(files, debug=os.environ.get("DEBUG", False))

    def run(self) -> None:
        self.finished.emit(self.processor.run())


class LoadingDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Processing...")
        self.setModal(True)
        self.setFixedSize(300, 70)

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)

        layout = QVBoxLayout()
        label = QLabel("Processing files, please wait...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        progress = QProgressBar()
        progress.setRange(0, 0)
        layout.addWidget(progress)

        self.setLayout(layout)

    def closeEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)


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

        self.excel_service = ExcelService()

    def select_pdfs(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF files", "", "PDF Files (*.pdf)"
        )
        if files:
            self.label.setText("Selected files:")
            self.file_list.clear()
            self.file_list.addItems(files)

            self.loading_dialog = LoadingDialog()
            self.thread = ProcessingThread(files)
            self.thread.finished.connect(self.processing_finished)

            self.timeout_timer = QTimer(self)
            self.timeout_timer.setSingleShot(True)
            self.timeout_timer.setInterval(600_000)  # 10 minutes
            self.timeout_timer.timeout.connect(self.processing_timeout)

            self.thread.start()
            self.timeout_timer.start()

            self.loading_dialog.exec()

    def processing_finished(self, result: Optional[list[BillPosition]]) -> None:
        self.timeout_timer.stop()
        self.loading_dialog.accept()

        if result is None:
            QMessageBox.critical(
                self, "Error", "Data could not be processed from the selected files."
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File As", "output.xlsx", "Excel Files (*.xlsx)"
        )

        if save_path:
            self.excel_service.create_invoice_file(result, save_path)
            QMessageBox.information(
                self, "Success", f"Excel file saved to:\n{save_path}"
            )
        else:
            QMessageBox.warning(self, "Canceled", "File save canceled.")

    def processing_timeout(self) -> None:
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

        self.loading_dialog.accept()
        QMessageBox.warning(
            self,
            "Timeout",
            "Processing took too long and was canceled.",
        )
