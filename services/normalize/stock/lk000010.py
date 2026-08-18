import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "Kode SKU Agen",
    "Kode JIM",
    "Nama SKU",
    "QTY Karton",
    "item_box",
    "qty_pcs",
]


class LK000010StockNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================
    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = (
                row.fillna("")
                .astype(str)
                .str.strip()
                .tolist()
            )

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            # Minimal 3 header cocok
            if match >= 3:
                return idx

        raise Exception(
            "Header stock LK-000010 tidak ditemukan"
        )
        
    def normalize(self, filepath, agent_id=None):

        # =====================================================
        # 1. BACA PREVIEW
        # =====================================================

        preview = self.read_excel(filepath)

        header_row = self.find_header_row(preview)

        # =====================================================
        # 2. BACA ULANG DENGAN HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 3. RAPINKAN NAMA KOLOM
        # =====================================================

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

        # =====================================================
        # 4. VALIDASI KOLOM
        # =====================================================

        required_columns = [
            "Kode SKU Agen",
            "Kode JIM",
            "Nama SKU",
            "QTY Karton",
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom stock LK-000010 tidak ditemukan: "
                + ", ".join(missing_columns)
            )

        # =====================================================
        # 5. AMBIL KOLOM
        # =====================================================

        # df = df[
        #     [
        #         "Kode SKU Agen",
        #         "Kode JIM",
        #         "Nama SKU",
        #         "QTY Karton",
        #     ]
        # ].copy()
        
        # =========================================================
        # 5. AMBIL KOLOM
        # =========================================================

        base_columns = [
            "Kode SKU Agen",
            "Kode JIM",
            "Nama SKU",
            "QTY Karton",
        ]

        # Kalau file sudah pernah dinormalisasi,
        # pertahankan kolom tambahan
        optional_columns = [
            "item_box",
            "qty_pcs",
        ]

        columns_to_keep = base_columns.copy()

        for col in optional_columns:
            if col in df.columns:
                columns_to_keep.append(col)

        df = df[columns_to_keep].copy()

        # =====================================================
        # 6. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 7. HAPUS BARIS TOTAL
        # =====================================================

        df = df[
            ~df.astype(str)
            .apply(
                lambda row:
                row.str.upper()
                .str.contains(
                    r"TOTAL",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]

        # =====================================================
        # 8. BERSIHKAN DATA
        # =====================================================

        df["Kode SKU Agen"] = (
            df["Kode SKU Agen"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df["Kode JIM"] = (
            df["Kode JIM"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df["Nama SKU"] = (
            df["Nama SKU"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 9. QTY KARTON → NUMERIC
        # =====================================================

        df["QTY Karton"] = pd.to_numeric(
            df["QTY Karton"],
            errors="coerce"
        ).fillna(0)
        
        # =====================================================
        # 10. ITEM BOX + QTY PCS
        # =====================================================

        if agent_id is not None:

            db = SessionLocal()

            try:

                mappings = (
                    db.query(
                        ItemAgentMapping.kode_sku_agent,
                        ItemAgentMapping.item_box
                    )
                    .filter(
                        ItemAgentMapping.agent_id == agent_id,
                        ItemAgentMapping.is_active == True
                    )
                    .all()
                )

            finally:
                db.close()

            mapping_dict = {
                str(row.kode_sku_agent).strip(): row.item_box
                for row in mappings
            }

            df["item_box"] = (
                df["Kode SKU Agen"]
                .map(mapping_dict)
            )

            df["item_box"] = pd.to_numeric(
                df["item_box"],
                errors="coerce"
            )

            df["qty_pcs"] = (
                df["QTY Karton"].fillna(0)
                *
                df["item_box"].fillna(0)
            )

        else:

            # RESET INDEX
            df = df.reset_index(drop=True)

            # NOMOR URUT
            df.insert(
                0,
                "No",
                range(1, len(df) + 1)
            )

            return df
