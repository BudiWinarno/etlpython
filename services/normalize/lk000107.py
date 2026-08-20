from services.normalize.base import BaseNormalizer
import pandas as pd
from pandas.api.types import is_numeric_dtype


class LK000107InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        # Baca tanpa header terlebih dahulu
        preview = pd.read_excel(
            filepath,
            header=None
        )

        # Header yang memang harus ada di Agent 107
        required_headers = [
            "Kode Principle",
            "Grp Brg 1",
            "Grp Brg 2",
            "Kd Barang",
            "Kd Supplier",
            "Nm Barang",
            "Kd Plg",
            "Nm Plg",
            "No FJ",
            "Tgl FJ",
            "Qty",
            "Satuan",
            "SalesPrice",
            "Gross Amt",
            "DPP",
            "PPN",
            "TOTAL",
            "PaymentType",
        ]

        # Cari baris yang mengandung header
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

            # Kalau minimal 5 header ketemu,
            # anggap sebagai header sebenarnya
            if match_count >= 5:
                return row_index

        raise ValueError(
            "Header Agent LK000107 tidak ditemukan."
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        # =====================================================
        # 1. CARI POSISI HEADER
        # =====================================================

        header_row = self._find_header_row(
            filepath
        )

        # =====================================================
        # 2. BACA EXCEL DENGAN HEADER YANG BENAR
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

        if "No FJ" in df.columns:

            df = df[
                ~df["No FJ"]
                .astype(str)
                .str.strip()
                .str.upper()
                .eq("TOTAL")
            ]

        # =====================================================
        # 6. NORMALIZE TANGGAL
        # =====================================================

        if "Tgl FJ" in df.columns:

            if is_numeric_dtype(
                df["Tgl FJ"]
            ):

                # Excel serial date
                df["Tgl FJ"] = pd.to_datetime(
                    df["Tgl FJ"],
                    unit="D",
                    origin="1899-12-30",
                    errors="coerce"
                )

            else:

                # Datetime / string
                df["Tgl FJ"] = pd.to_datetime(
                    df["Tgl FJ"],
                    errors="coerce"
                )

            # Hanya tanggal
            df["Tgl FJ"] = (
                df["Tgl FJ"]
                .dt.date
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

        # Normalisasi terlebih dahulu
        df = self.normalize(
            filepath
        )

        # Ambil HANYA nama kolom/header
        headers = [
            str(column).strip()
            for column in df.columns
        ]

        return headers