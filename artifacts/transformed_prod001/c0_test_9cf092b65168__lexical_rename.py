def print_table(data, headings=None, banner=None, footnote=None):
    # Here creates the "lines" list where the print function will put its content.
    lines_renamed = []

    #  !body
    if banner:
        lines_renamed.append(banner)
    if headings:
        lines_renamed.append('\t'.join(headings))
    for k, v in data.items():
        if not isinstance(k, str):
            k = str(k)  
        if not isinstance(v, list):
            v = [str(i) for i in v]
        lines_renamed.append('\t'.join([k] + v))
    if footnote:
        lines_renamed.append(footnote)

    # Here prints to the standard output.
    return '\n'.join(lines_renamed)
