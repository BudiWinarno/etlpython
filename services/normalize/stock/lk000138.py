from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000138StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        # =====================================================
        # BACA EXCEL TANPA HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # AMBIL DATA
        # =====================================================
        #
        # Baris pertama:
        # S129 | PT. JOENOES IKAMULYA | ...
        #
        # Bukan data, tetapi informasi/header.
        #

        df = df.iloc[1:].copy()

        # =====================================================
        # RENAME KOLOM
        # =====================================================

        df.columns = [
            "kode_produk",
            "nama_produk",
            "satuan",
            "pcs1",
            "pcs2",
            "pcs3"
        ]
        
        # =====================================================
        # HAPUS BARIS PEMISAH / TOTAL
        # =====================================================

        df = df[
            df["kode_produk"].notna()
        ]

        # =====================================================
        # HAPUS BARIS BUKAN PRODUK
        # =====================================================

        df = df[
            ~df["nama_produk"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin([
                "subtotal ni",
                "p.p.n",
                "jumlah"
            ])
        ]

        # =====================================================
        # RESET INDEX
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