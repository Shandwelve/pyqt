import regex as re

from src.strategies.base import BaseStrategy


class StandardStrategy(BaseStrategy):
    decimal_separator = ","

    def date_pattern(self) -> re.Pattern[str]:
        return r"data livrării\s+(?P<date>\d\d\.\d\d\.20\d\d)"

    def record_pattern(self) -> re.Pattern[str]:
        number_pattern = r"(\s\d+(.?( |\.)\d+)*(\,\d+))-?"
        number_pattern2 = r"(\s\d+(.?( )\d+)*(\.\d+))-?"
        return rf"(\d+\. )(?P<title>(.|\n){{,250}}?)(?P<measure_unit>\s.{{,5}}?)(?P<quantity>\s\d+(.\d+)?)(?P<unit_price>{number_pattern2})(?P<total_price_no_vat>{number_pattern})(?P<vat_rate>\s\d+)(?P<total_vat>{number_pattern})(?P<total_price_vat>{number_pattern})"

    def provider_pattern(self) -> re.Pattern[str]:
        return r"(Поставщик\s(?P<provider>.+?),)"
