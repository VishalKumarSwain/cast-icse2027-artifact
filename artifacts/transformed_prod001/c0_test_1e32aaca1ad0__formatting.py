if __name__ == "__main__":
    r, c = map(int, raw_input().strip().split())
    for i in xrange(1, r + 1):
        print(i + ((i + 10) % 2)) * 5 - (
            4
            if c == 1
            else 0 if c == 2 else -3 if c == 3 else 3 * (i % 2) if c == 4 else 1
        )
