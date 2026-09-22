from math import log2

x = int(input())
o = []
e = []
c = 0
while True:
    if log2(x + 1) <= 1:
        break
    o.append(str(int(log2(x + 1))))
    c += 1
    x = x + 1

    if log2(x - 1) <= 1:
        break
    e.append(str(int(log2(x - 1))))
    c += 1
    x = x - 1

o.reverse()
print(c)
if c % 2 == 1:
    print(" ".join(o))
else:
    print(" ".join(e))
