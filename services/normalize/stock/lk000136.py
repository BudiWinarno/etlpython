import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "S098",
    "PT JOENOES IKAMULYA",
]


class LK000136StockNormalizer(BaseNormalizer):

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = [
                str(v).strip()
                for v in row.fillna("").tolist()
            ]

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match == len(EXPECTED_HEADERS):
                return idx

        raise Exception("Header stock S098 tidak ditemukan")

    def normalize(self, filepath):
        
        # =====================================
        # Kalau file sudah hasil normalisasi
        # =====================================
        check_df = pd.read_excel(filepath)

        expected = ["kode_barang", "nama_barang", "qty_pcs"]

        if all(col in check_df.columns for col in expected):
            check_df = self.to_string(check_df, "kode_barang")
            return check_df
    

        # Preview untuk mencari baris judul
        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        # Baca ulang TANPA header
        df = pd.read_excel(
            filepath,
            header=None
        )

        # Lewati baris judul
        df = df.iloc[header_row + 1:].reset_index(drop=True)

        # Ambil hanya 4 kolom pertama
        df = df.iloc[:, :4]

        # Rename
        df.columns = [
            "kode_barang",
            "nama_barang",
            "satuan",
            "qty_pcs"
        ]
        
        # Nilai kosong pada qty_pcs menjadi 0
        df["qty_pcs"] = (
            pd.to_numeric(df["qty_pcs"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        # Hapus kolom PCS.PCS.PCS
        df = df.drop(columns=["satuan"])

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris yang kode barang kosong
        df = df[df["kode_barang"].notna()]

        df = df.reset_index(drop=True)

        df = self.to_string(df, "kode_barang")

        return df