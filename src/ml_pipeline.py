import sqlite3
import pandas as pd

from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "sap_booking.db"


def train_model():

    # Connect to database
    connection = sqlite3.connect(DB_PATH)

    # Load tables
    bookings = pd.read_sql_query(
        "SELECT * FROM bookings",
        connection
    )

    resources = pd.read_sql_query(
        "SELECT * FROM resources",
        connection
    )

    employees = pd.read_sql_query(
        "SELECT * FROM employees",
        connection
    )

    projects = pd.read_sql_query(
        "SELECT * FROM projects",
        connection
    )

    connection.close()

    # Merge booking information
    training_data = bookings.merge(
        resources,
        on="resource_id",
        how="left"
    )

    training_data = training_data.merge(
        employees,
        on="employee_id",
        how="left"
    )

    training_data = training_data.merge(
        projects,
        left_on="project_id_x",
        right_on="project_id",
        how="left"
    )

    # Select ML data
    ml_data = training_data[
        [
            "department_x",
            "role",
            "project_id_x",
            "location_y",
            "resource_type"
        ]
    ].copy()

    # Features
    X = ml_data[
        [
            "department_x",
            "role",
            "project_id_x",
            "location_y"
        ]
    ]

    # Target
    y = ml_data["resource_type"]

    # Categorical columns
    categorical_features = [
        "department_x",
        "role",
        "project_id_x",
        "location_y"
    ]

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ]
    )

    # Complete ML pipeline
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced"
                )
            )
        ]
    )

    # Train
    model.fit(X, y)

    return model


if __name__ == "__main__":

    model = train_model()

    print("ML pipeline trained successfully!")