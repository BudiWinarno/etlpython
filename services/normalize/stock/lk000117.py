import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "Divisi",
    "Product Grup Level 3",
    "Product Code",
    "Product Name",
    "Total Stock (Pcs)"
]


class LK000117StockNormalizer(BaseNormalizer):

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

        raise Exception("Header stock LK-000117 tidak ditemukan")

    def normalize(self, filepath):

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris Subtotal
        df = df[
            df["Product Code"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("Subtotal")
        ]

        # Hapus baris End of Report
        df = df[
            ~df.iloc[:, 0]
            .fillna("")
            .astype(str)
            .str.contains("End of Report", case=False, na=False)
        ]

        df = df.reset_index(drop=True)

        df = self.to_string(df, "Product Code")

        return df