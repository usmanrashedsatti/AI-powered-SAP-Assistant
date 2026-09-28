import sqlite3
import pandas as pd
from pathlib import Path

# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Locations of our data and database folders
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

# Make sure the database folder exists
DATABASE_DIR.mkdir(exist_ok=True)

# Database file
DB_PATH = DATABASE_DIR / "sap_booking.db"


def create_database():

    # Connect to SQLite database
    connection = sqlite3.connect(DB_PATH)

    # Read CSV files
    employees = pd.read_csv(DATA_DIR / "employees.csv")
    projects = pd.read_csv(DATA_DIR / "projects.csv")
    resources = pd.read_csv(DATA_DIR / "resources.csv")
    bookings = pd.read_csv(DATA_DIR / "bookings.csv")

    # Store the data in SQLite tables
    employees.to_sql(
        "employees",
        connection,
        if_exists="replace",
        index=False
    )

    projects.to_sql(
        "projects",
        connection,
        if_exists="replace",
        index=False
    )

    resources.to_sql(
        "resources",
        connection,
        if_exists="replace",
        index=False
    )

    bookings.to_sql(
        "bookings",
        connection,
        if_exists="replace",
        index=False
    )

    # Close database connection
    connection.close()

    print("Database created successfully!")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    create_database()