from services.normalize.base import BaseNormalizer


class LK000092InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Pastikan itemid menjadi string
        df["itemid"] = (
            df["itemid"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
        )

        # Tambahkan 0 di depan jika belum ada
        df["itemid"] = df["itemid"].apply(
            lambda x: x if x.startswith("0") else "0" + x
        )

        return df