from services.normalize.base import BaseNormalizer

class LK000115StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel(filepath)

        header_row = None

        for i, row in df.iterrows():

            values = row.astype(str).str.strip().tolist()

            if "NAMABARANG" in values:

                header_row = i
                break

        if header_row is None:
            raise Exception("Header tidak ditemukan")

        # Jadikan baris header sebagai nama kolom
        df.columns = (
            df.iloc[header_row]
            .astype(str)
            .str.strip()
        )

        # Ambil data setelah header
        df = df.iloc[header_row + 1:].reset_index(drop=True)

        # Hapus baris yang seluruh kolomnya kosong
        df = df.dropna(how="all").reset_index(drop=True)
        
        # Hapus baris kosong
        df = df.dropna(how="all")

        # Hapus baris total
        df = df[df["NAMABARANG"].notna()]

        return df