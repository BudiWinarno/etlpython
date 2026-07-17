import pandas as pd

from services.normalize.base import BaseNormalizer


EXPECTED_HEADERS = [
    "No. Barang",
    "Deskripsi Barang",
    "KIMA",
    "Unit 1",
    "Rasio 2",
    "Karton MT"
]


class LK000065StockNormalizer(BaseNormalizer):

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = (
                row.fillna("")
                .astype(str)
                .str.strip()
                .tolist()
            )

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 5:
                return idx

        raise Exception("Header stock LK-000065 tidak ditemukan")

    def normalize(self, filepath):

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Hapus baris kosong
        df = df.dropna(how="all").reset_index(drop=True)

        # Hapus baris yang bukan data
        df = df[
            df["No. Barang"].notna()
        ].reset_index(drop=True)

        # Pastikan kode barang bertipe string
        df = self.to_string(df, "No. Barang")

        return df