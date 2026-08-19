import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


class LK000037InvoiceNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def _find_header_row(self, filepath, sheet_name=0):

        preview = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=None,
            nrows=20
        )

        expected_headers = [
            "No",
            "Cd Outlet",
            "Nama Outlet",
            "So Num",
            "Order Date",
            "Kode Produk",
            "Nama Produk",
            "Krt",
            "Pack",
            "Pcs",
            "Bonus",
            "Gross. Sales",
            "Total Diskon",
            "Ppn",
            "Gross",
            "Retur",
            "Netto",
            "Id Sales",
            "Sales",
            "Cab",
            "Jenis Outlet",
        ]

        for idx, row in preview.iterrows():

            values = [
                str(value).strip()
                for value in row.tolist()
                if pd.notna(value)
            ]

            match_count = sum(
                1
                for header in expected_headers
                if header in values
            )

            if match_count >= 5:
                return idx

        raise ValueError(
            "Header Invoice LK-000037 tidak ditemukan"
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
        
        # KODE PRODUK -> STRING
        if "Kode Produk" in df.columns:
            df["Kode Produk"] = (
                df["Kode Produk"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
            )
            
            # =========================================================
            # GET KONVERSI DARI ITEM AGENT MAPPING
            # AGENT ID = 34
            # =========================================================

            db = SessionLocal()

            try:

                mappings = (
                    db.query(ItemAgentMapping)
                    .filter(
                        ItemAgentMapping.agent_id == 34
                    )
                    .all()
                )

                mapping_konversi = {
                    str(item.kode_sku_agent).strip(): item.item_box
                    for item in mappings
                }

            finally:
                db.close()


            # =========================================================
            # TAMBAHKAN KOLOM KONVERSI
            # =========================================================

            if "Kode Produk" in df.columns:

                df["Konversi"] = (
                    df["Kode Produk"]
                    .map(mapping_konversi)
                )
                
            # =========================================================
            # KRT / PACK -> PCS
            # =========================================================

            if (
                "Krt" in df.columns
                and "Pack" in df.columns
                and "Konversi" in df.columns
                and "Pcs" in df.columns
            ):

                krt = pd.to_numeric(
                    df["Krt"],
                    errors="coerce"
                ).fillna(0)

                pack = pd.to_numeric(
                    df["Pack"],
                    errors="coerce"
                ).fillna(0)

                konversi = pd.to_numeric(
                    df["Konversi"],
                    errors="coerce"
                )
                
                # =========================================================
                # SIMPAN PCS ASLI
                # =========================================================

                pcs_original = pd.to_numeric(
                    df["Pcs"],
                    errors="coerce"
                ).fillna(0)


                # =========================================================
                # KRT > 0
                # PCS = KRT * KONVERSI
                # =========================================================

                mask_krt_positive = krt > 0

                df.loc[mask_krt_positive, "Pcs"] = (
                    krt[mask_krt_positive]
                    * konversi[mask_krt_positive]
                )


                # =========================================================
                # KRT < 0
                # PCS = (KRT * KONVERSI) + PCS ASLI
                # =========================================================

                mask_krt_negative = krt < 0

                df.loc[mask_krt_negative, "Pcs"] = (
                    (
                        krt[mask_krt_negative]
                        * konversi[mask_krt_negative]
                    )
                    + pcs_original[mask_krt_negative]
                )


                # =========================================================
                # PACK > 0
                # PCS = PACK * KONVERSI
                # =========================================================

                mask_pack = pack > 0

                df.loc[mask_pack, "Pcs"] = (
                    pack[mask_pack]
                    * konversi[mask_pack]
                )

                # # Krt > 0
                # mask_krt = krt > 0

                # df.loc[mask_krt, "Pcs"] = (
                #     krt[mask_krt] * konversi[mask_krt]
                # )

                # # Pack > 0
                # mask_pack = pack > 0

                # df.loc[mask_pack, "Pcs"] = (
                #     pack[mask_pack] * konversi[mask_pack]
                # )


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
        # REMOVE TOTAL / NON DATA ROW
        # -----------------------------------------------------

        if "No" in df.columns:

            df = df[
                pd.to_numeric(
                    df["No"],
                    errors="coerce"
                ).notna()
            ]

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        if "Order Date" in df.columns:

            df["Order Date"] = pd.to_datetime(
                df["Order Date"],
                errors="coerce"
            )
            
        # =========================================================
        # POSISI KOLOM KONVERSI
        # =========================================================

        if "Konversi" in df.columns and "Pcs" in df.columns:

            columns = list(df.columns)

            columns.remove("Konversi")

            pcs_index = columns.index("Pcs")

            columns.insert(
                pcs_index,
                "Konversi"
            )

            df = df[columns]

        # -----------------------------------------------------
        # RESET INDEX
        # -----------------------------------------------------

        df = df.reset_index(drop=True)

        return df