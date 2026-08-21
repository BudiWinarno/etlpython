from services.normalize.base import BaseNormalizer
import pandas as pd
from datetime import datetime


class LK000167InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # =====================================================
        # NORMALIZE TANGGAL
        # =====================================================

        date_columns = [
            "Tanggal",
            "Tanggal Invoice",
            "Invoice Date",
            "Tgl Invoice",
            "Tgl FJ",
            "Tgl Ref",
        ]

        for column in date_columns:

            if column not in df.columns:
                continue

            def normalize_date(value):

                # ---------------------------------------------
                # NULL
                # ---------------------------------------------

                if pd.isna(value):
                    return None

                # ---------------------------------------------
                # Excel serial number
                # Contoh: 46233
                # ---------------------------------------------

                if isinstance(
                    value,
                    (int, float)
                ):

                    return (
                        pd.Timestamp(
                            "1899-12-30"
                        )
                        + pd.to_timedelta(
                            value,
                            unit="D"
                        )
                    ).date()

                # ---------------------------------------------
                # Sudah datetime
                # ---------------------------------------------

                if isinstance(
                    value,
                    (datetime, pd.Timestamp)
                ):

                    return value.date()

                # ---------------------------------------------
                # String / nilai lainnya
                # ---------------------------------------------

                value = str(value).strip()

                if not value:
                    return None

                # Kalau string berupa Excel serial
                try:

                    numeric_value = float(value)

                    return (
                        pd.Timestamp(
                            "1899-12-30"
                        )
                        + pd.to_timedelta(
                            numeric_value,
                            unit="D"
                        )
                    ).date()

                except ValueError:
                    pass

                # ---------------------------------------------
                # String tanggal
                # ---------------------------------------------

                parsed = pd.to_datetime(
                    value,
                    errors="coerce",
                    dayfirst=False
                )

                if pd.isna(parsed):
                    return None

                return parsed.date()

            df[column] = df[column].apply(
                normalize_date
            )

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(self, filepath):

        df = self.normalize(filepath)

        return df.columns.tolist()