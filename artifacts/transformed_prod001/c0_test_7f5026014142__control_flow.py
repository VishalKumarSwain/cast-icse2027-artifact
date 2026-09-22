class Solution:

	def waterOverflow(self, k, r, c):
		z = [k]
		for i in range(r - 1):
			q = [0] * (len(z) + 1)
			j = 0
			while j < len(z):
				a = max(0, (z[j] - 1) / 2)
				q[j] += a
				q[j + 1] += a
				j += 1
			z = q
		return round(min(1, z[c - 1]), 6)
