import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000046InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def _find_header_row(self, filepath, sheet_name=0):

        preview = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=None,
            nrows=30
        )

        expected_headers = [
            "no",
            "invoice",
            "remark",
            "tanggal",
            "noso",
            "nopo",
            "salesid",
            "salesperson",
            "princp_id",
            "princp_name",
            "div_id",
            "div_name",
            "custid",
            "custtype",
            "custname",
            "alamat",
            "fakturpajak",
            "tglfp",
            "namanpwp",
            "alamatnpwp",
            "nonpwp",
            "noktp",
            "email",
            "dpp",
            "ppn",
            "unit_dpp",
            "unit_ppn",
            "amount",
            "qty",
            "sat",
            "qty_item1",
            "itemid",
            "konversi",
            "ktn",
            "itemid2",
            "itemotherid",
            "itemname",
            "gdn",
            "price",
            "pcs price",
            "pc1",
            "diskon1",
            "pc2",
            "diskon2",
            "pc3",
            "diskon3",
            "pc4",
            "diskon4",
            "pc5",
            "diskon5",
            "pc6",
            "diskon6",
            "pc7",
            "diskon7",
            "disc_bottom",
            "sub_amount",
            "hrg_pkk",
            "sub_pkk",
            "createdby",
            "returno",
            "returqty",
            "returreason",
            "cabang",
            "phone1",
            "custgroup4",
        ]

        expected_headers = {
            header.strip().lower()
            for header in expected_headers
        }

        for idx, row in preview.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            match_count = len(
                values.intersection(expected_headers)
            )

            # Header memiliki banyak kolom yang cocok
            if match_count >= 10:
                return idx

        raise ValueError(
            "Header Invoice LK-000046 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        sheet_name = 0

        # -----------------------------------------------------
        # FIND HEADER
        # -----------------------------------------------------

        header_row = self._find_header_row(
            filepath,
            sheet_name
        )

        # -----------------------------------------------------
        # READ DATA
        # -----------------------------------------------------

        df = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=header_row
        )

        # -----------------------------------------------------
        # CLEAN HEADER
        # -----------------------------------------------------

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]
        
        # =========================================================
        # ITEM ID -> STRING
        # =========================================================

        for column in [
            "itemid",
            "itemid2",
            "itemotherid",
        ]:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.replace(r"\.0$", "", regex=True)
                )

        # -----------------------------------------------------
        # REMOVE EMPTY COLUMNS
        # -----------------------------------------------------

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # -----------------------------------------------------
        # REMOVE EMPTY ROWS
        # -----------------------------------------------------

        df = df.dropna(how="all")

        # -----------------------------------------------------
        # RESET INDEX
        # -----------------------------------------------------

        df = df.reset_index(drop=True)

        return df

