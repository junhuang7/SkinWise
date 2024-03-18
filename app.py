import calendar
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

import database as db

# -------------- SETTINGS --------------
patient_info_categories = ["Name", "Age", "Diagnosis"]
treatment_info = ["Treatment Plan", "Medication", "Follow-up Schedule"]
currency = "Patient"  # 可能需要根据上下文进行更改
page_title = "Patient Information Tracker"
page_icon = ":hospital:"  # 选择更适合医疗主题的图标
layout = "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year - i for i in range(100)]  # 假设这是出生年份的选择
months = list(calendar.month_name[1:])

# --- DATABASE INTERFACE ---
# 保留这部分，用于与数据库交互
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)

# --- INPUT & SAVE PATIENT INFORMATION ---
if selected == "Data Entry":
    st.header(f"Data Entry for {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Birth Month:", months, key="month")
        col2.selectbox("Select Birth Year:", years, key="year")

        "---"
        with st.expander("Patient Information"):
            for info in patient_info_categories:
                if info == "Age":
                    st.number_input(f"{info}:", min_value=0, max_value=120, format="%i", key=info)
                else:
                    st.text_input(f"{info}:", key=info)
        with st.expander("Skin Treatment Information"):
            for treatment in treatment_info:
                st.text_input(f"{treatment}:", key=treatment)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here ...")

        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            patient_data = {info: st.session_state[info] for info in patient_info_categories}
            treatments = {treatment: st.session_state[treatment] for treatment in treatment_info}
            db.insert_period(period, patient_data, treatments, comment)
            st.success("Data saved!")

# --- PLOT PATIENT INFORMATION ---
# 这部分可能需要根据实际需求进行适当调整
if selected == "Data Visualization":
    st.header("Patient Information Visualization")
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_periods())
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            # 获取数据库中的数据
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            treatments = period_data.get("treatments")
            patient_data = period_data.get("patient_data")

            # 创建图表来显示病人信息和治疗计划（需要根据实际数据进行调整）
            col1, col2 = st.columns(2)
            col1.metric("Patient Name", patient_data.get("Name"))
            col2.metric("Age", patient_data.get("Age"))
            st.text(f"Diagnosis: {patient_data.get('Diagnosis')}")
            st.text(f"Treatment Plan: {treatments.get('Treatment Plan')}")
            st.text(f"Medication: {treatments.get('Medication')}")
            st.text(f"Follow-up Schedule: {treatments.get('Follow-up Schedule')}")
            st.text(f"Comment: {comment}")

            # 这里可以添加更多视觉元素，例如时间线图表或病人治疗进度的流程图

# 以下为可视化部分的示例，根据实际需要调整
