from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000168InvoiceNormalizer(BaseNormalizer):

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
            "Ref",
            "Tgl Ref",
            "No. Ref",
            "Kode Cust",
            "Nama Cust",
            "Kode Sales",
            "Nama Sales",
            "Keterangan",
            "Kode",
            "Nama",
            "Nama Jns Brg",
            "Nama Div Pabrik",
            "Nama Grp Brg",
            "Qty",
            "Sat",
            "Harga Unit(Mu)",
            "Total(MU)",
            "Subtot Net   Pjk(Mu)",
            "Nama Kota",
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
            "Header invoice LK000150 tidak ditemukan."
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
        # 5. RESET INDEX
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