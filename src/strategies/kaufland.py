import regex as re

from src.strategies.base import BaseStrategy


class KauflandStrategy(BaseStrategy):
    decimal_separator = ","

    def date_pattern(self) -> re.Pattern[str]:
        return r"(data .+: (?P<date>\d\d\.\d\d.20\d\d))"

    def record_pattern(self) -> re.Pattern[str]:
        number_pattern = r"(\s\d+(.?( |\.)\d+)*(\,\d+))-?"
        return rf"(\d+\. )?(?P<title>(.)+?)(?P<measure_unit>\s.{{,5}}?)(?P<quantity>\s\d+(,\d+)?).?(?P<unit_price>{number_pattern}).?(?P<total_price_no_vat>{number_pattern}).?(?P<vat_rate>{number_pattern}%).?(?P<total_vat>{number_pattern}).?(?P<discount>{number_pattern})?.?(?P<total_price_vat>{number_pattern})"  # noqa: E501

    def parse_provider(self, page: str) -> str:
        return "KAUFLAND SRL"

    def page_pattern(self) -> re.Pattern[str]:
        return r"factura\s?fiscala"
