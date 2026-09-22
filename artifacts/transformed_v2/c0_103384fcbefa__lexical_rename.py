(n, m) = list(map(int, input().split()))
p_renamed = set()
for i in range(m):
	p_renamed.add(tuple(map(int, input().split())))
if len(p_renamed) == 1:
	print('YES')
	exit(0)
(x, y) = p_renamed.pop()
notx = []
noty = []
for (a, b) in p_renamed:
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
