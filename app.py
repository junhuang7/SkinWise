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

def fetch_data():
    st.session_state['fetch_clicked'] = True

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def fetch_patients():
    """Fetch the latest 20 patients sorted by creation date, requesting specific fields to improve performance."""
    search = Patient.where(struct={'_count': '20', '_sort': '-_lastUpdated', '_elements': 'id,name,birthDate'})
    results = search.perform_resources(smart.server)
    return results

def delete_patient(patient_id):
    """Deletes a patient from the FHIR server."""
    try:
        patient = Patient.read(patient_id, smart.server)
        patient.delete()
        fetch_data()  # Refresh data
        st.success("Patient deleted successfully.")
    except Exception as e:
        st.error("Failed to delete patient.")

def display_patients():
    """Displays patients in a table with a delete button."""
    patients = fetch_patients()
    if patients:
        data = []
        for patient in patients:
            data.append({
                "ID": patient.id,
                "Name": f"{patient.name[0].given[0]} {patient.name[0].family}" if patient.name else "Unknown",
                "Birth Date": format_date(patient.birthDate) if patient.birthDate else "Unknown",
            })
        df = pd.DataFrame(data)
        st.table(df.style.apply(lambda x: ['background-color: #2F4F4F' if i % 2 == 0 else 'background-color: #36454F' for i in range(len(x))], axis=1))
        for patient in patients:
            if st.button(f"Delete {patient.id}"):
                delete_patient(patient.id)
    else:
        st.write("No patients found.")

# Menu options
selected = option_menu(None, ["Data Entry", "Patients"], icons=["pencil-fill", "bar-chart-fill"], orientation="horizontal")

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
    if st.button('Fetch Latest Patients', on_click=fetch_data):
        display_patients()
