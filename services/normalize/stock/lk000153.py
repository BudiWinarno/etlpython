from services.normalize.base import BaseNormalizer


class LK000153StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Hapus baris SUBTOTAL dan TOTAL
        df = df[
            ~df.astype(str)
            .apply(
                lambda row: row.str.upper().str.contains(
                    r"SUBTOTAL|TOTAL",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]

        return df.reset_index(drop=True)