
class Scan_Query:
    def __init__(self, n, q):
        self.q = q
        self.n = n
        self.data = [1 << 31 - 1] * MAXN
        self.query = [None] * q
        self.result = [None] * q

    def update(self, i, x):
        self.data[i + MAXN] = x

        j = i + MAXN
        while True:
            j //= 2
            self.data[j] = min(self.data[2 * j], self.data[2 * j + 1])
            if j == 1:
                break

    def find(self, s, t):
        left = s + MAXN
        right = t + MAXN - 1

        ans = 1 << 31 - 1
        while left <= right:
            if left & 1:
                ans = min(ans, self.data[left])
                left += 1

            if right & 1:
                ans = min(ans, self.data[right])
                right -= 1

            left //= 2
            right //= 2

        return ans


if __name__ == '__main__':
    n, q = map(int, input().split())
    scan_query = Scan_Query(n, q)
    i = 0
    while i < q:
        com, x, y = map(int, input().split())

        if com == 0:
            scan_query.update(x, y)
        else:
            s, t = x, y
            scan_query.result[i] = scan_query.find(s, t + 1)
        i += 1

    for i in range(q):
        if scan_query.query[i] is None:
            continue
        print(scan_query.result[i])