import streamlit as st
import pandas as pd
from data.data_manager import DataManager
from components.kpi_cards import render_kpi_summary
from components.charts import (
    render_time_series_chart, 
    render_bar_chart, 
    render_pie_chart
)
from utils.calculations import (
    calculate_time_to_defense,
    calculate_completion_rate,
    calculate_success_rate
)

def render_page():
    """Render the Overview page"""
    
    st.title("📊 Visão Geral do Programa PPGE")
    
    # Get filtered data
    df = DataManager.get_data()
    
    # Calculate time to defense if needed
    if 'enrollment_date' in df.columns and 'defense_date' in df.columns:
        df = calculate_time_to_defense(df)
    
    # Show filter information
    st.info(
        f"Visualizando dados para: Ano = {st.session_state.selected_year}, "
        f"Programa = {st.session_state.selected_program}"
    )
    
    # Render KPI summary cards
    render_kpi_summary(df)
    
    # Add divider
    st.divider()
    
    # Create 2-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ingressos e Defesas por Período")
        
        # Get time series data
        time_series_data = DataManager.get_time_series_data()
        
        if not time_series_data.empty:
            # Prepare data for time series chart
            time_series_data['year_month'] = time_series_data['year_month'].dt.strftime('%Y-%m')
            
            render_time_series_chart(
                time_series_data,
                title="Atividade Estudantil ao Longo do Tempo",
                x_column="year_month",
                y_column="enrollments"
            )
        else:
            st.info("Sem dados de série temporal disponíveis.")
    
    with col2:
        st.subheader("Distribuição por Programa")
        
        if 'program' in df.columns:
            program_counts = df.groupby('program').size().reset_index(name='count')
            
            render_pie_chart(
                program_counts,
                title="Estudantes por Programa",
                values_column="count",
                names_column="program"
            )
        else:
            st.info("Sem dados de programa disponíveis.")
    
    # Add second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tempo Médio até a Defesa (em meses)")
        
        if 'time_to_defense' in df.columns and 'program' in df.columns:
            # Calculate average time to defense by program
            avg_time_by_program = df.groupby('program')['time_to_defense'].mean().reset_index()
            avg_time_by_program['time_to_defense'] = avg_time_by_program['time_to_defense'].round(1)
            
            render_bar_chart(
                avg_time_by_program,
                title="Tempo Médio até a Defesa por Programa",
                x_column="program",
                y_column="time_to_defense"
            )
        else:
            st.info("Sem dados de tempo até a defesa disponíveis.")
    
    with col2:
        st.subheader("Taxa de Sucesso nas Defesas")
        
        if 'defense_status' in df.columns and 'program' in df.columns:
            # Calculate success rate by program
            success_rate_by_program = calculate_success_rate(df, by_group='program')
            
            if not success_rate_by_program.empty:
                success_rate_by_program['success_rate'] = (success_rate_by_program['success_rate'] * 100).round(1)
                
                render_bar_chart(
                    success_rate_by_program,
                    title="Taxa de Sucesso nas Defesas por Programa (%)",
                    x_column="program",
                    y_column="success_rate"
                )
            else:
                st.info("Sem dados de status de defesa disponíveis.")
        else:
            st.info("Sem dados de status de defesa disponíveis.")
    
    # Add a third row for additional metrics
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Orientadores com Mais Alunos")
        
        if 'advisor_name' in df.columns:
            # Count students per advisor
            advisor_counts = df.groupby('advisor_name').size().reset_index(name='count')
            advisor_counts = advisor_counts.sort_values('count', ascending=False).head(10)
            
            render_bar_chart(
                advisor_counts,
                title="Top 10 Orientadores por Número de Alunos",
                x_column="advisor_name",
                y_column="count",
                orientation='h'
            )
        else:
            st.info("Sem dados de orientadores disponíveis.")
    
    with col2:
        st.subheader("Distribuição de Ingressos por Ano")
        
        if 'enrollment_date' in df.columns:
            # Extract year and count enrollments
            df['enrollment_year'] = pd.to_datetime(df['enrollment_date']).dt.year
            year_counts = df.groupby('enrollment_year').size().reset_index(name='count')
            year_counts = year_counts.sort_values('enrollment_year')
            
            render_bar_chart(
                year_counts,
                title="Número de Ingressos por Ano",
                x_column="enrollment_year",
                y_column="count"
            )
        else:
            st.info("Sem dados de data de ingresso disponíveis.")
    
    # Add a third row for additional metrics
    st.divider()
    
    st.subheader("Distribuição por Departamento")
    
    if 'department' in df.columns:
        # Get department counts
        dept_counts = df.groupby('department').size().reset_index(name='count')
        dept_counts = dept_counts.sort_values('count', ascending=False)
        
        render_pie_chart(
            dept_counts,
            title="Estudantes por Departamento",
            values_column="count",
            names_column="department"
        )
    else:
        st.info("Sem dados de departamento disponíveis.")
