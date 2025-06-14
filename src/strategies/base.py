import datetime
from typing import Optional

import regex as re

from src.schema import BillPosition
from dateutil import parser


class BaseStrategy:
    day_first = True
    timeout = 10
    decimal_separator = "."

    def __init__(self, text: str) -> None:
        self.text = text

    def date_pattern(self) -> re.Pattern[str]: ...
    def provider_pattern(self) -> re.Pattern[str]: ...
    def record_pattern(self) -> re.Pattern[str]: ...

    def execute(self) -> list[BillPosition]:
        records = self.parse_records()
        date = self.parse_date()
        provider = self.parse_provider()
        return [
           BillPosition(
               date=date,
               provider=provider,
               title=record["title"],
               quantity=self.build_quantity(record),
               total_price_no_vat=self.parse_number(record.get("total_price_no_vat", "0")),
               total_price_vat=self.parse_number(record.get("total_price_no_vat", "0")),
               total_vat=self.parse_number(record.get("total_vat", "0")),
           )
           for record in records
       ]

    def build_quantity(self, record: dict[str, str]) -> float:
        return self.parse_number(record.get("quantity", "0"))

    def parse_records(self) -> list[dict[str, str]]:
        pattern = self.record_pattern()
        if pattern is Ellipsis or not pattern:
            raise ValueError("Missing record pattern")
        matches = re.finditer(pattern, self.text, timeout=self.timeout)
        result = []
        for match in matches:
            match.detach_string()
            result.append(match.groupdict())
        return result


    def parse_date(self) -> datetime.date:
        pattern = self.date_pattern()
        if pattern is Ellipsis or not pattern:
            raise ValueError("Missing date pattern")
        date_match = re.search(pattern, self.text)
        if not date_match or not date_match.group("date"):
            raise ValueError("Can't parse date")
        try:
            return self.build_date(date_match.group("date"))
        except:
            raise ValueError("Can't parse date")

    def build_date(self, date: str) -> datetime.date:
        return parser.parse(date, dayfirst=self.day_first)

    def parse_provider(self) -> str:
        pattern = self.provider_pattern()
        if pattern is Ellipsis or not pattern:
            raise ValueError("Missing provider pattern")
        provider_match = re.search(pattern, self.text)
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
