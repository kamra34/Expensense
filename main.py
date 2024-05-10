import streamlit as st
import importlib.util
import os
import sys
sys.path.append('./')
from common import utils
from common.config import loan_params

st.set_page_config(page_title="My Expensensense App", layout="wide")

# Mapping and ordering.
PAGE_MAPPING = {
    "home": "Home",
    "AWS_S3_Status": "AWS S3 bucket Status",
    "expected_savings": "Income-Outcome",
    "Loan_selector": "Mortgage Optimizer",
}

def load_module(page_path):
    try:
        spec = importlib.util.spec_from_file_location("module.name", page_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Failed to load module {page_path}. Error: {str(e)}")
        return None

# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", options=list(PAGE_MAPPING.keys()), format_func=lambda x: PAGE_MAPPING[x])

if selection == "Loan_selector":
    st.sidebar.header("Mortgage Optimizer Settings")
    # Define inputs related to the mortgage optimizer
    #if 'P1' not in st.session_state:
    st.session_state['P1'] = st.sidebar.number_input("Principal Part 1", value=loan_params.principal_part1)
    #if 'P2' not in st.session_state:
    st.session_state['P2'] = st.sidebar.number_input("Principal Part 2", value=loan_params.principal_part2)
    #if 'P3' not in st.session_state:
    st.session_state['P3'] = st.sidebar.number_input("Principal Part 3", value=loan_params.principal_part3)
    st.session_state['discount'] = st.sidebar.number_input("Discount Rate (%)", value=loan_params.discount_val)
    st.session_state['base_rates'] = {
        'float': st.sidebar.number_input("Float Rate (%)", value=loan_params.init_float_val),
        'fixed_1_year': st.sidebar.number_input("Fixed 1 Year Rate (%)", value=loan_params.init_1_year_val),
        'fixed_2_year': st.sidebar.number_input("Fixed 2 Year Rate (%)", value=loan_params.init_2_year_val),
        'fixed_3_year': st.sidebar.number_input("Fixed 3 Year Rate (%)", value=loan_params.init_3_year_val)
    }

# Dynamic page loading
current_script_dir = os.path.dirname(__file__)
page_path = os.path.join(current_script_dir, f"sources/{selection}.py")
if os.path.isfile(page_path):
    page_module = load_module(page_path)
else:
    st.error(f"Page not found: {selection}")
