import pandas as pd

from services.normalize.base import BaseNormalizer


# =========================================================
# EXPECTED HEADERS
# =========================================================

EXPECTED_HEADERS = [
    "No",
    "Scope Cabang",
    "Direktori",
    "Supplier",
    "Barcode",
    "Nama Barang",
    "Kategori",
    "Merk",
    "Saldo Fisik",
    "#",
    "Package",
    "Harga Jual",
    "Nilai Jual (Rp)",
    "Status",
    "Sifat Barang",
    "Saldo QTY Terbesar",
    "Nama Satuan Terbesar",
    "Saldo QTY Terkecil",
    "Nama Satuan Terkecil",
]


class LK000120StockNormalizer(BaseNormalizer):

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
                values.intersection(
                    expected_headers
                )
            )

            if match >= 15:
                return idx

        raise Exception(
            "Header stock LK-000120 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        print("=" * 80)
        print("NORMALIZE STOCK LK-000120")
        print("=" * 80)

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

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
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
            "No",
            "Scope Cabang",
            "Direktori",
            "Supplier",
            "Barcode",
            "Nama Barang",
            "Kategori",
            "Merk",
            "Saldo Fisik",
            "#",
            "Package",
            "Harga Jual",
            "Nilai Jual (Rp)",
            "Status",
            "Sifat Barang",
            "Saldo QTY Terbesar",
            "Nama Satuan Terbesar",
            "Saldo QTY Terkecil",
            "Nama Satuan Terkecil",
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom stock LK-000120 tidak ditemukan: "
                + ", ".join(missing_columns)
            )

        # =====================================================
        # 6. REMOVE UNNAMED COLUMNS
        # =====================================================

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith(
                "Unnamed"
            )
        ]

        # =====================================================
        # 7. REMOVE EMPTY ROWS
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 8. KOLOM STRING
        # =====================================================

        string_columns = [
            "Scope Cabang",
            "Direktori",
            "Supplier",
            "Barcode",
            "Nama Barang",
            "Kategori",
            "Merk",
            "#",
            "Package",
            "Status",
            "Sifat Barang",
            "Nama Satuan Terbesar",
            "Nama Satuan Terkecil",
        ]

        for column in string_columns:

            if column in df.columns:

                df[column] = (
                    df[column]
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
        # 9. NUMERIC
        # =====================================================

        numeric_columns = [
            "No",
            "Saldo Fisik",
            "Harga Jual",
            "Nilai Jual (Rp)",
            "Saldo QTY Terbesar",
            "Saldo QTY Terkecil",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # =====================================================
        # 10. BULATKAN QTY
        # =====================================================

        df["Saldo QTY Terbesar"] = (
            df["Saldo QTY Terbesar"]
            .round()
            .astype(int)
        )

        df["Saldo QTY Terkecil"] = (
            df["Saldo QTY Terkecil"]
            .round()
            .astype(int)
        )

        # =====================================================
        # 11. FILTER DATA BARANG
        # =====================================================

        df = df[
            df["Barcode"]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        ]

        # =====================================================
        # 12. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 13. BUAT NOMOR URUT BARU
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
        # 14. URUTAN KOLOM FINAL
        # =====================================================

        df = df[
            [
                "No",
                "Scope Cabang",
                "Direktori",
                "Supplier",
                "Barcode",
                "Nama Barang",
                "Kategori",
                "Merk",
                "Saldo Fisik",
                "#",
                "Package",
                "Harga Jual",
                "Nilai Jual (Rp)",
                "Status",
                "Sifat Barang",
                "Saldo QTY Terbesar",
                "Nama Satuan Terbesar",
                "Saldo QTY Terkecil",
                "Nama Satuan Terkecil",
            ]
        ]

        # =====================================================
        # 15. DEBUG
        # =====================================================

        print("\n" + "=" * 80)
        print("AGENT: LK-000120")
        print("=" * 80)

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
        # 16. RETURN
        # =====================================================

        return df