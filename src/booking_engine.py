import sqlite3
import pandas as pd
from pathlib import Path

# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Location of our database
DB_PATH = BASE_DIR / "database" / "sap_booking.db"


def check_available_resources(
    resource_type,
    booking_date,
    start_time,
    end_time
):
    """
    Find resources that are available for a requested
    date and time period.
    """

    # Connect to our database
    connection = sqlite3.connect(DB_PATH)

    # SQL query to find available resources
    query = """
    SELECT
        r.resource_id,
        r.resource_type,
        r.resource_name,
        r.location,
        r.status,
        r.capacity
    FROM resources r
    WHERE r.resource_type = ?
    AND r.status = 'Available'
    AND r.resource_id NOT IN (
        SELECT resource_id
        FROM bookings
        WHERE booking_date = ?
        AND status IN ('Confirmed', 'Completed')
        AND start_time < ?
        AND end_time > ?
    )
    """

    # Run the query
    result = pd.read_sql_query(
        query,
        connection,
        params=(
            resource_type,
            booking_date,
            end_time,
            start_time
        )
    )

    # Close the database
    connection.close()

    return result
def create_booking(
    employee_id,
    resource_id,
    project_id,
    booking_date,
    start_time,
    end_time
):
    """
    Create a new booking after checking that the resource
    is available.
    """

    connection = sqlite3.connect(DB_PATH)
    employee_check = pd.read_sql_query(
        "SELECT employee_id FROM employees WHERE employee_id = ?",
        connection,
        params=(employee_id,)
    )

    if employee_check.empty:
        connection.close()
        return "Invalid employee ID. Employee does not exist."
    project_check = pd.read_sql_query(
        "SELECT project_id FROM projects WHERE project_id = ?",
        connection,
        params=(project_id,)
    )

    if project_check.empty:
        connection.close()
        return "Invalid project ID. Project does not exist."
    resource_check = pd.read_sql_query(
        "SELECT resource_id FROM resources WHERE resource_id = ?",
        connection,
        params=(resource_id,)
    )

    if resource_check.empty:
        connection.close()
        return "Invalid resource ID. Resource does not exist."

    # Check whether the resource is available
    availability_query = """
    SELECT resource_id
    FROM resources
    WHERE resource_id = ?
    AND status = 'Available'
    AND resource_id NOT IN (
        SELECT resource_id
        FROM bookings
        WHERE booking_date = ?
        AND status IN ('Confirmed', 'Completed')
        AND start_time < ?
        AND end_time > ?
    )
    """

    available = pd.read_sql_query(
        availability_query,
        connection,
        params=(
            resource_id,
            booking_date,
            end_time,
            start_time
        )
    )

    # Stop if the resource is not available
    if available.empty:
        connection.close()
        return "Resource is not available for this time."

    # Generate a new booking ID
    last_booking = pd.read_sql_query(
        "SELECT booking_id FROM bookings ORDER BY booking_id DESC LIMIT 1",
        connection
    )

    if last_booking.empty:
        new_booking_id = "B0001"
    else:
        last_id = last_booking.iloc[0]["booking_id"]
        number = int(last_id[1:]) + 1
        new_booking_id = f"B{number:04d}"

    # Create the new booking
    new_booking = pd.DataFrame([{
        "booking_id": new_booking_id,
        "employee_id": employee_id,
        "resource_id": resource_id,
        "project_id": project_id,
        "booking_date": booking_date,
        "start_time": start_time,
        "end_time": end_time,
        "status": "Confirmed"
    }])

    # Save booking into database
    new_booking.to_sql(
        "bookings",
        connection,
        if_exists="append",
        index=False
    )

    connection.close()

    return f"Booking confirmed successfully! Booking ID: {new_booking_id}"


# Test the booking engine
if __name__ == "__main__":

    result = check_available_resources(
        resource_type="Vehicle",
        booking_date="2026-09-22",
        start_time="08:00",
        end_time="17:00"
    )

    print("\nAvailable Resources:")
    print(result)
    booking_result = create_booking(
        employee_id="E001",
        resource_id="V001",
        project_id="P001",
        booking_date="2026-09-22",
        start_time="08:00",
        end_time="17:00"
    )

    print("\nBooking Result:")
    print(booking_result)