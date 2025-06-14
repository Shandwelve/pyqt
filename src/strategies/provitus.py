import datetime

import regex as re
from dateutil import parser

from src.helpers import replace_romanian_months
from src.strategies.base import BaseStrategy


class ProvitusStrategy(BaseStrategy):
    decimal_separator = ","

    def date_pattern(self) -> re.Pattern[str]:
        date_format = r"(\d\d .+ 20\d\d)"
        return rf"(\n(?P<date>{date_format})\s?/\s?{date_format})"

    def provider_pattern(self) -> re.Pattern[str]:
        return r"(?P<provider>SC(.+?),)"

    def record_pattern(self) -> re.Pattern[str]:
        number_pattern = r"(\s-?\d+(.?( |\.)\d+)*(\,\d+)?)"
        return rf"(?P<title>.+?)(?P<measure_unit>\s.{{,5}})(?P<quantity>\s\d+).?(?P<unit_price>{number_pattern})?(?P<total_price_no_vat>{number_pattern})?(?P<vat_rate>\s\d+%)(?P<total_vat>{number_pattern})?(?P<total_price_vat>{number_pattern})?"

    def build_date(self, date: str) -> datetime.date:
        date = replace_romanian_months(date)
        return parser.parse(date, dayfirst=self.day_first)
