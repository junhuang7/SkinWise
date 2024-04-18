import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models import humanname
import logging

from flask import Flask, request
import socket
import numpy as np
import io
import cv2
import json
import base64
import os
#custom
# from custom.credentials import token, account
from custom.essentials import stringToRGB, get_model
# from custom.whatsapp import whatsapp_message

import re
from io import StringIO

def input_validation(uploaded_file):
  #validate the inputs
  if not uploaded_file:
    st.error("Invalid file")
    st.stop()

def disease_detect(result_img):
    model_name = 'Model/best_model.h5'
    model = get_model()
    model.load_weights(model_name)
    classes = {4: ('nv', ' melanocytic nevi'), 6: ('mel', 'melanoma'), 2: ('bkl', 'benign keratosis-like lesions'),
               1: ('bcc', ' basal cell carcinoma'), 5: ('vasc', ' pyogenic granulomas and hemorrhage'),
               0: ('akiec', 'Actinic keratoses and intraepithelial carcinomae'), 3: ('df', 'dermatofibroma')}
    img = cv2.resize(result_img, (28, 28))
    result = model.predict(img.reshape(1, 28, 28, 3))
    result = result[0]
    max_prob = max(result)

    if max_prob > 0.80:
        class_ind = list(result).index(max_prob)
        class_name = classes[class_ind]
        # short_name = class_name[0]
        full_name = class_name[1]
    else:
        full_name = 'No Disease'  # if confidence is less than 80 percent then "No disease"

    # send message
    message = '''
       Disease Name : {}
       Confidence: {}

       '''.format(full_name, max_prob)
    return message

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
st.write(""" 
<style> 
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap'); 
    .welcome-message { 
        font-family: 'Roboto', sans-serif; 
        font-weight: 100; /* Specify Roboto Thin */ 
        font-size: 16px; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
        color: white; /* White text */ 
    } 
    .separator { 
        border-top: 2px solid white; /* White separator line */ 
        margin-top: 20px; /* Add some space between the welcome message and the separator */ 
        margin-bottom: 20px; /* Add some space between the separator and the content below */ 
    } 
</style> 
""", unsafe_allow_html=True) 
 
# Display the welcome message in an information box 
st.markdown(""" 
<div class="welcome-message"> 
 
### SkinWise: Web-based Diagnostic Tool 
SkinWise serves as a powerful tool for healthcare professionals, enabling them to effectively manage patient cases and detect skin cancers with precision. 
 
</div> 
""", unsafe_allow_html=True) 
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

def delete_patient_from_fhir(patient_id):
    try:
        patient = Patient.read(patient_id, smart.server)
        result = patient.delete(smart.server)
        if result:
            logger.info(f"Patient deleted from FHIR server: ID = {patient_id}")
            st.success(f"Patient with ID {patient_id} deleted successfully!")
        else:
            logger.error("Failed to delete patient")
            st.error("Error deleting patient from FHIR server")
    except Exception as e:
        logger.error(f"Failed to delete patient: {e}", exc_info=True)
        st.error(f"Error deleting from FHIR server: {e}")

def update_patient_to_fhir(patient_id, updated_data):
    try:
        patient = Patient.read(patient_id, smart.server)
        if 'First Name' in updated_data:
            patient.name[0].given = [updated_data['First Name']]
        if 'Family Name' in updated_data:
            patient.name[0].family = updated_data['Family Name']
        if 'BirthDate' in updated_data:
            patient.birthDate = FHIRDate(updated_data['BirthDate'].split('T')[0])
        result = patient.update(smart.server)
        if result:
            logger.info(f"Patient updated in FHIR server: ID = {patient_id}")
            st.success(f"Patient with ID {patient_id} updated successfully!")
        else:
            logger.error("Failed to update patient")
            st.error("Error updating patient in FHIR server")
    except Exception as e:
        logger.error(f"Failed to update patient: {e}", exc_info=True)
        st.error(f"Error updating patient: {e}")

# Menu options
selected = option_menu(None, ["Data Entry", "Patients"], icons=["pencil-fill", "bar-chart-fill"], orientation="horizontal")

if selected == "Data Entry":
    st.header("Data Entry for Patient")

    # Interface A
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

    # Interface B
    with st.form("boolq form"):
        label = 'choose a image file'
        uploaded_file = st.file_uploader(label, type=None, accept_multiple_files=False, key=None, help=None,
                                         on_change=None,
                                         args=None, kwargs=None)

        if st.form_submit_button("Get Answer"):
            input_validation(uploaded_file)  # Validate input

            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1]

            if file_extension in ['.jpg', '.jpeg', '.png']:
                bytes_data = uploaded_file.getvalue()

                with open(f'test_images/temp.{file_extension}', 'wb') as f:
                    f.write(bytes_data)

                result_img = cv2.imread(f'test_images/temp.{file_extension}')
                result = disease_detect(result_img)
                st.success(result)

            else:
                st.error('File must be one of .png, .jpg or .jpeg')
                st.stop()




if selected == "Patients":
    st.header("Patient Information Visualization")
    fetch_button = st.button('Fetch Latest Patients', on_click=fetch_data)

    if st.session_state['fetch_counter'] > 0:
        with st.spinner('Fetching latest patients...'):
            patients = fetch_patients()
            
            if patients:
                for patient in patients:
                    patient_id = patient.id if patient.id else "Unknown ID"
                    # Initialize session state for each patient if not already present
                    if f'{patient_id}_given_name' not in st.session_state:
                        st.session_state[f'{patient_id}_given_name'] = patient.name[0].given[0] if patient.name and patient.name[0].given else "Unknown"
                    if f'{patient_id}_family_name' not in st.session_state:
                        st.session_state[f'{patient_id}_family_name'] = patient.name[0].family if patient.name and patient.name[0].family else "Unknown"
                    if f'{patient_id}_birth_date' not in st.session_state:
                        st.session_state[f'{patient_id}_birth_date'] = format_date(patient.birthDate) if patient.birthDate else "Unknown"

                    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
                    col1.markdown(f"**Patient ID: {patient_id}**")
                    col1.text_input("First Name:", key=f'{patient_id}_given_name')
                    col1.text_input("Family Name:", key=f'{patient_id}_family_name')
                    col1.text_input("Birth Date (YYYY-MM-DD):", key=f'{patient_id}_birth_date')
                    
                    col2.button("Edit", key=f"edit_{patient_id}")
                    col3.button("Submit", key=f"submit_{patient_id}", on_click=update_patient_to_fhir, args=(patient_id, {
                        'First Name': st.session_state[f'{patient_id}_given_name'],
                        'Family Name': st.session_state[f'{patient_id}_family_name'],
                        'BirthDate': st.session_state[f'{patient_id}_birth_date']
                    }))
                    col4.button("Delete", key=f"delete_{patient_id}", on_click=delete_patient_from_fhir, args=(patient_id,))
            else:
                st.write("No patients found or failed to fetch patients.")