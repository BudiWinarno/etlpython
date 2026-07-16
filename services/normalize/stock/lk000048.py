import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "Kode_Kategori",
    "Nama_Kategori",
    "Kode_Barang",
    "Nama_Barang",
    "Qty",
    "Satuan",
    "Qty2",
    "Satuan2",
    "Jumlah",
    "Harga",
    "Nilai"
]


class LK000048StockNormalizer(BaseNormalizer):

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = row.fillna("").astype(str).tolist()

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 5:
                return idx

        raise Exception("Header stock LK-000048 tidak ditemukan")

    def normalize(self, filepath):

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Hapus baris kosong
        df = df.dropna(how="all")
        df = df.reset_index(drop=True)

        # Hapus baris yang bukan data
        df = df[
            df["Kode_Barang"].notna()
        ].reset_index(drop=True)

        # Kolom yang harus tetap string
        string_columns = [
            "Kode_Kategori",
            "Kode_Barang"
        ]

        for col in string_columns:
            if col in df.columns:
                df = self.to_string(df, col)

        return df