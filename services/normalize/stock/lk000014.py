import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "No. Barang",
    "Deskripsi Barang",
    "BAIK",
]


class LK000014StockNormalizer(BaseNormalizer):

    # =========================================================
    # FIND HEADER
    # =========================================================

    def find_header_row(self, df):

        for idx, row in df.iterrows():

            values = (
                row.fillna("")
                .astype(str)
                .str.replace(
                    "\u00A0",
                    " ",
                    regex=False
                )
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True
                )
                .str.strip()
                .tolist()
            )

            match = sum(
                1
                for header in EXPECTED_HEADERS
                if header in values
            )

            if match >= 3:
                return idx

        raise Exception(
            "Header stock LK-000014 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(
        self,
        filepath,
        agent_id=53
    ):

        # =====================================================
        # 1. BACA SEMUA BARIS
        # =====================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. CARI HEADER OTOMATIS
        # =====================================================

        header_row = self.find_header_row(
            preview
        )

        print("=" * 80)
        print("HEADER ROW:")
        print(header_row)
        print("=" * 80)

        # =====================================================
        # 3. BACA ULANG
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN HEADER
        # =====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.replace(
                "\u00A0",
                " ",
                regex=False
            )
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # =====================================================
        # 5. VALIDASI HEADER
        # =====================================================

        required_columns = [
            "No. Barang",
            "Deskripsi Barang",
            "BAIK"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom stock LK-000014 tidak ditemukan: "
                + ", ".join(
                    missing_columns
                )
            )

        # =====================================================
        # 6. JANGAN RENAME BAIK
        #
        # No. Barang       → tetap
        # Deskripsi Barang → tetap
        # BAIK              → tetap
        # =====================================================

        df = df[
            [
                "No. Barang",
                "Deskripsi Barang",
                "BAIK"
            ]
        ].copy()

        # =====================================================
        # 7. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 8. BERSIHKAN NO. BARANG
        # =====================================================

        df["No. Barang"] = (
            df["No. Barang"]
            .fillna("")
            .astype(str)
            .str.replace(
                "\u00A0",
                " ",
                regex=False
            )
            .str.strip()
        )

        # =====================================================
        # 9. BERSIHKAN DESKRIPSI
        # =====================================================

        df["Deskripsi Barang"] = (
            df["Deskripsi Barang"]
            .fillna("")
            .astype(str)
            .str.replace(
                "\u00A0",
                " ",
                regex=False
            )
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # =====================================================
        # 10. HAPUS BARIS TANPA SKU
        # =====================================================

        df = df[
            df["No. Barang"] != ""
        ].copy()

        # =====================================================
        # 11. BAIK → NUMERIC
        #
        # Tetap bernama BAIK
        # =====================================================

        df["BAIK"] = pd.to_numeric(
            df["BAIK"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 12. AMBIL ITEM AGENT MAPPING
        # =====================================================

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

        # =====================================================
        # 13. BUAT MAPPING
        #
        # kode_sku_agent
        #       ↓
        # item_box
        # =====================================================

        mapping_dict = {
            str(row.kode_sku_agent)
            .replace(
                "\u00A0",
                " "
            )
            .strip(): row.item_box
            for row in mappings
        }

        # =====================================================
        # 14. AMBIL KONVERSI
        #
        # No. Barang = kode_sku_agent
        # =====================================================

        df["konversi"] = (
            df["No. Barang"]
            .map(mapping_dict)
        )

        # =====================================================
        # 15. KONVERSI → NUMERIC
        # =====================================================

        df["konversi"] = pd.to_numeric(
            df["konversi"],
            errors="coerce"
        )

        # =====================================================
        # 16. TOTAL QTY PCS
        #
        # BAIK × KONVERSI
        # =====================================================

        df["total_qty_pcs"] = (
            df["BAIK"].fillna(0)
            *
            df["konversi"].fillna(0)
        )

        # =====================================================
        # 17. BULATKAN
        # =====================================================

        df["konversi"] = (
            df["konversi"]
            .round(0)
        )

        df["total_qty_pcs"] = (
            df["total_qty_pcs"]
            .round(0)
        )

        # =====================================================
        # 18. OUTPUT NORMALIZER
        # =====================================================

        df = df[
            [
                "No. Barang",
                "Deskripsi Barang",
                "BAIK",
                "konversi",
                "total_qty_pcs"
            ]
        ].copy()

        # =====================================================
        # 19. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 20. DEBUG
        # =====================================================

        print("=" * 80)

        print("AGENT ID:")
        print(agent_id)

        print("\nHEADER ROW:")
        print(header_row)

        print("\nCOLUMNS:")
        print(
            df.columns.tolist()
        )

        print("\nTOTAL DATA:")
        print(
            len(df)
        )

        print("\nDATA:")
        print(
            df.head(20)
        )

        # =====================================================
        # 21. SKU TANPA MAPPING
        # =====================================================

        print("\nSKU TANPA MAPPING:")

        unmapped = (
            df[
                df["konversi"].isna()
            ][
                [
                    "No. Barang",
                    "Deskripsi Barang"
                ]
            ]
            .drop_duplicates()
        )

        print(unmapped)

        print("=" * 80)

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(
        self,
        filepath
    ):

        df = pd.read_excel(
            filepath,
            header=0
        )

        headers = (
            df.columns
            .astype(str)
            .str.replace(
                "\u00A0",
                " ",
                regex=False
            )
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
            .tolist()
        )

        print("=" * 80)
        print("MAPPING HEADERS:")
        print(headers)
        print("=" * 80)

        return headers