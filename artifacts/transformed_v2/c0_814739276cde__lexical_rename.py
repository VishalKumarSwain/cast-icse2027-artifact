def _process_raw_lines(raw_lines):
    buffer_renamed = []
    for line in raw_lines:
        line = line.strip()
        if not line or line.startswith('!'):
            continue
        comment_index = line.find('!')
        if comment_index != -1:
            line = line[:comment_index]
        line = line.rstrip()
        if line.endswith('&'):
            buffer_renamed.append(line.rstrip('&').strip())
        else:
            buffer_renamed.append(line)
            yield ' '.join(buffer_renamed)
            buffer_renamed = []
    if buffer_renamed:
        yield ' '.join(buffer_renamed)
