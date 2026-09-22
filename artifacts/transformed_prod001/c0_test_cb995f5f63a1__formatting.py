def print_table(objects, display_fields):
    """
    Print a list of objects in a table format.

    :param objects:
        List of object dicts

    :param display_fields:
        Ordered list of 2-tuples of (field, display_name) used
        to translate field names for display
    """

    # Create column headers
    headers = [field_name for field_name, _ in display_fields]

    # Create table rows
    rows = []
    for obj in objects:
        row = []
        for field_name, _ in display_fields:
            field_value = obj.get(field_name)
            row.append(field_value)
        rows.append(row)

    # Print table
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
