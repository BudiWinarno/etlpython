import pandas as pd

from services.normalize.base import BaseNormalizer

EXPECTED_HEADERS = [
    "Kode_Sales",
    "Nama_Sales",
    "Kode_Customer",
    "Nama_Customer",
    "Nama_Kategori",
    "Satuan_Netto",
    "Kode_Barang",
    "Nama_Barang",
    "Tgl",
    "Qty_Jual",
    "Qty_Extra",
    "Harga_Jual",
    "Nilai_Jual",
    "PPN_Jual",
    "Netto_Jual",
    "Qty_Retur",
    "Harga_Retur",
    "Nilai_Retur",
    "PPN_Retur",
    "Netto_Retur",
    "Sales_Luar",
    "No_Trans",
    "Nama_Area",
    "Nama_Segment",
    "Qty_Pcs",
    "Harga_Pcs",
    "no_so",
    "id_pelanggan",
    "id_lot",
    "exp_date",
    "No_Manual",
    "No_DO",
    "Tgl_JT"
]


class LK000048InvoiceNormalizer(BaseNormalizer):

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

        raise Exception("Header invoice LK-000048 tidak ditemukan")

    def normalize(self, filepath):

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        df = df.dropna(how="all")
        df = df.reset_index(drop=True)
        
        # Hapus baris total
        df = df[
            df["Kode_Sales"].notna() &
            df["Kode_Barang"].notna()
        ].reset_index(drop=True)

        # Kolom yang harus tetap string
        string_columns = [
            "Kode_Barang",
            "Kode_Customer",
            "Kode_Sales",
            "No_Trans",
            "No_DO",
            "No_Manual",
            "no_so",
            "id_pelanggan",
            "id_lot"
        ]

        for col in string_columns:
            if col in df.columns:
                df = self.to_string(df, col)

        return df