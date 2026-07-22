from services.normalize.base import BaseNormalizer


class LK000121StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Hilangkan newline dan rapikan nama kolom
        df.columns = (
            df.columns.astype(str)
            .str.replace(r"[\r\n]+", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # Hapus baris Total
        df = df[
            ~df.iloc[:, 0]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.startswith("TOTAL")
        ]

        return df.reset_index(drop=True)