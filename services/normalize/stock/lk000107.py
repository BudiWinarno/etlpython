from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000107StockNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        # Baca Excel tanpa menentukan header
        preview = pd.read_excel(
            filepath,
            header=None
        )

        # Header yang menjadi identitas stock Agent 107
        required_headers = [
            "Kd Item",
            "Kd Item Principle",
            "Item",
            "Brand",
            "Gudang",
            "Base QTY",
            "Price Jual",
            "QTY CTN",
            "QTY PCS",
            "Total (PCS)",
            "Value",
            "Value + PPN",
            "HPP",
            "HPP Total",
        ]

        # Cari baris header
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

            # Minimal beberapa header harus cocok
            if match_count >= 5:
                return row_index

        raise ValueError(
            "Header stock LK000107 tidak ditemukan."
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        # =====================================================
        # 1. CARI BARIS HEADER
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
        # 3. BERSIHKAN NAMA HEADER
        # =====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # =====================================================
        # 4. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 5. HAPUS BARIS TOTAL
        # =====================================================

        if "Kd Item" in df.columns:

            df = df[
                ~df["Kd Item"]
                .astype(str)
                .str.strip()
                .str.upper()
                .eq("TOTAL:")
            ]

        # =====================================================
        # 6. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(self, filepath):

        # Normalisasi terlebih dahulu
        df = self.normalize(
            filepath
        )

        # Ambil nama header RAW
        headers = [
            str(column).strip()
            for column in df.columns
        ]

        return headers