import pandas as pd
from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "No. Barang",
    "Deskripsi Barang",
    "GT YURI",
    "Unit 1",
    "Rasio 2",
    "Karton GT",
]


class LK000130StockNormalizer(BaseNormalizer):

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

            if match >= 5:
                return idx

        raise Exception(
            "Header stock LK-000130 tidak ditemukan"
        )

    def normalize(self, filepath):

        print("\n==============================")
        print("NORMALIZE STOCK LK-000130")
        print("==============================")

        # Baca tanpa header
        preview = pd.read_excel(
            filepath,
            header=None
        )

        # Cari header berdasarkan isi
        header_row = self.find_header_row(preview)

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
        )

        # Baca ulang dengan header yang benar
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Bersihkan nama kolom
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

        # Validasi
        missing_columns = [
            column
            for column in EXPECTED_HEADERS
            if column not in df.columns
        ]

        if missing_columns:
            raise Exception(
                f"Header stock LK-000130 tidak lengkap: "
                f"{missing_columns}"
            )

        # Hapus kolom Unnamed
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # Hapus baris kosong
        df = df.dropna(how="all")

        # ==============================
        # KOLOM STRING
        # ==============================

        string_columns = [
            "No. Barang",
            "Deskripsi Barang",
            "Unit 1",
        ]

        for column in string_columns:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        # ==============================
        # KOLOM NUMERIC
        # ==============================

        numeric_columns = [
            "GT YURI",
            "Rasio 2",
            "Karton GT",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # ==============================
        # FILTER DATA
        # ==============================

        df = df[
            df["No. Barang"]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        ]

        # ==============================
        # RESET NO
        # ==============================

        df = df.reset_index(drop=True)

        if "No" in df.columns:
            df = df.drop(columns=["No"])

        df.insert(
            0,
            "No",
            range(1, len(df) + 1)
        )

        # ==============================
        # URUTAN KOLOM
        # ==============================

        df = df[
            [
                "No",
                "No. Barang",
                "Deskripsi Barang",
                "GT YURI",
                "Unit 1",
                "Rasio 2",
                "Karton GT",
            ]
        ]

        print("\nHASIL NORMALISASI")
        print(df.head(10).to_string())

        print("\nJumlah data:", len(df))
        print("\nKolom:", df.columns.tolist())

        print("\n==============================")
        print("NORMALIZE SELESAI")
        print("==============================")

        return df