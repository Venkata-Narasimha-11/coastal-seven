"""Default Database Seeding Script.

Delegates to SIVORA luxury fashion catalog refresh.
"""

from scripts.seed_sivora_fashion import refresh_catalog

if __name__ == "__main__":
    refresh_catalog()
