import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000064StockNormalizer(BaseNormalizer):

    # =========================================================
    # NORMALIZE
    # RAW EXCEL → DATA BERSIH
    # =========================================================
    def normalize(self, filepath):

        # =====================================================
        # 1. BACA EXCEL TANPA HEADER
        # =====================================================

        preview = pd.read_excel(
            filepath,
            header=None
        )

        # =====================================================
        # 2. CARI HEADER
        # =====================================================

        header_row = None

        for idx, row in preview.iterrows():

            values = [
                str(value)
                .strip()
                .replace("\n", " ")
                for value in row.tolist()
                if pd.notna(value)
            ]

            if (
                "Kode Barang" in values
                and "Nama Barang" in values
                and "Kode Barcode" in values
                and "Stok Akhir" in values
            ):
                header_row = idx
                break

        if header_row is None:
            raise ValueError(
                "Header Stock LK-000064 tidak ditemukan"
            )

        # =====================================================
        # 3. BACA DATA MULAI DARI HEADER
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=header_row
        )

        # =====================================================
        # 4. HAPUS 2 BARIS SETELAH HEADER
        # =====================================================

        df = df.iloc[2:].reset_index(drop=True)

        # =====================================================
        # 5. CLEAN HEADER
        # =====================================================

        df.columns = [
            str(col)
            .replace("\n", " ")
            .strip()
            for col in df.columns
        ]

        # =====================================================
        # 6. PECAH KOLOM STOK AKHIR
        #
        # RAW:
        #
        # Stok Akhir | Unnamed | Unnamed
        #     5       |    /    |    1
        #
        # HASIL:
        #
        # Qty Karton | Pemisah | Qty PCS
        #     5       |    /    |    1
        # =====================================================

        if "Stok Akhir" in df.columns:

            columns = list(df.columns)

            stok_index = columns.index(
                "Stok Akhir"
            )

            if stok_index + 2 < len(columns):

                columns[stok_index] = "Qty Karton"

                columns[stok_index + 1] = "Pemisah"

                columns[stok_index + 2] = "Qty PCS"

                df.columns = columns

        # =====================================================
        # 7. HITUNG TOTAL QTY PCS
        #
        # (Qty Karton * Isi Besar) + Qty PCS
        # =====================================================

        if (
            "Qty Karton" in df.columns
            and "Qty PCS" in df.columns
            and "Isi Besar" in df.columns
        ):

            qty_karton = pd.to_numeric(
                df["Qty Karton"],
                errors="coerce"
            ).fillna(0)

            qty_pcs = pd.to_numeric(
                df["Qty PCS"],
                errors="coerce"
            ).fillna(0)

            isi_besar = pd.to_numeric(
                df["Isi Besar"],
                errors="coerce"
            ).fillna(0)

            df["total_qty_pcs"] = (
                qty_karton * isi_besar
            ) + qty_pcs

        # =====================================================
        # 8. REMOVE EMPTY COLUMNS
        # =====================================================

        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # =====================================================
        # 9. REMOVE EMPTY ROWS
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 10. REMOVE BARIS NON DATA
        # =====================================================

        if "Kode Barang" in df.columns:

            df = df[
                df["Kode Barang"].notna()
                & (
                    df["Kode Barang"]
                    .astype(str)
                    .str.strip()
                    .ne("")
                )
            ]

        # =====================================================
        # 11. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # 12. RETURN
        # =====================================================

        return df

    # =========================================================
    # GET MAPPING HEADERS
    # HASIL NORMALISASI → AMBIL HEADER SAJA
    # =========================================================

    def get_mapping_headers(self, filepath):

        # File yang masuk ke sini adalah
        # HASIL NORMALISASI.
        #
        # Header sudah berada di row pertama.

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