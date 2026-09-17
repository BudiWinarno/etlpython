import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "No",
    "Scope Cabang",
    "Provinsi",
    "Kab/ Kota",
    "Zona",
    "Kode Customer",
    "Nama Customer",
    "List Customer",
    "Alamat Customer",
    "Kode Kecamatan",
    "Nama Kecamatan",
    "Contact Person",
    "Telf Customer",
    "No. HP Customer",
    "TOP",
    "Limit Piutang",
    "Limit Nota",
    "TMT Aktif",
    "Tipe Customer",
    "Kategori Customer",
    "Kode Salesman",
    "Bulan Faktur",
    "Tgl Faktur",
    "Tgl Jatuh Tempo",
    "Token Faktur",
    "No. Faktur",
    "Kode Barang",
    "Nama Barang",
    "QTY Faktur",
    "Satuan Faktur",
    "QTY Terbesar",
    "Satuan Terbesar",
    "QTY Terkecil",
    "Satuan Terkecil",
    "Harga Faktur",
    "Harga Sebelum Pot.",
    "Disc. 1",
    "Disc. 2",
    "Disc. 3",
    "Disc. 4",
    "Disc. Value",
    "Pot. Harga",
    "Subtotal Faktur",
    "DPP",
    "PPN%",
    "Nilai PPN",
    "Nilai Faktur",
    "Bonus?",
    "Direktori",
    "Supplier",
    "Jenis Barang",
    "Kategori Barang",
    "Merk Barang",
    "Sifat Barang",
    "Volume Satuan",
    "Satuan Terkecil",
    "Keterangan",
    "Kode Customer Lama",
    "Token Detail Penjualan",
    "Nomor Seri e-Faktur",
    "Alasan Retur",
    "Sifat Transaksi",
]


class LK000120InvoiceNormalizer(BaseNormalizer):

    # ==========================================================
    # CARI HEADER
    # ==========================================================

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = [
                str(v).strip()
                for v in row.tolist()
                if pd.notna(v)
            ]

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 40:
                return idx

        raise ValueError(
            "Header invoice LK-000120 tidak ditemukan"
        )

    # ==========================================================
    # HEADER UNTUK MAPPING
    # ==========================================================

    def get_mapping_headers(self, filepath):

        preview = pd.read_excel(
            filepath,
            header=None
        )

        header_row = self.find_header_row(preview)

        raw = pd.read_excel(
            filepath,
            header=None
        )

        headers = [
            str(v).strip()
            for v in raw.iloc[header_row].tolist()
            if pd.notna(v)
        ]

        return headers

    # ==========================================================
    # NORMALIZE
    # ==========================================================

    def normalize(self, filepath):

        print("\n==============================")
        print("NORMALIZE INVOICE LK-000120")
        print("==============================")

        # ======================================================
        # 1. BACA FILE TANPA HEADER
        # ======================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        header_row = self.find_header_row(preview)

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
        )

        # ======================================================
        # 2. BACA DATA
        # ======================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # ======================================================
        # 3. CLEAN HEADER
        # ======================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # ======================================================
        # 4. HAPUS KOLOM UNNAMED
        # ======================================================

        df = df.loc[
            :,
            ~df.columns.str.startswith("Unnamed:")
        ]

        # ======================================================
        # 5. VALIDASI HEADER
        # ======================================================

        missing_headers = [
            header
            for header in EXPECTED_HEADERS
            if header not in df.columns
        ]

        if missing_headers:
            print("\nHEADER YANG TIDAK DITEMUKAN:")

            for header in missing_headers:
                print("-", header)

            raise ValueError(
                "Header invoice LK-000120 tidak lengkap"
            )

        # ======================================================
        # 6. HAPUS BARIS KOSONG
        # ======================================================

        df = df.dropna(
            how="all"
        )

        # ======================================================
        # 7. KOLOM STRING
        # ======================================================

        string_columns = [
            "Scope Cabang",
            "Provinsi",
            "Kab/ Kota",
            "Zona",
            "Kode Customer",
            "Nama Customer",
            "List Customer",
            "Alamat Customer",
            "Kode Kecamatan",
            "Nama Kecamatan",
            "Contact Person",
            "Telf Customer",
            "No. HP Customer",
            "Tipe Customer",
            "Kategori Customer",
            "Kode Salesman",
            "Token Faktur",
            "No. Faktur",
            "Kode Barang",
            "Nama Barang",
            "Satuan Faktur",
            "Satuan Terbesar",
            "Satuan Terkecil",
            "Bonus?",
            "Direktori",
            "Supplier",
            "Jenis Barang",
            "Kategori Barang",
            "Merk Barang",
            "Sifat Barang",
            "Keterangan",
            "Kode Customer Lama",
            "Token Detail Penjualan",
            "Nomor Seri e-Faktur",
            "Alasan Retur",
            "Sifat Transaksi",
        ]

        for column in string_columns:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.replace(
                        r"\.0$",
                        "",
                        regex=True
                    )
                )

        # ======================================================
        # 8. KOLOM NUMERIC
        # ======================================================

        numeric_columns = [
            "No",
            "TOP",
            "Limit Piutang",
            "Limit Nota",
            "QTY Faktur",
            "QTY Terbesar",
            "QTY Terkecil",
            "Harga Faktur",
            "Harga Sebelum Pot.",
            "Disc. 1",
            "Disc. 2",
            "Disc. 3",
            "Disc. 4",
            "Disc. Value",
            "Pot. Harga",
            "Subtotal Faktur",
            "DPP",
            "PPN%",
            "Nilai PPN",
            "Nilai Faktur",
            "Volume Satuan",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # ======================================================
        # 9. TANGGAL
        # ======================================================

        date_columns = [
            "TMT Aktif",
            "Tgl Faktur",
            "Tgl Jatuh Tempo",
        ]

        for column in date_columns:

            if column in df.columns:

                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

        # ======================================================
        # 10. FILTER DATA VALID
        # ======================================================

        if "Kode Barang" in df.columns:

            df = df[
                df["Kode Barang"]
                .fillna("")
                .astype(str)
                .str.strip()
                != ""
            ]

        # ======================================================
        # 11. RESET INDEX
        # ======================================================

        df = df.reset_index(
            drop=True
        )

        # ======================================================
        # 12. BUAT NO BARU
        # ======================================================

        if "No" in df.columns:

            df = df.drop(
                columns=["No"]
            )

        df.insert(
            0,
            "No",
            range(
                1,
                len(df) + 1
            )
        )

        # ======================================================
        # 13. DEBUG
        # ======================================================

        print("\n==============================")
        print("HASIL NORMALISASI")
        print("==============================")

        print(
            df.head(10).to_string()
        )

        print(
            "\nJumlah data:",
            len(df)
        )

        print(
            "\nJumlah kolom:",
            len(df.columns)
        )

        print(
            "\nKolom:"
        )

        print(
            df.columns.tolist()
        )

        print("\n==============================")
        print("NORMALIZE SELESAI")
        print("==============================")

        return df