from services.normalize.base import BaseNormalizer
import pandas as pd
from pandas.api.types import is_numeric_dtype


class LK000121InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        if "Tgl Faktur" in df.columns:

            if is_numeric_dtype(df["Tgl Faktur"]):
                # Jika masih berupa serial Excel (46176, 46177, dst)
                df["Tgl Faktur"] = pd.to_datetime(
                    df["Tgl Faktur"],
                    unit="D",
                    origin="1899-12-30"
                )
            else:
                # Jika sudah berupa datetime atau string tanggal
                df["Tgl Faktur"] = pd.to_datetime(
                    df["Tgl Faktur"],
                    errors="coerce"
                )

            # Hanya simpan tanggal
            df["Tgl Faktur"] = df["Tgl Faktur"].dt.date

        return df