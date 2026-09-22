N, X = map(int, input().split())
m_min = None
for n in range(N):
    m = int(input())
    X -= m
    if m_min == None or m_min > m:
        m_min = m
print(N + X // m_min)
