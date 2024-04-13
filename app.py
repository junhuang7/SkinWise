import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models import humanname
import logging

# Enhanced logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

# FHIR Server Configuration
settings = {
    'app_id': 'my_streamlit_app',
    'api_base': 'http://hapi.fhir.org/baseR4/'
}
smart = client.FHIRClient(settings=settings)

# Application settings and layouts
st.set_page_config(page_title="Patient Information Tracker", page_icon=":hospital:", layout="centered")
st.title("Patient Information Tracker :hospital:")

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

def format_date(fhir_date):
    if fhir_date is not None and hasattr(fhir_date, 'date'):
        return fhir_date.date.isoformat()
    return "No date available"

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
            patient_name = st.text_input("Name:")
            patient_age = st.number_input("Age:", min_value=0, max_value=120)
            patient_diagnosis = st.text_input("Diagnosis:")

        if st.form_submit_button("Save Data"):
            form_data = {
                'Name': patient_name,
                'Age': patient_age,
                'Diagnosis': patient_diagnosis,
                'year': st.session_state['year'],
                'month': st.session_state['month']
            }
            fhir_patient = create_fhir_patient(form_data)
            save_patient_to_fhir(fhir_patient)

# Data Visualization
if selected == "Data Visualization":
    st.header("Patient Information Visualization")
    all_patients = fetch_all_patients()
    if all_patients:
        for patient in all_patients:
            birth_date = format_date(patient.birthDate)
            st.text(f"Patient Name: {patient.name[0].given[0]} {patient.name[0].family}, Birth Date: {birth_date}")
            if st.button('Delete', key=patient.id):
                delete_patient(patient.id)
    else:
        st.write("No patients found.")
