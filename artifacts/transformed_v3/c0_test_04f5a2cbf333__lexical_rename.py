def create_string(n, k, a):
    """
    Create a string of length n with 'a's and two 'b's.
    The position of the 'b's is determined by the variables k and a.
    """
    c_renamed = k - a * (a - 1) // 2
    s = ['a' for _ in range(n)]
    s[n - c_renamed], s[n - a - 1] = 'b', 'b'
    return ''.join(s)

# Example usage:
n = 10  # Length of the string
k = 5   # Some value to calculate c
a = 3   # Some value to calculate c and position of the second 'b'

result = create_string(n, k, a)
print(result)
