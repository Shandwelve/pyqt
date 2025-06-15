import os
from typing import Optional

import pymupdf
import torch
from doctr.io import DocumentFile
from doctr.models.detection import db_resnet50
from doctr.models.recognition import crnn_vgg16_bn
from doctr.models.predictor import OCRPredictor
from doctr.models.detection.predictor import DetectionPredictor
from doctr.models.recognition.predictor import RecognitionPredictor
from doctr.models.preprocessor import PreProcessor

from src.config import ROOT_PATH


class PDFService:
    root_path = ROOT_PATH


    def parse_pdf_ocr(self, full_path: str, password: Optional[str] = None) -> str:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        db_resnet_path = os.path.join(ROOT_PATH, "models", "db_resnet50.pt")
        crnn_vgg_path = os.path.join(ROOT_PATH, "models", "crnn_vgg16_bn.pt")

        det_preproc = PreProcessor(output_size=(640, 640), batch_size=1)
        reco_preproc = PreProcessor(output_size=(32, 100), batch_size=1)

        det_model = db_resnet50(pretrained=False)
        det_model.load_state_dict(torch.load(db_resnet_path, map_location=device))
        det_predictor = DetectionPredictor(det_preproc, det_model)

        reco_model = crnn_vgg16_bn(pretrained=False)
        reco_model.load_state_dict(torch.load(crnn_vgg_path, map_location=device))
        reco_predictor = RecognitionPredictor(reco_preproc, reco_model)

        predictor = OCRPredictor(
            det_predictor=det_predictor,
            reco_predictor=reco_predictor,
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
