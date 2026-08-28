import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "Nama Agen",
    "Kode Customer",
    "Nama Customer",
    "Invoice Nomor Agen",
    "Tanggal Invoice",
    "SKU Kode Agen",
    "Nama SKU",
    "Packaging",
    "Quantity Terjual",
]


class LK000004InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = (
                row.fillna("")
                .astype(str)
                .str.replace(
                    "\u00A0",
                    " ",
                    regex=False
                )
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True
                )
                .str.strip()
                .tolist()
            )

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 6:
                return idx

        raise Exception(
            "Header invoice LK-000014 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(
        self,
        filepath
    ):

        # =====================================================
        # 1. BACA SEMUA BARIS TANPA HEADER
        # =====================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. CARI HEADER OTOMATIS
        # =====================================================

        header_row = self.find_header_row(
            preview
        )

        print("=" * 80)

        print("FILE:")
        print(filepath)

        print("\nHEADER ROW:")
        print(header_row)

        print("=" * 80)

        # =====================================================
        # 3. BACA ULANG
        #
        # SEMUA KOLOM RAW DIPERTAHANKAN
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN NAMA HEADER
        #
        # Tidak membuang kolom apa pun.
        # =====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.replace(
                "\u00A0",
                " ",
                regex=False
            )
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )
        
        # =====================================================
        # 4B. PERBAIKI KOLOM QUANTITY
        # =====================================================

        df = df.rename(
            columns={
                "Quantity Terjual": "qty_karton",
                "Unnamed: 13": "Quantity Terjual"
            }
        )

        # =====================================================
        # 5. DEBUG SEMUA HEADER RAW
        # =====================================================

        print("=" * 80)

        print("SEMUA KOLOM RAW:")

        for i, column in enumerate(df.columns):
            print(
                i,
                "=>",
                repr(column)
            )

        print("=" * 80)

        # =====================================================
        # 6. HAPUS BARIS YANG BENAR-BENAR KOSONG
        #
        # Kolom tidak dihapus.
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 7. BERSIHKAN KOLOM TEXT
        #
        # Semua kolom tetap dipertahankan.
        # =====================================================

        for col in df.columns:

            if df[col].dtype == "object":

                df[col] = (
                    df[col]
                    .fillna("")
                    .astype(str)
                    .str.replace(
                        "\u00A0",
                        " ",
                        regex=False
                    )
                    .str.replace(
                        r"\s+",
                        " ",
                        regex=True
                    )
                    .str.strip()
                )
        # =====================================================
        # 7B. HAPUS BARIS REPORT TOTAL
        # =====================================================

        if "Nama Customer" in df.columns:

            df = df[
                df["Nama Customer"].str.strip().str.lower()
                != "report total"
            ].copy()

        # =====================================================
        # 8. QUANTITY TERJUAL
        #
        # Nilai dipakai langsung:
        #
        # 12
        # 36
        # 12
        # 6
        # 6
        # 6
        # 12
        # 36
        # 6
        # 2
        #
        # Tidak diubah menjadi 1.0.0.0 atau format lainnya.
        # =====================================================
        
        # =====================================================
        # 8. QTY KARTON
        # =====================================================

        if "qty_karton" in df.columns:

            df["qty_karton"] = pd.to_numeric(
                df["qty_karton"],
                errors="coerce"
            ).fillna(0)


        # =====================================================
        # 8B. QUANTITY TERJUAL
        # =====================================================

        if "Quantity Terjual" in df.columns:

            df["Quantity Terjual"] = pd.to_numeric(
                df["Quantity Terjual"],
                errors="coerce"
            ).fillna(0)

        if "Quantity Terjual" in df.columns:

            df["Quantity Terjual"] = pd.to_numeric(
                df["Quantity Terjual"],
                errors="coerce"
            ).fillna(0)

        # =====================================================
        # 9. TANGGAL INVOICE
        # =====================================================

        if "Tanggal Invoice" in df.columns:

            df["Tanggal Invoice"] = pd.to_datetime(
                df["Tanggal Invoice"],
                errors="coerce"
            )

        # =====================================================
        # 10. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 11. DEBUG HASIL NORMALISASI
        # =====================================================

        print("=" * 80)

        print("HASIL NORMALISASI")

        print("\nTOTAL KOLOM:")
        print(
            len(df.columns)
        )

        print("\nTOTAL DATA:")
        print(
            len(df)
        )

        print("\nKOLOM:")

        print(
            df.columns.tolist()
        )

        print("\nDATA:")

        print(
            df.head(20).to_string()
        )

        print("=" * 80)

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(
        self,
        filepath
    ):

        # =====================================================
        # 1. BACA SEMUA BARIS
        # =====================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. CARI HEADER OTOMATIS
        # =====================================================

        header_row = self.find_header_row(
            preview
        )

        # =====================================================
        # 3. BACA DENGAN HEADER YANG DITEMUKAN
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN HEADER
        # =====================================================

        headers = (
            df.columns
            .astype(str)
            .str.replace(
                "\u00A0",
                " ",
                regex=False
            )
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
            .tolist()
        )

        # =====================================================
        # 5. DEBUG
        # =====================================================

        print("=" * 80)

        print("MAPPING HEADERS:")

        for i, header in enumerate(headers):
            print(
                i,
                "=>",
                repr(header)
            )

        print("=" * 80)

        return headers