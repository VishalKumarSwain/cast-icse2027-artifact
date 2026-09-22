def sort_with_operations(a):
    sorted_a_renamed = sorted(a)
    n = len(a)
    operations = 0
    
    # Find the first position where the elements are out of order
    for i in range(n):
        if a[i] != sorted_a_renamed[i]:
            break
    
    # If all elements are in order, no operations are needed
    if i == n - 1:
        return 0
    
    # Find the last position where the elements are out of order
    for j in range(n - 1, i - 1, -1):
        if a[j] != sorted_a_renamed[j]:
            break
    
    # Sort the subarray from i+1 to j in ascending order
    while i < j:
        a[i], a[j] = a[j], a[i]
        i += 1
        j -= 1
    
    # Swap the elements at the positions i and n-1-i
    a[i], a[n-1-i] = a[n-1-i], a[i]
    
    return operations

if __name__ == "__main__":
    t = int(input())
    for _ in range(t):
        n = int(input())
        a = list(map(int, input().split()))
        operations = sort_with_operations(a)
        print(operations)
