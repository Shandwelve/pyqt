import os
from typing import Optional

from src.config import OUTPUT_PATH, STRATEGIES
from src.schema import BillPosition, FileType
from src.services.pdf import PDFService


class ProcessorService:
    def __init__(self, files: list[str], debug: bool = False) -> None:
        self.files = files
        self.pdf_service = PDFService()
        self.debug = debug
        self.output_path = OUTPUT_PATH
        self.strategies = STRATEGIES

    def run(self) -> Optional[list[BillPosition]]:
        result = []
        for file_path in self.files:
            data = self.process_file(file_path)
            if data:
                result += data
        return result or None

    def process_file(self, file_path: str) -> Optional[list[BillPosition]]:
        for file_type in FileType:
            text = self.get_pdf_content(file_path, file_type)
            for strategy in self.strategies:
                instance = strategy(text)
                try:
                    data = instance.execute()
                    if data:
                        return data
                except:
                    continue
        return None

    def get_pdf_content(self, path: str, file_type: FileType) -> str:
        content = ""
        if file_type == FileType.PDF:
            content = self.pdf_service.parse_pdf(path)
        elif file_type == FileType.OCR_PDF:
            content = self.pdf_service.parse_pdf_ocr(path)
        if self.debug:
            self.log_file(content, path, file_type)
        return content

    def log_file(self, content: str, path: str, file_type: FileType) -> None:
        os.makedirs(self.output_path, exist_ok=True)
        file_name = os.path.splitext(os.path.basename(path))[0]
        output_file = f"{file_name}_{file_type.value.lower()}.txt"
        with open(
            os.path.join(self.output_path, output_file), "w", encoding="utf-8"
        ) as file:
            file.write(content)
