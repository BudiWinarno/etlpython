import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000031StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = pd.read_excel(filepath)

        df["total_qty_pcs"] = (
            pd.to_numeric(df["QTY"], errors="coerce").fillna(0)
            + pd.to_numeric(df["GoodSKW"], errors="coerce").fillna(0)
            + pd.to_numeric(df["GoodKTP"], errors="coerce").fillna(0)
            + pd.to_numeric(df["GoodSTG"], errors="coerce").fillna(0)
        )

        return df