import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000129InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def _find_header_row(self, filepath, sheet_name=0):

        preview = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=None,
            nrows=30
        )

        expected_headers = {
            "nama agen",
            "kode customer",
            "nama customer",
            "alamat customer",
            "nomor telepon/hp customer",
            "invoice nomor agen",
            "tanggal invoice",
            "tipe customer",
            "kota",
            "sku kode agen",
            "nama sku",
            "quantity terjual",
            "% diskon 1",
            "% diskon 2",
            "% diskon 3",
            "% diskon 4",
            "% diskon 5",
            "diskon 6",
            "quantity bonus",
            "rafraksi (rp)",
            "total invoice value",
            "nama salesman",
            "nama supervisor",
        }

        for idx, row in preview.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            match_count = len(
                values.intersection(expected_headers)
            )

            if match_count >= 15:
                return idx

        raise ValueError(
            "Header Invoice LK-000062 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        sheet_name = 0

        # -----------------------------------------------------
        # FIND HEADER
        # -----------------------------------------------------

        header_row = self._find_header_row(
            filepath,
            sheet_name
        )

        # -----------------------------------------------------
        # READ DATA TANPA HEADER
        # -----------------------------------------------------

        raw = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=None
        )

        # -----------------------------------------------------
        # AMBIL HEADER UTAMA
        # -----------------------------------------------------

        headers = raw.iloc[header_row].tolist()

        # -----------------------------------------------------
        # DATA DIMULAI SETELAH SUB HEADER
        # -----------------------------------------------------

        df = raw.iloc[header_row + 2:].copy()

        # -----------------------------------------------------
        # BUAT NAMA KOLOM
        # -----------------------------------------------------

        columns = [
            str(col).strip()
            if pd.notna(col)
            else ""
            for col in headers
        ]

        # -----------------------------------------------------
        # QUANTITY TERJUAL
        # -----------------------------------------------------

        # Kolom berdasarkan posisi sumber:
        #
        # 12 = Quantity Terjual / KRT
        # 13 = PCS

        columns[12] = "Qty Terjual (Karton)"
        columns[13] = "Qty Terjual (Pcs)"

        df.columns = columns

        # -----------------------------------------------------
        # HAPUS BARIS KOSONG DI BAWAH HEADER
        # -----------------------------------------------------

        df = df.dropna(how="all")

        # -----------------------------------------------------
        # REMOVE EMPTY COLUMNS
        # -----------------------------------------------------

        df = df.loc[
            :,
            [
                col != ""
                and not str(col).startswith("Unnamed")
                for col in df.columns
            ]
        ]

        # -----------------------------------------------------
        # SKU -> STRING
        # -----------------------------------------------------

        if "SKU Kode Agen" in df.columns:

            df["SKU Kode Agen"] = (
                df["SKU Kode Agen"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

        # -----------------------------------------------------
        # KODE CUSTOMER -> STRING
        # -----------------------------------------------------

        if "Kode Customer" in df.columns:

            df["Kode Customer"] = (
                df["Kode Customer"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

        # -----------------------------------------------------
        # INVOICE -> STRING
        # -----------------------------------------------------

        if "Invoice Nomor Agen" in df.columns:

            df["Invoice Nomor Agen"] = (
                df["Invoice Nomor Agen"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        if "Tanggal Invoice" in df.columns:

            df["Tanggal Invoice"] = pd.to_datetime(
                df["Tanggal Invoice"],
                errors="coerce"
            )

        # -----------------------------------------------------
        # REMOVE EMPTY ROWS
        # -----------------------------------------------------

        df = df.dropna(how="all")

        # -----------------------------------------------------
        # RESET INDEX
        # -----------------------------------------------------

        df = df.reset_index(drop=True)

        return df