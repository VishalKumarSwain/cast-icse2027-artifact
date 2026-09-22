class Solution:

    def stringPartition(ob, S, a, b):
        l = 1
        ans = ""
        while l < len(S):
            left = S[0:l]
            right = S[l:]
            lefti = int(left)
            righti = int(right)
            if lefti % a == 0 and righti % b == 0:
                ans = str(left) + " " + str(right)
                break
            l = l + 1
        if ans == "":
            return -1
        return ans
