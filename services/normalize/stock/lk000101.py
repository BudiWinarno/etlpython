import pandas as pd

from services.normalize.base import BaseNormalizer


# =========================================================
# EXPECTED HEADERS
# =========================================================

EXPECTED_HEADERS = [
    "divisi_name",
    "item_id",
    "item_name",
    "stok_ctn",
    "stok_pcs",
    "end_value",
    "konversi",
]


class LK000101StockNormalizer(BaseNormalizer):

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

            if match >= 5:
                return idx

        raise Exception(
            "Header stock LK-000101 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(
        self,
        filepath
    ):

        # =====================================================
        # 1. BACA PREVIEW TANPA HEADER
        # =====================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. CARI HEADER
        # =====================================================

        header_row = self.find_header_row(
            preview
        )

        # =====================================================
        # 3. BACA ULANG DENGAN HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN HEADER
        # Header asli tetap
        # =====================================================

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

        # =====================================================
        # 5. VALIDASI KOLOM
        # =====================================================

        required_columns = [
            "divisi_name",
            "item_id",
            "item_name",
            "stok_ctn",
            "stok_pcs",
            "end_value",
            "konversi",
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom stock LK-000101 tidak ditemukan: "
                + ", ".join(missing_columns)
            )

        # =====================================================
        # 6. REMOVE UNNAMED COLUMNS
        # =====================================================

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =====================================================
        # 7. REMOVE EMPTY ROWS
        # =====================================================

        df = df.replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 8. ITEM ID -> STRING
        #    JAGA LEADING ZERO DARI RAW
        # =====================================================

        df["item_id"] = (
            df["item_id"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
        )

        # Jika item_id kehilangan leading zero
        # dan diawali 807, tambahkan 0
        df["item_id"] = df["item_id"].apply(
            lambda x: "0" + x
            if x.startswith("807")
            else x
        )

        # =====================================================
        # 9. ITEM NAME -> STRING
        # =====================================================

        df["item_name"] = (
            df["item_name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 10. DIVISI NAME -> STRING
        # =====================================================

        df["divisi_name"] = (
            df["divisi_name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 11. STOK CTN -> NUMERIC
        # =====================================================

        df["stok_ctn"] = pd.to_numeric(
            df["stok_ctn"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 12. STOK PCS -> NUMERIC
        # =====================================================

        df["stok_pcs"] = pd.to_numeric(
            df["stok_pcs"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 13. END VALUE -> NUMERIC
        # =====================================================

        df["end_value"] = pd.to_numeric(
            df["end_value"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 14. KONVERSI -> NUMERIC
        # =====================================================

        df["konversi"] = pd.to_numeric(
            df["konversi"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 15. TOTAL QTY PCS
        #
        # Jika stok_ctn > 0:
        #
        # stok_ctn * konversi + stok_pcs
        #
        # Jika stok_ctn = 0:
        #
        # stok_pcs
        # =====================================================

        df["total_qty_pcs"] = (
            df["stok_ctn"]
            * df["konversi"]
            + df["stok_pcs"]
        ).where(
            df["stok_ctn"] > 0,
            df["stok_pcs"]
        )

        # =====================================================
        # 16. BULATKAN TOTAL QTY PCS
        # =====================================================

        df["total_qty_pcs"] = (
            df["total_qty_pcs"]
            .fillna(0)
            .round()
            .astype(int)
        )

        # =====================================================
        # 17. REMOVE BARIS BUKAN DATA
        # =====================================================

        df = df[
            df["item_id"].notna()
            & df["item_id"].ne("")
        ]

        # =====================================================
        # 18. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 19. NOMOR URUT
        # =====================================================

        if "No" in df.columns:

            df = df.drop(
                columns=["No"]
            )

        df.insert(
            0,
            "No",
            range(
                1,
                len(df) + 1
            )
        )

        # =====================================================
        # 20. PINDAHKAN TOTAL QTY PCS
        #    TEPAT DI SEBELAH KONVERSI
        # =====================================================

        columns = df.columns.tolist()

        columns.remove("total_qty_pcs")

        konversi_index = columns.index(
            "konversi"
        )

        columns.insert(
            konversi_index + 1,
            "total_qty_pcs"
        )

        df = df[columns]

        # =====================================================
        # 21. DEBUG
        # =====================================================

        print("=" * 80)

        print("AGENT: LK-000101")

        print("\nCOLUMNS:")
        print(
            df.columns.tolist()
        )

        print("\nTOTAL DATA:")
        print(
            len(df)
        )

        print("\nDATA:")
        print(
            df.head(20)
        )

        print("=" * 80)

        # =====================================================
        # 22. RETURN
        # =====================================================

        return df