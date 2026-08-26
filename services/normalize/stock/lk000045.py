import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


EXPECTED_HEADERS = [
    "Kode SKU Agen",
    "Kode JIM",
    "Nama SKU",
    "QTY Karton",
]


class LK000045StockNormalizer(BaseNormalizer):

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
            "Header stock LK-000045 tidak ditemukan"
        )

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(
        self,
        filepath,
        agent_id=49
    ):

        # =====================================================
        # 1. BACA PREVIEW
        # =====================================================

        preview = self.read_excel(
            filepath
        )

        header_row = self.find_header_row(
            preview
        )

        # =====================================================
        # 2. BACA ULANG DENGAN HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 3. RAPIKAN NAMA KOLOM
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
                "Kolom stock LK-000045 tidak ditemukan: "
                + ", ".join(
                    missing_columns
                )
            )

        # =====================================================
        # 5. AMBIL KOLOM
        # =====================================================

        base_columns = [
            "Kode SKU Agen",
            "Kode JIM",
            "Nama SKU",
            "QTY Karton",
        ]

        optional_columns = [
            "QTY PCS",
        ]

        columns_to_keep = (
            base_columns.copy()
        )

        for col in optional_columns:

            if col in df.columns:

                columns_to_keep.append(
                    col
                )

        df = df[
            columns_to_keep
        ].copy()

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
            ~(
                df["Kode SKU Agen"].isna()
                &
                df["Kode JIM"].isna()
                &
                df["Nama SKU"].isna()
                &
                df["QTY Karton"].notna()
            )
        ].copy()

        # =====================================================
        # 8. HAPUS BARIS YANG MENGANDUNG TOTAL
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
        # 9. BERSIHKAN DATA
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
        # 10. QTY KARTON → NUMERIC
        # =====================================================

        df["QTY Karton"] = pd.to_numeric(
            df["QTY Karton"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 11. KONVERSI KARTON → PCS
        # Berdasarkan agent_id
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
                        ItemAgentMapping.agent_id
                        == agent_id,

                        ItemAgentMapping.is_active
                        == True
                    )
                    .all()
                )

            finally:

                db.close()

            # =================================================
            # Mapping:
            #
            # Kode SKU Agen
            #       ↓
            # item_box
            # =================================================

            mapping_dict = {
                str(
                    row.kode_sku_agent
                ).strip():
                    row.item_box

                for row in mappings
            }

            # =================================================
            # Ambil item_box berdasarkan Kode SKU Agen
            # =================================================

            df["item_box"] = (
                df["Kode SKU Agen"]
                .map(
                    mapping_dict
                )
            )

            # =================================================
            # Numeric
            # =================================================

            df["item_box"] = pd.to_numeric(
                df["item_box"],
                errors="coerce"
            )

            # =================================================
            # Total Qty PCS
            #
            # QTY Karton × item_box
            # =================================================

            df["QTY PCS"] = (
                df["QTY Karton"].fillna(0)
                *
                df["item_box"].fillna(0)
            )

            df["item_box"] = (
                df["item_box"]
                .round(0)
            )

            df["QTY PCS"] = (
                df["QTY PCS"]
                .round(0)
            )

        else:

            df["item_box"] = None
            df["QTY PCS"] = None

        # =====================================================
        # 12. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 13. NOMOR URUT
        # =====================================================

        df.insert(
            0,
            "No",
            range(
                1,
                len(df) + 1
            )
        )

        # =====================================================
        # DEBUG
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

        if agent_id is not None:

            print("\nSKU TANPA MAPPING:")

            print(
                df[
                    df["item_box"].isna()
                ][
                    [
                        "Kode SKU Agen",
                        "Nama SKU"
                    ]
                ]
                .drop_duplicates()
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

        # File sudah dinormalisasi.
        # Header ada di baris pertama.

        df = pd.read_excel(
            filepath,
            header=0
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

        print("=" * 80)

        print("MAPPING HEADERS:")

        print(headers)

        print("=" * 80)

        return headers