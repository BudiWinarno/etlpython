from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000168StockNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        preview = pd.read_excel(
            filepath,
            header=None
        )

        required_headers = [
            "No. Urut",
            "Kode Brg",
            "Nama Brg",
            "Sat Std",
            "Sat Trans",
            "Kode Jns Brg",
            "Nama Jns Brg",
            "Kode Grp Brg",
            "Nama Grp Brg",
            "Saldo Awal",
            "PB",
            "LPB",
            "NRB",
            "Total Pembelian",
            "Apotek",
            "Toko Obat",
            "Toko Kelontong",
            "Toko Kosmetik",
            "Grosir",
            "Market",
            "Lain2",
            "NRJ",
            "Total Penjualan",
            "BS",
            "Koreksi Stok",
            "TBL",
            "KBL",
            "MTB",
            "Saldo Akhir",
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

            if match_count >= 10:
                return row_index

        raise ValueError(
            "Header stock LK000150 tidak ditemukan."
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
        # 5. HAPUS BARIS TOTAL / REPORT
        # =====================================================

        if "No. Urut" in df.columns:

            df = df[
                ~df["No. Urut"]
                .astype(str)
                .str.strip()
                .str.upper()
                .str.startswith(
                    (
                        "TOTAL",
                        "REPORT TOTAL",
                        "END OF REPORT"
                    )
                )
            ]

        # =====================================================
        # 6. HAPUS BARIS TANPA KODE BARANG
        # =====================================================

        if "Kode Brg" in df.columns:

            df = df[
                df["Kode Brg"].notna()
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

        headers = [
            str(column).strip()
            for column in df.columns
        ]

        return headers