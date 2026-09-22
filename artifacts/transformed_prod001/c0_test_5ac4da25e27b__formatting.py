def process_annotated_comment(remaining_lines):
    """
    Must be called once we visit an annotated comment, to get the remaining
    parts of a statement written on multiple lines.
    """
    result = []
    for line in remaining_lines:
        stripped_line = line.strip()
        if stripped_line:
            result.append(stripped_line)
    return " ".join(result)
