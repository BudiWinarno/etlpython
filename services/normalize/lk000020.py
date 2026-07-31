from services.normalize.base import BaseNormalizer


class LK000020InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel(filepath)

        header_row = None

        # Cari baris header
        for i, row in df.iterrows():

            values = (
                row.fillna("")
                   .astype(str)
                   .str.strip()
                   .tolist()
            )

            if "No" in values and "Tanggal" in values:
                header_row = i
                break

        if header_row is None:
            raise Exception("Header tidak ditemukan")

        # Jadikan baris header sebagai nama kolom
        df.columns = (
            df.iloc[header_row]
              .fillna("")
              .astype(str)
              .str.strip()
        )

        # Ambil data setelah header
        df = df.iloc[header_row + 1:].reset_index(drop=True)

        # Hapus kolom kosong akibat merge cell
        df = df.loc[:, df.columns != ""]

        # Ganti string kosong menjadi None
        df = df.replace(r'^\s*$', None, regex=True)

        # Hapus baris yang benar-benar kosong
        df = df.dropna(how="all")

        # Hapus baris yang kolom "No"-nya kosong
        if "No" in df.columns:
            df = df[df["No"].notna()]
            df = df[df["No"].astype(str).str.strip() != ""]

        # Reset index
        df = df.reset_index(drop=True)

        return df