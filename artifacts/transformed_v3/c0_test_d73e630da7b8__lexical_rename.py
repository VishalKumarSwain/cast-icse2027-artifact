def collect_signatures(signatures):
    """
    Return a dictionary with all signatures and their counts.

    Args:
        signatures (list): A list of function signatures.

    Returns:
        dict: A dictionary with signatures as keys and their counts as values.
    """
    signature_counts_renamed = {}
    for signature in signatures:
        if signature in signature_counts_renamed:
            signature_counts_renamed[signature] += 1
        else:
            signature_counts_renamed[signature] = 1
    return signature_counts_renamed
