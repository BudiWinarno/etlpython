from services.normalize.base import BaseNormalizer


class LK000146StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Hapus footer mulai dari baris yang mengandung M_TGL
        footer_mask = df.astype(str).apply(
            lambda row: row.str.upper().str.contains(
                r"M_TGL",
                regex=True,
                na=False
            ).any(),
            axis=1
        )

        if footer_mask.any():
            footer_index = footer_mask.idxmax()
            df = df.iloc[:footer_index]

        # Product Code menjadi string
        if "Product Code" in df.columns:
            df = self.to_string(df, "Product Code")

        # Tambah kolom qty_pcs = Q_AKHIR_CT × ISI
        df["qty_pcs"] = (
            df["Q_AKHIR_CT"].fillna(0).astype(float)
            * df["ISI"].fillna(0).astype(float)
        )

        return df.reset_index(drop=True)