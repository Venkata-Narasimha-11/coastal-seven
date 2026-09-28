# Python Intensive Learning Plan: September 18, 2026

Welcome! Below is the roadmap and file index prepared for today's learning sessions.

---

## 📅 Schedule Overview

| Session | Topic | Key Coverage | Learning Outcome |
| :--- | :--- | :--- | :--- |
| **1st Half** *(Before Lunch)* | **Control Flow & Functions** | `if/elif/else`, `for/while` loops, `break/continue/pass`, `range()`, list comprehensions, `*args`, `**kwargs`, multiple returns, lambdas, LEGB scope rule | Confidently write structured logic and modular, reusable functions. |
| **2nd Half** *(Post Lunch)* | **Data Structures + File Handling** | Lists, Tuples, Sets, Dictionaries, JSON & CSV I/O, `try/except` handling, Capstone: Contact Book with JSON persistence | Master Python's 4 core data structures, handle file I/O safely, and build persistent applications. |

---

## 📂 Workspace Structure & Code Files

### 1️⃣ First Half: Control Flow & Functions
Located in: [`01_control_flow_and_functions/`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions)

- [`notes_and_examples.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/notes_and_examples.py)
  - Interactive walkthrough covering condition branches, loop control, list comprehensions, `*args` / `**kwargs`, lambdas, and LEGB scope.
- [`fizzbuzz.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/fizzbuzz.py)
  - Classic modulus and conditional branching problem (multiples of 3, 5, and both).
- [`prime_checker.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/prime_checker.py)
  - Prime detection optimized to $\mathcal{O}(\sqrt{n})$ plus list comprehension range generation.
- [`temp_converter.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/temp_converter.py)
  - Conversions between Celsius, Fahrenheit, and Kelvin with input validation.

### 2️⃣ Second Half: Data Structures & File Handling
Located in: [`02_data_structures_and_file_handling/`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling)

- [`data_structures_examples.py`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling/data_structures_examples.py)
  - Lists (CRUD, slicing, `sort()`, `reverse()`), Tuples (immutability, unpacking), Sets (union, intersection, difference), Dictionaries (`.get()`, `.items()`, comprehensions), and nested objects.
- [`file_handling_examples.py`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling/file_handling_examples.py)
  - Structured file storage with `json` (`dump`/`load`), `csv` (`DictReader`/`DictWriter`), and safe execution with `try/except/else/finally`.
- [`contact_book.py`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling/contact_book.py)
  - **Capstone Project**: Full CRUD CLI contact book with automatic JSON persistence and error handling.

---

## 🚀 How to Run the Programs

```powershell
# Run Part 1 Examples & Practice Programs
python 01_control_flow_and_functions/notes_and_examples.py
python 01_control_flow_and_functions/fizzbuzz.py
python 01_control_flow_and_functions/prime_checker.py
python 01_control_flow_and_functions/temp_converter.py

# Run Part 2 Examples & Contact Book
python 02_data_structures_and_file_handling/data_structures_examples.py
python 02_data_structures_and_file_handling/file_handling_examples.py
python 02_data_structures_and_file_handling/contact_book.py
```
