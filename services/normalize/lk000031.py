from services.normalize.base import BaseNormalizer


class LK000031InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        if "QTY_BRG" in df.columns:
            df["QTY_BRG"] = (
                df["QTY_BRG"]
                .apply(lambda x: int(float(x) + 0.5) if x is not None else x)
            )

        return df