t = int(input())
for i in range(t):
	n = int(input())
	b = []
	a = [int(i) for i in input().split()]
	i = 0
	while i < len(a):
		if a[i] not in b:
			b += [a[i]]
		i += 1
	for i in range(len(b)):
		print(b[i], end=' ')
	print()
