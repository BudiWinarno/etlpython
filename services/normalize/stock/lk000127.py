import re

from services.normalize.base import BaseNormalizer
from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping


class LK000127StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel_with_header(filepath)

        # =============================
        # Pecah kolom OnSales
        # =============================
        def split_onsales(value):
            numbers = re.findall(r"\d+", str(value))

            qty_ctn = int(numbers[0]) if len(numbers) > 0 else 0
            qty_pcs = int(numbers[1]) if len(numbers) > 1 else 0

            return qty_ctn, qty_pcs

        df[["qty_ctn", "qty_pcs"]] = (
            df["OnSales"]
            .apply(split_onsales)
            .tolist()
        )

        # =============================
        # Ambil konversi dari master
        # =============================
        session = SessionLocal()

        mapping = {
            m.kode_sku_agent: int(m.item_box) if m.item_box is not None else 0
            for m in session.query(ItemAgentMapping).all()
        }

        session.close()

        df["konversi"] = (
            df["Item#"]
            .map(mapping)
            .fillna(0)
            .astype(int)
        )

        # =============================
        # Hitung Total PCS
        # =============================
        df["total_pcs"] = (
            df["qty_ctn"] * df["konversi"].fillna(0)
        ) + df["qty_pcs"]
        
        df["total_pcs"] = df["total_pcs"].astype(int)

        return df