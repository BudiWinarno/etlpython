import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "Kode Agen",
    "Kode JIM",
    "Product Name",
    "Karton",
]


class LK000004StockNormalizer(BaseNormalizer):

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

            if match >= 4:
                return idx

        raise Exception(
            "Header stock tidak ditemukan. "
            "Header yang dicari: "
            + ", ".join(EXPECTED_HEADERS)
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(
        self,
        filepath,
        agent_id=54
    ):

        # =====================================================
        # 1. BACA PREVIEW TANPA HEADER
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
        print("FILE:")
        print(filepath)

        print("\nAGENT ID:")
        print(agent_id)

        print("\nHEADER ROW:")
        print(header_row)

        print("=" * 80)

        # =====================================================
        # 3. BACA ULANG DENGAN HEADER
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
        # 5. VALIDASI
        # =====================================================

        missing_columns = [
            col
            for col in EXPECTED_HEADERS
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom stock tidak ditemukan: "
                + ", ".join(missing_columns)
            )

        # =====================================================
        # 6. AMBIL KOLOM RAW
        # =====================================================

        df = df[
            [
                "Kode Agen",
                "Kode JIM",
                "Product Name",
                "Karton"
            ]
        ].copy()

        # =====================================================
        # 7. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 8. BERSIHKAN KOLOM TEXT
        # =====================================================

        text_columns = [
            "Kode Agen",
            "Kode JIM",
            "Product Name",
        ]

        for col in text_columns:

            df[col] = (
                df[col]
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
        # 9. KARTON → NUMERIC
        # =====================================================

        df["Karton"] = pd.to_numeric(
            df["Karton"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 10. AMBIL ITEM AGENT MAPPING
        #
        # Kode Agen
        #     ↓
        # ItemAgentMapping.kode_sku_agent
        #     ↓
        # item_box
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
        # 11. BUAT DICTIONARY MAPPING
        # =====================================================

        mapping_dict = {

            str(row.kode_sku_agent)
            .replace(
                "\u00A0",
                " "
            )
            .strip():

            row.item_box

            for row in mappings

        }

        # =====================================================
        # 12. AMBIL KONVERSI
        #
        # Kode Agen → item_box
        # =====================================================

        df["konversi"] = (
            df["Kode Agen"]
            .map(mapping_dict)
        )

        # =====================================================
        # 13. KONVERSI → NUMERIC
        # =====================================================

        df["konversi"] = pd.to_numeric(
            df["konversi"],
            errors="coerce"
        )

        # =====================================================
        # 14. TOTAL QTY PCS
        #
        # Karton × konversi
        # =====================================================

        df["total_qty_pcs"] = (
            df["Karton"].fillna(0)
            *
            df["konversi"].fillna(0)
        )

        # =====================================================
        # 15. BULATKAN
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
        # 16. HASIL AKHIR
        # =====================================================

        df = df[
            [
                "Kode Agen",
                "Kode JIM",
                "Product Name",
                "Karton",
                "konversi",
                "total_qty_pcs"
            ]
        ].copy()

        # =====================================================
        # 17. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 18. DEBUG
        # =====================================================

        print("=" * 80)

        print("HASIL NORMALISASI")

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
            df.head(20).to_string()
        )

        # =====================================================
        # 19. SKU TANPA MAPPING
        # =====================================================

        print("\nSKU TANPA MAPPING:")

        unmapped = (
            df[
                df["konversi"].isna()
            ][
                [
                    "Kode Agen",
                    "Kode JIM",
                    "Product Name"
                ]
            ]
            .drop_duplicates()
        )

        print(
            unmapped.to_string(
                index=False
            )
        )

        print("=" * 80)

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # =========================================================

    def get_mapping_headers(
        self,
        filepath
    ):

        # =====================================================
        # 1. BACA PREVIEW
        # =====================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. CARI HEADER
        # =====================================================

        header_row = self.find_header_row(
            preview
        )

        # =====================================================
        # 3. BACA HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN HEADER
        # =====================================================

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