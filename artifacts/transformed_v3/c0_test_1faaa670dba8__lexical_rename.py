# Function to check if a number is prime
def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

# Function to generate the i-th prime number
def generate_nth_prime(n):
    count_renamed = 0
    num = 1
    while True:
        num += 1
        if is_prime(num):
            count_renamed += 1
            if count_renamed == n:
                return num

# Main function to calculate the sum of the first n prime numbers
def sum_of_primes(n):
    total_sum = 0
    for i in range(1, n + 1):
        total_sum += generate_nth_prime(i)
    return total_sum

# Main loop to process multiple datasets
while True:
    n = int(input())
    if n == 0:
        break
    print(sum_of_primes(n))
