import pandas as pd
from services.normalize.base import BaseNormalizer


class LK000130InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Ubah Tgl Faktur menjadi DATE
        if "Tgl Faktur" in df.columns:

            bulan_map = {
                "Jan": "Jan",
                "Feb": "Feb",
                "Mar": "Mar",
                "Apr": "Apr",
                "Mei": "May",
                "Jun": "Jun",
                "Jul": "Jul",
                "Agu": "Aug",
                "Sep": "Sep",
                "Okt": "Oct",
                "Nov": "Nov",
                "Des": "Dec",
            }

            df["Tgl Faktur"] = (
                df["Tgl Faktur"]
                .astype(str)
                .str.strip()
            )

            for indo, eng in bulan_map.items():
                df["Tgl Faktur"] = df["Tgl Faktur"].str.replace(
                    f" {indo} ",
                    f" {eng} ",
                    regex=False
                )

            df["Tgl Faktur"] = pd.to_datetime(
                df["Tgl Faktur"],
                errors="coerce"
            ).dt.date

        return df