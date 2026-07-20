import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "com_id",
    "groupcompanyname",
    "tgl",
    "ware_id",
    "principle_id",
    "principle_name",
    "divisi_id",
    "divisi_name",
    "item_id",
    "item_name",
    "stok_ctn",
    "stok_pcs",
    "end_value",
    "konversi",
    "STOK TOTAL"
]


class LK000093StockNormalizer(BaseNormalizer):

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = row.fillna("").astype(str).tolist()

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 8:
                return idx

        raise Exception("Header stock tidak ditemukan")

    def normalize(self, filepath):

        # Preview tanpa header
        preview = self.read_excel(filepath)

        # Cari posisi header
        header_row = self.find_header_row(preview)

        # Baca ulang
        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Reset index
        df = df.reset_index(drop=True)

        # Ubah kode menjadi string
        df = self.to_string(df, "item_id")
        df = self.to_string(df, "com_id")
        df = self.to_string(df, "ware_id")
        df = self.to_string(df, "principle_id")
        df = self.to_string(df, "divisi_id")

        # Pastikan kolom numerik
        df["stok_ctn"] = pd.to_numeric(df["stok_ctn"], errors="coerce").fillna(0)
        df["stok_pcs"] = pd.to_numeric(df["stok_pcs"], errors="coerce").fillna(0)
        df["konversi"] = pd.to_numeric(df["konversi"], errors="coerce").fillna(0)

        # Hitung Total Qty (PCS)
        df["total_qty"] = (
            df["stok_ctn"] * df["konversi"]
        ) + df["stok_pcs"]

        return df