import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, date
import calendar
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models import humanname
import logging

# Ensure logs are visible in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# FHIR Server Configuration
settings = {
    'app_id': 'my_streamlit_app',
    'api_base': 'http://hapi.fhir.org/baseR4/'
}
smart = client.FHIRClient(settings=settings)

# Application settings and layouts
st.set_page_config(page_title="Patient Information Tracker", page_icon=":hospital:", layout="centered")
st.title("Patient Information Tracker 🏥")

# Dropdown values for selecting the date
years = [datetime.today().year - i for i in range(100)]
months = list(calendar.month_name[1:])
days = list(range(1, 32))  # Assuming all months have up to 31 days

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
selected = option_menu(None, ["Data Entry", "Data Visualization", "Search Patients"], icons=["pencil-fill", "bar-chart-fill", "search"], orientation="horizontal")

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
        logger.info(f"Patient saved to FHIR server: ID = {result['id']}, Name = {patient.name[0].text}, Birth Date = {format_date(patient.birthDate)}")
        st.success("Patient data saved to FHIR server successfully!")
    except Exception as e:
        logger.error(f"Failed to save patient: {e}", exc_info=True)
        st.error(f"Error saving to FHIR server: {e}")

def fetch_all_patients():
    search = Patient.where(struct={})
    results = search.perform_resources(smart.server)
    return results

def search_patients_by_name(name):
    search = Patient.where(struct={'name': name})
    results = search.perform_resources(smart.server)
    return results

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

if selected == "Search Patients":
    st.header("Search Patients by Name")
    name_query = st.text_input("Enter name to search:")
    if st.button("Search"):
        result_patients = search_patients_by_name(name_query)
        for patient in result_patients:
            birth_date = format_date(patient.birthDate)
            st.text(f"Patient Name: {patient.name[0].given[0]} {patient.name[0].family}, Birth Date: {birth_date}")

if selected == "Data Visualization":
    st.header("Patient Information Visualization")
    refresh = st.button("Refresh Data")
    if refresh or not st.session_state.get('fetched', False):
        all_patients = fetch_all_patients()
        st.session_state['fetched'] = True
    else:
        all_patients = st.session_state.get('all_patients', [])

    if all_patients:
        for patient in all_patients:
            birth_date = format_date(patient.birthDate)
            st.text(f"Patient Name: {patient.name[0].given[0]} {patient.name[0].family}, Birth Date: {birth_date}")
    else:
        st.write("No patients found.")
