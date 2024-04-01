import calendar
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

# Assuming 'database.py' contains SQLAlchemy setup and CRUD operations
from database import db_session, insert_period_data, fetch_all_periods, get_period_data

# ---------------- SETTINGS ----------------
patient_info_categories = ["Name", "Age", "Diagnosis"]
treatment_info = ["Treatment Plan", "Medication", "Follow-up Schedule"]
page_title = "Patient Information Tracker"
page_icon = ":hospital:"
layout = "centered"
# ------------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(f"{page_title} {page_icon}")

# Dropdown values for selecting the period
years = [datetime.today().year - i for i in range(100)]
months = list(calendar.month_name[1:])

# Hide Streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Navigation menu
selected = option_menu(None, ["Data Entry", "Data Visualization"], icons=["pencil-fill", "bar-chart-fill"], orientation="horizontal")

# Input & Save Patient Information
if selected == "Data Entry":
    st.header("Data Entry for Patient")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Birth Month:", months, index=0, key="month")
        col2.selectbox("Select Birth Year:", years, index=0, key="year")

        with st.expander("Patient Information"):
            for info in patient_info_categories:
                if info == "Age":
                    st.number_input(f"{info}:", min_value=0, max_value=120, key=info)
                else:
                    st.text_input(f"{info}:", key=info)
        with st.expander("Treatment Information"):
            for treatment in treatment_info:
                st.text_input(f"{treatment}:", key=treatment)
        comment = st.text_area("Comment:", placeholder="Enter a comment here...")

        if st.form_submit_button("Save Data"):
            # Convert form data to a dictionary
            form_data = {info: st.session_state[info] for info in patient_info_categories + treatment_info}
            form_data["comment"] = comment
            form_data["period"] = f"{st.session_state['year']}_{st.session_state['month']}"
            
            # Insert data into database
            insert_period_data(form_data)
            st.success("Data saved successfully!")

# Plot Patient Information
if selected == "Data Visualization":
    st.header("Patient Information Visualization")
    period = st.selectbox("Select Period:", fetch_all_periods())

    if st.button("Plot Period"):
        period_data = get_period_data(period)
        # Visualization logic here
        # For example, display patient names and ages as a simple list for now
        if period_data:
            for patient in period_data:
                st.write(f"Patient Name: {patient['name']}, Age: {patient['age']}")
        else:
            st.write("No data available for this period.")

# Cleanup session on exit
def cleanup():
    db_session.remove()

st.on_session_end(cleanup)
