import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "Item Name",
    "Item / Box",
    "Item Code Agen",
    "Stock in karton",
]


class LK000144StockNormalizer(BaseNormalizer):

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

            if match >= 3:
                return idx

        raise Exception(
            "Header stock LK-000144 tidak ditemukan"
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

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
        )

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
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
        )

        # -----------------------------------------------------
        # VALIDASI HEADER
        # -----------------------------------------------------

        missing_columns = [
            column
            for column in EXPECTED_HEADERS
            if column not in df.columns
        ]

        if missing_columns:
            raise Exception(
                f"Header stock LK-000144 tidak lengkap: "
                f"{missing_columns}"
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
        # ITEM NAME -> STRING
        # -----------------------------------------------------

        if "Item Name" in df.columns:

            df["Item Name"] = (
                df["Item Name"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # -----------------------------------------------------
        # ITEM / BOX = KONVERSI
        # -----------------------------------------------------

        df["Item / Box"] = pd.to_numeric(
            df["Item / Box"],
            errors="coerce"
        ).fillna(0)

        # -----------------------------------------------------
        # STOCK IN KARTON
        # -----------------------------------------------------

        df["Stock in karton"] = pd.to_numeric(
            df["Stock in karton"],
            errors="coerce"
        ).fillna(0)

        # -----------------------------------------------------
        # QTY PCS
        # -----------------------------------------------------

        df["qty_pcs"] = (
            df["Item / Box"]
            * df["Stock in karton"]
        ).round().astype(int)

        # -----------------------------------------------------
        # REMOVE BARIS YANG BUKAN DATA
        # -----------------------------------------------------

        df = df[
            (df["Item Code Agen"] != "") &
            (df["Item Name"] != "")
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

        # -----------------------------------------------------
        # URUTAN KOLOM
        # -----------------------------------------------------

        df = df[
            [
                "No",
                "Item Name",
                "Item / Box",
                "Item Code Agen",
                "Stock in karton",
                "qty_pcs",
            ]
        ]

        # -----------------------------------------------------
        # DEBUG
        # -----------------------------------------------------

        print("\n==============================")
        print("HASIL NORMALISASI LK-000144")
        print("==============================")

        print(
            df.head(10).to_string()
        )

        print(
            "\nJumlah data:",
            len(df)
        )

        print(
            "\nKolom:",
            df.columns.tolist()
        )

        print("\n==============================")
        print("NORMALIZE SELESAI")
        print("==============================")

        return df