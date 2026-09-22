import sys
import heapq
from collections import defaultdict, deque

# Constants
MOD_renamed = 10**9 + 7
INF = float('inf')

def inp():
    return int(sys.stdin.readline())

def inpl():
    return list(map(int, sys.stdin.readline().split()))

def main():
    n = inp()
    a = list(map(lambda x: int(x) - 1, sys.stdin.readline().split()))

    max_count_heap = []
    min_count_heap = []
    max_count_to_remove = []
    min_count_to_remove = []
    value_count = defaultdict(int)
    unique_values = set()

    result = 0

    for i, x in enumerate(a):
        if value_count[x] > 0:
            heapq.heappush(max_count_to_remove, -value_count[x])
            heapq.heappush(min_count_to_remove, value_count[x])

        value_count[x] += 1
        unique_values.add(x)

        heapq.heappush(max_count_heap, -value_count[x])
        heapq.heappush(min_count_heap, value_count[x])

        while max_count_heap and max_count_to_remove and -max_count_heap[0] == max_count_to_remove[0]:
            heapq.heappop(max_count_heap)
            heapq.heappop(max_count_to_remove)

        while min_count_heap and min_count_to_remove and min_count_heap[0] == min_count_to_remove[0]:
            heapq.heappop(min_count_heap)
            heapq.heappop(min_count_to_remove)

        max_count = -max_count_heap[0]
        min_count = min_count_heap[0]
        unique_value_count = len(unique_values)

        if max_count - min_count == 1:
            max_count_contribution = i + 1 - unique_value_count *  min_count
            if max_count_contribution  == max_count:
                result = i + 1

        elif min_count == 1 and unique_value_count + 1 == i:
            result = i + 1

    print(result)

if __name__ == "__main__":
    main()
