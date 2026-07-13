import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "Kode Brg",
    "Nama Brg",
    "Sat Std",
    "Saldo Awal",
    "Saldo Akhir"
]


class LK000148StockNormalizer(BaseNormalizer):

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

        raise Exception("Header stock LK-000148 tidak ditemukan")

    def normalize(self, filepath):

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        df = df.dropna(how="all")

        df = df.reset_index(drop=True)

        df = self.to_string(df, "Kode Brg")

        return df