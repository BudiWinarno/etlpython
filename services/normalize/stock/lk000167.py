from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000167StockNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        preview = pd.read_excel(
            filepath,
            header=None
        )

        required_headers = [
            "Pemasok",
            "Kode Barang",
            "UPC/Barcode",
            "Nama Barang",
            "Nama Gudang",
            "ISI",
            "Stock Akhir",
        ]

        for row_index in range(len(preview)):

            row_values = (
                preview.iloc[row_index]
                .astype(str)
                .str.strip()
                .tolist()
            )

            match_count = sum(
                1
                for header in required_headers
                if header in row_values
            )

            if match_count >= 5:
                return row_index

        raise ValueError(
            "Header stock LK000167 tidak ditemukan."
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        # =====================================================
        # 1. CARI HEADER
        # =====================================================

        header_row = self._find_header_row(
            filepath
        )

        # =====================================================
        # 2. BACA EXCEL
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 3. HANYA AMBIL KOLOM HEADER YANG DIPERLUKAN
        # =====================================================

        expected_columns = [
            "Pemasok",
            "Kode Barang",
            "UPC/Barcode",
            "Nama Barang",
            "Nama Gudang",
            "ISI",
            "Stock Akhir",
        ]

        df = df[
            [
                column
                for column in expected_columns
                if column in df.columns
            ]
        ]

        # =====================================================
        # 4. BERSIHKAN NAMA HEADER
        # =====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 5. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 6. HAPUS BARIS TANPA KODE BARANG
        # =====================================================

        if "Kode Barang" in df.columns:

            df = df[
                df["Kode Barang"].notna()
            ]

        # =====================================================
        # 7. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(self, filepath):

        df = self.normalize(
            filepath
        )

        return df.columns.tolist()