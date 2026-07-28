import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "No",
    "Kode SKU Agen",
    "Kode SKU JIM",
    "Nama SKU JIM",
    "Isi/Carton",
    "QTY Carton",
]


class LK000021StockNormalizer(BaseNormalizer):

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

            # Minimal 4 kolom cocok dianggap header
            if match >= 4:
                return idx

        raise Exception("Header stock tidak ditemukan")

    def normalize(self, filepath):

        # Preview tanpa header
        preview = self.read_excel(filepath)

        # Cari posisi header
        header_row = self.find_header_row(preview)

        # Baca ulang menggunakan header yang ditemukan
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Rapikan nama kolom
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.replace(r"\s*/\s*", "/", regex=True)
            .str.replace(r"\s+", " ", regex=True)
        )

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris Total
        df = df[
            ~df.astype(str)
            .apply(
                lambda row: row.str.upper().str.contains(
                    r"TOTAL",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]

        # Reset index
        df = df.reset_index(drop=True)

        # Pastikan kolom numerik
        df["Isi/Carton"] = pd.to_numeric(
            df["Isi/Carton"],
            errors="coerce"
        )

        df["QTY Carton"] = pd.to_numeric(
            df["QTY Carton"],
            errors="coerce"
        )

        # Tambah qty_pcs
        df["qty_pcs"] = (
            df["Isi/Carton"].fillna(0)
            * df["QTY Carton"].fillna(0)
        )

        # Hapus baris terakhir (summary)
        df = df.iloc[:-1]

        # Reset index
        df = df.reset_index(drop=True)

        # Nomor urut
        df["No"] = range(1, len(df) + 1)

        return df