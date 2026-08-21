from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000155StockNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        preview = pd.read_excel(
            filepath,
            header=None
        )

        required_headers = [
            "NAMA SUPPLIER",
            "ITEM ID",
            "KETERANGAN ITEM",
            "QTY CTN",
            "UNIT",
            "QTY PCS",
            "CCY",
            "HARGA JUAL",
            "HARGA BELI",
            "NILAI",
            "SUPPLIER 2",
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

            if match_count >= 8:
                return row_index

        raise ValueError(
            "Header stock LK000155 tidak ditemukan."
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
        # 3. BERSIHKAN HEADER
        # =====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 4. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 5. HAPUS GRAND TOTAL
        # =====================================================

        if "NAMA SUPPLIER" in df.columns:

            df = df[
                ~df["NAMA SUPPLIER"]
                .astype(str)
                .str.strip()
                .str.upper()
                .str.startswith(
                    "GRAND TOTAL"
                )
            ]

        # =====================================================
        # 6. HAPUS BARIS TANPA ITEM ID
        # =====================================================

        if "ITEM ID" in df.columns:

            df = df[
                df["ITEM ID"].notna()
            ]

            # =================================================
            # ITEM ID HARUS STRING
            # =================================================

            df["ITEM ID"] = (
                df["ITEM ID"]
                .astype("string")
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

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

        headers = [
            str(column).strip()
            for column in df.columns
        ]

        return headers