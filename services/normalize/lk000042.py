import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


class LK000042InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        # =========================================================
        # READ EXCEL
        # HEADER SUDAH DI BARIS PERTAMA
        # =========================================================

        df = pd.read_excel(
            filepath,
            header=0
        )

        # =========================================================
        # CLEAN HEADER
        # =========================================================

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # =========================================================
        # KODE PRINSIPAL -> STRING
        # =========================================================

        if "KODE PRINSIPAL" in df.columns:

            df["KODE PRINSIPAL"] = (
                df["KODE PRINSIPAL"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
            )

        # =========================================================
        # GET KONVERSI DARI ITEM AGENT MAPPING
        # AGENT ID = 37
        # =========================================================

        agent_id = 37

        db = SessionLocal()

        try:

            mappings = (
                db.query(ItemAgentMapping)
                .filter(
                    ItemAgentMapping.agent_id == agent_id
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
        # MAPPING BERDASARKAN KODE PRINSIPAL
        # =========================================================

        if "KODE PRINSIPAL" in df.columns:

            df["Konversi"] = (
                df["KODE PRINSIPAL"]
                .map(mapping_konversi)
            )

        # =========================================================
        # TAMBAHKAN TOTAL QTY PCS
        #
        # CTN  -> QTY * Konversi
        # LAIN -> QTY
        # =========================================================

        if (
            "QTY" in df.columns
            and "SATUAN" in df.columns
            and "Konversi" in df.columns
        ):

            qty = pd.to_numeric(
                df["QTY"],
                errors="coerce"
            )

            konversi = pd.to_numeric(
                df["Konversi"],
                errors="coerce"
            )

            satuan = (
                df["SATUAN"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )

            # Default: total_qty_pcs = QTY
            df["total_qty_pcs"] = qty

            # Kalau SATUAN = CTN
            # QTY dikali Konversi
            mask_ctn = satuan == "CTN"

            df.loc[mask_ctn, "total_qty_pcs"] = (
                qty[mask_ctn] * konversi[mask_ctn]
            )

        # =========================================================
        # POSISI KOLOM
        #
        # SATUAN
        # Konversi
        # total_qty_pcs
        # =========================================================

        if (
            "Konversi" in df.columns
            and "SATUAN" in df.columns
        ):

            columns = list(df.columns)

            # Hapus dulu kalau sudah ada
            columns.remove("Konversi")

            if "total_qty_pcs" in columns:
                columns.remove("total_qty_pcs")

            # Cari posisi SATUAN
            satuan_index = columns.index("SATUAN")

            # Konversi setelah SATUAN
            columns.insert(
                satuan_index + 1,
                "Konversi"
            )

            # total_qty_pcs setelah Konversi
            columns.insert(
                satuan_index + 2,
                "total_qty_pcs"
            )

            df = df[columns]

        # =========================================================
        # REMOVE EMPTY COLUMNS
        # =========================================================

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =========================================================
        # REMOVE EMPTY ROWS
        # =========================================================

        df = df.dropna(how="all")

        # =========================================================
        # RESET INDEX
        # =========================================================

        df = df.reset_index(drop=True)

        return df