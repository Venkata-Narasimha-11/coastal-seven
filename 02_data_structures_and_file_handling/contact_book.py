"""
Capstone Project: Contact Book with JSON Persistence
Features:
- Add new contact (Name, Phone, Email, Tags/Category)
- View all contacts in a formatted table
- Search contact by name or phone
- Update an existing contact
- Delete a contact
- Automatic JSON persistence (loads on start, saves on change)
- Robust try/except error handling
"""

import json
import os
import sys

DEFAULT_STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")


class ContactBook:
    def __init__(self, storage_path: str = DEFAULT_STORAGE_FILE):
        self.storage_path = storage_path
        self.contacts: dict[str, dict] = {}
        self.load_from_file()

    def load_from_file(self) -> None:
        """Loads contacts from JSON file if it exists."""
        if not os.path.exists(self.storage_path):
            self.contacts = {}
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self.contacts = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Warning] Failed to load contacts from {self.storage_path}: {e}")
            self.contacts = {}

    def save_to_file(self) -> bool:
        """Saves current contacts dictionary to JSON file."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, indent=4)
            return True
        except IOError as e:
            print(f"[Error] Failed to save contacts: {e}")
            return False

    def add_contact(self, name: str, phone: str, email: str, category: str = "General") -> bool:
        """Adds a contact; key is normalized name."""
        key = name.strip().lower()
        if not key:
            print("[Error] Name cannot be empty.")
            return False

        if key in self.contacts:
            print(f"[Warning] Contact '{name}' already exists. Use update instead.")
            return False

        self.contacts[key] = {
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "category": category.strip()
        }
        self.save_to_file()
        print(f"[OK] Contact '{name}' added successfully.")
        return True

    def list_contacts(self) -> None:
        """Displays all contacts."""
        if not self.contacts:
            print("\n[!] No contacts found. Contact book is empty.")
            return

        print("\n" + "=" * 65)
        print(f"{'NAME':<20} | {'PHONE':<15} | {'CATEGORY':<10} | {'EMAIL'}")
        print("-" * 65)
        for contact in sorted(self.contacts.values(), key=lambda c: c["name"]):
            print(f"{contact['name']:<20} | {contact['phone']:<15} | {contact['category']:<10} | {contact['email']}")
        print("=" * 65)

    def search_contact(self, query: str) -> list[dict]:
        """Searches contacts by name, phone, or email substring."""
        query = query.strip().lower()
        matches = [
            c for c in self.contacts.values()
            if query in c["name"].lower() or query in c["phone"] or query in c["email"].lower()
        ]
        return matches

    def update_contact(self, name: str, phone: str = None, email: str = None, category: str = None) -> bool:
        """Updates fields of an existing contact."""
        key = name.strip().lower()
        if key not in self.contacts:
            print(f"[Error] Contact '{name}' not found.")
            return False

        if phone:
            self.contacts[key]["phone"] = phone.strip()
        if email:
            self.contacts[key]["email"] = email.strip()
        if category:
            self.contacts[key]["category"] = category.strip()

        self.save_to_file()
        print(f"[OK] Contact '{self.contacts[key]['name']}' updated successfully.")
        return True

    def delete_contact(self, name: str) -> bool:
        """Deletes a contact by name."""
        key = name.strip().lower()
        if key in self.contacts:
            deleted = self.contacts.pop(key)
            self.save_to_file()
            print(f"[OK] Contact '{deleted['name']}' deleted.")
            return True
        else:
            print(f"[Error] Contact '{name}' does not exist.")
            return False


def run_demo():
    """Runs a non-interactive demonstration of ContactBook functionality."""
    print("\n--- Running ContactBook Automated Demonstration ---")
    book = ContactBook()

    # Add sample contacts
    book.add_contact("Venkat Narasimha", "+91 98765 43210", "venkat@example.com", "Work")
    book.add_contact("Anita Sharma", "+91 91234 56789", "anita@example.com", "Personal")
    book.add_contact("Rohan Verma", "+91 99887 76655", "rohan@example.com", "Work")

    # List all
    book.list_contacts()

    # Search
    print("\nSearch for 'anita':")
    results = book.search_contact("anita")
    for r in results:
        print(f" - Found: {r['name']} ({r['phone']})")

    # Update
    book.update_contact("Anita Sharma", phone="+91 90000 11111")

    # Delete sample
    book.delete_contact("Rohan Verma")

    # Final list
    book.list_contacts()


def interactive_cli():
    """CLI Menu loop for manual user interaction."""
    book = ContactBook()

    menu = """
    +====================================+
    |        CONTACT BOOK MENU           |
    +====================================+
    | 1. View All Contacts               |
    | 2. Add New Contact                 |
    | 3. Search Contact                  |
    | 4. Update Contact                  |
    | 5. Delete Contact                  |
    | 6. Run Demo                        |
    | 7. Exit                            |
    +====================================+
    """

    while True:
        print(menu)
        choice = input("Enter choice (1-7): ").strip()

        try:
            if choice == "1":
                book.list_contacts()
            elif choice == "2":
                name = input("Enter Name: ")
                phone = input("Enter Phone: ")
                email = input("Enter Email: ")
                category = input("Enter Category (e.g. Work/Personal): ") or "General"
                book.add_contact(name, phone, email, category)
            elif choice == "3":
                q = input("Enter Name, Phone, or Email to search: ")
                results = book.search_contact(q)
                if results:
                    print(f"\nFound {len(results)} match(es):")
                    for r in results:
                        print(f" - {r['name']} | {r['phone']} | {r['email']} ({r['category']})")
                else:
                    print("No matches found.")
            elif choice == "4":
                name = input("Enter Name of contact to update: ")
                phone = input("New phone (leave blank to keep unchanged): ") or None
                email = input("New email (leave blank to keep unchanged): ") or None
                cat = input("New category (leave blank to keep unchanged): ") or None
                book.update_contact(name, phone, email, cat)
            elif choice == "5":
                name = input("Enter Name of contact to delete: ")
                book.delete_contact(name)
            elif choice == "6":
                run_demo()
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please choose between 1 and 7.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # If standard input is connected and interactive, run CLI, else run demo
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        # Default to demo check if running headlessly or test
        run_demo()
