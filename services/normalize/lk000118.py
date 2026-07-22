import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000118InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel(filepath)

        header_row = None

        for i, row in df.iterrows():

            values = [str(x).strip().lower() for x in row.tolist()]

            if (
                "invoice" in values
                and "custid" in values
                and "itemid" in values
            ):
                header_row = i
                break

        if header_row is None:
            raise Exception("Header LK-000118 tidak ditemukan")

        # Jadikan baris header sebagai nama kolom
        df.columns = df.iloc[header_row]

        # Ambil data setelah header
        df = (
            df.iloc[header_row + 1:]
            .reset_index(drop=True)
        )

        # Rapikan nama kolom
        df.columns = (
            df.columns.astype(str)
            .str.strip()
        )

        # ==========================
        # Konversi tipe data
        # ==========================

        # Kolom tanggal menjadi date
        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(
                df["tanggal"],
                errors="coerce"
            ).dt.date

        # Kolom itemid menjadi string
        if "itemid" in df.columns:
            df["itemid"] = (
                df["itemid"]
                .fillna("")
                .astype(str)
                .str.replace(".0", "", regex=False)
                .str.strip()
            )

        # ==========================
        # Bersihkan data
        # ==========================

        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris total (invoice kosong)
        if "invoice" in df.columns:
            df = (
                df[
                    df["invoice"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    != ""
                ]
                .reset_index(drop=True)
            )

        return df