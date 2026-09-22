class Solution:

	def waterOverflow(self, k, r, c):
		z_renamed = [k]
		for i in range(r - 1):
			q = [0] * (len(z_renamed) + 1)
			for j in range(len(z_renamed)):
				a = max(0, (z_renamed[j] - 1) / 2)
				q[j] += a
				q[j + 1] += a
			z_renamed = q
		return round(min(1, z_renamed[c - 1]), 6)
