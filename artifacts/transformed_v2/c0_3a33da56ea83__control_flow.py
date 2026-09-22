def is_lucky_number(n):
    """Check if a number is a lucky number (only contains digits 4 and 7)."""
    return all(digit in '47' for digit in str(n))

def generate_lucky_numbers(limit):
    """Generate all lucky numbers up to a given limit."""
    lucky_numbers = []
    j = 1
    while j < limit:
        if is_lucky_number(j):
            lucky_numbers.append(j)
        j += 1
    return lucky_numbers

def main():
    # Generate all lucky numbers up to 1000
    lucky_numbers = generate_lucky_numbers(1000)
    
    # Read input number
    a = input().strip()
    
    # Check if the input number itself is a lucky number
    if is_lucky_number(int(a)):
        print('YES')
    else:
        # Check divisibility by any lucky number
        if any(int(a) % lucky == 0 for lucky in lucky_numbers):
            print('YES')
        else:
            print('NO')

if __name__ == "__main__":
    main()
