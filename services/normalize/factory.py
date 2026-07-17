from services.normalize.lk000019 import LK000019Normalizer
from services.normalize.lk000105 import LK000105Normalizer
from services.normalize.lk000117 import LK000117Normalizer
from services.normalize.lk000075 import LK000075Normalizer
from services.normalize.lk000115 import LK000115Normalizer
from services.normalize.lk000148 import LK000148InvoiceNormalizer
from services.normalize.lk000048 import LK000048InvoiceNormalizer
from services.normalize.lk000065 import LK000065InvoiceNormalizer


class NormalizeFactory:

    @staticmethod
    def get(agent_code):

        if agent_code == "LK-000019":
            return LK000019Normalizer()

        elif agent_code == "LK-000105":
            return LK000105Normalizer()
        
        elif agent_code == "LK-000117":
            return LK000117Normalizer()
        
        elif agent_code == "LK-000075":
            return LK000075Normalizer()
        
        elif agent_code == "LK-000115":
            return LK000115Normalizer()
        
        elif agent_code == "LK-000148":
            return LK000148InvoiceNormalizer()
        
        elif agent_code == "LK-000048":
            return LK000048InvoiceNormalizer()
        
        elif agent_code == "LK-000065":
            return LK000065InvoiceNormalizer()

        raise Exception("Template belum didukung")