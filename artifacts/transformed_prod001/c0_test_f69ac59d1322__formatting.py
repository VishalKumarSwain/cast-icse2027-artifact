def convert(y, m, d):
    if m <= 2:
        m += 12
        y -= 1
    mjd = int(365.25 * y) + y // 400 - y // 100 + int(30.59 * (m - 2)) + d - 678912
    return mjd


while 1:
    y1, m1, d1, y2, m2, d2 = map(int, input().split())
    if y1 == -1:
        break
    print(convert(y2, m2, d2) - convert(y1, m1, d1))
