import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime, date
import calendar
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models import humanname
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# FHIR Server Configuration
settings = {
    'app_id': 'my_streamlit_app',
    'api_base': 'http://hapi.fhir.org/baseR4/'
}
smart = client.FHIRClient(settings=settings)

# Streamlit page setup
st.set_page_config(page_title="Patient Information Tracker", page_icon=":hospital:", layout="centered")
st.title("Patient Information Tracker 🏥")

# UI style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Time handling
years = [datetime.today().year - i for i in range(100)]
months = list(calendar.month_name[1:])
days = list(range(1, 32))

def format_date(fhir_date):
    # Format the date to exclude time component.
    if fhir_date is not None and hasattr(fhir_date, 'date'):
        return fhir_date.date.strftime('%Y-%m-%d')
    return "No date available"

def create_fhir_patient(form_data):
    patient = Patient()
    name = humanname.HumanName()
    name.given = [form_data['First Name']]
    name.family = form_data['Family Name']
    patient.name = [name]
    patient.birthDate = FHIRDate(form_data['BirthDate'].split('T')[0])  # Use only the date part
    return patient

def save_patient_to_fhir(patient):
    try:
        result = patient.create(smart.server)
        if 'id' in result:
            patient_id = result['id']
            patient_name = f"{patient.name[0].given[0]} {patient.name[0].family}" if patient.name else "Name Unknown"
            patient_birth_date = format_date(patient.birthDate) if patient.birthDate else "Birth Date Unknown"
            logger.info(f"Patient saved to FHIR server: ID = {patient_id}, Name = {patient_name}, Birth Date = {patient_birth_date}")
            st.success("Patient data saved to FHIR server successfully!")
        else:
            logger.error("Failed to save patient: No ID returned")
            st.error("Error saving to FHIR server: No ID returned")
    except Exception as e:
        logger.error(f"Failed to save patient: {e}", exc_info=True)
        st.error(f"Error saving to FHIR server: {e}")

if 'fetch_clicked' not in st.session_state:
    st.session_state['fetch_clicked'] = False

if 'fetch_counter' not in st.session_state:
    st.session_state['fetch_counter'] = 0

def fetch_data():
    # Increment the counter to trigger a rerun
    st.session_state['fetch_counter'] += 1

#@st.cache_resource(ttl=300)  # Cache for 5 minutes
def fetch_patients():
    """Fetch the latest 20 patients sorted by creation date, requesting specific fields to improve performance."""
    search = Patient.where(struct={'_count': '20', '_sort': '-_lastUpdated', '_elements': 'id,name,birthDate'})
    results = search.perform_resources(smart.server)
    return results

# Menu options
selected = option_menu(None, ["Data Entry", "Patients"], icons=["pencil-fill", "bar-chart-fill"], orientation="horizontal")

if selected == "Data Entry":
    st.header("Data Entry for Patient")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        day = col1.selectbox("Select Birth Day:", days, index=0)
        month = col2.selectbox("Select Birth Month:", months, index=0)
        year = col3.selectbox("Select Birth Year:", years, index=0)
        col1, col2 = st.columns(2)
        first_name = col1.text_input("First Name:")
        family_name = col2.text_input("Family Name:")
        patient_diagnosis = st.text_input("Diagnosis:")
        birth_date = datetime(year, months.index(month) + 1, day)

        if st.form_submit_button("Save Data"):
            form_data = {
                'First Name': first_name,
                'Family Name': family_name,
                'Diagnosis': patient_diagnosis,
                'BirthDate': birth_date.isoformat()
            }
            fhir_patient = create_fhir_patient(form_data)
            save_patient_to_fhir(fhir_patient)

if selected == "Patients":
    st.header("Patient Information Visualization")
    
    # Button to trigger data fetching
    fetch_button = st.button('Fetch Latest Patients', on_click=fetch_data)

    # Use the counter to check for button presses
    if st.session_state['fetch_counter'] > 0:
        with st.spinner('Fetching latest patients...'):
            patients = fetch_patients()
            
            if patients:
                for patient in patients:
                    if patient.name and patient.birthDate:
                        given_name = patient.name[0].given[0] if patient.name[0].given else "Unknown"
                        family_name = patient.name[0].family if patient.name[0].family else "Unknown"
                        birth_date = format_date(patient.birthDate) if patient.birthDate else "Unknown"
                        patient_id = patient.id if patient.id else "Unknown ID"
                        st.text(f"Patient ID: {patient_id}, Name: {given_name} {family_name}, Birth Date: {birth_date}")
                    else:
                        patient_id = patient.id if patient.id else "Unknown ID"
                        st.text(f"Patient ID: {patient_id}, Data Incomplete")
            else:
                st.write("No patients found or failed to fetch patients.")

