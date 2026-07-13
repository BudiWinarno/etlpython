from services.normalize.stock.lk000019 import LK000019StockNormalizer
from services.normalize.stock.lk000105 import LK000105StockNormalizer
from services.normalize.stock.lk000148 import LK000148StockNormalizer


class StockNormalizeFactory:

    @staticmethod
    def get(agent_code):

        if agent_code == "LK-000019":
            return LK000019StockNormalizer()
        
        elif agent_code == "LK-000105":
            return LK000105StockNormalizer()
        
        elif agent_code == "LK-000148":
            return LK000148StockNormalizer()

        raise Exception("Template stock belum didukung")