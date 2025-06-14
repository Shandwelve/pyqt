import os
from typing import Optional

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

from src.schema import BillPosition
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

            self.loading_dialog = LoadingDialog()
            self.thread = ProcessingThread(files)
            self.thread.finished.connect(self.processing_finished)
            self.thread.start()
            self.loading_dialog.exec()

    def processing_finished(self, result: Optional[list[BillPosition]]) -> None:
        self.loading_dialog.close()

        if result is None:
            QMessageBox.critical(
                self, "Error", "Data could not be processed from the selected files."
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File As", "output.xlsx", "Excel Files (*.xlsx)"
        )

        if save_path:
            self.create_excel_file(result, save_path)
            QMessageBox.information(
                self, "Success", f"Excel file saved to:\n{save_path}"
            )
        else:
            QMessageBox.warning(self, "Canceled", "File save canceled.")

    def create_excel_file(self, data: list[BillPosition], output_path: str) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "Extracted Data"

        ws.append(
            [
                "Provider",
                "Title",
                "Date",
                "Quantity",
                "Total No VAT",
                "Total VAT",
                "Total with VAT",
            ]
        )

        for item in data:
            ws.append(
                [
                    item["provider"],
                    item["title"],
                    item["date"].strftime("%Y-%m-%d") if item["date"] else "",
                    item["quantity"],
                    item["total_price_no_vat"],
                    item["total_vat"],
                    item["total_price_vat"],
                ]
            )

        wb.save(output_path)
