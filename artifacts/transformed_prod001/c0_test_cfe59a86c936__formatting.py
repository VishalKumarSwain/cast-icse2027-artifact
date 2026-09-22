def __init__(self):
    self.memo = {}


def knapSack(self, W, wt, val, n):

    if n == 0 or W == 0:
        return 0
    if n in self.memo:
        return self.memo[n]
    else:
        if wt[n - 1] > W:
            self.memo[n] = self.knapSack(W, wt, val, n - 1)
            return self.memo[n]

        self.memo[n] = max(
            self.knapSack(W, wt, val, n - 1),
            (val[n - 1] + self.knapSack(W - wt[n - 1], wt, val, n - 1)),
        )
        return self.memo[n]
