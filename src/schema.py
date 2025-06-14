import datetime
from enum import Enum
from typing import TypedDict


class FileType(str, Enum):
    PDF = "PDF"
    OCR_PDF = "OCR_PDF"


class BillPosition(TypedDict):
    provider: str
    title: str
    date: datetime.date
    quantity: float
    total_price_no_vat: float
    total_price_vat: float
    total_vat: float
