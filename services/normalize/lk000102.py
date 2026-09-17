import pandas as pd

from services.normalize.base import BaseNormalizer


# =========================================================
# EXPECTED HEADERS
# =========================================================

EXPECTED_HEADERS = [
    "Kode 1",
    "Kode 2",
    "No Faktur",
    "Tanggal",
    "Kode Customer",
    "Nama Customer",
    "Alamat",
    "Sales",
    "Kode Barang",
    "Nama Barang",
    "Satuan",
    "Q",
    "Pcs",
    "Total Qty",
    "Retail/Grosir/E",
    "Type Outlet",
    "P/sat",
    "Total Jual",
    "Total Diskon",
    "Diskon Program (%)",
    "Diskon Program (Nominal)",
    "Diskon Promosi (%)",
    "Diskon Promosi (Nominal)",
    "Subtotal",
    "Diskon Distributor (%)",
    "Diskon Distributor (Nominal)",
    "TOTAL",
    "DPP",
    "PPN Keluaran",
]


class LK000102InvoiceNormalizer(BaseNormalizer):

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

            # Header utama punya hampir semua kolom
            if match >= 20:
                return idx

        raise Exception(
            "Header invoice LK-000102 tidak ditemukan"
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
        # 3. BACA DATA DENGAN HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN HEADER
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
            "Kode 1",
            "Kode 2",
            "No Faktur",
            "Tanggal",
            "Kode Customer",
            "Nama Customer",
            "Kode Barang",
            "Nama Barang",
            "Satuan",
            "Q",
            "Pcs",
            "Total Qty",
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom invoice LK-000102 tidak ditemukan: "
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
        # 8. KODE 1 -> STRING
        # =====================================================

        df["Kode 1"] = (
            df["Kode 1"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
        )

        # =====================================================
        # 9. KODE 2 -> STRING
        # =====================================================

        df["Kode 2"] = (
            df["Kode 2"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 10. NO FAKTUR -> STRING
        # =====================================================

        df["No Faktur"] = (
            df["No Faktur"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 11. KODE CUSTOMER -> STRING
        # =====================================================

        df["Kode Customer"] = (
            df["Kode Customer"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 12. NAMA CUSTOMER -> STRING
        # =====================================================

        df["Nama Customer"] = (
            df["Nama Customer"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 13. KODE BARANG -> STRING
        # =====================================================

        df["Kode Barang"] = (
            df["Kode Barang"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
        )

        # =====================================================
        # 14. NAMA BARANG -> STRING
        # =====================================================

        df["Nama Barang"] = (
            df["Nama Barang"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 15. TANGGAL -> DATE
        # =====================================================

        df["Tanggal"] = pd.to_datetime(
            df["Tanggal"],
            errors="coerce"
        ).dt.date

        # =====================================================
        # 16. KOLOM NUMERIC
        # =====================================================

        numeric_columns = [
            "Q",
            "Pcs",
            "Total Qty",
            "P/sat",
            "Total Jual",
            "Total Diskon",
            "Diskon Program (%)",
            "Diskon Program (Nominal)",
            "Diskon Promosi (%)",
            "Diskon Promosi (Nominal)",
            "Subtotal",
            "Diskon Distributor (%)",
            "Diskon Distributor (Nominal)",
            "TOTAL",
            "DPP",
            "PPN Keluaran",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # =====================================================
        # 17. REMOVE BARIS BUKAN DATA
        # =====================================================

        df = df[
            df["No Faktur"].notna()
            & df["No Faktur"].ne("")
            & df["Kode Barang"].notna()
            & df["Kode Barang"].ne("")
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
        # 20. DEBUG
        # =====================================================

        print("=" * 80)

        print("AGENT: LK-000102")

        print("\nHEADER ROW:")
        print(header_row)

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
        # 21. RETURN
        # =====================================================

        return df