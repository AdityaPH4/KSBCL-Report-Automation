def assign_serial_numbers(df, starting_serial):

    df.insert(
        0,
        "Serial No.",
        range(
            starting_serial,
            starting_serial + len(df)
        )
    )

    return df