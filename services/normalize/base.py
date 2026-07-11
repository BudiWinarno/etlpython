import pandas as pd

class BaseNormalizer:

    def read_excel(self, filepath):

        return pd.read_excel(filepath, header=None)
    
    def to_string(self, df, column):

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.replace(".0", "", regex=False)
            )

        return df
    
    def read_excel_with_header(self, filepath):

        return pd.read_excel(filepath)