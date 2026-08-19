import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000037StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        # =========================================================
        # READ EXCEL
        # HEADER SUDAH DI BARIS PERTAMA
        # =========================================================

        df = pd.read_excel(
            filepath,
            header=0
        )

        # =========================================================
        # CLEAN HEADER
        # =========================================================

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # =========================================================
        # CD PRODUCT -> STRING
        # =========================================================

        if "Cd Product" in df.columns:

            df["Cd Product"] = (
                df["Cd Product"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
            )

        # =========================================================
        # REMOVE EMPTY ROW
        # =========================================================

        df = df.dropna(how="all")

        # =========================================================
        # RESET INDEX
        # =========================================================

        df = df.reset_index(drop=True)

        return df