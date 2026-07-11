from services.normalize.base import BaseNormalizer

class LK000019Normalizer(BaseNormalizer):

    def normalize(self, filepath):

        df = self.read_excel(filepath)

        header_row = None

        for i, row in df.iterrows():

            values = row.astype(str).tolist()

            if "Jenis" in values:

                header_row = i

                break

        if header_row is None:

            raise Exception("Header tidak ditemukan")

        df.columns = df.iloc[header_row]

        df = df.iloc[header_row + 1:].reset_index(drop=True)

        return df