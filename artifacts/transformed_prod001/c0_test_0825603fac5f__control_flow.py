import math
_ = 0
while _ < int(input()):
	n = int(input())
	a = list(map(int, input().split()))
	b = a[0]
	for i in a:
		b = math.gcd(b, i)
	print(n * b)
	_ += 1
