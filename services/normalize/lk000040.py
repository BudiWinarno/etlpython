import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000040InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):
        df = self.read_excel_with_header(filepath)

        # Ganti nama kolom setelah KODE_C menjadi NAMABARANG
        cols = list(df.columns)
        if "KODE_C" in cols:
            idx = cols.index("KODE_C")
            if idx + 1 < len(cols):
                cols[idx + 1] = "NAMABARANG"
        df.columns = cols

        # Perbaiki kolom tanggal
        if "TANGGAL" in df.columns:

            def parse_tanggal(value):
                if pd.isna(value):
                    return pd.NaT

                value = str(value).strip()

                # Format YYYYMMDD
                if value.isdigit() and len(value) == 8:
                    return pd.to_datetime(
                        value,
                        format="%Y%m%d",
                        errors="coerce"
                    )

                # Format DD/MM/YYYY
                return pd.to_datetime(
                    value,
                    format="%d/%m/%Y",
                    errors="coerce"
                )

            df["TANGGAL"] = df["TANGGAL"].apply(parse_tanggal)

        return df