from openpyxl.workbook.workbook import Workbook

from src.schema import BillPosition


class ExcelService:
    def create_invoice_file(self, data: list[BillPosition], output_path: str) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "Extracted Data"

        ws.append(
            [
                "Provider",
                "Title",
                "Date",
                "Quantity",
                "Total No VAT",
                "Total VAT",
                "Total with VAT",
            ]
        )

        for item in data:
            ws.append(
                [
                    item["provider"],
                    item["title"],
                    item["date"].strftime("%Y-%m-%d") if item["date"] else "",
                    item["quantity"],
                    item["total_price_no_vat"],
                    item["total_vat"],
                    item["total_price_vat"],
                ]
            )

        wb.save(output_path)
