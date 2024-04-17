import re
import streamlit as st
def input_validation(uploaded_file):
  #validate the inputs
  if not uploaded_file:
    st.error("Invalid file")
    st.stop()



  # patient_contact_number = patient_contact_number.replace(' ', '')
  # doctor_contact_number = doctor_contact_number.replace(' ', '')

  # re_patient = re.match(r'[0-9]{10}', patient_contact_number)
  # re_doctor = re.match(r'[0-9]{10}', doctor_contact_number)

  # if not re_doctor:
  #   st.error("Incorrect doctor's contact number. Enter without extension")
  #   st.stop()
  # if not re_patient:
  #   st.error("Incorrect patient's contact number. Enter without extension")
  #   st.stop()
