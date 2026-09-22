N,X=map(int,input().split())
m_min_renamed=None
for n in range(N):
    m=int(input())
    X-=m
    if m_min_renamed==None or m_min_renamed>m:
        m_min_renamed=m
print(N+X//m_min_renamed)
