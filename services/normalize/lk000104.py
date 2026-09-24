import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "No. Faktur",
    "Tgl Faktur",
    "No. Pelanggan",
    "Nama Pelanggan",
    "Alamat 1 Pelanggan",
    "Nama Penjual",
    "No. Barang",
    "Keterangan Barang",
    "Nama Kategori Barang Barang",
    "Kuantitas",
    "Unit 1 barang",
    "% Diskon",
    "Jumlah",
    "Net+Ppn",
]


class LK000104InvoiceNormalizer(BaseNormalizer):

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

            match = len(values.intersection(expected_headers))

            # Minimal 8 header cocok
            if match >= 8:
                return idx

        raise Exception("Header invoice LK-000104 tidak ditemukan")

    def normalize(self, filepath):

        # =====================================================
        # 1. Baca preview tanpa header
        # =====================================================
        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. Cari posisi header
        # =====================================================
        header_row = self.find_header_row(preview)

        print(f"Header LK-000104 ditemukan di baris: {header_row}")

        # =====================================================
        # 3. Baca ulang menggunakan header
        # =====================================================
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. Bersihkan nama kolom
        # =====================================================
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        # Hapus kolom Unnamed
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =====================================================
        # 5. Validasi header
        # =====================================================
        missing_columns = [
            column
            for column in EXPECTED_HEADERS
            if column not in df.columns
        ]

        if missing_columns:
            raise Exception(
                f"Header invoice LK-000104 tidak lengkap: "
                f"{missing_columns}"
            )

        # =====================================================
        # 6. Hapus baris kosong
        # =====================================================
        df = (
            df
            .replace(r"^\s*$", pd.NA, regex=True)
            .dropna(how="all")
        )

        # =====================================================
        # 7. Hapus subtotal / total / footer
        # =====================================================
        mask_total = pd.Series(
            False,
            index=df.index
        )

        text_columns = [
            "No. Faktur",
            "No. Pelanggan",
            "Nama Pelanggan",
            "No. Barang",
            "Keterangan Barang",
        ]

        for column in text_columns:

            if column in df.columns:

                mask_total = (
                    mask_total
                    |
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .str.contains(
                        r"SUBTOTAL|TOTAL|END OF REPORT|REPORT TOTAL",
                        regex=True,
                        na=False
                    )
                )

        df = df[~mask_total]

        # =====================================================
        # 8. Kolom string
        # =====================================================
        string_columns = [
            "No. Faktur",
            "No. Pelanggan",
            "Nama Pelanggan",
            "Alamat 1 Pelanggan",
            "Nama Penjual",
            "No. Barang",
            "Keterangan Barang",
            "Nama Kategori Barang Barang",
            "Unit 1 barang",
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

        # =====================================================
        # 9. Kolom numeric
        # =====================================================
        numeric_columns = [
            "Kuantitas",
            "% Diskon",
            "Jumlah",
            "Net+Ppn",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # =====================================================
        # 10. Tanggal
        # =====================================================
        if "Tgl Faktur" in df.columns:

            bulan_map = {
                "Jan": "Jan",
                "Feb": "Feb",
                "Mar": "Mar",
                "Apr": "Apr",
                "Mei": "May",
                "Jun": "Jun",
                "Jul": "Jul",
                "Agu": "Aug",
                "Sep": "Sep",
                "Okt": "Oct",
                "Nov": "Nov",
                "Des": "Dec",
            }

            df["Tgl Faktur"] = (
                df["Tgl Faktur"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            for indo, eng in bulan_map.items():

                df["Tgl Faktur"] = df[
                    "Tgl Faktur"
                ].str.replace(
                    f" {indo} ",
                    f" {eng} ",
                    regex=False
                )

            df["Tgl Faktur"] = (
                pd.to_datetime(
                    df["Tgl Faktur"],
                    errors="coerce"
                )
                .dt.date
            )

        # =====================================================
        # 11. Hanya ambil transaksi yang memiliki barang
        # =====================================================
        df = df[
            (df["No. Barang"] != "")
            &
            (df["Keterangan Barang"] != "")
        ]

        # =====================================================
        # 12. Reset index
        # =====================================================
        df = df.reset_index(drop=True)

        # =====================================================
        # 13. Tambahkan nomor urut
        # =====================================================
        if "No" in df.columns:
            df = df.drop(columns=["No"])

        df.insert(
            0,
            "No",
            range(1, len(df) + 1)
        )

        # =====================================================
        # 14. Final columns
        # =====================================================
        final_columns = [
            "No",
            "No. Faktur",
            "Tgl Faktur",
            "No. Pelanggan",
            "Nama Pelanggan",
            "Alamat 1 Pelanggan",
            "Nama Penjual",
            "No. Barang",
            "Keterangan Barang",
            "Nama Kategori Barang Barang",
            "Kuantitas",
            "Unit 1 barang",
            "% Diskon",
            "Jumlah",
            "Net+Ppn",
        ]

        df = df[
            [
                column
                for column in final_columns
                if column in df.columns
            ]
        ]

        # =====================================================
        # 15. Debug
        # =====================================================
        print("\n=== LK-000104 INVOICE NORMALIZER ===")
        print(f"Header row : {header_row}")
        print(f"Jumlah data: {len(df)}")
        print("Columns:")
        print(df.columns.tolist())

        print("\nPreview:")
        print(df.head())

        return df