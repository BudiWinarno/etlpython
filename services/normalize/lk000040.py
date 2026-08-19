import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000040InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):
        df = pd.read_excel(
            filepath,
            dtype={"TANGGAL": object}
        )

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

                # Kalau sudah datetime
                if isinstance(value, pd.Timestamp):
                    return pd.Timestamp(
                        year=value.year,
                        month=value.day,
                        day=value.month
                    )

                value = str(value).strip()

                if not value:
                    return pd.NaT

                # Format YYYYMMDD
                if value.isdigit() and len(value) == 8:
                    return pd.to_datetime(
                        value,
                        format="%Y%m%d",
                        errors="coerce"
                    )

                # Format MM/DD/YYYY
                result = pd.to_datetime(
                    value,
                    format="%m/%d/%Y",
                    errors="coerce"
                )

                if pd.notna(result):
                    return result

                # Format YYYY-MM-DD
                result = pd.to_datetime(
                    value,
                    format="%Y-%m-%d",
                    errors="coerce"
                )

                if pd.notna(result):
                    return result

                # Fallback
                return pd.to_datetime(
                    value,
                    errors="coerce"
                )

            df["TANGGAL"] = df["TANGGAL"].apply(parse_tanggal)

        return df