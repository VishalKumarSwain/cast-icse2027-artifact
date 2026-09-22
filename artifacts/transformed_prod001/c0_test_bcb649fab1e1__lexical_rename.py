(n, m) = list(map(int, input().split()))
g_renamed = [[] for _ in range(n)]
a = list(map(int, input().split()))
b = list(map(int, input().split()))
for _ in range(m):
	(x, y) = list(map(int, input().split()))
	x -= 1
	y -= 1
	g_renamed[x].append(y)
	g_renamed[y].append(x)

# Optional: you can add some input validation here to ensure that the graph is undirected
# and that the graph is connected, if that's what you want

# If you want to print the graph, you can do it like this:
for i in range(n):
	print(f"Vertex {i}: {g_renamed[i]}")

# Or, if you want to perform some operation on the graph, you can do it here
