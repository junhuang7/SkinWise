import streamlit as st
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

# Time handling
years = [datetime.today().year - i for i in range(100)]
months = list(calendar.month_name[1:])
days = list(range(1, 32))

# UI style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Menu options
selected = option_menu(None, ["Data Entry", "Patients"], icons=["pencil-fill", "bar-chart-fill"], orientation="horizontal")

def format_date(fhir_date):
    if fhir_date is not None and hasattr(fhir_date, 'date'):
        return fhir_date.date.isoformat()
    return "No date available"

def create_fhir_patient(form_data):
    patient = Patient()
    name = humanname.HumanName()
    name.family = form_data['Name'].split()[-1]
    name.given = [form_data['Name'].split()[0]]
    patient.name = [name]
    patient.birthDate = FHIRDate(form_data['BirthDate'])
    return patient

def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def save_patient_to_fhir(patient):
    try:
        result = patient.create(smart.server)
        logger.info(f"Patient saved to FHIR server: ID = {result['id']}, Name = {result.name[0].text}, Birth Date = {format_date(patient.birthDate)}")
        st.success("Patient data saved to FHIR server successfully!")
    except Exception as e:
        logger.error(f"Failed to save patient: {e}", exc_info=True)
        st.error(f"Error saving to FHIR server: {e}")

def fetch_patients(page):
    """Fetch patients with pagination."""
    search = Patient.where({'_count': '100', '_page': str(page)})
    results = search.perform_resources(smart.server)
    return results

def search_patients_by_name(name):
    try:
        search = Patient.where(struct={'name': name})
        results = search.perform_resources(smart.server)
        logger.info(f"Found {len(results)} patients by name search.")
        return results
    except Exception as e:
        logger.error(f"Failed to search patients by name: {e}", exc_info=True)
        return []

if selected == "Data Entry":
    st.header("Data Entry for Patient")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        day = col1.selectbox("Select Birth Day:", days, index=0)
        month = col2.selectbox("Select Birth Month:", months, index=0)
        year = col3.selectbox("Select Birth Year:", years, index=0)
        patient_name = st.text_input("Name:")
        patient_diagnosis = st.text_input("Diagnosis:")
        birth_date = datetime(year, months.index(month) + 1, day)
        age = calculate_age(birth_date)
        st.text(f"Calculated Age: {age}")

        if st.form_submit_button("Save Data"):
            form_data = {
                'Name': patient_name,
                'Diagnosis': patient_diagnosis,
                'BirthDate': birth_date.isoformat()
            }
            fhir_patient = create_fhir_patient(form_data)
            save_patient_to_fhir(fhir_patient)

if selected == "Patients":
    st.header("Patient Information Visualization")
    page_number = st.number_input("Select page number", min_value=1, value=1, step=1)
    if st.button("Fetch Patients"):
        patients = fetch_patients(page_number)
        if patients:
            for patient in patients:
                birth_date = format_date(patient.birthDate) if patient.birthDate else "Unknown"
                st.text(f"Patient ID: {patient.id}, Name: {patient.name[0].given[0]} {patient.name[0].family}, Birth Date: {birth_date}")
        else:
            st.write("No patients found or failed to fetch patients.")
