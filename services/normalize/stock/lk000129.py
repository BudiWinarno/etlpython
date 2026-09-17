import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "Item Code PT JIM",
    "Item Name",
    "Item / Box",
    "Item Code Agen",
    "Stock in karton",
]


class LK000129StockNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================
    def find_header_row(self, df):

        expected_headers = {
            header.strip().lower()
            for header in EXPECTED_HEADERS
        }

        for idx, row in df.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            match = len(
                values.intersection(expected_headers)
            )

            if match >= 4:
                return idx

        raise Exception(
            "Header stock LK-000062 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================
    def normalize(self, filepath):

        # -----------------------------------------------------
        # PREVIEW TANPA HEADER
        # -----------------------------------------------------
        preview = pd.read_excel(
            filepath,
            header=None
        )

        # -----------------------------------------------------
        # CARI HEADER
        # -----------------------------------------------------
        header_row = self.find_header_row(preview)

        # -----------------------------------------------------
        # BACA DATA DENGAN HEADER
        # -----------------------------------------------------
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # -----------------------------------------------------
        # CLEAN HEADER
        # -----------------------------------------------------
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
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
        df = df.replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )

        df = df.dropna(how="all")

        # -----------------------------------------------------
        # ITEM CODE AGEN -> STRING
        # -----------------------------------------------------
        if "Item Code Agen" in df.columns:

            df["Item Code Agen"] = (
                df["Item Code Agen"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

        # -----------------------------------------------------
        # ITEM CODE PT JIM -> STRING
        # -----------------------------------------------------
        if "Item Code PT JIM" in df.columns:

            df["Item Code PT JIM"] = (
                df["Item Code PT JIM"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

        # -----------------------------------------------------
        # ITEM / BOX = KONVERSI
        # -----------------------------------------------------
        df["Item / Box"] = pd.to_numeric(
            df["Item / Box"],
            errors="coerce"
        )

        # -----------------------------------------------------
        # STOCK IN KARTON
        # -----------------------------------------------------
        df["Stock in karton"] = pd.to_numeric(
            df["Stock in karton"],
            errors="coerce"
        )

        # -----------------------------------------------------
        # QTY PCS
        # -----------------------------------------------------
        df["qty_pcs"] = (
            df["Item / Box"].fillna(0)
            * df["Stock in karton"].fillna(0)
        ).round().astype(int)

        # -----------------------------------------------------
        # REMOVE BARIS YANG BUKAN DATA
        # -----------------------------------------------------
        df = df[
            df["Item Code PT JIM"].notna()
            & df["Item Name"].notna()
        ]

        # -----------------------------------------------------
        # RESET INDEX
        # -----------------------------------------------------
        df = df.reset_index(drop=True)

        # -----------------------------------------------------
        # NOMOR URUT
        # -----------------------------------------------------
        if "No" in df.columns:
            df = df.drop(columns=["No"])

        df.insert(
            0,
            "No",
            range(1, len(df) + 1)
        )

        return df