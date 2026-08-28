import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000014InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        if "Tgl Faktur" in df.columns:
            df["Tgl Faktur"] = pd.to_datetime(
                df["Tgl Faktur"],
                dayfirst=True,
                errors="coerce"
            ).dt.date

        return df