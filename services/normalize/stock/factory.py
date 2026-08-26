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
from services.normalize.stock.lk000136 import LK000136StockNormalizer
from services.normalize.stock.lk000117 import LK000117StockNormalizer
from services.normalize.stock.lk000139 import LK000139StockNormalizer
from services.normalize.stock.lk000021 import LK000021StockNormalizer
from services.normalize.stock.lk000124 import LK000124StockNormalizer
from services.normalize.stock.lk000131 import LK000131StockNormalizer
from services.normalize.stock.lk000132 import LK000132StockNormalizer
from services.normalize.stock.lk000170 import LK000170StockNormalizer
from services.normalize.stock.lk000059 import LK000059StockNormalizer
from services.normalize.stock.lk000127 import LK000127StockNormalizer
from services.normalize.stock.lk000010 import LK000010StockNormalizer
from services.normalize.stock.lk000035 import LK000035StockNormalizer
from services.normalize.stock.lk000037 import LK000037StockNormalizer
from services.normalize.stock.lk000042 import LK000042StockNormalizer
from services.normalize.stock.lk000064 import LK000064StockNormalizer
from services.normalize.stock.lk000106 import LK000106StockNormalizer
from services.normalize.stock.lk000107 import LK000107StockNormalizer
from services.normalize.stock.lk000138 import LK000138StockNormalizer
from services.normalize.stock.lk000143 import LK000143StockNormalizer
from services.normalize.stock.lk000150 import LK000150StockNormalizer
from services.normalize.stock.lk000151 import LK000151StockNormalizer
from services.normalize.stock.lk000155 import LK000155StockNormalizer
from services.normalize.stock.lk000167 import LK000167StockNormalizer
from services.normalize.stock.lk000003 import LK000003StockNormalizer
from services.normalize.stock.lk000020 import LK000020StockNormalizer
from services.normalize.stock.lk000031 import LK000031StockNormalizer
from services.normalize.stock.lk000045 import LK000045StockNormalizer
from services.normalize.stock.lk000109 import LK000109StockNormalizer

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
        
        elif agent_code == "LK-000136":
            return LK000136StockNormalizer()
        
        elif agent_code == "LK-000117":
            return LK000117StockNormalizer()
        
        elif agent_code == "LK-000139":
            return LK000139StockNormalizer()
        
        elif agent_code == "LK-000021":
            return LK000021StockNormalizer()
        
        elif agent_code == "LK-000124":
            return LK000124StockNormalizer()
        
        elif agent_code == "LK-000131":
            return LK000131StockNormalizer()
        
        elif agent_code == "LK-000132":
            return LK000132StockNormalizer()
        
        elif agent_code == "LK-000170":
            return LK000170StockNormalizer()
        
        elif agent_code == "LK-000059":
            return LK000059StockNormalizer()
        
        elif agent_code == "LK-000127":
            return LK000127StockNormalizer()
        
        elif agent_code == "LK-000010":
            return LK000010StockNormalizer()
        
        elif agent_code == "LK-000035":
            return LK000035StockNormalizer()
        
        elif agent_code == "LK-000037":
            return LK000037StockNormalizer()
        
        elif agent_code == "LK-000042":
            return LK000042StockNormalizer()
        
        elif agent_code == "LK-000064":
            return LK000064StockNormalizer()
        
        elif agent_code == "LK-000106":
            return LK000106StockNormalizer()
        
        elif agent_code == "LK-000107":
            return LK000107StockNormalizer()
        
        elif agent_code == "LK-000138":
            return LK000138StockNormalizer()
        
        elif agent_code == "LK-000143":
            return LK000143StockNormalizer()
        
        elif agent_code == "LK-000150":
            return LK000150StockNormalizer()
        
        elif agent_code == "LK-000151":
            return LK000151StockNormalizer()
        
        elif agent_code == "LK-000155":
            return LK000155StockNormalizer()
        
        elif agent_code == "LK-000167":
            return LK000167StockNormalizer()
        
        elif agent_code == "LK-000003":
            return LK000003StockNormalizer()
        
        elif agent_code == "LK-000020":
            return LK000020StockNormalizer()
        
        elif agent_code == "LK-000031":
            return LK000031StockNormalizer()
        
        elif agent_code == "LK-000045":
            return LK000045StockNormalizer()
        
        elif agent_code == "LK-000109":
            return LK000109StockNormalizer()

        raise Exception("Template stock belum didukung")