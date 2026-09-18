import pandas as pd
from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "Nama Agen",
    "Kode Customer",
    "Nama Customer",
    "Alamat Customer",
    "Nomor Telepon/HP Customer",
    "Invoice Nomor Agen",
    "Tanggal Invoice",
    "Tipe Customer",
    "Kota",
    "SKU Kode Agen",
    "Nama SKU",
    "Quantity Terjual",
    "NAMA SALESMAN",
    "NAMA SUPERVISOR",
]


class LK000144InvoiceNormalizer(BaseNormalizer):

    def find_header_row(self, df):

        expected_headers = {
            header.strip().lower()
            for header in EXPECTED_HEADERS
        }

        for idx, row in df.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            match = len(
                values.intersection(expected_headers)
            )

            if match >= 10:
                return idx

        raise Exception(
            "Header invoice LK-000144 tidak ditemukan"
        )

    def normalize(self, filepath):

        print("\n==============================")
        print("NORMALIZE INVOICE LK-000144")
        print("==============================")

        # ======================================================
        # 1. BACA FILE TANPA HEADER
        # ======================================================

        raw = pd.read_excel(
            filepath,
            header=None
        )

        # ======================================================
        # 2. CARI HEADER
        # ======================================================

        header_row = self.find_header_row(raw)

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
        )

        # ======================================================
        # 3. DATA DIMULAI 2 BARIS SETELAH HEADER
        # ======================================================

        data_start = header_row + 2

        data = raw.iloc[data_start:].copy()

        # Ambil kolom yang digunakan
        data = data.iloc[:, :25]

        # ======================================================
        # 4. SET NAMA KOLOM
        # ======================================================

        columns = [
            "Nama Agen",
            "Kode Customer",
            "Nama Customer",
            "Alamat Customer",
            "Nomor Telepon/HP Customer",
            "Invoice Nomor Agen",
            "Tanggal Invoice",
            "Tipe Customer",
            "Kota",
            "SKU Kode Agen",
            "Nama SKU",
            "Quantity Terjual (Karton)",
            "Quantity Terjual (Pcs)",
            "% Diskon 1",
            "% Diskon 2",
            "% Diskon 3",
            "% Diskon 4",
            "% Diskon 5",
            "Diskon 6",
            "Quantity Bonus",
            "Rafraksi (Rp)",
            "Total Invoice Value",
            "NAMA SALESMAN",
            "NAMA SUPERVISOR",
        ]

        # Buang kolom pertama yang kosong
        data = data.iloc[:, 1:25]

        data.columns = columns

        # ======================================================
        # 5. HAPUS BARIS KOSONG
        # ======================================================

        data = data.dropna(how="all")

        # ======================================================
        # 6. KOLOM STRING
        # ======================================================

        string_columns = [
            "Nama Agen",
            "Kode Customer",
            "Nama Customer",
            "Alamat Customer",
            "Nomor Telepon/HP Customer",
            "Invoice Nomor Agen",
            "Tipe Customer",
            "Kota",
            "SKU Kode Agen",
            "Nama SKU",
            "NAMA SALESMAN",
            "NAMA SUPERVISOR",
        ]

        for column in string_columns:

            if column in data.columns:

                data[column] = (
                    data[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        # ======================================================
        # 7. KOLOM NUMERIC
        # ======================================================

        numeric_columns = [
            "Quantity Terjual (Karton)",
            "Quantity Terjual (Pcs)",
            "% Diskon 1",
            "% Diskon 2",
            "% Diskon 3",
            "% Diskon 4",
            "% Diskon 5",
            "Diskon 6",
            "Quantity Bonus",
            "Rafraksi (Rp)",
            "Total Invoice Value",
        ]

        for column in numeric_columns:

            if column in data.columns:

                data[column] = pd.to_numeric(
                    data[column],
                    errors="coerce"
                ).fillna(0)

        # ======================================================
        # 8. TANGGAL
        # ======================================================

        if "Tanggal Invoice" in data.columns:

            data["Tanggal Invoice"] = pd.to_datetime(
                data["Tanggal Invoice"],
                errors="coerce"
            ).dt.date

        # ======================================================
        # 9. FILTER DATA VALID
        # ======================================================

        data = data[
            data["Invoice Nomor Agen"]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        ]

        data = data[
            data["SKU Kode Agen"]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        ]

        # ======================================================
        # 10. RESET INDEX
        # ======================================================

        data = data.reset_index(drop=True)

        # ======================================================
        # 11. BUAT NO
        # ======================================================

        data.insert(
            0,
            "No",
            range(1, len(data) + 1)
        )

        # ======================================================
        # 12. URUTAN KOLOM
        # ======================================================

        data = data[
            [
                "No",
                "Nama Agen",
                "Kode Customer",
                "Nama Customer",
                "Alamat Customer",
                "Nomor Telepon/HP Customer",
                "Invoice Nomor Agen",
                "Tanggal Invoice",
                "Tipe Customer",
                "Kota",
                "SKU Kode Agen",
                "Nama SKU",
                "Quantity Terjual (Karton)",
                "Quantity Terjual (Pcs)",
                "% Diskon 1",
                "% Diskon 2",
                "% Diskon 3",
                "% Diskon 4",
                "% Diskon 5",
                "Diskon 6",
                "Quantity Bonus",
                "Rafraksi (Rp)",
                "Total Invoice Value",
                "NAMA SALESMAN",
                "NAMA SUPERVISOR",
            ]
        ]

        # ======================================================
        # 13. DEBUG
        # ======================================================

        print("\n==============================")
        print("HASIL NORMALISASI")
        print("==============================")

        print(
            data.head(10).to_string()
        )

        print(
            "\nJumlah data:",
            len(data)
        )

        print(
            "\nJumlah kolom:",
            len(data.columns)
        )

        print(
            "\nKolom:"
        )

        print(
            data.columns.tolist()
        )

        print("\n==============================")
        print("NORMALIZE SELESAI")
        print("==============================")

        return data