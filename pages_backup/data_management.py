import streamlit as st
import pandas as pd
import numpy as np
from data.data_manager import DataManager
from components.data_import import (
    render_file_uploader,
    process_uploaded_file,
    render_data_mapping_tool,
    save_imported_data
)
from utils.export import export_to_excel, export_to_csv

def render_page():
    """Render the Data Management page"""
    
    st.title("⚙️ Data Management")
    
    # Create tabs for different data management functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Import Data", 
        "View & Export Data", 
        "Data Summary",
        "Comparação Temporal"
    ])
    
    with tab1:
        render_import_section()
    
    with tab2:
        render_view_export_section()
    
    with tab3:
        render_data_summary_section()
        
    with tab4:
        render_temporal_comparison_section()

def render_temporal_comparison_section():
    """Render the Temporal Comparison section"""
    
    st.subheader("Comparação Temporal de Dados")
    
    # Get data history
    data_history = DataManager.get_data_history()
    
    if not data_history or len(data_history) < 2:
        st.warning("Para realizar comparações temporais, é necessário importar pelo menos dois conjuntos de dados diferentes.")
        st.info("Importe diferentes arquivos CSV ou Excel na aba 'Import Data' para habilitar esta funcionalidade.")
        return
    
    # Show history of imported datasets
    st.subheader("Histórico de Importações")
    
    # Create a table of imported datasets
    history_data = []
    for entry in data_history:
        history_data.append({
            "Data de Importação": entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "Nome do Arquivo": entry["file_name"],
            "Número de Registros": len(entry["data"])
        })
    
    # Convert to DataFrame and display
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)
    
    # Selection for comparison
    st.subheader("Selecionar Dados para Comparação")
    
    col1, col2 = st.columns(2)
    
    # Format timestamp and filename for select boxes
    dataset_options = [f"{entry['timestamp'].strftime('%Y-%m-%d %H:%M')} - {entry['file_name']}" 
                       for entry in data_history]
    
    with col1:
        dataset1_idx = st.selectbox(
            "Dataset 1 (Anterior):",
            options=range(len(dataset_options)),
            format_func=lambda x: dataset_options[x],
            index=max(0, len(dataset_options) - 2)  # Default to second-to-last
        )
    
    with col2:
        dataset2_idx = st.selectbox(
            "Dataset 2 (Atual):",
            options=range(len(dataset_options)),
            format_func=lambda x: dataset_options[x],
            index=len(dataset_options) - 1  # Default to most recent
        )
    
    # Metrics to compare
    st.subheader("Métricas para Comparar")
    metrics_to_compare = st.multiselect(
        "Selecione as métricas para comparação:",
        options=["total_records", "avg_time_to_defense", "success_rate", "program_distribution"],
        default=["total_records", "avg_time_to_defense", "success_rate"],
        format_func=lambda x: {
            "total_records": "Total de Registros",
            "avg_time_to_defense": "Tempo Médio até Defesa",
            "success_rate": "Taxa de Aprovação",
            "program_distribution": "Distribuição por Programa"
        }[x]
    )
    
    # Compare button
    if st.button("Comparar Datasets"):
        # Get timestamp for each dataset
        ts1 = data_history[dataset1_idx]["timestamp"]
        ts2 = data_history[dataset2_idx]["timestamp"]
        
        # Run comparison
        comparison_results = DataManager.compare_datasets(ts1, ts2, metrics_to_compare)
        
        if comparison_results:
            # Display results
            st.subheader("Resultados da Comparação")
            
            st.markdown(f"**Comparando:**")
            st.markdown(f"- **{comparison_results['dataset1_name']}** (Dataset Base)")
            st.markdown(f"- **{comparison_results['dataset2_name']}** (Dataset Atual)")
            
            # Display metric comparisons
            for metric, values in comparison_results['metrics'].items():
                if metric == 'program_distribution':
                    # Display program distribution with charts
                    st.subheader("Distribuição por Programa")
                    
                    # Create DataFrames for visualization
                    prog_dist1 = pd.DataFrame(values['dataset1'])
                    prog_dist2 = pd.DataFrame(values['dataset2'])
                    
                    # Display side by side charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**{comparison_results['dataset1_name']}**")
                        
                        # Bar chart
                        import plotly.express as px
                        fig = px.bar(
                            prog_dist1, 
                            x="program", 
                            y="percentage",
                            title="Distribuição por Programa (%)",
                            labels={"program": "Programa", "percentage": "Porcentagem (%)"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show data table
                        st.dataframe(prog_dist1, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"**{comparison_results['dataset2_name']}**")
                        
                        # Bar chart
                        fig = px.bar(
                            prog_dist2, 
                            x="program", 
                            y="percentage",
                            title="Distribuição por Programa (%)",
                            labels={"program": "Programa", "percentage": "Porcentagem (%)"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show data table
                        st.dataframe(prog_dist2, use_container_width=True)
                    
                else:
                    # Display numeric metrics with comparison
                    metric_names = {
                        "total_records": "Total de Registros",
                        "avg_time_to_defense": "Tempo Médio até Defesa (meses)",
                        "success_rate": "Taxa de Aprovação (%)"
                    }
                    
                    st.subheader(metric_names.get(metric, metric))
                    
                    # Format values
                    val1 = values['dataset1']
                    val2 = values['dataset2']
                    diff = values['difference']
                    perc_change = values['percent_change']
                    
                    # Format based on metric type
                    if metric == 'success_rate':
                        val1 = f"{val1 * 100:.2f}%"
                        val2 = f"{val2 * 100:.2f}%"
                        diff_text = f"{diff * 100:+.2f}%"
                    elif metric == 'avg_time_to_defense':
                        val1 = f"{val1:.2f} meses"
                        val2 = f"{val2:.2f} meses"
                        diff_text = f"{diff:+.2f} meses"
                    else:
                        diff_text = f"{diff:+d}" if isinstance(diff, int) else f"{diff:+.2f}"
                    
                    # Determine color for change indicator
                    if metric in ['success_rate']:
                        # Higher is better
                        change_color = "green" if diff > 0 else "red"
                    elif metric in ['avg_time_to_defense']:
                        # Lower is better
                        change_color = "green" if diff < 0 else "red"
                    else:
                        # Neutral
                        change_color = "blue"
                    
                    # Create comparison display
                    cols = st.columns([2, 2, 3])
                    with cols[0]:
                        st.metric(
                            label=f"{comparison_results['dataset1_name']}",
                            value=val1
                        )
                    
                    with cols[1]:
                        st.metric(
                            label=f"{comparison_results['dataset2_name']}",
                            value=val2,
                            delta=diff_text
                        )
                    
                    with cols[2]:
                        if abs(perc_change) != float('inf'):
                            st.markdown(f"**Variação Percentual:** <span style='color:{change_color};'>{perc_change:+.2f}%</span>", 
                                         unsafe_allow_html=True)
                        else:
                            st.markdown("**Variação Percentual:** N/A (divisão por zero)")
            
            # Set current dataset button
            st.divider()
            if st.button("Usar Dataset 2 como Dataset Atual"):
                # Get the data from history
                selected_data = DataManager.get_data_by_timestamp(ts2)
                
                if selected_data is not None:
                    # Update the current data
                    DataManager.update_data(selected_data)
                    st.session_state['current_data_timestamp'] = ts2
                    st.success(f"Dataset '{comparison_results['dataset2_name']}' definido como dataset atual.")
                    st.info("Todas as visualizações e relatórios agora usarão este conjunto de dados.")
                    
                    # Rerun to reflect changes
                    st.rerun()
                else:
                    st.error("Não foi possível carregar o dataset selecionado.")
        else:
            st.error("Não foi possível comparar os datasets selecionados. Verifique se eles contêm dados compatíveis.")

def render_import_section():
    """Render the Import Data section"""
    
    st.subheader("Import Data")
    
    # Info card about data import
    st.info(
        "Import data from Excel, CSV, or JSON files. The system will help you map your data "
        "fields to the required format for the PPGE KPI Dashboard."
    )
    
    # File uploader
    uploaded_file, file_type = render_file_uploader()
    
    if uploaded_file is not None:
        # Process uploaded file
        imported_df, error_message = process_uploaded_file(uploaded_file, file_type)
        
        if error_message:
            st.error(error_message)
            return
        
        if imported_df is not None:
            st.success(f"File processed successfully! Found {len(imported_df)} records.")
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(imported_df.head(5), use_container_width=True)
            
            # Data mapping
            mapped_df, mapping_applied = render_data_mapping_tool(imported_df)
            
            if mapping_applied:
                # Save button
                if st.button("Save Imported Data"):
                    # Get filename for reference
                    file_name = uploaded_file.name if uploaded_file else "Imported Data"
                    
                    # Save the data with filename
                    success = DataManager.import_data(mapped_df, file_name)
                    
                    if success:
                        st.success("Data imported and saved successfully!")
                        
                        # Update timestamp
                        st.session_state['data_import_timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        st.error("Failed to save imported data.")
    else:
        # Show sample data option
        st.subheader("No file uploaded")
        
        if st.button("Load Sample Data"):
            from data.sample_data import generate_sample_data
            
            # Generate sample data
            sample_size = st.slider("Number of sample records", 50, 200, 100)
            sample_df = generate_sample_data(num_students=sample_size)
            
            # Save the sample data
            success = DataManager.import_data(sample_df, f"Sample Data ({sample_size} records)")
            
            if success:
                st.success(f"Sample data with {sample_size} records loaded successfully!")
                
                # Update timestamp
                st.session_state['data_import_timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Show preview
                st.subheader("Sample Data Preview")
                st.dataframe(sample_df.head(5), use_container_width=True)
            else:
                st.error("Failed to load sample data.")
    
    # Display import history
    if 'data_import_timestamp' in st.session_state:
        st.divider()
        st.subheader("Import History")
        st.info(f"Last import: {st.session_state['data_import_timestamp']}")

def render_view_export_section():
    """Render the View & Export Data section"""
    
    st.subheader("View & Export Data")
    
    # Get the current data
    df = DataManager.get_data()
    
    if df.empty:
        st.warning("No data available. Please import data first.")
        return
    
    # Show filter information
    st.info(
        f"Viewing data for: Year = {st.session_state.selected_year}, "
        f"Program = {st.session_state.selected_program}"
    )
    
    # Create a tab for each data category
    data_tabs = st.tabs([
        "Student Data", 
        "Faculty Data", 
        "Program Data"
    ])
    
    with data_tabs[0]:
        # Student data view
        st.subheader("Student Data")
        
        # Columns to display for students
        student_cols = ['student_id', 'student_name', 'program', 'department', 
                       'enrollment_date', 'defense_date', 'defense_status', 
                       'advisor_id', 'advisor_name', 'research_area', 'publications']
        
        # Filter columns that exist in the dataframe
        student_cols = [col for col in student_cols if col in df.columns]
        
        if student_cols:
            # Search functionality
            search_term = st.text_input("Search Students by Name or ID", "")
            
            if search_term:
                # Search in student_id and student_name if they exist
                search_mask = pd.Series([False] * len(df))
                
                if 'student_id' in df.columns:
                    search_mask |= df['student_id'].astype(str).str.contains(search_term, case=False)
                
                if 'student_name' in df.columns:
                    search_mask |= df['student_name'].astype(str).str.contains(search_term, case=False)
                
                display_df = df[search_mask][student_cols]
            else:
                display_df = df[student_cols]
            
            # Show the data
            st.dataframe(display_df, use_container_width=True)
            
            # Export options
            st.subheader("Export Student Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                export_filename = st.text_input(
                    "Filename (without extension)", 
                    value=f"ppge_student_data_{pd.Timestamp.now().strftime('%Y%m%d')}"
                )
            
            with col2:
                export_format = st.selectbox(
                    "Export Format",
                    options=["Excel", "CSV"]
                )
            
            if st.button("Export Student Data"):
                if export_format == "Excel":
                    download_link = export_to_excel(display_df, export_filename)
                else:  # CSV
                    download_link = export_to_csv(display_df, export_filename)
                
                st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.info("No student data available.")
    
    with data_tabs[1]:
        # Faculty data view
        st.subheader("Faculty Data")
        
        if 'advisor_id' in df.columns:
            # Calculate faculty metrics
            from utils.calculations import calculate_advisor_metrics
            faculty_df = calculate_advisor_metrics(df)
            
            if not faculty_df.empty:
                # Search functionality
                search_term = st.text_input("Search Faculty by Name or ID", "")
                
                if search_term:
                    # Search in advisor_id and advisor_name if they exist
                    search_mask = pd.Series([False] * len(faculty_df))
                    
                    if 'advisor_id' in faculty_df.columns:
                        search_mask |= faculty_df['advisor_id'].astype(str).str.contains(search_term, case=False)
                    
                    if 'advisor_name' in faculty_df.columns:
                        search_mask |= faculty_df['advisor_name'].astype(str).str.contains(search_term, case=False)
                    
                    display_df = faculty_df[search_mask]
                else:
                    display_df = faculty_df
                
                # Show the data
                st.dataframe(display_df, use_container_width=True)
                
                # Export options
                st.subheader("Export Faculty Data")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    export_filename = st.text_input(
                        "Filename (without extension)", 
                        value=f"ppge_faculty_data_{pd.Timestamp.now().strftime('%Y%m%d')}"
                    )
                
                with col2:
                    export_format = st.selectbox(
                        "Export Format",
                        options=["Excel", "CSV"],
                        key="faculty_export_format"
                    )
                
                if st.button("Export Faculty Data"):
                    if export_format == "Excel":
                        download_link = export_to_excel(display_df, export_filename)
                    else:  # CSV
                        download_link = export_to_csv(display_df, export_filename)
                    
                    st.markdown(download_link, unsafe_allow_html=True)
            else:
                st.info("No faculty metrics available.")
        else:
            st.info("No faculty data available.")
    
    with data_tabs[2]:
        # Program data view
        st.subheader("Program Data")
        
        if 'program' in df.columns:
            # Get program metrics
            program_metrics = DataManager.get_program_metrics()
            
            if not program_metrics.empty:
                # Show the data
                st.dataframe(program_metrics, use_container_width=True)
                
                # Export options
                st.subheader("Export Program Data")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    export_filename = st.text_input(
                        "Filename (without extension)", 
                        value=f"ppge_program_data_{pd.Timestamp.now().strftime('%Y%m%d')}"
                    )
                
                with col2:
                    export_format = st.selectbox(
                        "Export Format",
                        options=["Excel", "CSV"],
                        key="program_export_format"
                    )
                
                if st.button("Export Program Data"):
                    if export_format == "Excel":
                        download_link = export_to_excel(program_metrics, export_filename)
                    else:  # CSV
                        download_link = export_to_csv(program_metrics, export_filename)
                    
                    st.markdown(download_link, unsafe_allow_html=True)
            else:
                st.info("No program metrics available.")
        else:
            st.info("No program data available.")

def render_data_summary_section():
    """Render the Data Summary section"""
    
    st.subheader("Data Summary")
    
    # Get the current data
    df = DataManager.get_data()
    
    if df.empty:
        st.warning("No data available. Please import data first.")
        return
    
    # Data statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Records",
            value=len(df)
        )
    
    with col2:
        if 'program' in df.columns:
            num_programs = df['program'].nunique()
            st.metric(
                label="Number of Programs",
                value=num_programs
            )
        else:
            st.metric(
                label="Number of Programs",
                value="N/A"
            )
    
    with col3:
        if 'department' in df.columns:
            num_departments = df['department'].nunique()
            st.metric(
                label="Number of Departments",
                value=num_departments
            )
        else:
            st.metric(
                label="Number of Departments",
                value="N/A"
            )
    
    # More statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'advisor_id' in df.columns:
            num_faculty = df['advisor_id'].nunique()
            st.metric(
                label="Number of Faculty",
                value=num_faculty
            )
        else:
            st.metric(
                label="Number of Faculty",
                value="N/A"
            )
    
    with col2:
        if 'defense_status' in df.columns:
            num_defenses = df['defense_status'].notna().sum()
            st.metric(
                label="Number of Defenses",
                value=num_defenses
            )
        else:
            st.metric(
                label="Number of Defenses",
                value="N/A"
            )
    
    with col3:
        if 'publications' in df.columns:
            total_publications = df['publications'].sum()
            st.metric(
                label="Total Publications",
                value=int(total_publications)
            )
        else:
            st.metric(
                label="Total Publications",
                value="N/A"
            )
    
    # Data quality assessment
    st.subheader("Data Quality Assessment")
    
    # Calculate missing values
    missing_data = df.isnull().sum().reset_index()
    missing_data.columns = ['Column', 'Missing Values']
    missing_data['Missing Percentage'] = (missing_data['Missing Values'] / len(df) * 100).round(2)
    missing_data = missing_data.sort_values('Missing Percentage', ascending=False)
    
    # Display missing data
    st.dataframe(missing_data, use_container_width=True)
    
    # Data types
    st.subheader("Data Types")
    
    # Get data types
    data_types = pd.DataFrame({
        'Column': df.columns,
        'Data Type': df.dtypes.astype(str)
    })
    
    # Display data types
    st.dataframe(data_types, use_container_width=True)
    
    # Date range information
    st.subheader("Date Range Information")
    
    if 'enrollment_date' in df.columns:
        min_enrollment = pd.to_datetime(df['enrollment_date']).min()
        max_enrollment = pd.to_datetime(df['enrollment_date']).max()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Earliest Enrollment",
                value=min_enrollment.strftime("%Y-%m-%d")
            )
        
        with col2:
            st.metric(
                label="Latest Enrollment",
                value=max_enrollment.strftime("%Y-%m-%d")
            )
    
    if 'defense_date' in df.columns:
        # Filter out NaN values
        defense_dates = pd.to_datetime(df['defense_date'].dropna())
        
        if not defense_dates.empty:
            min_defense = defense_dates.min()
            max_defense = defense_dates.max()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Earliest Defense",
                    value=min_defense.strftime("%Y-%m-%d")
                )
            
            with col2:
                st.metric(
                    label="Latest Defense",
                    value=max_defense.strftime("%Y-%m-%d")
                )
