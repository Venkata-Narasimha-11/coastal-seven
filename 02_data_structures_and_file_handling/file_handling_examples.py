"""
Part 2B: File Handling (JSON & CSV) & Exception Handling
Coverage:
- json.dump, json.load, json.dumps, json.loads
- csv.reader, csv.writer, csv.DictReader, csv.DictWriter
- try / except / else / finally
"""
import csv
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_JSON = os.path.join(BASE_DIR, "sample_data.json")
SAMPLE_CSV = os.path.join(BASE_DIR, "sample_data.csv")


def demonstrate_json():
    print("--- 1. JSON Read & Write ---")
    data = {
        "batch": "2026-Python-Track",
        "total_modules": 8,
        "learners": [
            {"id": 1, "name": "Narasimha", "topics_completed": ["Control Flow", "Functions"]},
            {"id": 2, "name": "Priya", "topics_completed": ["Basics"]}
        ]
    }

    # Writing JSON to a file
    try:
        with open(SAMPLE_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"JSON written successfully to {SAMPLE_JSON}")

        # Reading JSON from file
        with open(SAMPLE_JSON, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        print(f"Loaded batch name: {loaded_data['batch']}")
        print(f"Learners count: {len(loaded_data['learners'])}")
    except IOError as e:
        print(f"File error occurred: {e}")


def demonstrate_csv():
    print("\n--- 2. CSV Read & Write ---")
    rows = [
        {"id": 101, "name": "Narasimha", "city": "Hyderabad", "score": 95},
        {"id": 102, "name": "Ananya", "city": "Bangalore", "score": 88},
        {"id": 103, "name": "Rahul", "city": "Pune", "score": 91}
    ]
    fieldnames = ["id", "name", "city", "score"]

    # Writing CSV with DictWriter
    try:
        with open(SAMPLE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV written successfully to {SAMPLE_CSV}")

        # Reading CSV with DictReader
        with open(SAMPLE_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            print("Reading CSV records:")
            for row in reader:
                print(f" - #{row['id']} {row['name']} ({row['city']}): {row['score']} pts")
    except Exception as e:
        print(f"Error handling CSV: {e}")


def demonstrate_try_except():
    print("\n--- 3. Basic try / except / else / finally ---")
    filename = "non_existent_file.txt"
    try:
        print(f"Attempting to open '{filename}'...")
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Handled error: '{filename}' does not exist on disk.")
    except Exception as err:
        print(f"Caught generic exception: {err}")
    else:
        print("Success: File read without errors!")
    finally:
        print("Finally block: Execution cleanup finished.")


if __name__ == "__main__":
    demonstrate_json()
    demonstrate_csv()
    demonstrate_try_except()
