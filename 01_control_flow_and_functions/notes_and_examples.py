"""
Part 1: Control Flow & Functions
Coverage:
- if / elif / else
- while / for loops, break / continue / pass, range()
- List comprehensions
- Defining functions, default parameters, *args, **kwargs
- Returning multiple values
- Lambda functions
- Variable scope & LEGB rule
"""

# ==========================================
# 1. CONTROL FLOW (if / elif / else)
# ==========================================
def check_score(score: float) -> str:
    if score >= 90:
        return "Grade A"
    elif score >= 75:
        return "Grade B"
    elif score >= 50:
        return "Grade C"
    else:
        return "Needs Improvement"


# ==========================================
# 2. LOOPS & LOOP CONTROL
# ==========================================
def demonstrate_loops():
    print("--- For loop with range() ---")
    for i in range(1, 6):
        if i == 2:
            print(f"Skipping {i} with continue")
            continue
        if i == 5:
            print(f"Stopping at {i} with break")
            break
        print(f"Value: {i}")

    print("\n--- While loop ---")
    count = 3
    while count > 0:
        print(f"Countdown: {count}")
        count -= 1
    else:
        print("Countdown finished!")


# ==========================================
# 3. LIST COMPREHENSIONS
# ==========================================
# Syntax: [expression for item in iterable if condition]
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares_of_evens = [x**2 for x in numbers if x % 2 == 0]


# ==========================================
# 4. FUNCTIONS: *args, **kwargs, Multiple Return Values
# ==========================================
def calculate_stats(*numbers: float, precision: int = 2) -> tuple[float, float, float]:
    """Accepts any number of positional arguments (*args) and keyword config."""
    if not numbers:
        return 0.0, 0.0, 0.0
    total = sum(numbers)
    average = round(total / len(numbers), precision)
    maximum = max(numbers)
    # Returning multiple values as a tuple
    return total, average, maximum


def print_user_profile(user_id: int, **details):
    """**kwargs collects arbitrary key-value pairs into a dictionary."""
    print(f"User ID: {user_id}")
    for key, value in details.items():
        print(f" - {key.capitalize()}: {value}")


# ==========================================
# 5. LAMBDA FUNCTIONS
# ==========================================
square = lambda x: x ** 2
sort_by_length = sorted(["apple", "banana", "kiwi", "fig"], key=lambda word: len(word))


# ==========================================
# 6. SCOPE: LEGB RULE (Local -> Enclosing -> Global -> Built-in)
# ==========================================
global_var = "I am Global"

def outer_function():
    enclosing_var = "I am Enclosing"

    def inner_function():
        local_var = "I am Local"
        print(f"Inside inner(): {local_var} | {enclosing_var} | {global_var}")

    inner_function()


if __name__ == "__main__":
    print("=== Demo 1: Grade Check ===")
    print(check_score(82))

    print("\n=== Demo 2: Loops ===")
    demonstrate_loops()

    print("\n=== Demo 3: List Comprehension ===")
    print(f"Even squares: {squares_of_evens}")

    print("\n=== Demo 4: *args & Multiple Return ===")
    total, avg, high = calculate_stats(10, 25, 40, 55, precision=1)
    print(f"Total: {total}, Avg: {avg}, Max: {high}")

    print("\n=== Demo 5: **kwargs ===")
    print_user_profile(101, name="Narasimha", role="Developer", status="Active")

    print("\n=== Demo 6: Scope Demo ===")
    outer_function()
