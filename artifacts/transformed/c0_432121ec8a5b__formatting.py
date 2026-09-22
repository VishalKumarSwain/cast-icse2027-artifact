def check_course_blocks(course, expected_blocks, unexpected_blocks):
    """
    Check that the course has the expected blocks and does not have the unexpected blocks
    """
    for block in expected_blocks:
        if block not in course:
            return False
    for block in unexpected_blocks:
        if block in course:
            return False
    return True
