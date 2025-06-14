from typing import Optional

import pymupdf
from doctr.io import DocumentFile
from doctr.models import ocr_predictor


class PDFService:
    def parse_pdf_ocr(self, full_path: str, password: Optional[str] = None) -> str:
        predictor = ocr_predictor(
            det_arch="db_resnet50",
            reco_arch="crnn_vgg16_bn",
            pretrained=True,
            detect_orientation=True,
            straighten_pages=True,
        )
        doc = DocumentFile.from_pdf(full_path, password=password)

        full_text = ""
        for page in predictor(doc).export()["pages"]:
            for block in page["blocks"]:
                for line in block["lines"]:
                    line_text = " ".join([word["value"] for word in line["words"]])
                    full_text += line_text + "\n"
        return full_text

    def parse_pdf(
        self, full_path: str, password: Optional[str] = None, sort: bool = False
    ) -> str:
        try:
            doc = pymupdf.open(full_path)
            if password:
                doc.authenticate(password)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text", sort=sort)
            doc.close()
            return text
        except Exception as e:
            return f"Error with PyMuPDF: {e}"
