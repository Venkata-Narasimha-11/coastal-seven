"""
Practice Program 2: Prime Number Checker
Rule:
- A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.
- Optimized check: test divisors up to sqrt(n).
"""
import math

def is_prime(n: int) -> bool:
    """Checks if a given integer n is prime."""
    if n <= 1:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Check divisors from 5 up to sqrt(n), stepping by 6 (6k +/- 1)
    limit = int(math.isqrt(n))
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True


def find_primes_in_range(start: int, end: int) -> list[int]:
    """Returns a list of all primes between start and end inclusive using list comprehension."""
    return [num for num in range(start, end + 1) if is_prime(num)]


if __name__ == "__main__":
    test_numbers = [1, 2, 17, 20, 29, 49, 97, 100]
    print("=== Single Number Checks ===")
    for num in test_numbers:
        print(f"{num:3d} -> {'Prime' if is_prime(num) else 'Not Prime'}")

    print("\n=== Primes between 1 and 50 ===")
    print(find_primes_in_range(1, 50))
