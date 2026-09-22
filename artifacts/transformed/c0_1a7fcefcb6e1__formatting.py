def solve():
    n, m, q = [int(x) for x in input().split()]
    busCount = 0
    dicti = {}
    ls = []
    for i in range(q):
        temp = [x for x in input().split()]
        ls.append(temp)
    for temp in ls:
        ch = temp[0]
        i = int(temp[1])
        if ch == "+":
            if i in dicti:
                print("Inconsistent")
                return
            elif busCount < m:
                dicti[i] = 1
                busCount += 1
            else:
                print("Inconsistent")
                return
        if ch == "-":
            if i in dicti:
                del dicti[i]
                busCount -= 1
            else:
                print("Inconsistent")
                return
    print("Consistent")


t = int(input())
while t != 0:
    solve()
    t -= 1
