from services.normalize.base import BaseNormalizer


class LK000101InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Buang baris terakhir (total/footer)
        df = df.iloc[:-1].copy()

        # Pastikan itemid menjadi string
        df["itemid"] = (
            df["itemid"]
            .fillna("")
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )

        # Tambahkan 0 di depan
        df["itemid"] = df["itemid"].apply(
            lambda x: "0" + x if x and not x.startswith("0") else x
        )

        return df