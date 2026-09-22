from collections import defaultdict

MyDict = defaultdict(int)
input()
for i in list(map(int, input().split())):
    MyDict[i] += 1
if list(MyDict.values()).count(1) + list(MyDict.values()).count(2) != len(MyDict):
    print("NO")
    exit()
inc, dec = ([], [])
for i in MyDict.keys():
    inc.append(i)
    if MyDict[i] == 2:
        dec.append(i)
print("YES\n" + str(len(inc)))
print(*sorted(inc))
print(str(len(dec)))
print(*sorted(dec, reverse=True))
