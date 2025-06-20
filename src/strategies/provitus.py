import datetime

import regex as re
from dateutil import parser

from src.helpers import replace_romanian_months
from src.strategies.base import BaseStrategy


class ProvitusStrategy(BaseStrategy):
    decimal_separator = ","

    def date_pattern(self) -> re.Pattern[str]:
        date_format = r"(\d{1,2} .+ 20\d\d)"
        return rf"(\n(?P<date>{date_format})\s?/\s?{date_format})"

    def record_pattern(self) -> re.Pattern[str]:
        number_pattern = r"(\s-?\d+(.?( |\.)\d+)*(\,\d+)?)"
        return rf"(?P<title>.+?)(?P<volume>\s\(?\d+.{{,7}}?)?(?P<measure_unit>\s.{{,5}})(?P<quantity>\s\d+).?(?P<unit_price>{number_pattern})?(?P<total_price_no_vat>{number_pattern})?(?P<vat_rate>\s\d+%)(?P<total_vat>{number_pattern})?(?P<total_price_vat>{number_pattern})?"  # noqa: E501

    def build_date(self, date: str) -> datetime.date:
        date = replace_romanian_months(date)
        return parser.parse(date, dayfirst=self.day_first)

    def parse_provider(self, page: str) -> str:
        return "Provitus Grup"

    def page_pattern(self) -> re.Pattern[str]:
        return r"factura\s?fiscala seria"

    def build_quantity(self, record: dict[str, str]) -> float:
        product_weight = {
            r"migdal.{,3}? in ciocolata": 5
        }
        title = record.get("title", "")
        quantity = self.parse_number(record.get("quantity", "0"))
        volume = self.parse_number(record.get("volume", "1") or "1")

        multiplier = 1
        for pattern, weight in product_weight.items():
            if re.search(pattern, title, re.IGNORECASE):
                multiplier = weight
                break
        return quantity * volume * multiplier
