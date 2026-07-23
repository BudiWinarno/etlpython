from services.normalize.stock.lk000019 import LK000019StockNormalizer
from services.normalize.stock.lk000105 import LK000105StockNormalizer
from services.normalize.stock.lk000148 import LK000148StockNormalizer
from services.normalize.lk000075 import LK000075Normalizer
from services.normalize.stock.lk000115 import LK000115StockNormalizer
from services.normalize.stock.lk000048 import LK000048StockNormalizer
from services.normalize.stock.lk000065 import LK000065StockNormalizer
from services.normalize.stock.lk000093 import LK000093StockNormalizer
from services.normalize.stock.lk000118 import LK000118StockNormalizer
from services.normalize.stock.lk000121 import LK000121StockNormalizer
from services.normalize.stock.lk000032 import LK000032StockNormalizer
from services.normalize.stock.lk000108 import LK000108StockNormalizer
from services.normalize.stock.lk000145 import LK000145StockNormalizer
from services.normalize.stock.lk000146 import LK000146StockNormalizer
from services.normalize.stock.lk000153 import LK000153StockNormalizer

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
        
        elif agent_code == "LK-000118":
            return LK000118StockNormalizer()
        
        elif agent_code == "LK-000121":
            return LK000121StockNormalizer()
        
        elif agent_code == "LK-000032":
            return LK000032StockNormalizer()
        
        elif agent_code == "LK-000108":
            return LK000108StockNormalizer()
        
        elif agent_code == "LK-000145":
            return LK000145StockNormalizer()
        
        elif agent_code == "LK-000146":
            return LK000146StockNormalizer()
        
        elif agent_code == "LK-000153":
            return LK000153StockNormalizer()

        raise Exception("Template stock belum didukung")