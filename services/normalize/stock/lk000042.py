import pandas as pd

from services.normalize.base import BaseNormalizer


class LK000042StockNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = pd.read_excel(filepath)

        return df