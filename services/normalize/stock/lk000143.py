from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000143StockNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        preview = pd.read_excel(
            filepath,
            header=None
        )

        required_headers = [
            "Divisi",
            "Product Grup Level 3",
            "Product Code",
            "Product Name",
            "Packaging",
            "Stock",
            "Stock (pcs)",
            "Tonnage",
            "Volume",
            "Stock Uom1",
            "Stock Uom2",
            "Stock Uom3",
            "Value@Selling",
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
            "Header stock LK000143 tidak ditemukan."
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
        # 5. HAPUS REPORT TOTAL
        # =====================================================

        if "Divisi" in df.columns:

            df = df[
                ~df["Divisi"]
                .astype(str)
                .str.strip()
                .str.upper()
                .eq("REPORT TOTAL")
            ]

        # =====================================================
        # 6. HAPUS END OF REPORT
        # =====================================================

        if "Divisi" in df.columns:

            df = df[
                ~df["Divisi"]
                .astype(str)
                .str.strip()
                .str.upper()
                .str.startswith("END OF REPORT")
            ]

        # =====================================================
        # 7. HAPUS BARIS TANPA PRODUCT CODE
        # =====================================================

        if "Product Code" in df.columns:

            df = df[
                df["Product Code"].notna()
            ]

        # =====================================================
        # 8. RESET INDEX
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