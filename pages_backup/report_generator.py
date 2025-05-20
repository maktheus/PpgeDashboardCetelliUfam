import streamlit as st
import pandas as pd
from data.data_manager import DataManager
from components.reports import render_report_options, generate_excel_report, generate_csv_report, generate_pdf_report
from components.filters import render_date_range_filter, render_multi_select_filter, apply_filters, create_date_filter, create_category_filter
from datetime import datetime

def render_page():
    """Render the Report Generator page"""
    
    st.title("📝 Gerador de Relatórios")
    
    # Get filtered data
    df = DataManager.get_data()
    
    # Show filter information
    st.info(
        f"Visualizando dados para: Ano = {st.session_state.selected_year}, "
        f"Programa = {st.session_state.selected_program}"
    )
    
    if df.empty:
        st.warning("Não há dados disponíveis para gerar relatórios. Por favor, importe dados primeiro.")
        return
    
    # Create tabs for different report types
    tab1, tab2, tab3 = st.tabs([
        "Relatórios de Estudantes", 
        "Relatórios de Docentes", 
        "Relatórios de Desempenho do Programa"
    ])
    
    with tab1:
        render_student_report_section(df)
    
    with tab2:
        render_faculty_report_section(df)
    
    with tab3:
        render_program_report_section(df)

def render_student_report_section(df):
    """Render the student reports section"""
    
    st.subheader("Relatórios de Estudantes")
    
    # Store available columns for report generation
    if 'report_columns' not in st.session_state:
        st.session_state.report_columns = list(df.columns)
    
    # Filter options
    st.markdown("### Filtros de Relatório")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Date range filter
        if 'enrollment_date' in df.columns:
            start_date, end_date = render_date_range_filter(
                label="Período de Matrícula",
                key_prefix="student_report_date"
            )
        else:
            start_date = end_date = None
            st.info("Não há dados de data de matrícula disponíveis para filtragem.")
    
    with col2:
        # Program filter
        if 'program' in df.columns:
            programs = ["All"] + sorted(df['program'].unique().tolist())
            selected_programs = render_multi_select_filter(
                programs[1:],  # Skip "All"
                "Selecionar Programas",
                "student_report_programs",
                default=[]
            )
        else:
            selected_programs = []
            st.info("Não há dados de programa disponíveis para filtragem.")
    
    # Apply filters
    filters = {}
    
    if start_date and end_date and 'enrollment_date' in df.columns:
        filters['enrollment_date'] = create_date_filter('enrollment_date', start_date, end_date)
    
    if selected_programs:
        filters['program'] = create_category_filter('program', selected_programs)
    
    if filters:
        filtered_df = apply_filters(df, filters)
    else:
        filtered_df = df.copy()
    
    # Report preview
    st.markdown("### Pré-visualização do Relatório")
    st.write(f"Mostrando {len(filtered_df)} registros")
    
    # Student columns to display
    display_cols = ['student_id', 'student_name', 'program', 'department', 
                   'enrollment_date', 'defense_date', 'defense_status', 
                   'advisor_name', 'research_area', 'publications']
    
    # Filter columns that exist in the dataframe
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    # Display preview
    st.dataframe(filtered_df[display_cols].head(10), use_container_width=True)
    
    # Report options
    st.markdown("### Opções de Relatório")
    
    report_title, report_filename, report_type, selected_columns = render_report_options(key_prefix="student")
    
    # Check if columns were selected
    if not selected_columns:
        selected_columns = display_cols
    
    # Generate report button
    if st.button("Gerar Relatório de Estudantes", key="student_report_button"):
        if report_type == "Excel":
            download_link = generate_excel_report(
                filtered_df[selected_columns],
                filename=report_filename
            )
        elif report_type == "CSV":
            download_link = generate_csv_report(
                filtered_df[selected_columns],
                filename=report_filename
            )
        elif report_type == "PDF":
            download_link = generate_pdf_report(
                filtered_df[selected_columns],
                title=report_title,
                filename=report_filename
            )
        else:
            st.error("Tipo de relatório inválido")
            return
        
        st.markdown(download_link, unsafe_allow_html=True)

