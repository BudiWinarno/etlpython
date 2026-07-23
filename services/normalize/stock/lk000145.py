from services.normalize.base import BaseNormalizer


class LK000145StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # Hapus footer M_TGL dan baris tanggal/UTAMA
        df = df[
            ~df.astype(str)
            .apply(
                lambda row: row.str.upper().str.contains(
                    r"M_TGL|A_TGL|GUD_NAME|UTAMA",
                    regex=True,
                    na=False
                ).any(),
                axis=1
            )
        ]

        # Product Code menjadi string
        if "Product Code" in df.columns:
            df = self.to_string(df, "Product Code")

        # Tambah kolom qty_pcs = Q_AKHIR_CT × ISI
        df["qty_pcs"] = (
            df["Q_AKHIR_CT"].fillna(0).astype(float)
            * df["ISI"].fillna(0).astype(float)
        )

        return df.reset_index(drop=True)