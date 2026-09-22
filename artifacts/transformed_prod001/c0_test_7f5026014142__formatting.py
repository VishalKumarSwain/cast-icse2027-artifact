class Solution:

    def waterOverflow(self, k, r, c):
        z = [k]
        for i in range(r - 1):
            q = [0] * (len(z) + 1)
            for j in range(len(z)):
                a = max(0, (z[j] - 1) / 2)
                q[j] += a
                q[j + 1] += a
            z = q
        return round(min(1, z[c - 1]), 6)