def render_faculty_report_section(df):
    """Render the faculty reports section"""
    
    st.subheader("Relatórios de Docentes")
    
    # Check if we have faculty data
    if 'advisor_id' not in df.columns:
        st.warning("Não há dados de docentes disponíveis.")
        return
    
    # Get faculty metrics
    from utils.calculations import calculate_advisor_metrics
    faculty_df = calculate_advisor_metrics(df)
    
    if faculty_df.empty:
        st.warning("Não há métricas de docentes disponíveis.")
        return
    
    # Store available columns for report generation
    if 'faculty_report_columns' not in st.session_state:
        st.session_state.faculty_report_columns = list(faculty_df.columns)
        st.session_state.report_columns = list(faculty_df.columns)
    
    # Filter options
    st.markdown("### Filtros de Relatório")
    
    # Department filter if available
    if 'department' in df.columns:
        departments = df['department'].unique().tolist()
        selected_departments = render_multi_select_filter(
            departments,
            "Selecionar Departamentos",
            "faculty_report_departments",
            default=[]
        )
        
        if selected_departments:
            # Filter faculty by department
            dept_advisors = df[df['department'].isin(selected_departments)]['advisor_id'].unique()
            faculty_df = faculty_df[faculty_df['advisor_id'].isin(dept_advisors)]
    
    # Add minimum student filter
    min_students = st.slider(
        "Número Mínimo de Estudantes",
        min_value=1,
        max_value=20,
        value=1,
        step=1
    )
    
    faculty_df = faculty_df[faculty_df['total_students'] >= min_students]
    
    # Report preview
    st.markdown("### Pré-visualização do Relatório")
    st.write(f"Mostrando {len(faculty_df)} docentes")
    
    # Display preview
    st.dataframe(faculty_df.head(10), use_container_width=True)
    
    # Report options
    st.markdown("### Opções de Relatório")
    
    report_title, report_filename, report_type, selected_columns = render_report_options(key_prefix="faculty")
    
    # Check if columns were selected
    if not selected_columns:
        selected_columns = list(faculty_df.columns)
    
    # Generate report button
    if st.button("Gerar Relatório de Docentes", key="faculty_report_button"):
        if report_type == "Excel":
            download_link = generate_excel_report(
                faculty_df[selected_columns],
                filename=report_filename
            )
        elif report_type == "CSV":
            download_link = generate_csv_report(
                faculty_df[selected_columns],
                filename=report_filename
            )
        elif report_type == "PDF":
            download_link = generate_pdf_report(
                faculty_df[selected_columns],
                title=report_title,
                filename=report_filename
            )
        else:
            st.error("Tipo de relatório inválido")
            return
        
        st.markdown(download_link, unsafe_allow_html=True)

def render_program_report_section(df):
    """Render the program performance reports section"""
    
    st.subheader("Relatórios de Desempenho do Programa")
    
    # Check if we have program data
    if 'program' not in df.columns:
        st.warning("Não há dados de programa disponíveis.")
        return
    
    # Report type selection
    report_types = [
        "Visão Geral do Programa", 
        "Tempo até Defesa por Programa",
        "Análise de Publicações", 
        "Taxas de Sucesso em Defesas",
        "Tendências de Matrícula"
    ]
    
    selected_report = st.selectbox(
        "Selecione o Tipo de Relatório",
        options=report_types
    )
    
    # Generate the selected report data
    if selected_report == "Visão Geral do Programa":
        report_df = generate_program_overview(df)
        report_title = "Relatório de Visão Geral do Programa"
    elif selected_report == "Tempo até Defesa por Programa":
        report_df = generate_time_to_defense_report(df)
        report_title = "Relatório de Tempo até Defesa por Programa"
    elif selected_report == "Análise de Publicações":
        report_df = generate_publication_report(df)
        report_title = "Relatório de Análise de Publicações"
    elif selected_report == "Taxas de Sucesso em Defesas":
        report_df = generate_defense_rates_report(df)
        report_title = "Relatório de Taxas de Sucesso em Defesas"
    elif selected_report == "Tendências de Matrícula":
        report_df = generate_enrollment_trends_report(df)
        report_title = "Relatório de Tendências de Matrícula"
    else:
        st.error("Tipo de relatório inválido")
        return
    
    if report_df.empty:
        st.warning("Não há dados disponíveis para o tipo de relatório selecionado.")
        return
    
    # Store available columns for report generation
    st.session_state.report_columns = list(report_df.columns)
    
    # Report preview
    st.markdown("### Pré-visualização do Relatório")
    st.dataframe(report_df, use_container_width=True)
    
    # Report options
    st.markdown("### Opções de Relatório")
    
    report_filename = st.text_input(
        "Nome do arquivo (sem extensão)", 
        value=f"ppge_{selected_report.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
        key="program_report_filename"
    )
    
    report_type = st.selectbox(
        "Formato do Relatório", 
        ["Excel", "CSV", "PDF"],
        key="program_report_format"
    )
    
    # Generate report button
    if st.button("Gerar Relatório do Programa", key="program_report_button"):
        if report_type == "Excel":
            download_link = generate_excel_report(
                report_df,
                filename=report_filename
            )
        elif report_type == "CSV":
            download_link = generate_csv_report(
                report_df,
                filename=report_filename
            )
        elif report_type == "PDF":
            download_link = generate_pdf_report(
                report_df,
                title=report_title,
                filename=report_filename
            )
        else:
            st.error("Tipo de relatório inválido")
            return
        
        st.markdown(download_link, unsafe_allow_html=True)

