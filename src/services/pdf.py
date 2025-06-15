import os
from typing import Optional

import pymupdf
import torch
from doctr.models import ocr_predictor

from src.config import ROOT_PATH
from doctr.models.detection import db_resnet50
from doctr.models.recognition import crnn_vgg16_bn
from doctr.io import DocumentFile


class PDFService:
    root_path = ROOT_PATH

    def parse_pdf_ocr(self, full_path: str, password: Optional[str] = None) -> str:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        detection_model_path = os.path.join(ROOT_PATH, "models", "db_resnet50.pt")
        recognition_model_path = os.path.join(ROOT_PATH, "models", "crnn_vgg16_bn.pt")

        det_model = db_resnet50(pretrained=False, pretrained_backbone=False)
        det_params = torch.load(detection_model_path, map_location=device)
        det_model.load_state_dict(det_params)
        reco_model = crnn_vgg16_bn(pretrained=False, pretrained_backbone=False)
        reco_params = torch.load(recognition_model_path, map_location=device)
        reco_model.load_state_dict(reco_params)

        predictor = ocr_predictor(det_model, reco_model)
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
