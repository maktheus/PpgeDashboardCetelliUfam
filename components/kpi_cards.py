import streamlit as st
import pandas as pd

def metric_card(title, value, delta=None, help_text="", prefix="", suffix="", detailed_description=""):
    """
    Display a metric card with title, value, and optional delta
    
    Parameters:
    - title: Title of the metric
    - value: Main value to display
    - delta: Change compared to previous period (optional)
    - help_text: Tooltip text explaining the metric
    - prefix: Text to display before the value (e.g., "$")
    - suffix: Text to display after the value (e.g., "%")
    - detailed_description: Detailed explanation of the KPI (for KPI detail view)
    """
    # Format value, handling NaN values
    if pd.isna(value):
        formatted_value = "N/A"
    else:
        formatted_value = f"{prefix}{value}{suffix}"
    
    # Create a card with CSS styling
    with st.container():
        st.markdown(f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f2f6;
            box-shadow: 0 0.15rem 0.5rem rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
        ">
            <h4 style="margin-top: 0; color: #555;">{title}</h4>
            <h2 style="margin-bottom: 0.5rem; font-size: 1.8rem; color: #0068c9;">{formatted_value}</h2>
            <p style="margin-bottom: 0; font-size: 0.8rem; color: #777;">{help_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # If detailed description is provided, show it below the metric card
    if detailed_description:
        st.caption(detailed_description)

def detailed_kpi_card(title, value, description, formula=None, prefix="", suffix=""):
    """
    Display a detailed KPI card with title, value, and detailed explanation
    
    Parameters:
    - title: Title of the KPI
    - value: The calculated value of the KPI
    - description: Detailed explanation of what the KPI measures
    - formula: Optional formula explaining how the KPI is calculated
    - prefix: Text to display before the value
    - suffix: Text to display after the value
    """
    # Format value, handling NaN values
    if pd.isna(value):
        formatted_value = "N/A"
    else:
        formatted_value = f"{prefix}{value}{suffix}"
    
    # Create a card-like container with enhanced styling
    with st.container():
        # Main card container
        st.markdown(f"""
        <div style="
            padding: 1.2rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            box-shadow: 0 0.2rem 0.6rem rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            border-left: 4px solid #0068c9;
        ">
            <h3 style="margin-top: 0; color: #333; font-size: 1.3rem;">{title}</h3>
            <h2 style="margin-bottom: 1rem; font-size: 2rem; color: #0068c9;">{formatted_value}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Display description separately
        st.markdown("**Descrição:**")
        st.markdown(description)
        
        # Display formula if available
        if formula:
            st.markdown("**Fórmula de Cálculo:**")
            st.code(formula)

def render_kpi_summary(df):
    """
    Render a row of KPI summary cards
    
    Parameters:
    - df: DataFrame containing the data
    """
    # Calculate KPIs for Masters and Doctorate separately
    total_masters = 0
    total_doctorate = 0
    
    if 'program' in df.columns:
        total_masters = len(df[df['program'].str.contains('Mestrado|Masters', case=False, na=False)]['student_id'].unique()) if 'student_id' in df.columns else 0
        total_doctorate = len(df[df['program'].str.contains('Doutorado|Doctorate', case=False, na=False)]['student_id'].unique()) if 'student_id' in df.columns else 0
    else:
        # Fallback if no program column
        total_students = len(df['student_id'].unique()) if 'student_id' in df.columns else 0
        total_masters = total_students // 2  # Rough estimation
        total_doctorate = total_students - total_masters
    
    # Calculate total faculty (permanent + collaborators)
    from utils.kpi_calculations import get_all_data_from_table
    total_faculty = 0
    
    try:
        # Get permanent faculty
        docentes_permanentes_df = get_all_data_from_table('docentes_permanentes')
        permanentes_count = 0
        if not docentes_permanentes_df.empty and 'docente' in docentes_permanentes_df.columns:
            permanentes_count = len(docentes_permanentes_df['docente'].unique())
            total_faculty += permanentes_count
        
        # Note: docentes_colaboradores table doesn't exist in the database
        # Using only permanent faculty for now
        colaboradores_count = 0
            
        # Debug info - will be visible in console
        print(f"Debug: Docentes permanentes: {permanentes_count}")
        print(f"Debug: Docentes colaboradores: {colaboradores_count}")
        print(f"Debug: Total de docentes calculado: {total_faculty}")
        
    except Exception as e:
        print(f"Erro ao calcular total de docentes: {str(e)}")
        # Fallback to advisor count from main data
        total_faculty = len(df['advisor_id'].unique()) if 'advisor_id' in df.columns else 0
    
    # Calculate average time to defense for Masters and Doctorate separately
    avg_time_masters = 0
    avg_time_doctorate = 0
    
    if 'enrollment_date' in df.columns and 'defense_date' in df.columns and 'program' in df.columns:
        df['time_to_defense'] = (pd.to_datetime(df['defense_date']) - 
                                pd.to_datetime(df['enrollment_date'])).dt.days / 30.44  # Average days per month
        
        # Masters time
        masters_df = df[df['program'].str.contains('Mestrado|Masters', case=False, na=False)]
        if not masters_df.empty and 'time_to_defense' in masters_df.columns:
            avg_time_masters = round(masters_df['time_to_defense'].mean(), 1)
        
        # Doctorate time
        doctorate_df = df[df['program'].str.contains('Doutorado|Doctorate', case=False, na=False)]
        if not doctorate_df.empty and 'time_to_defense' in doctorate_df.columns:
            avg_time_doctorate = round(doctorate_df['time_to_defense'].mean(), 1)
    
    # Calculate defense success rate (keep code but don't display)
    if 'defense_status' in df.columns:
        defense_success_rate = round(df[df['defense_status'] == 'Approved'].shape[0] / 
                                    max(1, df[df['defense_status'].notna()].shape[0]) * 100, 1)
    else:
        defense_success_rate = 0
    
    # Display metrics in a simple card layout
    st.markdown("## Principais Indicadores de Desempenho (KPIs)")
    
    # Create a 4-column layout for the new metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            title="Total de Alunos Mestrado",
            value=total_masters,
            help_text="Número total de alunos de mestrado no programa"
        )
    
    with col2:
        metric_card(
            title="Total de Alunos Doutorado",
            value=total_doctorate,
            help_text="Número total de alunos de doutorado no programa"
        )
    
    with col3:
        metric_card(
            title="Total de Docentes",
            value=total_faculty,
            help_text="Número total de docentes (permanentes + colaboradores)"
        )
    
    with col4:
        metric_card(
            title="Tempo Médio de Defesa de Mestrado",
            value=avg_time_masters,
            suffix=" meses",
            help_text="Tempo médio desde o ingresso até a defesa - Mestrado"
        )
    
    # Second row for doctorate defense time
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        metric_card(
            title="Tempo Médio de Defesa de Doutorado",
            value=avg_time_doctorate,
            suffix=" meses",
            help_text="Tempo médio desde o ingresso até a defesa - Doutorado"
        )
    
    # Keep other columns empty for now, can be used for future metrics
    
    return {
        "total_masters": total_masters,
        "total_doctorate": total_doctorate,
        "total_faculty": total_faculty,
        "avg_time_masters": avg_time_masters,
        "avg_time_doctorate": avg_time_doctorate,
        "defense_success_rate": defense_success_rate  # Keep for future use
    }

def render_detailed_kpi_cards(kpi_data):
    """
    Render detailed KPI cards with explanations
    
    Parameters:
    - kpi_data: Dictionary with calculated KPI values
    """
    st.markdown("## Detalhamento dos KPIs")
    
    # Create 2-column layout for detailed KPI cards
    col1, col2 = st.columns(2)
    
    with col1:
        detailed_kpi_card(
            title="Total de Alunos Mestrado",
            value=kpi_data.get("total_masters", 0),
            description="Representa o número total de alunos de mestrado matriculados no programa de pós-graduação. "
                       "Este indicador é fundamental para entender a dimensão do programa de mestrado e sua capacidade "
                       "de formação de recursos humanos qualificados em nível de mestrado.",
            formula="Contagem distinta de IDs de estudantes de mestrado no conjunto de dados"
        )
        
        st.markdown("---")
        
        detailed_kpi_card(
            title="Total de Docentes",
            value=kpi_data.get("total_faculty", 0),
            description="Representa o número total de professores (permanentes + colaboradores) ativos no programa. "
                       "Este indicador reflete a capacidade de orientação e a diversidade de especialidades "
                       "disponíveis para os alunos do programa.",
            formula="Contagem de docentes permanentes + docentes colaboradores"
        )
        
        st.markdown("---")
        
        detailed_kpi_card(
            title="Tempo Médio de Defesa de Mestrado",
            value=kpi_data.get("avg_time_masters", 0),
            suffix=" meses",
            description="Calcula o tempo médio que os alunos de mestrado levam desde a matrícula até a defesa da "
                       "dissertação. Este indicador é importante para avaliar a eficiência do programa "
                       "em formar seus mestrandos dentro do prazo esperado (24 meses).",
            formula="Média(Data de Defesa - Data de Matrícula) em meses para mestrandos"
        )
    
    with col2:
        detailed_kpi_card(
            title="Total de Alunos Doutorado",
            value=kpi_data.get("total_doctorate", 0),
            description="Representa o número total de alunos de doutorado matriculados no programa de pós-graduação. "
                       "Este indicador é fundamental para entender a dimensão do programa de doutorado e sua capacidade "
                       "de formação de doutores qualificados.",
            formula="Contagem distinta de IDs de estudantes de doutorado no conjunto de dados"
        )
        
        st.markdown("---")
        
        detailed_kpi_card(
            title="Tempo Médio de Defesa de Doutorado",
            value=kpi_data.get("avg_time_doctorate", 0),
            suffix=" meses",
            description="Calcula o tempo médio que os alunos de doutorado levam desde a matrícula até a defesa da "
                       "tese. Este indicador é importante para avaliar a eficiência do programa "
                       "em formar seus doutorandos dentro do prazo esperado (48 meses).",
            formula="Média(Data de Defesa - Data de Matrícula) em meses para doutorandos"
        )
        
        # Taxa de Sucesso na Defesa - keeping code but commented out for display
        # st.markdown("---")
        # detailed_kpi_card(
        #     title="Taxa de Sucesso na Defesa",
        #     value=kpi_data.get("defense_success_rate", 0),
        #     suffix="%",
        #     description="Percentual de alunos que defenderam com sucesso suas dissertações/teses em relação "
        #                "ao total que chegou à fase de defesa. Este indicador reflete a qualidade da "
        #                "preparação dos alunos e a efetividade do processo de orientação.",
        #     formula="(Número de defesas aprovadas / Total de defesas) × 100"
        # )
