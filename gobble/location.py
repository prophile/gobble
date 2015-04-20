def compute_location(source, index):
    if not source:
        return (1, 1)
    if index >= len(source):
        return source.count('\n') + 2, 1
    preceding_newlines = source.count('\n', 0, index + 1)
    previous_newline_index = source.rfind('\n', 0, index + 1)
    if previous_newline_index == -1:
        previous_newline_index = 0
    return preceding_newlines + 1, index - previous_newline_index + 1
