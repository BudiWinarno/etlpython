import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000106StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        # =========================================================
        # BACA EXCEL TANPA HEADER
        # =========================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =========================================================
        # CARI HEADER
        # =========================================================

        header_row = None

        for idx, row in preview.iterrows():

            values = [
                str(value)
                .replace("\n", " ")
                .strip()
                for value in row.tolist()
                if pd.notna(value)
            ]

            if (
                "Item No." in values
                and "Item Description" in values
                and "Ratio 3" in values
                and "CENTRE CV. AP" in values
                and "M-CENTRE CV. APM" in values
            ):
                header_row = idx
                break

        if header_row is None:
            raise ValueError(
                "Header Stock LK-000106 tidak ditemukan"
            )

        # =========================================================
        # BACA DATA MULAI DARI HEADER
        # =========================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =========================================================
        # CLEAN HEADER
        # =========================================================

        df.columns = [
            str(col)
            .replace("\n", " ")
            .strip()
            for col in df.columns
        ]

        # =========================================================
        # HITUNG TOTAL QTY PCS
        #
        # CENTRE CV. AP
        # +
        # M-CENTRE CV. APM
        # =========================================================

        if (
            "CENTRE CV. AP" in df.columns
            and "M-CENTRE CV. APM" in df.columns
        ):

            centre_ap = pd.to_numeric(
                df["CENTRE CV. AP"],
                errors="coerce"
            ).fillna(0)

            m_centre_apm = pd.to_numeric(
                df["M-CENTRE CV. APM"],
                errors="coerce"
            ).fillna(0)

            df["total_qty_pcs"] = (
                centre_ap
                + m_centre_apm
            )

        # =========================================================
        # HAPUS KOLOM UNNAMED
        # =========================================================

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =========================================================
        # HAPUS BARIS KOSONG
        # =========================================================

        df = df.dropna(how="all")

        # =========================================================
        # HANYA DATA YANG PUNYA ITEM NO.
        # =========================================================

        if "Item No." in df.columns:

            df = df[
                df["Item No."].notna()
                & (
                    df["Item No."]
                    .astype(str)
                    .str.strip()
                    .ne("")
                )
            ]
        
        # =========================================================
        # HAPUS BARIS FOOTER
        # =========================================================

        if "Item No." in df.columns:
            df = df[
                df["Item No."]
                .astype(str)
                .str.strip()
                .ne("Fina Business & Accounting Software")
            ]

        # =========================================================
        # RESET INDEX
        # =========================================================

        df = df.reset_index(drop=True)

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(self, filepath):

        df = pd.read_excel(
            filepath,
            header=0,
            nrows=0
        )

        headers = (
            df.columns
            .astype(str)
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
            .tolist()
        )

        return headers