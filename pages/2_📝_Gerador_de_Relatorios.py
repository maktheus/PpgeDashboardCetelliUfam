import streamlit as st
import sys
import os

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the page configuration
st.set_page_config(
    page_title="Gerador de Relatórios | PPGEE KPI Dashboard",
    page_icon="📝",
    layout="wide",
)

# Initialize session state for filters if not already done
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = 'All'

if 'selected_program' not in st.session_state:
    st.session_state.selected_program = 'All'

# Import our modules
from pages_backup.report_generator import render_page

# Render the page content
render_page()