import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000020StockNormalizer(BaseNormalizer):

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(self, filepath):

        # =====================================================
        # 1. BACA EXCEL RAW
        # =====================================================

        df = self.read_excel(filepath)

        # =====================================================
        # 2. CARI BARIS HEADER
        # =====================================================

        header_row = None

        for i in range(len(df) - 1):

            row1 = (
                df.iloc[i]
                .fillna("")
                .astype(str)
                .str.strip()
                .tolist()
            )

            row2 = (
                df.iloc[i + 1]
                .fillna("")
                .astype(str)
                .str.strip()
                .tolist()
            )

            if (
                "No" in row1
                and "Group" in row1
                and "Kode" in row1
                and "Nama Barang" in row1
                and "Stock" in row1
            ):
                header_row = i
                break

        if header_row is None:

            raise Exception(
                "Header stock LK-000020 tidak ditemukan"
            )

        # =====================================================
        # 3. HEADER UTAMA
        # =====================================================

        header1 = (
            df.iloc[header_row]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 4. SUB HEADER
        # =====================================================

        header2 = (
            df.iloc[header_row + 1]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =====================================================
        # 5. GABUNGKAN HEADER
        #
        # Mengikuti struktur RAW.
        #
        # Contoh:
        #
        # Stock + PCS
        #       ↓
        # Stock PCS
        #
        # Stock Akhir + kosong
        #       ↓
        # Stock Akhir
        #
        # Tidak mengganti nama header.
        # =====================================================

        headers = []

        for h1, h2 in zip(
            header1,
            header2
        ):

            h1 = str(h1).strip()
            h2 = str(h2).strip()

            # -------------------------------------------------
            # Keduanya kosong
            # -------------------------------------------------

            if h1 == "" and h2 == "":

                headers.append("")

            # -------------------------------------------------
            # Hanya header utama
            # -------------------------------------------------

            elif h2 == "" or h2.lower() == "nan":

                headers.append(h1)

            # -------------------------------------------------
            # Hanya sub-header
            # -------------------------------------------------

            elif h1 == "" or h1.lower() == "nan":

                headers.append(h2)

            # -------------------------------------------------
            # Header sama
            # -------------------------------------------------

            elif h1.lower() == h2.lower():

                headers.append(h1)

            # -------------------------------------------------
            # Header utama + sub-header
            # -------------------------------------------------

            else:

                headers.append(
                    f"{h1} {h2}"
                )

        # =====================================================
        # 6. AMBIL DATA SETELAH 2 BARIS HEADER
        # =====================================================

        df = (
            df.iloc[header_row + 2:]
            .reset_index(drop=True)
        )

        df.columns = headers

        # =====================================================
        # 7. BERSIHKAN SPASI HEADER
        #
        # Hanya membersihkan spasi.
        # Nama header tidak diubah.
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
        # 8. HAPUS KOLOM TANPA HEADER
        # =====================================================

        df = df.loc[
            :,
            df.columns != ""
        ]

        # =====================================================
        # 9. STRING KOSONG -> NONE
        # =====================================================

        df = df.replace(
            r"^\s*$",
            None,
            regex=True
        )

        # =====================================================
        # 10. HAPUS BARIS KOSONG
        # =====================================================

        df = df.dropna(
            how="all"
        )

        # =====================================================
        # 11. HAPUS BARIS TOTAL / JUMLAH
        # =====================================================

        df = df[
            ~df.astype(str)
            .apply(
                lambda row:
                row.str.upper()
                .str.contains(
                    r"TOTAL|JUMLAH",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]


        # 12. KODE -> STRING
        #
        # Hanya kolom Kode yang diubah menjadi string.
        # Kolom lainnya tidak diubah.
        # =====================================================

        if "Kode" in df.columns:

            df["Kode"] = (
                df["Kode"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

            # Pastikan Kode benar-benar object/string
            df["Kode"] = df["Kode"].astype(object)
    
        # =====================================================
        # 13. BERSIHKAN NAMA BARANG
        # =====================================================

        if "Nama Barang" in df.columns:

            df["Nama Barang"] = (
                df["Nama Barang"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # =====================================================
        # 14. STOCK PCS -> NUMERIC
        #
        # Header tetap "Stock PCS"
        # =====================================================

        if "Stock PCS" in df.columns:

            df["Stock PCS"] = pd.to_numeric(
                df["Stock PCS"],
                errors="coerce"
            ).fillna(0)

        # =====================================================
        # 15. STOCK AKHIR -> NUMERIC
        #
        # Bisa menangani:
        # Stock Akhir
        # Stock Akhir PCS
        # Stock Akhir KRT
        # dll.
        # =====================================================

        stock_akhir_columns = [
            col
            for col in df.columns
            if str(col).startswith("Stock Akhir")
        ]

        for col in stock_akhir_columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        # =====================================================
        # 16. HARGA -> NUMERIC
        # =====================================================

        harga_columns = [
            col
            for col in df.columns
            if str(col).startswith("Harga")
        ]

        for col in harga_columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        # =====================================================
        # 17. JUMLAH-RP -> NUMERIC
        # =====================================================

        jumlah_columns = [
            col
            for col in df.columns
            if str(col).startswith("Jumlah-Rp")
        ]

        for col in jumlah_columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        # =====================================================
        # 18. RESET INDEX
        # =====================================================

        df = df.reset_index(
            drop=True
        )

        # =====================================================
        # DEBUG
        # =====================================================

        print("\nDATA:")
        print(
            df.head(10)
        )

        print("\nDEBUG KODE:")
        print(
            df["Kode"].head(20).tolist()
        )

        print("DTYPE KODE:")
        print(
            df["Kode"].dtype
        )

        print("=" * 80)

        return df

    # =========================================================
    # GET MAPPING HEADERS
    #
    # File yang masuk adalah FILE HASIL NORMALISASI.
    #
    # Jadi langsung baca baris pertama sebagai header.
    # TIDAK menjalankan normalize().
    # =========================================================

    def get_mapping_headers(self, filepath):

        print("=" * 80)

        print("GET MAPPING HEADERS")

        print(
            "FILEPATH:",
            filepath
        )

        # =====================================================
        # BACA FILE HASIL NORMALISASI
        # =====================================================

        df = pd.read_excel(
            filepath,
            header=0
        )

        # =====================================================
        # BACA HEADER SAJA
        # =====================================================

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

        # =====================================================
        # DEBUG
        # =====================================================

        print("\nHASIL MAPPING HEADERS:")

        print(headers)

        print("\nJUMLAH HEADER:")

        print(
            len(headers)
        )

        print("=" * 80)

        return headers