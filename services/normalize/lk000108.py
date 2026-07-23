from services.normalize.base import BaseNormalizer


class LK000108InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Hapus baris Report Total dan End of Report
        df = df[
            ~df.astype(str)
            .apply(
                lambda row: row.str.upper().str.contains(
                    r"REPORT TOTAL|END OF REPORT",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]

        return df.reset_index(drop=True)