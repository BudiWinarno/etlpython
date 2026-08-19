import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000035StockNormalizer(BaseNormalizer):

    # =========================================================
    # NORMALIZE
    # RAW EXCEL → DATA BERSIH
    # =========================================================
    def normalize(self, filepath):

        # =====================================================
        # 1. BACA EXCEL TANPA HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. DATA MULAI ROW INDEX 7
        # =====================================================

        df = df.iloc[7:].copy()

        # =====================================================
        # 3. AMBIL KOLOM
        # =====================================================

        df = df[
            [
                2,
                3,
                5,
                7,
                9
            ]
        ].copy()

        # =====================================================
        # 4. RENAME HEADER
        # =====================================================

        df.columns = [
            "No. Barang",
            "Deskripsi Barang",
            "G. Promo Medan",
            "G. Utama Medan",
            "Harga satuan"
        ]

        # =====================================================
        # 5. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            subset=[
                "No. Barang",
                "Deskripsi Barang"
            ],
            how="all"
        )

        # =====================================================
        # 6. BERSIHKAN KODE BARANG
        # =====================================================

        df["No. Barang"] = (
            df["No. Barang"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 7. BERSIHKAN DESKRIPSI
        # =====================================================

        df["Deskripsi Barang"] = (
            df["Deskripsi Barang"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 8. NUMERIC G. PROMO MEDAN
        # =====================================================

        df["G. Promo Medan"] = pd.to_numeric(
            df["G. Promo Medan"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 9. NUMERIC G. UTAMA MEDAN
        # =====================================================

        df["G. Utama Medan"] = pd.to_numeric(
            df["G. Utama Medan"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 10. TOTAL QTY PCS
        # =====================================================

        df["total_qty_pcs"] = (
            df["G. Promo Medan"]
            +
            df["G. Utama Medan"]
        )

        # =====================================================
        # 11. HARGA SATUAN
        # =====================================================

        df["Harga satuan"] = pd.to_numeric(
            df["Harga satuan"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 12. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 13. NOMOR URUT
        # =====================================================

        df.insert(
            0,
            "No",
            range(
                1,
                len(df) + 1
            )
        )

        # =====================================================
        # 14. RETURN
        # =====================================================

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # HASIL NORMALISASI → AMBIL HEADER SAJA
    # =========================================================
    def get_mapping_headers(self, filepath):

        # File yang masuk ke sini adalah
        # HASIL NORMALISASI.
        #
        # Header sudah berada di row pertama.

        df = pd.read_excel(
            filepath,
            header=0,
            nrows=0
        )

        headers = (
            df.columns
            .astype(str)
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
            .tolist()
        )

        return headers