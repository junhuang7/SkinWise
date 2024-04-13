import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models import humanname
from fhirclient.models.fhirdate import FHIRDate
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FHIR Server Configuration
settings = {
    'app_id': 'my_streamlit_app',
    'api_base': 'http://hapi.fhir.org/baseR4/'  # Replace with your FHIR server URL
}
smart = client.FHIRClient(settings=settings)

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

def create_fhir_patient(form_data):
    patient = Patient()
    name = humanname.HumanName()
    name.family = form_data['Name'].split()[-1]  # Family name is typically the last name
    name.given = [form_data['Name'].split()[0]]  # Given name is typically the first name
    patient.name = [name]
    # Ensure birthDate is in the correct format "YYYY-MM-DD"
    patient.birthDate = FHIRDate(datetime.strptime(f"{form_data['year']}-{form_data['month']}-01", "%Y-%B-%d").date().isoformat())
    return patient

def save_patient_to_fhir(patient):
    try:
        json_output = patient.as_json()
        logger.info(f"Patient JSON: {json_output}")  # Log the JSON output
        patient.create(smart.server)
        logger.info("Patient saved to FHIR server.")
    except client.server.FHIRServerException as e:  # More specific exception for server errors
        error_message = e.response.json()  # Assuming the server returns error details in JSON format
        logger.error(f"Server responded with an error: {error_message}")
        st.error(f"Error saving to FHIR server: {error_message}")
        raise
    except Exception as e:
        logger.error(f"General Error: {e}")
        st.error(f"An error occurred: {e}")
        raise

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
            form_data["year"] = st.session_state["year"]
            form_data["month"] = st.session_state["month"]
            
            # Create FHIR patient object
            fhir_patient = create_fhir_patient(form_data)
            # Save FHIR patient to server
            save_patient_to_fhir(fhir_patient)
            st.success("Patient data saved to FHIR server successfully!")

# Plot Patient Information (Simplified example to be replaced with actual FHIR fetch operations)
if selected == "Data Visualization":
    st.header("Patient Information Visualization")
    st.write("Note: Replace this section with actual data fetching and visualization based on FHIR data.")

# Example usage of FHIR client to fetch data would go here

# This application does not interact with a local database since all operations are assumed to be handled via FHIR.
