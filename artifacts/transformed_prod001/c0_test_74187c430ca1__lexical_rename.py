
import sys

previous_limit_renamed = sys.gettrace()
overflow_detected = False

def check_overflow(frame, event, arg, nesting=[0]):
    if event == 'call':
        nesting[0] += 1
        if nesting[0] > recursionlimit:
            overflow_detected = True
    elif event == 'return':
        nesting[0] -= 1
        if nesting[0] < 0:
            nesting[0] = 0
    return check_overflow

sys.settrace(check_overflow)
huge_stuff_that_may_overflow()
sys.settrace(previous_limit_renamed)
if overflow_detected:
    print("integer overflow occurred :(")