def generate_program_overview(df):
    """Gera dados de visão geral do programa para relatório"""
    
    # Visão geral do programa
    program_counts = df.groupby('program').size().reset_index(name='total_alunos')
    
    # Adicionar mais métricas se disponíveis
    if 'defense_status' in df.columns:
        # Calcular defesas por programa
        defenses = df[df['defense_status'].notna()].groupby('program').size().reset_index(name='total_defesas')
        program_counts = program_counts.merge(defenses, on='program', how='left')
        program_counts['total_defesas'] = program_counts['total_defesas'].fillna(0).astype(int)
        
        # Calcular taxas de sucesso
        success = df[df['defense_status'] == 'Approved'].groupby('program').size().reset_index(name='defesas_com_sucesso')
        program_counts = program_counts.merge(success, on='program', how='left')
        program_counts['defesas_com_sucesso'] = program_counts['defesas_com_sucesso'].fillna(0).astype(int)
        program_counts['taxa_sucesso'] = (program_counts['defesas_com_sucesso'] / program_counts['total_defesas']).fillna(0).round(4) * 100
    
    # Adicionar tempo até defesa se disponível
    if 'enrollment_date' in df.columns and 'defense_date' in df.columns:
        df_with_time = df.copy()
        df_with_time['time_to_defense'] = (pd.to_datetime(df_with_time['defense_date']) - 
                                          pd.to_datetime(df_with_time['enrollment_date'])).dt.days / 30.44
        
        time_metrics = df_with_time[df_with_time['time_to_defense'].notna()].groupby('program')['time_to_defense'].agg(
            ['mean', 'median', 'std']).reset_index()
        
        time_metrics.columns = ['program', 'media_meses_ate_defesa', 'mediana_meses_ate_defesa', 'desvio_padrao_meses']
        time_metrics = time_metrics.round(2)
        
        program_counts = program_counts.merge(time_metrics, on='program', how='left')
    
    # Adicionar publicações se disponível
    if 'publications' in df.columns:
        pub_metrics = df.groupby('program')['publications'].agg(['sum', 'mean', 'median']).reset_index()
        pub_metrics.columns = ['program', 'total_publicacoes', 'media_publicacoes_por_aluno', 'mediana_publicacoes']
        pub_metrics['media_publicacoes_por_aluno'] = pub_metrics['media_publicacoes_por_aluno'].round(2)
        
        program_counts = program_counts.merge(pub_metrics, on='program', how='left')
    
    return program_counts

def generate_time_to_defense_report(df):
    """Gera dados de relatório de tempo até a defesa"""
    
    if 'enrollment_date' not in df.columns or 'defense_date' not in df.columns:
        return pd.DataFrame()
    
    # Calcular tempo até a defesa
    df_with_time = df.copy()
    df_with_time['time_to_defense'] = (pd.to_datetime(df_with_time['defense_date']) - 
                                      pd.to_datetime(df_with_time['enrollment_date'])).dt.days / 30.44
    
    # Incluir apenas estudantes que já defenderam
    df_with_time = df_with_time[df_with_time['time_to_defense'].notna()]
    
    if df_with_time.empty:
        return pd.DataFrame()
    
    # Agrupar por programa e ano
    if 'enrollment_date' in df_with_time.columns:
        df_with_time['enrollment_year'] = pd.to_datetime(df_with_time['enrollment_date']).dt.year
        
        time_metrics = df_with_time.groupby(['program', 'enrollment_year'])['time_to_defense'].agg(
            ['count', 'mean', 'median', 'min', 'max']).reset_index()
        
        time_metrics.columns = ['Programa', 'Ano de Ingresso', 'Número de Defesas', 
                               'Média de Meses', 'Mediana de Meses', 'Mínimo de Meses', 'Máximo de Meses']
        
        # Arredondar colunas de ponto flutuante
        for col in ['Média de Meses', 'Mediana de Meses', 'Mínimo de Meses', 'Máximo de Meses']:
            time_metrics[col] = time_metrics[col].round(1)
        
        return time_metrics
    else:
        # Se data de matrícula não estiver disponível, agrupar apenas por programa
        time_metrics = df_with_time.groupby('program')['time_to_defense'].agg(
            ['count', 'mean', 'median', 'min', 'max']).reset_index()
        
        time_metrics.columns = ['Programa', 'Número de Defesas', 
                               'Média de Meses', 'Mediana de Meses', 'Mínimo de Meses', 'Máximo de Meses']
        
        # Arredondar colunas de ponto flutuante
        for col in ['Média de Meses', 'Mediana de Meses', 'Mínimo de Meses', 'Máximo de Meses']:
            time_metrics[col] = time_metrics[col].round(1)
        
        return time_metrics

