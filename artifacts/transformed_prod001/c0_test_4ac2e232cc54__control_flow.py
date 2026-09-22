import sys
input = sys.stdin.readline
_ = 0
while _ < int(input()):
	(x, y, n) = list(map(int, input().split()))
	if n < x:
		print(y)
		continue
	if n % x == y:
		print(n)
		continue
	r = n % x
	if r >= y:
		n -= r - y
	else:
		n = n - n % x
		n -= x - y
	print(n)
	_ += 1
