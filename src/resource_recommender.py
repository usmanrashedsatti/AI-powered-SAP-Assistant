import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "sap_booking.db"


def recommend_resources(
    resource_type,
    location,
    required_capacity,
    booking_date,
    start_time,
    end_time
):
    connection = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        r.resource_id,
        r.resource_type,
        r.resource_name,
        r.location,
        r.capacity
    FROM resources r
    WHERE r.resource_type = ?
    AND r.location = ?
    AND r.capacity >= ?
    AND r.status = 'Available'
    AND r.resource_id NOT IN (
        SELECT resource_id
        FROM bookings
        WHERE booking_date = ?
        AND status IN ('Confirmed', 'Completed')
        AND start_time < ?
        AND end_time > ?
    )
    ORDER BY r.capacity ASC
    """

    result = pd.read_sql_query(
        query,
        connection,
        params=(
            resource_type,
            location,
            required_capacity,
            booking_date,
            end_time,
            start_time
        )
    )

    connection.close()

    return result