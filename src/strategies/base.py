import datetime
from typing import Optional

import regex as re
from dateutil import parser

from src.schema import BillPosition


class BaseStrategy:
    day_first = True
    timeout = 10
    decimal_separator = "."

    def __init__(self, text: str) -> None:
        self.text = text

    def date_pattern(self) -> re.Pattern[str]: ...
    def provider_pattern(self) -> re.Pattern[str]: ...
    def record_pattern(self) -> re.Pattern[str]: ...
    def page_pattern(self) -> re.Pattern[str]: ...

    def execute(self) -> list[BillPosition]:
        result = []
        for page in self.split_by_page():
            try:
                date = self.parse_date(page)
                provider = self.parse_provider(page)
                records = self.parse_records(page)
                result += [
                    BillPosition(
                        date=date,
                        provider=provider,
                        title=record["title"],
                        quantity=self.build_quantity(record),
                        total_price_no_vat=self.parse_number(
                            record.get("total_price_no_vat", "0")
                        ),
                        total_price_vat=self.parse_number(
                            record.get("total_price_no_vat", "0")
                        ),
                        total_vat=self.parse_number(record.get("total_vat", "0")),
                    )
                    for record in records
                ]
            except Exception:
                continue
        return result

    def build_quantity(self, record: dict[str, str]) -> float:
        return self.parse_number(record.get("quantity", "0"))

    def parse_records(self, page: str) -> list[dict[str, str]]:
        pattern = self.record_pattern()
        if pattern is Ellipsis or not pattern:
            raise ValueError("Missing record pattern")
        matches = re.finditer(pattern, page, timeout=self.timeout, flags=re.IGNORECASE)
        result = []
        for match in matches:
            match.detach_string()
            result.append(match.groupdict())
        return result

    def parse_date(self, page: str) -> datetime.date:
        pattern = self.date_pattern()
        if pattern is Ellipsis or not pattern:
            raise ValueError("Missing date pattern")
        date_match = re.search(pattern, page, flags=re.IGNORECASE)
        if not date_match or not date_match.group("date"):
            raise ValueError("Can't parse date")
        try:
            return self.build_date(date_match.group("date"))
        except:
            return datetime.date.min

    def build_date(self, date: str) -> datetime.date:
        return parser.parse(date, dayfirst=self.day_first)

    def parse_provider(self, page: str) -> str:
        pattern = self.provider_pattern()
        if pattern is Ellipsis or not pattern:
            raise ValueError("Missing provider pattern")
        provider_match = re.search(pattern, page, flags=re.IGNORECASE)
        if not provider_match or not provider_match.group("provider"):
            raise ValueError("Can't parse provider")
        return provider_match.group("provider")

    def parse_number(self, number: Optional[str]) -> float:
        if number is None:
            return 0
        processed_number = re.sub(rf"[^\d{self.decimal_separator}]", "", number)
        if self.decimal_separator == ",":
            processed_number = processed_number.replace(",", ".")
        float_number = float(processed_number)
        return -float_number if "-" in number else float_number

    def split_by_page(self) -> list[str]:
        page_pattern = self.page_pattern()
        pages = [self.text]
        if page_pattern is not Ellipsis and page_pattern:
            pages = re.split(page_pattern, self.text, flags=re.IGNORECASE)
        return pages
