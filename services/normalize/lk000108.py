# from services.normalize.base import BaseNormalizer


# class LK000108InvoiceNormalizer(BaseNormalizer):

#     def normalize(self, filepath):

#         df = self.read_excel_with_header(filepath)

#         # Hapus baris Report Total dan End of Report
#         df = df[
#             ~df.astype(str)
#             .apply(
#                 lambda row: row.str.upper().str.contains(
#                     r"REPORT TOTAL|END OF REPORT",
#                     regex=True,
#                     na=False
#                 ).any(),
#                 axis=1
#             )
#         ]

#         return df.reset_index(drop=True)

import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "Customer Name",
    "Customer#",
    "Product Code",
    "Product Name",
    "Packaging",
    "Varian",
    "Invoice Date",
    "Invoice No",
    "SalesOrder#",
    "Salesman",
    "Quantity",
    "Qty (Pcs)",
    "Freegood",
    "LineDisc1",
    "LineDisc2",
    "LineDisc3",
    "LineDisc4",
    "LineDisc5",
    "DPP",
    "Tax",
    "Net Amount",
]


class LK000108InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def find_header_row(self, df):

        expected_headers = {
            header.strip().lower()
            for header in EXPECTED_HEADERS
        }

        for idx, row in df.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            match = len(
                values.intersection(expected_headers)
            )

            if match >= 15:
                return idx

        raise Exception(
            "Header invoice LK-000108 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        print("\n==============================")
        print("NORMALIZE INVOICE LK-000108")
        print("==============================")

        # -----------------------------------------------------
        # 1. BACA PREVIEW TANPA HEADER
        # -----------------------------------------------------

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # -----------------------------------------------------
        # 2. CARI HEADER
        # -----------------------------------------------------

        header_row = self.find_header_row(preview)

        print(
            f"Header ditemukan di baris Excel: "
            f"{header_row + 1}"
        )

        # -----------------------------------------------------
        # 3. BACA DATA DENGAN HEADER
        # -----------------------------------------------------

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # -----------------------------------------------------
        # 4. CLEAN HEADER
        # -----------------------------------------------------

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
        )

        # -----------------------------------------------------
        # 5. REMOVE KOLOM UNNAMED
        # -----------------------------------------------------

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # -----------------------------------------------------
        # 6. VALIDASI HEADER
        # -----------------------------------------------------

        missing_columns = [
            column
            for column in EXPECTED_HEADERS
            if column not in df.columns
        ]

        if missing_columns:

            raise Exception(
                f"Header invoice LK-000108 tidak lengkap: "
                f"{missing_columns}"
            )

        # -----------------------------------------------------
        # 7. REMOVE EMPTY ROWS
        # -----------------------------------------------------

        df = df.replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # STRING
        # =====================================================

        string_columns = [
            "Customer Name",
            "Customer#",
            "Product Code",
            "Product Name",
            "Packaging",
            "Varian",
            "Invoice No",
            "SalesOrder#",
            "Salesman",
        ]

        for column in string_columns:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.replace(
                        r"\.0$",
                        "",
                        regex=True
                    )
                )
        # =====================================================
        # PRODUCT CODE YURI
        # =====================================================

        db = SessionLocal()

        mapping_data = (
            db.query(ItemAgentMapping)
            .filter(
                ItemAgentMapping.agent_id == 17,
                ItemAgentMapping.is_active == True
            )
            .all()
        )

        mapping_dict = {
            str(item.kode_sku_agent).strip(): item.kode_sku_jim
            for item in mapping_data
        }

        db.close()

        df["Product Code Yuri"] = (
            df["Product Code"]
            .map(mapping_dict)
            .fillna("")
        )

        # =====================================================
        # QUANTITY
        # =====================================================

        if "Quantity" in df.columns:

            df["Quantity"] = (
                df["Quantity"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # =====================================================
        # NUMERIC
        # =====================================================

        numeric_columns = [
            "Qty (Pcs)",
            "Freegood",
            "LineDisc1",
            "LineDisc2",
            "LineDisc3",
            "LineDisc4",
            "LineDisc5",
            "DPP",
            "Tax",
            "Net Amount",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0)

        # =====================================================
        # TANGGAL
        # =====================================================

        if "Invoice Date" in df.columns:

            df["Invoice Date"] = pd.to_datetime(
                df["Invoice Date"],
                errors="coerce"
            ).dt.date

        # =====================================================
        # REMOVE SUBTOTAL / TOTAL
        # =====================================================

        text_columns_for_total_check = [
            "Customer Name",
            "Customer#",
            "Product Code",
            "Product Name",
        ]

        mask_total = pd.Series(
            False,
            index=df.index
        )

        for column in text_columns_for_total_check:

            if column in df.columns:

                mask_total = (
                    mask_total |
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.contains(
                        r"subtotal|sub total|total",
                        regex=True,
                        na=False
                    )
                )

        df = df[~mask_total]

        # =====================================================
        # REMOVE BARIS YANG BUKAN DATA
        # =====================================================

        df = df[
            (df["Customer#"] != "") &
            (df["Product Code"] != "")
        ]

        # =====================================================
        # HAPUS KOLOM SUBTOTAL JIKA ADA
        # =====================================================

        if "Subtotal" in df.columns:

            df = df.drop(
                columns=["Subtotal"]
            )

        # =====================================================
        # RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # BUAT NOMOR URUT
        # =====================================================

        if "No" in df.columns:

            df = df.drop(
                columns=["No"]
            )

        df.insert(
            0,
            "No",
            range(
                1,
                len(df) + 1
            )
        )

        # =====================================================
        # URUTAN KOLOM
        # =====================================================

        final_columns = [
            "No",
            "Customer Name",
            "Customer#",
            "Product Code",
            "Product Code Yuri",
            "Product Name",
            "Packaging",
            "Varian",
            "Invoice Date",
            "Invoice No",
            "SalesOrder#",
            "Salesman",
            "Quantity",
            "Qty (Pcs)",
            "Freegood",
            "LineDisc1",
            "LineDisc2",
            "LineDisc3",
            "LineDisc4",
            "LineDisc5",
            "DPP",
            "Tax",
            "Net Amount",
        ]

        df = df[
            [
                column
                for column in final_columns
                if column in df.columns
            ]
        ]

        # =====================================================
        # DEBUG
        # =====================================================

        print("\n==============================")
        print("HASIL NORMALISASI")
        print("==============================")

        print(
            df.head(10).to_string()
        )

        print(
            "\nJumlah data:",
            len(df)
        )

        print(
            "\nJumlah kolom:",
            len(df.columns)
        )

        print(
            "\nKolom:"
        )

        print(
            df.columns.tolist()
        )

        print("\n==============================")
        print("NORMALIZE SELESAI")
        print("==============================")

        return df