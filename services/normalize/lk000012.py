from services.normalize.base import BaseNormalizer
import pandas as pd
from pandas.api.types import is_numeric_dtype


class LK000012InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # ==========================================
        # NORMALISASI TANGGAL INVOICE
        # ==========================================
        if "Invoice Date" in df.columns:

            if is_numeric_dtype(df["Invoice Date"]):
                # Jika masih berupa serial Excel
                df["Invoice Date"] = pd.to_datetime(
                    df["Invoice Date"],
                    unit="D",
                    origin="1899-12-30",
                    errors="coerce"
                )
            else:
                # Jika sudah berupa datetime atau string tanggal
                df["Invoice Date"] = pd.to_datetime(
                    df["Invoice Date"],
                    errors="coerce"
                )

            # Hanya simpan tanggal
            df["Invoice Date"] = df["Invoice Date"].dt.date

        # ==========================================
        # NORMALISASI KOLOM NUMERIC
        # ==========================================
        numeric_columns = [
            "Customer#",
            "Product Code",
            "Qty (Pcs)",
            "Price",
            "Gross Amount",
            "LineDisc1",
            "LineDisc2",
            "LineDisc3",
            "LineDisc4",
            "LineDisc5",
            "LD Amount",
            "%Disc1",
            "%Disc2",
            "%Disc3",
            "Discount",
            "DPP",
            "Tax",
            "Net Amount"
        ]

        for column in numeric_columns:

            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        # ==========================================
        # NORMALISASI QUANTITY
        # ==========================================
        if "Quantity" in df.columns:

            def parse_quantity(value):

                if pd.isna(value):
                    return pd.Series({
                        "Karton": 0,
                        "Box": 0,
                        "Pcs": 0
                    })

                value = str(value).strip()

                parts = value.split(".")

                if len(parts) == 3:

                    try:
                        return pd.Series({
                            "Karton": int(parts[0]),
                            "Box": int(parts[1]),
                            "Pcs": int(parts[2])
                        })

                    except ValueError:
                        pass

                return pd.Series({
                    "Karton": 0,
                    "Box": 0,
                    "Pcs": 0
                })

            quantity = df["Quantity"].apply(parse_quantity)

            df["Karton"] = quantity["Karton"]
            df["Box"] = quantity["Box"]
            df["Pcs"] = quantity["Pcs"]

        # ==========================================
        # FILL DOWN DATA INVOICE
        # ==========================================
        fill_down_columns = [
            "Customer Name",
            "Customer#",
            "Address",
            "Area",
            "Channel",
            "Invoice Date",
            "Invoice No",
            "SalesOrder#",
            "Salesman"
        ]

        for column in fill_down_columns:

            if column in df.columns:
                df[column] = df[column].ffill()

        # Reset index
        df = df.reset_index(drop=True)

        return df

