"""
Part 2A: Python Core Data Structures
Coverage:
- Lists (CRUD, indexing, slicing, sort(), reverse())
- Tuples (immutability, packing/unpacking)
- Sets (uniqueness, union, intersection, difference)
- Dictionaries (.get(), .items(), .keys(), comprehensions)
- Nested structures
"""

def demonstrate_lists():
    print("--- 1. Lists (Mutable, Ordered) ---")
    fruits = ["apple", "banana", "cherry"]

    # CRUD
    fruits.append("date")          # Create (append)
    fruits.insert(1, "blueberry")  # Create (insert at index)
    first_item = fruits[0]         # Read (indexing)
    sub_slice = fruits[1:4]        # Read (slicing)
    fruits[2] = "blackberry"       # Update
    removed = fruits.pop(1)        # Delete by index
    fruits.remove("apple")         # Delete by value

    # Sort & Reverse
    nums = [42, 12, 89, 5, 23]
    nums.sort()                    # In-place ascending sort
    print(f"Sorted in-place: {nums}")
    nums.reverse()                 # In-place reverse
    print(f"Reversed: {nums}")


def demonstrate_tuples():
    print("\n--- 2. Tuples (Immutable, Ordered) ---")
    point = (10, 20, 30)
    # Unpacking
    x, y, z = point
    print(f"Unpacked: x={x}, y={y}, z={z}")

    # Immutability: point[0] = 50 -> TypeError!
    # Useful for dictionary keys or fixed coordinates/records


def demonstrate_sets():
    print("\n--- 3. Sets (Mutable, Unique, Unordered) ---")
    frontend_skills = {"HTML", "CSS", "JavaScript", "React"}
    backend_skills = {"Python", "Django", "SQL", "JavaScript"}

    print("Union (|):", frontend_skills | backend_skills)
    print("Intersection (&):", frontend_skills & backend_skills)
    print("Difference (frontend - backend):", frontend_skills - backend_skills)
    print("Symmetric Difference (^):", frontend_skills ^ backend_skills)


def demonstrate_dictionaries():
    print("\n--- 4. Dictionaries (Key-Value, Mutable) ---")
    student = {
        "id": "STU101",
        "name": "Narasimha",
        "courses": ["Python", "Algorithms"],
        "active": True
    }

    # Safe retrieval with .get()
    gpa = student.get("gpa", "N/A")
    print(f"Student GPA (safe fallback): {gpa}")

    # Iteration methods
    print("Keys:", list(student.keys()))
    print("Values:", list(student.values()))
    for key, value in student.items():
        print(f"  {key}: {value}")

    # Dictionary Comprehension
    grades = {"Alice": 85, "Bob": 72, "Charlie": 94, "David": 60}
    passed_students = {name: score for name, score in grades.items() if score >= 75}
    print(f"Passed Students: {passed_students}")


def demonstrate_nested():
    print("\n--- 5. Nested Structures ---")
    company = {
        "engineering": [
            {"id": 1, "name": "Aarav", "role": "Backend Engineer"},
            {"id": 2, "name": "Bhavna", "role": "Frontend Engineer"},
        ],
        "design": [
            {"id": 3, "name": "Chirag", "role": "UI/UX Designer"},
        ]
    }
    # Accessing nested item
    lead_dev = company["engineering"][0]["name"]
    print(f"First engineer name: {lead_dev}")


if __name__ == "__main__":
    demonstrate_lists()
    demonstrate_tuples()
    demonstrate_sets()
    demonstrate_dictionaries()
    demonstrate_nested()
