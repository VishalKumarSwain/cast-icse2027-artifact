class Solution:

	def stringPartition(ob, S, a, b):
		l_renamed = 1
		ans = ''
		while l_renamed < len(S):
			left = S[0:l_renamed]
			right = S[l_renamed:]
			lefti = int(left)
			righti = int(right)
			if lefti % a == 0 and righti % b == 0:
				ans = str(left) + ' ' + str(right)
				break
			l_renamed = l_renamed + 1
		if ans == '':
			return -1
		return ans
