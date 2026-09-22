N,X=map(int,input().split())
m_min=None
n = 0
while n < N:
    m=int(input())
    X-=m
    if m_min==None or m_min>m:
        m_min=m
    n += 1
print(N+X//m_min)
