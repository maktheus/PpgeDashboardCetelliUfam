import streamlit as st
import pandas as pd
import os
from datetime import datetime

def get_available_years():
    """Obtém os anos disponíveis nos dados"""
    # Se tivermos dados no session state
    if 'data' in st.session_state and 'enrollment_date' in st.session_state['data'].columns:
        df = st.session_state['data']
        
        # Extrair anos únicos da coluna enrollment_date
        years = sorted(df['enrollment_date'].dt.year.unique().tolist(), reverse=True)
        
        # Adicionar "All" como primeira opção
        return ["All"] + [str(year) for year in years]
    
    # Valores padrão caso não tenha dados
    return ["All", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2005"]

def get_available_programs():
    """Obtém os programas disponíveis nos dados"""
    # Se tivermos dados no session state
    if 'data' in st.session_state and 'program' in st.session_state['data'].columns:
        df = st.session_state['data']
        
        # Extrair programas únicos
        programs = sorted(df['program'].unique().tolist())
        
        # Adicionar "All" como primeira opção
        return ["All"] + programs
    
    # Valores padrão caso não tenha dados
    return ["All", "Mestrado", "Doutorado"]

def render_sidebar():
    """Renders the sidebar with navigation and filtering options"""
    
    with st.sidebar:
        st.title("PPGE KPI Dashboard")
        
        # Usar o ícone gerado
        if os.path.exists("generated-icon.png"):
            st.image("generated-icon.png", width=96)
        else:
            st.image("https://img.icons8.com/fluency/96/000000/graduation-cap.svg")
        
        st.subheader("Navigation")
        
        # Navigation buttons
        if st.button("📊 Visão Geral", use_container_width=True, 
                    help="Visualizar indicadores gerais do programa"):
            st.session_state.active_page = 'overview'
            st.rerun()
            
        if st.button("👨‍🎓 Métricas dos Estudantes", use_container_width=True, 
                    help="Visualizar métricas relacionadas aos estudantes"):
            st.session_state.active_page = 'student_metrics'
            st.rerun()
            
        if st.button("👨‍🏫 Métricas dos Docentes", use_container_width=True, 
                    help="Visualizar métricas de desempenho dos docentes"):
            st.session_state.active_page = 'faculty_metrics'
            st.rerun()
            
        if st.button("🏫 Desempenho do Programa", use_container_width=True, 
                    help="Visualizar indicadores de desempenho do programa"):
            st.session_state.active_page = 'program_performance'
            st.rerun()
            
        if st.button("📝 Gerador de Relatórios", use_container_width=True, 
                    help="Gerar e exportar relatórios"):
            st.session_state.active_page = 'report_generator'
            st.rerun()
            
        if st.button("⚙️ Gerenciamento de Dados", use_container_width=True, 
                    help="Importar e gerenciar dados"):
            st.session_state.active_page = 'data_management'
            st.rerun()
        
        st.divider()
        
        # Filters section
        st.subheader("Filtros")
        
        # Year filter
        years = get_available_years()
        
        if st.session_state.selected_year not in years:
            st.session_state.selected_year = "All"
            
        selected_year = st.selectbox("Ano Acadêmico", years, 
                                    index=years.index(st.session_state.selected_year))
        
        if selected_year != st.session_state.selected_year:
            st.session_state.selected_year = selected_year
            st.rerun()
        
        # Program filter
        programs = get_available_programs()
        
        if st.session_state.selected_program not in programs:
            st.session_state.selected_program = "All"
            
        selected_program = st.selectbox("Programa", programs, 
                                       index=programs.index(st.session_state.selected_program))
        
        if selected_program != st.session_state.selected_program:
            st.session_state.selected_program = selected_program
            st.rerun()
        
        st.divider()
        
        # Footer
        st.caption("© 2023-2025 PPGE Dashboard")
        st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y')}")
        st.caption("Versão 1.1.0")
