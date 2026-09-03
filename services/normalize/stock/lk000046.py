import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000046StockNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def _find_header_row(self, filepath, sheet_name=0):

        preview = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=None,
            nrows=30
        )

        expected_headers = [
            "no",
            "com_id",
            "groupcompanyname",
            "tgl",
            "ware_id",
            "principle_id",
            "principle_name",
            "divisi_id",
            "divisi_name",
            "item_id",
            "item_name",
            "stok_ctn",
            "stok_pcs",
            "end_value",
            "konversi",
            "konv pcs",
            "stok global",
        ]

        expected_headers = {
            header.strip().lower()
            for header in expected_headers
        }

        for idx, row in preview.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            match_count = len(
                values.intersection(expected_headers)
            )

            # Header memiliki minimal beberapa kolom yang cocok
            if match_count >= 5:
                return idx

        raise ValueError(
            "Header Stock LK-000046 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        sheet_name = 0

        # -----------------------------------------------------
        # FIND HEADER
        # -----------------------------------------------------

        header_row = self._find_header_row(
            filepath,
            sheet_name
        )

        # -----------------------------------------------------
        # READ DATA
        # -----------------------------------------------------

        df = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=header_row
        )

        # -----------------------------------------------------
        # CLEAN HEADER
        # -----------------------------------------------------

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # -----------------------------------------------------
        # ITEM ID -> STRING
        # -----------------------------------------------------

        if "item_id" in df.columns:

            df["item_id"] = (
                df["item_id"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
            )

        # -----------------------------------------------------
        # REMOVE EMPTY COLUMNS
        # -----------------------------------------------------

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # -----------------------------------------------------
        # REMOVE EMPTY ROWS
        # -----------------------------------------------------

        df = df.dropna(how="all")

        # -----------------------------------------------------
        # REMOVE TOTAL / NON DATA ROW
        # -----------------------------------------------------

        if "no" in df.columns:

            df = df[
                pd.to_numeric(
                    df["no"],
                    errors="coerce"
                ).notna()
            ]

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        if "tgl" in df.columns:

            df["tgl"] = pd.to_datetime(
                df["tgl"],
                errors="coerce"
            )
            
        # -----------------------------------------------------
        # TOTAL QTY PCS
        # -----------------------------------------------------

        if (
            "stok_ctn" in df.columns
            and "konversi" in df.columns
            and "stok_pcs" in df.columns
        ):

            stok_ctn = pd.to_numeric(
                df["stok_ctn"],
                errors="coerce"
            ).fillna(0)

            konversi = pd.to_numeric(
                df["konversi"],
                errors="coerce"
            ).fillna(0)

            stok_pcs = pd.to_numeric(
                df["stok_pcs"],
                errors="coerce"
            ).fillna(0)

            df["total_qty_pcs"] = (
                stok_ctn * konversi
            ) + stok_pcs


        # -----------------------------------------------------
        # RESET INDEX
        # -----------------------------------------------------

        df = df.reset_index(drop=True)

        return df
