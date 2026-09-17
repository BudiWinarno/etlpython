import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "Item#",
    "Item Description",
    "OnSales",
    "Stock Value OnSales",
]


class LK000071StockNormalizer(BaseNormalizer):

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

            if match >= 3:
                return idx

        raise Exception(
            "Header stock LK-000071 tidak ditemukan"
        )

    # =========================================================
    # PARSE ONSALES
    # =========================================================
    def parse_onsales(self, value):

        if pd.isna(value):
            return 0, 0

        text = str(value).strip()

        if not text:
            return 0, 0

        # Contoh:
        # 1. 11. 0
        # 2.  3. 0
        # 47. 1. 0

        parts = [
            part.strip()
            for part in text.split(".")
            if part.strip() != ""
        ]

        try:

            karton = (
                int(float(parts[0]))
                if len(parts) >= 1
                else 0
            )

            pcs = (
                int(float(parts[1]))
                if len(parts) >= 2
                else 0
            )

        except (ValueError, TypeError):

            karton = 0
            pcs = 0

        return karton, pcs

    # =========================================================
    # NORMALIZE
    # =========================================================
    def normalize(
        self,
        filepath,
        agent_id=60
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
        # 3. BACA ULANG DENGAN HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. RAPIKAN HEADER
        # Header asli TETAP
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
        # 5. VALIDASI KOLOM
        # =====================================================

        required_columns = [
            "Item#",
            "Item Description",
            "OnSales",
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise Exception(
                "Kolom stock LK-000071 tidak ditemukan: "
                + ", ".join(missing_columns)
            )

        # =====================================================
        # 6. REMOVE UNNAMED COLUMNS
        # =====================================================

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =====================================================
        # 7. REMOVE EMPTY ROWS
        # =====================================================

        df = df.replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 8. ITEM# -> STRING
        # =====================================================

        df["Item#"] = (
            df["Item#"]
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
        # 9. ITEM DESCRIPTION -> STRING
        # =====================================================

        df["Item Description"] = (
            df["Item Description"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 10. SPLIT ONSALES
        # =====================================================

        df[
            [
                "OnSales Karton",
                "OnSales Pcs"
            ]
        ] = (
            df["OnSales"]
            .apply(self.parse_onsales)
            .apply(pd.Series)
        )

        # =====================================================
        # 11. NUMERIC ONSALES
        # =====================================================

        df["OnSales Karton"] = (
            pd.to_numeric(
                df["OnSales Karton"],
                errors="coerce"
            )
            .fillna(0)
            .round()
            .astype(int)
        )

        df["OnSales Pcs"] = (
            pd.to_numeric(
                df["OnSales Pcs"],
                errors="coerce"
            )
            .fillna(0)
            .round()
            .astype(int)
        )

        # =====================================================
        # 12. AMBIL KONVERSI DARI AGENT MAPPING
        # Agent 71 = agent_id 60
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
        # 13. BUAT DICTIONARY MAPPING
        #
        # Item#
        #   ↓
        # kode_sku_agent
        #   ↓
        # item_box
        # =====================================================

        mapping_dict = {
            str(row.kode_sku_agent).strip():
                row.item_box
            for row in mappings
        }

        # =====================================================
        # 14. AMBIL KONVERSI
        # =====================================================

        df["Konversi"] = (
            df["Item#"]
            .map(mapping_dict)
        )

        # =====================================================
        # 15. KONVERSI -> NUMERIC
        # =====================================================

        df["Konversi"] = (
            pd.to_numeric(
                df["Konversi"],
                errors="coerce"
            )
            .round()
        )
        
        # =====================================================
        # 16. TOTAL QTY PCS
        # =====================================================

        df["Total Qty Pcs"] = (
            df["OnSales Karton"] * df["Konversi"].fillna(0)
            + df["OnSales Pcs"]
        ).where(
            df["OnSales Karton"] > 0,
            df["OnSales Pcs"]
        )

        # Bulatkan
        df["Total Qty Pcs"] = (
            df["Total Qty Pcs"]
            .fillna(0)
            .round()
            .astype(int)
        )

        # =====================================================
        # 16. REMOVE BARIS BUKAN DATA
        # =====================================================

        df = df[
            df["Item#"].notna()
            & df["Item#"].ne("")
        ]

        # =====================================================
        # 17. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 18. NOMOR URUT
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
        # 19. DEBUG
        # =====================================================

        print("=" * 80)

        print("AGENT ID:")
        print(agent_id)

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

        print("\nSKU TANPA MAPPING:")

        print(
            df[
                df["Konversi"].isna()
            ][
                [
                    "Item#",
                    "Item Description"
                ]
            ]
            .drop_duplicates()
        )

        print("=" * 80)

        return df