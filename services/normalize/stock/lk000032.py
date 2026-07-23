import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "Divisi",
    "Product Grup Level 3",
    "Product Code",
    "Product Name",
    "Packaging",
    "Stock",
    "Stock (pcs)",
    "Tonnage",
    "Volume",
    "Stock Uom1",
    "Stock Uom2",
    "Stock Uom3",
    "Stock Uom4",
    "On SalesOrder",
    "On PFI",
    "Available",
    "Value@Selling",
]


class LK000032StockNormalizer(BaseNormalizer):

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

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris REPORT TOTAL dan End of Report
        df = df[
            ~df.astype(str)
            .apply(
                lambda row: row.str.upper().str.contains(
                    r"REPORT TOTAL|END OF REPORT",
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