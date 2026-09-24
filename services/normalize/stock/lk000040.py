import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "NO",
    "KODE",
    "NAMA BARANG",
    "SISA (AC)",
]


class LK000040StockNormalizer(BaseNormalizer):

    def find_header_row(self, df):
        for idx, row in df.iterrows():

            values = [
                str(v).strip()
                for v in row.fillna("").tolist()
            ]

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match == len(EXPECTED_HEADERS):
                return idx

        raise Exception(
            "Header stock LK-000040 tidak ditemukan"
        )

    def normalize(self, filepath):

        # ==========================================
        # CARI HEADER
        # ==========================================

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        # ==========================================
        # BACA DATA
        # ==========================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # ==========================================
        # BERSIHKAN NAMA KOLOM
        # ==========================================

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # ==========================================
        # AMBIL KOLOM YANG DIBUTUHKAN
        # ==========================================

        df = df[
            [
                "NO",
                "KODE",
                "NAMA BARANG",
                "SISA (AC)"
            ]
        ]

        # ==========================================
        # STRING
        # ==========================================

        string_columns = [
            "KODE",
            "NAMA BARANG",
        ]

        for column in string_columns:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # ==========================================
        # SISA (AC) → NUMERIC
        # ==========================================

        df["SISA (AC)"] = (
            pd.to_numeric(
                df["SISA (AC)"],
                errors="coerce"
            )
            .fillna(0)
        )

        # ==========================================
        # HAPUS BARIS KOSONG
        # ==========================================

        df = df[
            (df["KODE"] != "") |
            (df["NAMA BARANG"] != "")
        ]

        df = df.reset_index(drop=True)

        # ==========================================
        # NOMOR URUT
        # ==========================================

        df["NO"] = range(
            1,
            len(df) + 1
        )

        # ==========================================
        # AMBIL ITEM MAPPING AGENT 30
        # ==========================================

        db = SessionLocal()

        mapping_data = (
            db.query(ItemAgentMapping)
            .filter(
                ItemAgentMapping.agent_id == 30,
                ItemAgentMapping.is_active == True
            )
            .all()
        )

        mapping_dict = {
            str(item.kode_sku_agent).strip(): {
                "kode_sku_jim": item.kode_sku_jim,
                "item_box": item.item_box,
            }
            for item in mapping_data
        }

        db.close()

        # ==========================================
        # MAPPING KODE AGEN → KODE JIM
        # ==========================================

        df["KODE JIM"] = (
            df["KODE"]
            .map(
                lambda x: mapping_dict.get(
                    x,
                    {}
                ).get(
                    "kode_sku_jim",
                    ""
                )
            )
        )

        # ==========================================
        # MAPPING ITEM BOX
        # ==========================================

        df["ITEM BOX"] = (
            df["KODE"]
            .map(
                lambda x: mapping_dict.get(
                    x,
                    {}
                ).get(
                    "item_box",
                    0
                )
            )
        )

        # ==========================================
        # ITEM BOX → NUMERIC
        # ==========================================

        df["ITEM BOX"] = pd.to_numeric(
            df["ITEM BOX"],
            errors="coerce"
        ).fillna(0)

        # ==========================================
        # TOTAL PCS
        # SISA (AC) × ITEM BOX
        # ==========================================

        df["TOTAL PCS"] = (
            df["SISA (AC)"] *
            df["ITEM BOX"]
        )

        return df