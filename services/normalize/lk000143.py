from services.normalize.base import BaseNormalizer
import pandas as pd


class LK000143InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # CARI HEADER
    # =========================================================

    def _find_header_row(self, filepath):

        preview = pd.read_excel(
            filepath,
            header=None
        )

        required_headers = [
            "Customer Name",
            "Customer#",
            "Address",
            "Area",
            "Product Code",
            "Product Name",
            "Packaging",
            "Varian",
            "Invoice Date",
            "Invoice No",
            "SalesOrder#",
            "Salesman",
            "Quantity",
            "Qty (Pcs)",
            "Freegood",
            "Price",
            "Gross Amount",
            "LineDisc1",
            "LineDisc2",
            "LineDisc3",
            "LineDisc4",
            "LineDisc5",
            "LD Amount",
            "%Disc1",
            "%Disc2",
            "%Disc3",
            "Discount",
            "DPP",
            "Tax",
            "Net Amount",
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
            "Header invoice LK000143 tidak ditemukan."
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
        # 3. BERSIHKAN NAMA HEADER
        # =====================================================
        #
        # Nama header tetap raw.
        # Hanya membersihkan spasi di awal/akhir.
        #

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
        # 5. HAPUS BARIS SUBTOTAL
        # =====================================================
        #
        # Contoh:
        # Subtotal ALTON
        # Subtotal AMIRA
        #

        if "Customer Name" in df.columns:

            df = df[
                ~df["Customer Name"]
                .astype(str)
                .str.strip()
                .str.lower()
                .str.startswith("subtotal")
            ]
        
        # =====================================================
        # 6. HAPUS REPORT TOTAL
        # =====================================================

        if "Customer Name" in df.columns:

            df = df[
                ~df["Customer Name"]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq("report total")
            ]

        # =====================================================
        # 7. HAPUS END OF REPORT
        # =====================================================

        if "Customer Name" in df.columns:

            df = df[
                ~df["Customer Name"]
                .astype(str)
                .str.strip()
                .str.lower()
                .str.startswith("end of")
            ]

        # =====================================================
        # 8. HAPUS BARIS YANG TIDAK PUNYA CUSTOMER
        # =====================================================

        df = df[
            df["Customer Name"].notna()
        ]

        # =====================================================
        # 6. NORMALIZE INVOICE DATE
        # =====================================================

        if "Invoice Date" in df.columns:

            df["Invoice Date"] = pd.to_datetime(
                df["Invoice Date"],
                errors="coerce"
            )

            # Hanya tanggal
            df["Invoice Date"] = (
                df["Invoice Date"]
                .dt.date
            )

        # =====================================================
        # 7. HAPUS BARIS YANG TIDAK PUNYA CUSTOMER
        # =====================================================

        if "Customer Name" in df.columns:

            df = df[
                df["Customer Name"]
                .notna()
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