# tests


def test_1():
    a = "aba"
    s = "abbaab"
    assert string_constructing(a, s) == 6, "BAABAA"


def test_2():
    a = "aba"
    s = "a"
    assert string_constructing(a, s) == 3, "A"


def test_3():
    a = "aba"
    s = "abaa"
    assert string_constructing(a, s) == 4, "AABA"


if __name__ == "__main__":
    for i in [1, 2, 3]:
        locals()["test_%s()" % i]()
