def _process_raw_lines(raw_lines):
    buffer = []
    for line in raw_lines:
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        comment_index = line.find("!")
        if comment_index != -1:
            line = line[:comment_index]
        line = line.rstrip()
        if line.endswith("&"):
            buffer.append(line.rstrip("&").strip())
        else:
            buffer.append(line)
            yield " ".join(buffer)
            buffer = []
    if buffer:
        yield " ".join(buffer)
