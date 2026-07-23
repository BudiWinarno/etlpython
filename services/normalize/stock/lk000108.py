import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "Branch",
    "Divisi",
    "Product Grup Level 3",
    "Product Code",
    "Product Name",
    "Packaging",
    "Unit of Measure",
    "UOM Conversion",
    "Stock",
    "Stock (Pcs)",
    "Value @Selling",
    "StockBS",
    "StockBS (Pcs)",
    "ValueBS @Selling",
    "Unit Cost",
]


class LK000108StockNormalizer(BaseNormalizer):

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

            # Minimal 6 kolom cocok dianggap header
            if match >= 6:
                return idx

        raise Exception("Header stock tidak ditemukan")

    def normalize(self, filepath):

        # Baca tanpa header
        preview = self.read_excel(filepath)

        # Cari posisi header
        header_row = self.find_header_row(preview)

        # Baca ulang menggunakan header yang ditemukan
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Ganti kolom Unnamed menjadi Kode Produk
        df.columns = [
            "Kode Produk" if str(col).startswith("Unnamed") else col
            for col in df.columns
        ]

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris subtotal / total / footer
        df = df[
            ~df.astype(str)
            .apply(
                lambda row: row.str.upper().str.contains(
                    r"SUBTOTAL LAIN-LAIN|REPORT TOTAL|END OF REPORT",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]

        # Reset index
        df = df.reset_index(drop=True)

        # Ubah Product Code menjadi string
        df = self.to_string(df, "Product Code")

        return df