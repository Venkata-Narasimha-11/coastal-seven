"""
Practice Program 1: FizzBuzz
Rule:
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both 3 and 5, print "FizzBuzz"
- Otherwise, print the number
"""

def fizzbuzz(limit: int = 50) -> list[str]:
    results = []
    for num in range(1, limit + 1):
        if num % 3 == 0 and num % 5 == 0:
            results.append("FizzBuzz")
        elif num % 3 == 0:
            results.append("Fizz")
        elif num % 5 == 0:
            results.append("Buzz")
        else:
            results.append(str(num))
    return results


if __name__ == "__main__":
    print("=== FizzBuzz (1 to 30) ===")
    for item in fizzbuzz(30):
        print(item, end=" ")
    print()
