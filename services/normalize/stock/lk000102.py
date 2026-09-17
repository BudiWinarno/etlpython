import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "NO",
    "KODE BARANG",
    "NAMA BARANG",
    "Pcs",
    "SALDO AKHIR",
]


class LK000102StockNormalizer(BaseNormalizer):

    # ==========================================================
    # CARI HEADER RAW
    # Dipakai hanya ketika melakukan NORMALIZE
    # ==========================================================

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = [
                str(v).strip().upper()
                for v in row.tolist()
                if pd.notna(v)
            ]

            required_headers = [
                "NO",
                "KODE BARANG",
                "NAMA BARANG",
                "PCS",
                "SALDO AKHIR",
            ]

            match = sum(
                1
                for header in required_headers
                if header in values
            )

            if match >= 4:
                return idx

        raise ValueError(
            "Header stock LK-000102 tidak ditemukan"
        )

    # ==========================================================
    # HEADER UNTUK MAPPING
    #
    # Mapping menggunakan FILE HASIL NORMALISASI
    #
    # Jadi TIDAK perlu find_header_row()
    # ==========================================================

    def get_mapping_headers(self, filepath):

        return [
            "No",
            "KODE BARANG",
            "NAMA BARANG",
            "Pcs",
            "Qty Karton",
            "Qty Pcs",
        ]

    # ==========================================================
    # NORMALIZE
    #
    # RAW:
    #
    # NO
    # KODE BARANG
    # NAMA BARANG
    # Pcs
    # SALDO AKHIR
    #
    # SALDO AKHIR terdiri dari:
    # Qty in Q
    # Qty in PCS
    #
    # HASIL:
    #
    # No
    # KODE BARANG
    # NAMA BARANG
    # Pcs
    # Qty Karton
    # Qty Pcs
    # ==========================================================

    def normalize(self, filepath):

        print("\n==============================")
        print("NORMALIZE STOCK LK-000102")
        print("==============================")

        # ======================================================
        # 1. BACA FILE RAW TANPA HEADER
        # ======================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        header_row = self.find_header_row(preview)

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
        )

        # ======================================================
        # 2. BACA RAW
        # ======================================================

        raw = pd.read_excel(
            filepath,
            header=None
        )

        # ======================================================
        # 3. DEBUG HEADER
        # ======================================================

        print("\nMAIN HEADER:")

        print(
            raw.iloc[header_row].tolist()
        )

        # ======================================================
        # 4. DATA DIMULAI 2 BARIS SETELAH HEADER
        #
        # Contoh:
        #
        # Baris header:
        # NO | KODE BARANG | NAMA BARANG | Pcs | SALDO AKHIR
        #
        # Baris berikutnya:
        # Periode : Juni 2026 | ... | Qty in Q | Qty in PCS
        #
        # Data:
        # 1 | AGA080391 | Aganol Lavender | 12 | 2 | 24
        #
        # ======================================================

        data_start = header_row + 2

        df = raw.iloc[data_start:].copy()

        # ======================================================
        # 5. AMBIL 6 KOLOM
        # ======================================================

        df = df.iloc[:, :6]

        df.columns = [
            "NO",
            "KODE BARANG",
            "NAMA BARANG",
            "Pcs",
            "Qty Karton",
            "Qty Pcs",
        ]

        # ======================================================
        # 6. CLEAN HEADER
        # ======================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # ======================================================
        # 7. HAPUS BARIS KOSONG
        # ======================================================

        df = df.dropna(
            how="all"
        )

        # ======================================================
        # 8. KODE BARANG -> STRING
        # ======================================================

        df["KODE BARANG"] = (
            df["KODE BARANG"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
        )

        # ======================================================
        # 9. NAMA BARANG -> STRING
        # ======================================================

        df["NAMA BARANG"] = (
            df["NAMA BARANG"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # ======================================================
        # 10. PCS
        #
        # Ini adalah jumlah PCS dalam 1 karton
        # ======================================================

        df["Pcs"] = pd.to_numeric(
            df["Pcs"],
            errors="coerce"
        ).fillna(0)

        # ======================================================
        # 11. QTY KARTON
        #
        # SALDO AKHIR -> Qty in Q
        # ======================================================

        df["Qty Karton"] = pd.to_numeric(
            df["Qty Karton"],
            errors="coerce"
        ).fillna(0)

        # ======================================================
        # 12. QTY PCS
        #
        # SALDO AKHIR -> Qty in PCS
        # ======================================================

        df["Qty Pcs"] = pd.to_numeric(
            df["Qty Pcs"],
            errors="coerce"
        ).fillna(0)

        # ======================================================
        # 13. BULATKAN QTY PCS
        # ======================================================

        df["Qty Pcs"] = (
            df["Qty Pcs"]
            .round()
            .astype(int)
        )

        # ======================================================
        # 14. FILTER KODE BARANG
        # ======================================================

        df = df[
            df["KODE BARANG"].str.strip() != ""
        ]

        # ======================================================
        # 15. RESET INDEX
        # ======================================================

        df = df.reset_index(
            drop=True
        )

        # ======================================================
        # 16. BUAT NO BARU
        # ======================================================

        if "No" in df.columns:
            df = df.drop(
                columns=["No"]
            )

        if "NO" in df.columns:
            df = df.drop(
                columns=["NO"]
            )

        df.insert(
            0,
            "No",
            range(
                1,
                len(df) + 1
            )
        )

        # ======================================================
        # 17. URUTAN KOLOM FINAL
        # ======================================================

        df = df[
            [
                "No",
                "KODE BARANG",
                "NAMA BARANG",
                "Pcs",
                "Qty Karton",
                "Qty Pcs",
            ]
        ]

        # ======================================================
        # 18. DEBUG
        # ======================================================

        print("\n==============================")
        print("HASIL NORMALISASI")
        print("==============================")

        print(
            df.head(10)
        )

        print(
            "\nJumlah data:",
            len(df)
        )

        print(
            "\nKolom:"
        )

        print(
            df.columns.tolist()
        )

        print("\n==============================")
        print("NORMALIZE SELESAI")
        print("==============================")

        return df