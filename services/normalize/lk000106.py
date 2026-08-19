import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000106InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        # =========================================================
        # BACA EXCEL
        # HEADER SUDAH DI BARIS PERTAMA
        # =========================================================

        df = self.read_excel_with_header(filepath)

        # =========================================================
        # CLEAN HEADER
        # =========================================================

        df.columns = [
            str(col)
            .replace("\n", " ")
            .strip()
            for col in df.columns
        ]

        # =========================================================
        # FORMAT TANGGAL
        # HASIL: MM/DD/YYYY
        # =========================================================

        # Ganti "Tanggal" sesuai nama kolom tanggal di Excel
        if "Tanggal" in df.columns:

            df["Tanggal"] = pd.to_datetime(
                df["Tanggal"],
                errors="coerce"
            )

            df["Tanggal"] = df["Tanggal"].dt.strftime(
                "%m/%d/%Y"
            )

        # =========================================================
        # KONVERSI
        # AMBIL DARI ITEM AGENT MAPPING
        # AGENT ID = 39
        # MATCH DENGAN KOLOM Code
        # =========================================================

        from database import SessionLocal
        from models.item_agent_mapping import ItemAgentMapping

        agent_id = 39

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
        # MATCH:
        # Excel "Code"
        #      ↓
        # kode_sku_agent
        # =========================================================

        if "Code" in df.columns:

            df["Konversi"] = (
                df["Code"]
                .fillna("")
                .astype(str)
                .str.strip()
                .map(mapping_konversi)
            )

        # =========================================================
        # POSISI KONVERSI
        # SETELAH "Penjualan Lsn"
        # =========================================================

        if (
            "Konversi" in df.columns
            and "Penjualan Lsn" in df.columns
        ):

            columns = list(df.columns)

            columns.remove("Konversi")

            index = columns.index("Penjualan Lsn")

            columns.insert(
                index + 1,
                "Konversi"
            )

            df = df[columns]

        # =========================================================
        # HITUNG PENJUALAN PCS
        # =========================================================

        if (
            "Penjualan Pcs" in df.columns
            and "Konversi" in df.columns
        ):

            penjualan_pcs = pd.to_numeric(
                df["Penjualan Pcs"],
                errors="coerce"
            ).fillna(0)

            konversi = pd.to_numeric(
                df["Konversi"],
                errors="coerce"
            ).fillna(0)

            if "Penjualan Karton" in df.columns:

                penjualan_karton = pd.to_numeric(
                    df["Penjualan Karton"],
                    errors="coerce"
                ).fillna(0)

                mask_karton = penjualan_karton > 0

                penjualan_pcs.loc[mask_karton] = (
                    penjualan_karton.loc[mask_karton]
                    * konversi.loc[mask_karton]
                )

            if "Penjualan Lsn" in df.columns:

                penjualan_lsn = pd.to_numeric(
                    df["Penjualan Lsn"],
                    errors="coerce"
                ).fillna(0)

                mask_lsn = (
                    (penjualan_lsn > 0)
                    & ~mask_karton
                )

                penjualan_pcs.loc[mask_lsn] = (
                    penjualan_lsn.loc[mask_lsn]
                    * konversi.loc[mask_lsn]
                )

            df["Penjualan Pcs"] = penjualan_pcs

        # =========================================================
        # RESET INDEX
        # =========================================================

        df = df.reset_index(drop=True)

        return df