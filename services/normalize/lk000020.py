import pandas as pd

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


class LK000020InvoiceNormalizer(BaseNormalizer):

    AGENT_ID = 31

    def normalize(self, filepath):

        df = self.read_excel(filepath)

        header_row = None

        # =====================================================
        # 1. CARI BARIS HEADER
        # =====================================================

        for i, row in df.iterrows():

            values = (
                row.fillna("")
                .astype(str)
                .str.strip()
                .tolist()
            )

            if "No" in values and "Tanggal" in values:

                header_row = i
                break

        if header_row is None:

            raise Exception(
                "Header tidak ditemukan"
            )

        # =====================================================
        # 2. JADIKAN HEADER
        # =====================================================

        df.columns = (
            df.iloc[header_row]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 3. AMBIL DATA SETELAH HEADER
        # =====================================================

        df = (
            df.iloc[header_row + 1:]
            .reset_index(drop=True)
        )

        # =====================================================
        # 4. HAPUS KOLOM KOSONG
        # =====================================================

        df = df.loc[
            :,
            df.columns != ""
        ]

        # =====================================================
        # 5. BERSIHKAN NAMA HEADER
        # =====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # =====================================================
        # 6. STRING KOSONG → NONE
        # =====================================================

        df = df.replace(
            r'^\s*$',
            None,
            regex=True
        )

        # =====================================================
        # 7. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )
        
        # =====================================================
        # 8. NORMALISASI TANGGAL
        # =====================================================

        if "Tanggal" in df.columns:

            df["Tanggal"] = pd.to_datetime(
                df["Tanggal"],
                dayfirst=True,
                errors="coerce"
            )

            df["Tanggal"] = df["Tanggal"].apply(
                lambda x: x.date()
                if pd.notna(x)
                else None
            )

        # =====================================================
        # 8. HAPUS BARIS NO KOSONG
        # =====================================================

        if "No" in df.columns:

            df = df[
                df["No"].notna()
            ]

            df = df[
                df["No"]
                .astype(str)
                .str.strip()
                != ""
            ]

        # =====================================================
        # 9. AMBIL MAPPING ITEM BOX
        # AGENT ID = 31
        # =====================================================

        db = SessionLocal()

        try:

            mappings = (
                db.query(
                    ItemAgentMapping.kode_sku_agent,
                    ItemAgentMapping.item_box
                )
                .filter(
                    ItemAgentMapping.agent_id
                    == self.AGENT_ID,

                    ItemAgentMapping.is_active
                    == True
                )
                .all()
            )

        finally:

            db.close()

        # =====================================================
        # 10. BUAT DICTIONARY KONVERSI
        # =====================================================

        mapping_dict = {

            str(
                row.kode_sku_agent
            )
            .strip()
            .replace(
                ".0",
                ""
            ):
                row.item_box

            for row in mappings
        }

        # =====================================================
        # 11. NORMALISASI KODE BARANG
        # =====================================================

        if "Kode Barang" not in df.columns:

            raise Exception(
                "Kolom 'Kode Barang' tidak ditemukan"
            )

        df["Kode Barang"] = (
            df["Kode Barang"]
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
        # 12. CARI KOLOM QTY
        # =====================================================

        qty_column = None

        for col in df.columns:

            if (
                str(col)
                .strip()
                .startswith("QTY")
            ):

                qty_column = col
                break

        if qty_column is None:

            raise Exception(
                "Kolom QTY tidak ditemukan"
            )

        # =====================================================
        # 13. TAMBAH KOLOM KONVERSI
        # SETELAH QTY Satuan Lengkap
        # =====================================================

        qty_position = (
            df.columns.get_loc(
                qty_column
            )
        )

        df.insert(
            qty_position + 1,
            "Konversi",
            None
        )

        # =====================================================
        # 14. ISI KONVERSI
        # BERDASARKAN KODE BARANG
        # =====================================================

        df["Konversi"] = (
            df["Kode Barang"]
            .map(
                mapping_dict
            )
        )

        # =====================================================
        # 15. KONVERSI → NUMERIC
        # =====================================================

        df["Konversi"] = pd.to_numeric(
            df["Konversi"],
            errors="coerce"
        )

        # =====================================================
        # 16. HITUNG TOTAL QTY PCS
        #
        # PCS = QTY
        # KRT = QTY × Konversi
        # =====================================================

        if qty_column not in df.columns:

            raise Exception(
                "Kolom QTY Satuan Lengkap tidak ditemukan"
            )

        # =====================================================
        # Ambil angka dari QTY Satuan Lengkap
        # =====================================================

        qty_value = pd.to_numeric(
            df[qty_column]
            .astype(str)
            .str.extract(
                r"(\d+(?:\.\d+)?)"
            )[0],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # Ambil satuan PCS / KRT
        # =====================================================

        qty_unit = (
            df[qty_column]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # =====================================================
        # Default PCS = QTY
        # =====================================================

        df["total_qty_pcs"] = qty_value

        # =====================================================
        # KRT = QTY × Konversi
        # =====================================================

        mask_krt = qty_unit.str.contains(
            r"\bKRT\b",
            regex=True,
            na=False
        )

        df.loc[
            mask_krt,
            "total_qty_pcs"
        ] = (
            qty_value[mask_krt]
            *
            df.loc[
                mask_krt,
                "Konversi"
            ].fillna(0)
        )

        # =====================================================
        # Numeric
        # =====================================================

        df["total_qty_pcs"] = pd.to_numeric(
            df["total_qty_pcs"],
            errors="coerce"
        ).fillna(0)

        # =====================================================
        # 17. PINDAHKAN total_qty_pcs
        # TEPAT SETELAH Konversi
        # =====================================================

        columns = df.columns.tolist()

        columns.remove(
            "total_qty_pcs"
        )

        konversi_position = columns.index(
            "Konversi"
        )

        columns.insert(
            konversi_position + 1,
            "total_qty_pcs"
        )

        df = df[columns]

        # =====================================================
        # 18. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # DEBUG
        # =====================================================

        print("=" * 80)

        print("AGENT ID:")
        print(
            self.AGENT_ID
        )

        print("\nCOLUMNS:")
        print(
            df.columns.tolist()
        )

        print("\nDATA:")
        print(
            df.head(20)
        )

        print("\nKODE BARANG TANPA KONVERSI:")

        print(
            df[
                df["Konversi"].isna()
            ][
                [
                    "Kode Barang",
                    "Konversi"
                ]
            ]
            .drop_duplicates()
            .head(20)
        )

        print("=" * 80)

        return df

    # =========================================================
    # GET MAPPING HEADERS
    #
    # KHUSUS MEMBACA HEADER FILE HASIL NORMALISASI
    # TIDAK MENJALANKAN normalize()
    # =========================================================

    def get_mapping_headers(self, filepath):

        print("=" * 80)
        print("GET MAPPING HEADERS")
        print("FILEPATH:", filepath)

        # =====================================================
        # BACA FILE HASIL NORMALISASI
        # =====================================================

        df = self.read_excel(
            filepath
        )

        # =====================================================
        # CARI HEADER NORMALISASI
        # =====================================================

        header_row = None

        for i, row in df.iterrows():

            values = (
                row.fillna("")
                .astype(str)
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True
                )
                .str.strip()
                .tolist()
            )

            # Header normalisasi
            if (
                "No" in values
                and "Tanggal" in values
                and "Kode Barang" in values
                and "Konversi" in values
                and "total_qty_pcs" in values
            ):

                header_row = i
                break

        if header_row is None:

            raise Exception(
                "Header normalisasi LK-000020 tidak ditemukan"
            )

        # =====================================================
        # AMBIL HEADER SAJA
        # =====================================================

        headers = (
            df.iloc[header_row]
            .fillna("")
            .astype(str)
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
            .tolist()
        )

        # =====================================================
        # HAPUS HEADER KOSONG
        # =====================================================

        headers = [
            header
            for header in headers
            if header != ""
        ]

        # =====================================================
        # DEBUG
        # =====================================================

        print("HEADER ROW:", header_row)

        print("\nHEADERS:")
        print(
            headers
        )

        print("\nJUMLAH HEADER:")
        print(
            len(headers)
        )

        print("=" * 80)

        return headers