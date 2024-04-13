import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models import humanname
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FHIR Server Configuration
settings = {
    'app_id': 'my_streamlit_app',
    'api_base': 'http://hapi.fhir.org/baseR4/'  # Use your FHIR server URL
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
    patient.birthDate = FHIRDate(datetime.strptime(f"{form_data['year']}-{form_data['month']}-01", "%Y-%B-%d").date().isoformat())
    return patient

def save_patient_to_fhir(patient):
    try:
        patient.create(smart.server)
        logger.info("Patient saved to FHIR server.")
        st.success("Patient data saved to FHIR server successfully!")
    except Exception as e:
        logger.error(f"Failed to save patient: {e}")
        st.error(f"Error saving to FHIR server: {e}")

def fetch_all_patients():
    search = Patient.where(struct={})
    results = search.perform_resources(smart.server)
    return results

def delete_patient(patient_id):
    patient = Patient.read(patient_id, smart.server)
    try:
        patient.delete()
        logger.info(f"Deleted patient {patient_id}")
        st.success('Patient deleted successfully!')
    except Exception as e:
        logger.error(f"Failed to delete patient {patient_id}: {e}")
        st.error(f"Failed to delete patient: {e}")

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

# Data Visualization
if selected == "Data Visualization":
    st.header("Patient Information Visualization")
    all_patients = fetch_all_patients()
    if all_patients:
        for patient in all_patients:
            st.text(f"Patient Name: {patient.name[0].given[0]} {patient.name[0].family}, Birth Date: {patient.birthDate}")
            if st.button('Delete', key=patient.id):
                delete_patient(patient.id)
    else:
        st.write("No patients found.")
