import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000139InvoiceNormalizer(BaseNormalizer):

    @staticmethod
    def convert_date(value):
        if pd.isna(value):
            return None

        try:
            # Excel serial date
            if isinstance(value, (int, float)):
                return pd.to_datetime(
                    value,
                    unit="D",
                    origin="1899-12-30"
                ).date()

            # Sudah berupa string atau datetime
            return pd.to_datetime(value).date()

        except Exception:
            return None

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        if "TANGGAL" in df.columns:
            df["TANGGAL"] = df["TANGGAL"].apply(self.convert_date)

        return df