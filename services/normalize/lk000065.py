import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000065InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

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
                "Des": "Dec"
            }

            df["Tgl Faktur"] = (
                df["Tgl Faktur"]
                .astype(str)
                .replace(bulan_map, regex=True)
            )

            df["Tgl Faktur"] = pd.to_datetime(
                df["Tgl Faktur"],
                format="%d %b %Y",
                errors="coerce"
            )

            # Hapus baris footer / TOTAL
            df = df[df["Tgl Faktur"].notna()].reset_index(drop=True)

            df["Tgl Faktur"] = df["Tgl Faktur"].dt.date

        return df