
# tests


def test_1():
    a_renamed = "aba"
    s = "abbaab"
    assert string_constructing(a_renamed, s) == 6, "BAABAA"


def test_2():
    a_renamed = "aba"
    s = "a"
    assert string_constructing(a_renamed, s) == 3, "A"


def test_3():
    a_renamed = "aba"
    s = "abaa"
    assert string_constructing(a_renamed, s) == 4, "AABA"


if __name__ == "__main__":
    for i in [1,2,3]:
        locals()['test_%s()' % i]()
