(n, m) = list(map(int, input().split()))
p = set()
i = 0
while i < (m):
	p.add(tuple(map(int, input().split())))
	i += 1
if len(p) == 1:
	print('YES')
	exit(0)
(x, y) = p.pop()
notx = []
noty = []
for (a, b) in p:
	if x not in (a, b):
		notx.append(set([a, b]))
	if y not in (a, b):
		noty.append(set([a, b]))
(inotx, inoty) = (False, False)
if notx:
	inotx = set.intersection(*notx)
if noty:
	inoty = set.intersection(*noty)
if inotx or inoty:
	print('YES')
else:
	print('NO')
