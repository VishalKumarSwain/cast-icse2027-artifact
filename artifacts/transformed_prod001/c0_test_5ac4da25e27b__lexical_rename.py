def process_annotated_comment(remaining_lines):
    """
    Must be called once we visit an annotated comment, to get the remaining
    parts of a statement written on multiple lines.
    """
    result_renamed = []
    for line in remaining_lines:
        stripped_line = line.strip()
        if stripped_line:
            result_renamed.append(stripped_line)
    return ' '.join(result_renamed)
