from services.normalize.base import BaseNormalizer

class LK000145InvoiceNormalizer(BaseNormalizer):

    def normalize(self, filepath):

        return self.read_excel_with_header(filepath)