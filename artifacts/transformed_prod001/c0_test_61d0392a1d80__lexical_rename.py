from collections import defaultdict
MyDict_renamed = defaultdict(int)
input()
for i in list(map(int, input().split())):
	MyDict_renamed[i] += 1
if list(MyDict_renamed.values()).count(1) + list(MyDict_renamed.values()).count(2) != len(MyDict_renamed):
	print('NO')
	exit()
(inc, dec) = ([], [])
for i in MyDict_renamed.keys():
	inc.append(i)
	if MyDict_renamed[i] == 2:
		dec.append(i)
print('YES\n' + str(len(inc)))
print(*sorted(inc))
print(str(len(dec)))
print(*sorted(dec, reverse=True))