def generate_publication_report(df):
    """Generate publication analysis report data"""
    
    if 'publications' not in df.columns:
        return pd.DataFrame()
    
    # Create a basic report with publication stats by program
    if 'program' in df.columns:
        pub_stats = df.groupby('program')['publications'].agg(
            ['count', 'sum', 'mean', 'median', 'max']).reset_index()
        
        pub_stats.columns = ['Program', 'Number of Students', 'Total Publications', 
                            'Average Publications', 'Median Publications', 'Maximum Publications']
        
        # Round floating point columns
        for col in ['Average Publications', 'Median Publications']:
            pub_stats[col] = pub_stats[col].round(2)
        
        return pub_stats
    else:
        # If program not available, create an overall summary
        pub_stats = pd.DataFrame({
            'Metric': ['Total Students', 'Total Publications', 'Average Publications', 
                      'Median Publications', 'Maximum Publications'],
            'Value': [
                len(df),
                df['publications'].sum(),
                df['publications'].mean().round(2),
                df['publications'].median(),
                df['publications'].max()
            ]
        })
        
        return pub_stats

def generate_defense_rates_report(df):
    """Generate defense success rates report data"""
    
    if 'defense_status' not in df.columns:
        return pd.DataFrame()
    
    # Calculate defense rates by program and year if available
    if 'program' in df.columns and 'defense_date' in df.columns:
        # Only include students with defense data
        defended_df = df[df['defense_status'].notna()].copy()
        
        if defended_df.empty:
            return pd.DataFrame()
        
        # Extract defense year
        defended_df['defense_year'] = pd.to_datetime(defended_df['defense_date']).dt.year
        
        # Count defenses and successes by program and year
        defense_counts = defended_df.groupby(['program', 'defense_year']).size().reset_index(name='total_defenses')
        
        success_counts = defended_df[defended_df['defense_status'] == 'Approved'].groupby(
            ['program', 'defense_year']).size().reset_index(name='successful_defenses')
        
        # Merge the data
        defense_rates = defense_counts.merge(success_counts, on=['program', 'defense_year'], how='left')
        defense_rates['successful_defenses'] = defense_rates['successful_defenses'].fillna(0).astype(int)
        
        # Calculate success rate
        defense_rates['success_rate_pct'] = (defense_rates['successful_defenses'] / 
                                           defense_rates['total_defenses'] * 100).round(1)
        
        # Rename columns for report
        defense_rates.columns = ['Program', 'Year', 'Total Defenses', 'Successful Defenses', 'Success Rate (%)']
        
        return defense_rates
    else:
        # If detailed data not available, create a simple report
        defended_df = df[df['defense_status'].notna()].copy()
        
        if defended_df.empty:
            return pd.DataFrame()
        
        # Count defenses and successes by program
        defense_counts = defended_df.groupby('program').size().reset_index(name='total_defenses')
        
        success_counts = defended_df[defended_df['defense_status'] == 'Approved'].groupby(
            'program').size().reset_index(name='successful_defenses')
        
        # Merge the data
        defense_rates = defense_counts.merge(success_counts, on='program', how='left')
        defense_rates['successful_defenses'] = defense_rates['successful_defenses'].fillna(0).astype(int)
        
        # Calculate success rate
        defense_rates['success_rate_pct'] = (defense_rates['successful_defenses'] / 
                                           defense_rates['total_defenses'] * 100).round(1)
        
        # Rename columns for report
        defense_rates.columns = ['Program', 'Total Defenses', 'Successful Defenses', 'Success Rate (%)']
        
        return defense_rates

def generate_enrollment_trends_report(df):
    """Generate enrollment trends report data"""
    
    if 'enrollment_date' not in df.columns:
        return pd.DataFrame()
    
    # Extract enrollment year and month
    df_copy = df.copy()
    df_copy['enrollment_year'] = pd.to_datetime(df_copy['enrollment_date']).dt.year
    df_copy['enrollment_month'] = pd.to_datetime(df_copy['enrollment_date']).dt.month
    
    # Create a yearly report
    yearly_enrollments = df_copy.groupby('enrollment_year').size().reset_index(name='total_enrollments')
    yearly_enrollments.columns = ['Year', 'Total Enrollments']
    
    # Add program breakdown if available
    if 'program' in df_copy.columns:
        program_pivot = df_copy.pivot_table(
            index='enrollment_year',
            columns='program',
            values='student_id',
            aggfunc='count',
            fill_value=0
        ).reset_index()
        
        program_pivot.columns.name = None
        program_pivot = program_pivot.rename(columns={'enrollment_year': 'Year'})
        
        # Merge with yearly enrollments
        enrollment_report = program_pivot.merge(yearly_enrollments, on='Year')
        
        return enrollment_report
    else:
        return yearly_enrollments
