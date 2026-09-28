import streamlit as st
import sqlite3
import pandas as pd

from ml_pipeline import train_model
from resource_recommender import recommend_resources
model = train_model()

st.set_page_config(
    page_title="AI-Powered SAP Booking Assistant",
    page_icon="🚗",
    layout="wide"
)

st.title("AI-Powered SAP Booking Assistant")

st.write(
    "Use this application to find and book resources "
    "using machine learning and business rules."
)

# Connect to database
connection = sqlite3.connect("../database/sap_booking.db")

# Load employees
employees = pd.read_sql_query(
    "SELECT * FROM employees",
    connection
)

connection.close()

# Employee selection
st.subheader("Employee Information")

employee_id = st.selectbox(
    "Select Employee",
    employees["employee_id"]
)

selected_employee = employees[
    employees["employee_id"] == employee_id
].iloc[0]

st.write("**Employee Name:**", selected_employee["name"])
st.write("**Department:**", selected_employee["department"])
st.write("**Role:**", selected_employee["role"])
# Load projects
connection = sqlite3.connect("../database/sap_booking.db")

projects = pd.read_sql_query(
    "SELECT * FROM projects WHERE status = 'Active'",
    connection
)

connection.close()

# Project selection
st.subheader("Project Information")

project_id = st.selectbox(
    "Select Project",
    projects["project_id"]
)

selected_project = projects[
    projects["project_id"] == project_id
].iloc[0]

st.write("**Project Name:**", selected_project["project_name"])
st.write("**Location:**", selected_project["location"])
st.write("**Department:**", selected_project["department"])
# Booking Requirements
st.subheader("Booking Requirements")

required_capacity = st.number_input(
    "Required Capacity",
    min_value=1,
    max_value=20,
    value=4,
    step=1
)

booking_date = st.date_input(
    "Booking Date"
)

col1, col2 = st.columns(2)

with col1:
    start_time = st.time_input(
        "Start Time"
    )

with col2:
    end_time = st.time_input(
        "End Time"
    )

st.write("**Required Capacity:**", required_capacity)
st.write("**Booking Date:**", booking_date)
st.write("**Start Time:**", start_time)
st.write("**End Time:**", end_time)
find_resource = st.button(
    "🔎 Find Available Resource",
    type="primary"
)


if find_resource:

    # Prepare request for ML model
    new_request = pd.DataFrame({
        "department_x": [selected_employee["department"]],
        "role": [selected_employee["role"]],
        "project_id_x": [project_id],
        "location_y": [selected_project["location"]]
    })

    # ML prediction
    prediction = model.predict(new_request)
    predicted_type = prediction[0]

    st.success(
        f"ML Prediction: {predicted_type}"
    )

    # Find available resources
    recommendations = recommend_resources(
        resource_type=predicted_type,
        location=selected_project["location"],
        required_capacity=required_capacity,
        booking_date=str(booking_date),
        start_time=str(start_time),
        end_time=str(end_time)
    )

    if recommendations.empty:

        st.warning(
            "No suitable resources are currently available."
        )

    else:

        st.subheader("Recommended Resources")

        st.dataframe(
            recommendations,
            use_container_width=True
        )

        selected_resource = st.selectbox(
            "Select Resource to Book",
            recommendations["resource_id"]
        )

        confirm_booking = st.button(
            "✅ Confirm Booking",
            type="primary"
        )

        if confirm_booking:

            from booking_engine import create_booking

            booking_result = create_booking(
                employee_id=employee_id,
                resource_id=selected_resource,
                project_id=project_id,
                booking_date=str(booking_date),
                start_time=str(start_time),
                end_time=str(end_time)
            )

            st.success(booking_result)    