import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "KodeSupplier",
    "Supplier",
    "KodeBarang",
    "NamaBarang",
    "StockPcs"
]


class LK000019StockNormalizer(BaseNormalizer):

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = row.fillna("").astype(str).tolist()

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 4:
                return idx

        raise Exception("Header stock tidak ditemukan")

    def normalize(self, filepath):

        # baca excel tanpa header
        preview = self.read_excel(filepath)

        # cari posisi header
        header_row = self.find_header_row(preview)

        # baca ulang menggunakan header yang ditemukan
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # hapus baris kosong
        df = df.dropna(how="all")

        # reset index
        df = df.reset_index(drop=True)

        # ubah kode menjadi string
        df = self.to_string(df, "KodeBarang")
        df = self.to_string(df, "KodeSupplier")
        df = self.to_string(df, "KodeGudang")

        return df