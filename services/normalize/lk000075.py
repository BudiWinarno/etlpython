from services.normalize.base import BaseNormalizer
import pandas as pd
from datetime import datetime


class LK000075Normalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        def parse_tanggal(x):

            if pd.isna(x):
                return None

            # Kalau sudah datetime, biarkan
            if isinstance(x, (pd.Timestamp, datetime)):
                return x

            # Kalau string, ubah ke datetime
            return pd.to_datetime(
                str(x).strip(),
                dayfirst=True,
                errors="coerce"
            )

        if "tanggal" in df.columns:
            df["tanggal"] = df["tanggal"].apply(parse_tanggal)

        return df