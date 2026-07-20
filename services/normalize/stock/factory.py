from services.normalize.stock.lk000019 import LK000019StockNormalizer
from services.normalize.stock.lk000105 import LK000105StockNormalizer
from services.normalize.stock.lk000148 import LK000148StockNormalizer
from services.normalize.lk000075 import LK000075Normalizer
from services.normalize.stock.lk000115 import LK000115StockNormalizer
from services.normalize.stock.lk000048 import LK000048StockNormalizer
from services.normalize.stock.lk000065 import LK000065StockNormalizer
from services.normalize.stock.lk000093 import LK000093StockNormalizer


class StockNormalizeFactory:

    @staticmethod
    def get(agent_code):

        if agent_code == "LK-000019":
            return LK000019StockNormalizer()
        
        elif agent_code == "LK-000105":
            return LK000105StockNormalizer()
        
        elif agent_code == "LK-000148":
            return LK000148StockNormalizer()
        
        elif agent_code == "LK-000075":
            return LK000075Normalizer()
        
        elif agent_code == "LK-000115":
            return LK000115StockNormalizer()
        
        elif agent_code == "LK-000048":
            return LK000048StockNormalizer()
        
        elif agent_code == "LK-000065":
            return LK000065StockNormalizer()
        
        elif agent_code == "LK-000093":
            return LK000093StockNormalizer()

        raise Exception("Template stock belum didukung")