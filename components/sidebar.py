import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.translations import get_translation

def get_available_years():
    """Returns the available years in the data"""
    # If we have data in the session state
    if 'data' in st.session_state and 'enrollment_date' in st.session_state['data'].columns:
        df = st.session_state['data']
        
        # Extract unique years from the enrollment_date column
        years = sorted(df['enrollment_date'].dt.year.unique().tolist(), reverse=True)
        
        # Add "All" as the first option
        all_text = get_translation("all", st.session_state.language)
        return [all_text] + [str(year) for year in years]
    
    # Default values if no data is available
    all_text = get_translation("all", st.session_state.language)
    return [all_text, "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2005"]

def get_available_programs():
    """Returns the available programs in the data"""
    # If we have data in the session state
    if 'data' in st.session_state and 'program' in st.session_state['data'].columns:
        df = st.session_state['data']
        
        # Extract unique programs
        programs = sorted(df['program'].unique().tolist())
        
        # Map program names based on current language if needed
        if st.session_state.language == 'en':
            # Replace Portuguese program names with English equivalents
            programs = [("Masters" if p == "Mestrado" else 
                        "Doctorate" if p == "Doutorado" else p) for p in programs]
        elif st.session_state.language == 'pt':
            # Replace English program names with Portuguese equivalents
            programs = [("Mestrado" if p == "Masters" else 
                        "Doutorado" if p == "Doctorate" else p) for p in programs]
        
        # Add "All" as the first option
        all_text = get_translation("all", st.session_state.language)
        return [all_text] + programs
    
    # Default values if no data is available
    all_text = get_translation("all", st.session_state.language)
    
    if st.session_state.language == 'en':
        return [all_text, "Masters", "Doctorate"]
    else:
        return [all_text, "Mestrado", "Doutorado"]

def render_sidebar():
    """Renders the sidebar with navigation and filtering options"""
    
    # Get current language
    lang = st.session_state.language
    
    with st.sidebar:
        st.title("PPGEE KPI Dashboard")
        
        # Use the generated icon
        if os.path.exists("generated-icon.png"):
            st.image("generated-icon.png", width=96)
        else:
            st.image("https://img.icons8.com/fluency/96/000000/graduation-cap.svg")
        
        # Language selector
        language_options = {
            "pt": get_translation("pt_language", lang),
            "en": get_translation("en_language", lang)
        }
        
        selected_language = st.selectbox(
            get_translation("language_selector", lang),
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=0 if lang == "pt" else 1
        )
        
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()
        
        st.subheader(get_translation("navigation", lang))
        
        # Navigation buttons
        if st.button(get_translation("overview_nav", lang), use_container_width=True, 
                    help="Visualizar indicadores gerais do programa"):
            st.session_state.active_page = 'overview'
            st.rerun()
            
        if st.button(get_translation("student_metrics_nav", lang), use_container_width=True, 
                    help="Visualizar métricas relacionadas aos estudantes"):
            st.session_state.active_page = 'student_metrics'
            st.rerun()
            
        if st.button(get_translation("faculty_metrics_nav", lang), use_container_width=True, 
                    help="Visualizar métricas de desempenho dos docentes"):
            st.session_state.active_page = 'faculty_metrics'
            st.rerun()
            
        if st.button(get_translation("program_performance_nav", lang), use_container_width=True, 
                    help="Visualizar indicadores de desempenho do programa"):
            st.session_state.active_page = 'program_performance'
            st.rerun()
            
        if st.button(get_translation("report_generator_nav", lang), use_container_width=True, 
                    help="Gerar e exportar relatórios"):
            st.session_state.active_page = 'report_generator'
            st.rerun()
            
        if st.button(get_translation("data_management_nav", lang), use_container_width=True, 
                    help="Importar e gerenciar dados"):
            st.session_state.active_page = 'data_management'
            st.rerun()
            
        if st.button("➕ Adicionar Estudante", use_container_width=True, 
                    help="Adicionar novo estudante à base de dados"):
            st.session_state.active_page = 'add_student'
            st.rerun()
        
        st.divider()
        
        # Filters section
        st.subheader(get_translation("filters", lang))
        
        # Year filter
        years = get_available_years()
        
        if st.session_state.selected_year not in years:
            st.session_state.selected_year = years[0]  # Use first item (All)
            
        selected_year = st.selectbox(get_translation("year_filter", lang), years, 
                                    index=years.index(st.session_state.selected_year))
        
        if selected_year != st.session_state.selected_year:
            st.session_state.selected_year = selected_year
            st.rerun()
        
        # Program filter
        programs = get_available_programs()
        
        if st.session_state.selected_program not in programs:
            st.session_state.selected_program = programs[0]  # Use first item (All)
            
        selected_program = st.selectbox(get_translation("program_filter", lang), programs, 
                                       index=programs.index(st.session_state.selected_program))
        
        if selected_program != st.session_state.selected_program:
            st.session_state.selected_program = selected_program
            st.rerun()
        
        st.divider()
        
        # Footer
        st.caption(get_translation("copyright", lang))
        st.caption(get_translation("last_update", lang).format(datetime.now().strftime('%d/%m/%Y')))
        st.caption(get_translation("version", lang))
