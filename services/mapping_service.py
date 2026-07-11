def mapping(df, mapping_dict):

    # Rename header
    df = df.rename(columns=mapping_dict)

    # Ambil hanya kolom yang ada di mapping
    df = df[list(mapping_dict.values())]

    return df