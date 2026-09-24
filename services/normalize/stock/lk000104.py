import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "No. Barang",
    "Deskripsi Barang",
    "Kts. Stok",
    "Unit 1",
    "Kts dalam Unit 2",
    "Kts dalam Unit 3",
]


class LK000104StockNormalizer(BaseNormalizer):

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

            # Minimal 4 header cocok
            if match >= 4:
                return idx

        raise Exception(
            "Header stock LK-000104 tidak ditemukan"
        )

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

        print(
            f"Header LK-000104 Stock ditemukan di baris: "
            f"{header_row}"
        )

        # =====================================================
        # 3. Baca ulang dengan header yang ditemukan
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
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
        )

        # =====================================================
        # 5. Hapus kolom Unnamed
        # =====================================================
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =====================================================
        # 6. Validasi header
        # =====================================================
        missing_columns = [
            column
            for column in EXPECTED_HEADERS
            if column not in df.columns
        ]

        if missing_columns:
            raise Exception(
                "Header stock LK-000104 tidak lengkap: "
                f"{missing_columns}"
            )

        # =====================================================
        # 7. Hapus baris kosong
        # =====================================================
        df = (
            df
            .replace(
                r"^\s*$",
                pd.NA,
                regex=True
            )
            .dropna(how="all")
        )

        # =====================================================
        # 8. Hapus subtotal / total / footer
        # =====================================================
        mask_total = pd.Series(
            False,
            index=df.index
        )

        text_columns = [
            "No. Barang",
            "Deskripsi Barang",
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
        # 9. Kolom string
        # =====================================================
        string_columns = [
            "No. Barang",
            "Deskripsi Barang",
            "Unit 1",
            "Kts dalam Unit 2",
            "Kts dalam Unit 3",
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
        # 10. Kts. Stok menjadi numeric
        # =====================================================
        if "Kts. Stok" in df.columns:

            df["Kts. Stok"] = pd.to_numeric(
                df["Kts. Stok"],
                errors="coerce"
            ).fillna(0)

        # =====================================================
        # 11. Hanya ambil barang yang memiliki kode
        # =====================================================
        df = df[
            df["No. Barang"] != ""
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
            "No. Barang",
            "Deskripsi Barang",
            "Kts. Stok",
            "Unit 1",
            "Kts dalam Unit 2",
            "Kts dalam Unit 3",
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
        print(
            "\n=== LK-000104 STOCK NORMALIZER ==="
        )
        print(
            f"Header row : {header_row}"
        )
        print(
            f"Jumlah data: {len(df)}"
        )
        print(
            "Columns:"
        )
        print(
            df.columns.tolist()
        )

        print("\nPreview:")
        print(df.head())

        return df