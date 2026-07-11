from services.normalize.lk000019 import LK000019Normalizer
from services.normalize.lk000105 import LK000105Normalizer
from services.normalize.lk000117 import LK000117Normalizer

class NormalizeFactory:

    @staticmethod
    def get(agent_code):

        if agent_code == "LK-000019":
            return LK000019Normalizer()

        elif agent_code == "LK-000105":
            return LK000105Normalizer()
        
        elif agent_code == "LK-000117":
            return LK000117Normalizer()

        raise Exception("Template belum didukung")