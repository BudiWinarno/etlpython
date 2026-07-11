import pandas as pd


def normalize_lk000019(filepath):

    # Baca tanpa header
    df = pd.read_excel(filepath, header=None)

    header_row = None

    # Cari baris yang berisi "Jenis"
    for i, row in df.iterrows():

        values = row.astype(str).tolist()

        if "Jenis" in values:
            header_row = i
            break

    if header_row is None:
        raise Exception("Header tidak ditemukan")

    # Jadikan baris tersebut sebagai header
    df.columns = df.iloc[header_row]

    # Hapus baris sebelum header
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    return df