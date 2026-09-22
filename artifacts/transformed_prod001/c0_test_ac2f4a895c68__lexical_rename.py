from math import log2
x_renamed = int(input())
o = []
e = []
c = 0
while True:
    if log2(x_renamed+1) <= 1:
        break
    o.append(str(int(log2(x_renamed+1))))
    c += 1
    x_renamed = x_renamed + 1

    if log2(x_renamed-1) <= 1:
        break
    e.append(str(int(log2(x_renamed-1))))
    c += 1
    x_renamed = x_renamed - 1

o.reverse()
print(c)
if c % 2 == 1:
    print(" ".join(o))
else:
    print(" ".join(e))
