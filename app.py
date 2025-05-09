import streamlit as st
import os
import sys
import pandas as pd
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Health check handler
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

# Start health check server if in deployment
if os.environ.get('DEPLOYMENT_HEALTH_CHECK') == '1':
    def run_health_check():
        server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
        server.serve_forever()
    
    threading.Thread(target=run_health_check, daemon=True).start()

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure the app
st.set_page_config(
    page_title="PPGE KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import necessary components
from data.data_manager import DataManager
from components.kpi_cards import render_kpi_summary, render_detailed_kpi_cards
from utils.calculations import calculate_time_to_defense
from components.charts import render_time_series_chart, render_bar_chart, render_pie_chart, render_histogram

# Main app page - this will be the home page
def main():
    # Initialize session state for filters and selected KPI
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = 'All'
    
    if 'selected_program' not in st.session_state:
        st.session_state.selected_program = 'All'
    
    if 'selected_kpi' not in st.session_state:
        st.session_state.selected_kpi = None
    
    # Add sidebar filters (moved from the sidebar.py module)
    with st.sidebar:
        st.title("PPGE KPI Dashboard")
        
        # Display logo
        if os.path.exists("generated-icon.png"):
            st.image("generated-icon.png", width=96)
        else:
            st.image("https://img.icons8.com/fluency/96/000000/graduation-cap.svg")
        
        # Filters section
        st.subheader("Filtros")
        
        # Get available years
        from components.sidebar import get_available_years, get_available_programs
        
        # Year filter
        years = get_available_years()
        
        if st.session_state.selected_year not in years:
            st.session_state.selected_year = "All"
            
        selected_year = st.selectbox("Ano Acadêmico", years, 
                                    index=years.index(st.session_state.selected_year),
                                    key="year_filter")
        
        if selected_year != st.session_state.selected_year:
            st.session_state.selected_year = selected_year
        
        # Program filter
        programs = get_available_programs()
        
        if st.session_state.selected_program not in programs:
            st.session_state.selected_program = "All"
            
        selected_program = st.selectbox("Programa", programs, 
                                      index=programs.index(st.session_state.selected_program),
                                      key="program_filter")
        
        if selected_program != st.session_state.selected_program:
            st.session_state.selected_program = selected_program
        
        # Navigation options
        st.sidebar.divider()
        st.sidebar.subheader("Navegação")
        
        view_options = {
            "KPI Dashboard": "kpi_dashboard",
            "Visualizações Gerais": "visualizations"
        }
        
        selected_view = st.sidebar.radio(
            "Escolher Visualização",
            list(view_options.keys()),
            key="view_selector",
            index=0
        )
        
        current_view = view_options[selected_view]
        
        # Reset selected KPI when changing views
        if current_view != "kpi_dashboard" and st.session_state.selected_kpi is not None:
            st.session_state.selected_kpi = None
    
    # Main content area
    st.title("📊 PPGE KPI Dashboard")
    
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
    
    # Render the selected view
    if current_view == "kpi_dashboard":
        # If a specific KPI is selected, render its detailed view
        if st.session_state.selected_kpi is not None:
            render_kpi_detail_view(st.session_state.selected_kpi, df)
        else:
            # Render interactive KPI summary cards
            kpi_data = render_interactive_kpi_cards(df)
            
            # Add a divider
            st.divider()
            
            # Render the detailed KPI cards with explanations
            render_detailed_kpi_cards(kpi_data)
        
    elif current_view == "visualizations":
        # For visualization view, use the original overview page
        st.subheader("Visualizações e Análises Detalhadas")
        
        # Add the existing visualization components
        # This is done by calling a modified version of the render_page function
        render_visualizations(df)

def render_interactive_kpi_cards(df):
    """
    Render interactive KPI cards that can be clicked to show detailed charts
    
    Parameters:
    - df: DataFrame containing the data
    
    Returns:
    - Dict with KPI values
    """
    # Calculate KPIs
    total_students = len(df['student_id'].unique()) if 'student_id' in df.columns else 0
    total_faculty = len(df['advisor_id'].unique()) if 'advisor_id' in df.columns else 0
    
    # Calculate defense related metrics
    if 'defense_status' in df.columns:
        # Total completed defenses
        completed_defenses = df['defense_status'].notna().sum()
        
        # Success rate for those who defended
        defense_success_rate = round(df[df['defense_status'] == 'Approved'].shape[0] / 
                                    max(1, df[df['defense_status'].notna()].shape[0]) * 100, 1)
        
        # Percentage of students who have defended
        defense_completion_rate = round(completed_defenses / max(1, len(df)) * 100, 1)
    else:
        completed_defenses = 0
        defense_success_rate = 0
        defense_completion_rate = 0
    
    # Calculate time metrics
    if 'enrollment_date' in df.columns and 'defense_date' in df.columns:
        # Time to defense
        df['time_to_defense'] = (pd.to_datetime(df['defense_date']) - 
                                pd.to_datetime(df['enrollment_date'])).dt.days / 30.44  # Average days per month
        
        # Average time to defense
        avg_time_to_defense = round(df['time_to_defense'].mean(), 1)
        
        # Median time to defense (more robust to outliers)
        median_time_to_defense = round(df['time_to_defense'].median(), 1)
        
        # Calculate time metrics by program
        if 'program' in df.columns:
            # Handle Masters program data
            masters_data = df[df['program'].isin(['Masters', 'Mestrado'])]['time_to_defense']
            if not masters_data.empty:
                masters_time = round(masters_data.mean(), 1)
            else:
                masters_time = 0
                
            # Handle Doctorate program data
            doctorate_data = df[df['program'].isin(['Doctorate', 'Doutorado'])]['time_to_defense']
            if not doctorate_data.empty:
                doctorate_time = round(doctorate_data.mean(), 1)
            else:
                doctorate_time = 0
        else:
            masters_time = 0
            doctorate_time = 0
            
        # Time to defense standard deviation
        std_time_to_defense = round(df['time_to_defense'].std(), 1)
        
        # Minimum and maximum time to defense
        min_time_to_defense = round(df['time_to_defense'].min(), 1)
        max_time_to_defense = round(df['time_to_defense'].max(), 1)
        
        # Calculate time efficiency (ratio of actual time to expected time)
        df = df.copy()  # Criar cópia para evitar avisos do pandas
        df['expected_time'] = df['program'].map({'Masters': 24, 'Doctorate': 48, 'Mestrado': 24, 'Doutorado': 48})  # Expected times in months
        
        # Filtrar estudantes com tempo válido para calcular eficiência
        valid_students = df[(df['time_to_defense'].notna()) & (df['time_to_defense'] > 0) & (df['expected_time'].notna())].copy()
        
        if not valid_students.empty:
            valid_students.loc[:, 'time_efficiency'] = valid_students['expected_time'] / valid_students['time_to_defense']
            # Limitar eficiência para um máximo de 200% para melhor visualização
            valid_students.loc[:, 'time_efficiency'] = valid_students['time_efficiency'].clip(upper=2.0)
            avg_time_efficiency = round(valid_students['time_efficiency'].mean() * 100, 1)  # As percentage
        else:
            avg_time_efficiency = 0
        
    else:
        avg_time_to_defense = 0
        median_time_to_defense = 0
        masters_time = 0
        doctorate_time = 0
        std_time_to_defense = 0
        min_time_to_defense = 0
        max_time_to_defense = 0
        avg_time_efficiency = 0
    
    # Import the custom card component
    from components.kpi_cards import metric_card
    
    # Main KPI layout
    st.markdown("## Principais Indicadores de Desempenho (KPIs)")
    st.caption("Clique em um KPI para visualizar gráficos e análises detalhadas")
    
    # First row - main KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        students_card = st.container()
        with students_card:
            metric_card(
                title="Total de Alunos",
                value=total_students,
                help_text="Número total de alunos no programa"
            )
            if st.button("Ver Detalhes", key="btn_students"):
                st.session_state.selected_kpi = "students"
                st.rerun()
    
    with col2:
        faculty_card = st.container()
        with faculty_card:
            metric_card(
                title="Total de Docentes",
                value=total_faculty,
                help_text="Número total de docentes orientando alunos"
            )
            if st.button("Ver Detalhes", key="btn_faculty"):
                st.session_state.selected_kpi = "faculty"
                st.rerun()
    
    with col3:
        defense_time_card = st.container()
        with defense_time_card:
            metric_card(
                title="Tempo Médio até Defesa",
                value=avg_time_to_defense,
                suffix=" meses",
                help_text="Tempo médio desde o ingresso até a defesa"
            )
            if st.button("Ver Detalhes", key="btn_defense_time"):
                st.session_state.selected_kpi = "defense_time"
                st.rerun()
    
    with col4:
        success_rate_card = st.container()
        with success_rate_card:
            metric_card(
                title="Taxa de Sucesso na Defesa",
                value=defense_success_rate,
                suffix="%",
                help_text="Porcentagem de defesas com aprovação"
            )
            if st.button("Ver Detalhes", key="btn_success_rate"):
                st.session_state.selected_kpi = "success_rate"
                st.rerun()
    
    # Second row - Time-related KPIs
    st.markdown("### Métricas de Tempo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            title="Mediana do Tempo até Defesa",
            value=median_time_to_defense,
            suffix=" meses",
            help_text="Mediana do tempo desde o ingresso até a defesa (valor central)"
        )
    
    with col2:
        metric_card(
            title="Mestrado (Tempo Médio)",
            value=masters_time,
            suffix=" meses",
            help_text="Tempo médio até a defesa para alunos de Mestrado"
        )
    
    with col3:
        metric_card(
            title="Doutorado (Tempo Médio)",
            value=doctorate_time,
            suffix=" meses",
            help_text="Tempo médio até a defesa para alunos de Doutorado"
        )
    
    with col4:
        metric_card(
            title="Variação do Tempo (Desvio)",
            value=std_time_to_defense,
            suffix=" meses",
            help_text="Desvio padrão do tempo até a defesa (medida de variabilidade)"
        )
    
    # Third row - Additional KPIs
    st.markdown("### Métricas de Eficiência")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        efficiency_card = st.container()
        with efficiency_card:
            metric_card(
                title="Eficiência de Tempo",
                value=avg_time_efficiency,
                suffix="%",
                help_text="Proporção do tempo esperado vs. tempo real (maior = mais eficiente)"
            )
            if st.button("Ver Detalhes", key="btn_efficiency"):
                st.session_state.selected_kpi = "efficiency"
                st.rerun()
    
    with col2:
        min_time_card = st.container()
        with min_time_card:
            metric_card(
                title="Tempo Mínimo",
                value=min_time_to_defense,
                suffix=" meses",
                help_text="Menor tempo registrado para conclusão"
            )
    
    with col3:
        max_time_card = st.container()
        with max_time_card:
            metric_card(
                title="Tempo Máximo",
                value=max_time_to_defense,
                suffix=" meses",
                help_text="Maior tempo registrado para conclusão"
            )
    
    with col4:
        completion_card = st.container()
        with completion_card:
            metric_card(
                title="Taxa de Conclusão",
                value=defense_completion_rate,
                suffix="%",
                help_text="Porcentagem de alunos que concluíram a defesa"
            )
            if st.button("Ver Detalhes", key="btn_completion"):
                st.session_state.selected_kpi = "completion"
                st.rerun()
    
    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "avg_time_to_defense": avg_time_to_defense,
        "defense_success_rate": defense_success_rate,
        "median_time_to_defense": median_time_to_defense,
        "masters_time": masters_time,
        "doctorate_time": doctorate_time,
        "std_time_to_defense": std_time_to_defense,
        "min_time_to_defense": min_time_to_defense,
        "max_time_to_defense": max_time_to_defense,
        "avg_time_efficiency": avg_time_efficiency,
        "defense_completion_rate": defense_completion_rate
    }

def render_kpi_detail_view(kpi_type, df):
    """
    Render detailed visualizations for a specific KPI
    
    Parameters:
    - kpi_type: Type of KPI ('students', 'faculty', 'defense_time', 'success_rate', 'efficiency', 'completion')
    - df: DataFrame containing the data
    """
    # Add a back button
    if st.button("← Voltar para KPI Dashboard"):
        st.session_state.selected_kpi = None
        st.rerun()
    
    # Render specific visualizations based on KPI type
    if kpi_type == "students":
        render_student_kpi_detail(df)
    
    elif kpi_type == "faculty":
        render_faculty_kpi_detail(df)
    
    elif kpi_type == "defense_time":
        render_defense_time_kpi_detail(df)
    
    elif kpi_type == "success_rate":
        render_success_rate_kpi_detail(df)
        
    elif kpi_type == "efficiency":
        render_efficiency_kpi_detail(df)
        
    elif kpi_type == "completion":
        render_completion_kpi_detail(df)

def render_student_kpi_detail(df):
    """Render detailed visualizations for student KPI"""
    st.header("Análise Detalhada: Total de Alunos")
    
    # Calculate total students
    total_students = len(df['student_id'].unique()) if 'student_id' in df.columns else 0
    
    # Display the KPI
    st.metric(
        label="Total de Alunos",
        value=total_students,
        help="Número total de alunos no programa"
    )
    
    # Create 2-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição de Alunos por Programa")
        
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
    
    with col2:
        st.subheader("Evolução do Número de Alunos")
        
        # Get time series data
        time_series_data = DataManager.get_time_series_data()
        
        if not time_series_data.empty:
            # Prepare data for time series chart
            time_series_data['year_month'] = time_series_data['year_month'].dt.strftime('%Y-%m')
            
            render_time_series_chart(
                time_series_data,
                title="Matrículas ao Longo do Tempo",
                x_column="year_month",
                y_column="enrollments"
            )
        else:
            st.info("Sem dados de série temporal disponíveis.")
    
    # Create second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição por Departamento")
        
        if 'department' in df.columns:
            dept_counts = df.groupby('department').size().reset_index(name='count')
            dept_counts = dept_counts.sort_values('count', ascending=False)
            
            render_bar_chart(
                dept_counts,
                title="Estudantes por Departamento",
                x_column="department",
                y_column="count"
            )
        else:
            st.info("Sem dados de departamento disponíveis.")
    
    with col2:
        st.subheader("Distribuição por Ano de Ingresso")
        
        if 'enrollment_date' in df.columns:
            df['enrollment_year'] = pd.to_datetime(df['enrollment_date']).dt.year
            year_counts = df.groupby('enrollment_year').size().reset_index(name='count')
            
            render_bar_chart(
                year_counts,
                title="Ingressos por Ano",
                x_column="enrollment_year",
                y_column="count"
            )
        else:
            st.info("Sem dados de data de ingresso disponíveis.")

def render_faculty_kpi_detail(df):
    """Render detailed visualizations for faculty KPI"""
    st.header("Análise Detalhada: Total de Docentes")
    
    # Calculate total faculty
    total_faculty = len(df['advisor_id'].unique()) if 'advisor_id' in df.columns else 0
    
    # Display the KPI
    st.metric(
        label="Total de Docentes",
        value=total_faculty,
        help="Número total de docentes orientando alunos"
    )
    
    # Create 2-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Orientadores com Mais Alunos")
        
        if 'advisor_name' in df.columns and 'student_id' in df.columns:
            advisor_counts = df.groupby('advisor_name').nunique()['student_id'].reset_index()
            advisor_counts.columns = ['advisor_name', 'student_count']
            advisor_counts = advisor_counts.sort_values('student_count', ascending=False).head(10)
            
            render_bar_chart(
                advisor_counts,
                title="Top 10 Orientadores por Número de Alunos",
                x_column="advisor_name",
                y_column="student_count",
                orientation='h'
            )
        else:
            st.info("Sem dados de orientadores disponíveis.")
    
    with col2:
        st.subheader("Distribuição de Alunos por Orientador")
        
        if 'advisor_id' in df.columns and 'student_id' in df.columns:
            # Count students per advisor
            students_per_advisor = df.groupby('advisor_id').nunique()['student_id'].reset_index()
            students_per_advisor.columns = ['advisor_id', 'student_count']
            
            # Create histogram of student counts
            counts_distribution = students_per_advisor['student_count'].value_counts().reset_index()
            counts_distribution.columns = ['student_count', 'advisor_count']
            counts_distribution = counts_distribution.sort_values('student_count')
            
            render_bar_chart(
                counts_distribution,
                title="Distribuição de Orientadores por Número de Alunos",
                x_column="student_count",
                y_column="advisor_count"
            )
        else:
            st.info("Sem dados suficientes para análise de orientadores.")
    
    # Create second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Taxa de Sucesso por Orientador")
        
        if 'advisor_name' in df.columns and 'defense_status' in df.columns:
            # Calculate success rate per advisor
            def calc_success_rate(group):
                return (group == 'Approved').mean()
            
            success_by_advisor = df.groupby('advisor_name')['defense_status'].agg(calc_success_rate).reset_index()
            success_by_advisor.columns = ['advisor_name', 'success_rate']
            success_by_advisor['success_rate'] = (success_by_advisor['success_rate'] * 100).round(1)
            success_by_advisor = success_by_advisor.sort_values('success_rate', ascending=False).head(10)
            
            render_bar_chart(
                success_by_advisor,
                title="Top 10 Orientadores por Taxa de Sucesso (%)",
                x_column="advisor_name",
                y_column="success_rate",
                orientation='h'
            )
        else:
            st.info("Sem dados suficientes para análise de sucesso por orientador.")
    
    with col2:
        st.subheader("Tempo Médio até Defesa por Orientador")
        
        if 'advisor_name' in df.columns and 'time_to_defense' in df.columns:
            # Calculate average time to defense per advisor
            time_by_advisor = df.groupby('advisor_name')['time_to_defense'].mean().reset_index()
            time_by_advisor['time_to_defense'] = time_by_advisor['time_to_defense'].round(1)
            time_by_advisor = time_by_advisor.sort_values('time_to_defense').head(10)
            
            render_bar_chart(
                time_by_advisor,
                title="Top 10 Orientadores por Menor Tempo até Defesa (meses)",
                x_column="advisor_name",
                y_column="time_to_defense",
                orientation='h'
            )
        else:
            st.info("Sem dados suficientes para análise de tempo por orientador.")

def render_defense_time_kpi_detail(df):
    """Render detailed visualizations for defense time KPI"""
    st.header("Análise Detalhada: Tempo até Defesa")
    
    # Calculate all time-related metrics
    if 'time_to_defense' in df.columns:
        valid_defenses = df[df['time_to_defense'].notna()]
        
        # Basic time metrics
        avg_time_to_defense = round(valid_defenses['time_to_defense'].mean(), 1)
        median_time_to_defense = round(valid_defenses['time_to_defense'].median(), 1)
        std_time = round(valid_defenses['time_to_defense'].std(), 1)
        min_time = round(valid_defenses['time_to_defense'].min(), 1)
        max_time = round(valid_defenses['time_to_defense'].max(), 1)
        
        # Calculate time range quantiles for better distribution understanding
        q25 = round(valid_defenses['time_to_defense'].quantile(0.25), 1)
        q75 = round(valid_defenses['time_to_defense'].quantile(0.75), 1)
        iqr = q75 - q25  # Interquartile range
        
        # Calculate percentage of students finishing on time
        if 'expected_time' in df.columns:
            on_time_pct = round(100 * (valid_defenses['time_to_defense'] <= valid_defenses['expected_time']).mean(), 1)
        else:
            # Assume Masters should finish in 24 months, PhD in 48 months
            if 'program' in df.columns:
                valid_defenses['expected_time'] = valid_defenses['program'].map({'Masters': 24, 'Doctorate': 48})
                on_time_pct = round(100 * (valid_defenses['time_to_defense'] <= valid_defenses['expected_time']).mean(), 1)
            else:
                on_time_pct = 0
    else:
        avg_time_to_defense = 0
        median_time_to_defense = 0
        std_time = 0
        min_time = 0
        max_time = 0
        q25 = 0
        q75 = 0
        iqr = 0
        on_time_pct = 0
    
    # Display metrics in a summary box
    st.markdown("### Resumo Estatístico do Tempo até Defesa")
    
    # Show metrics in a 4-column layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Média",
            value=f"{avg_time_to_defense} meses",
            help="Tempo médio desde o ingresso até a defesa"
        )
        
        st.metric(
            label="Mínimo",
            value=f"{min_time} meses",
            help="Menor tempo registrado para conclusão"
        )
    
    with col2:
        st.metric(
            label="Mediana",
            value=f"{median_time_to_defense} meses",
            help="Valor central (50% dos alunos concluem antes deste tempo)"
        )
        
        st.metric(
            label="Máximo",
            value=f"{max_time} meses",
            help="Maior tempo registrado para conclusão"
        )
    
    with col3:
        st.metric(
            label="Desvio Padrão",
            value=f"{std_time} meses",
            help="Medida de variabilidade/dispersão dos tempos de conclusão"
        )
        
        st.metric(
            label="1º Quartil (Q1)",
            value=f"{q25} meses",
            help="25% dos alunos concluem antes deste tempo"
        )
    
    with col4:
        st.metric(
            label="Amplitude Interquartil",
            value=f"{iqr} meses",
            help="Diferença entre Q3 e Q1, mostra a dispersão dos 50% centrais"
        )
        
        st.metric(
            label="3º Quartil (Q3)",
            value=f"{q75} meses",
            help="75% dos alunos concluem antes deste tempo"
        )
    
    # Create a concluding metric for "on time" percentage
    st.metric(
        label="Conclusões no Prazo",
        value=f"{on_time_pct}%",
        help="Porcentagem de alunos que concluem dentro do prazo esperado"
    )
    
    # Distribution and comparative charts
    st.markdown("### Análises Temporais")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição do Tempo até Defesa")
        
        if 'time_to_defense' in df.columns:
            # Create a more informative histogram with normal distribution overlay
            render_histogram(
                df[df['time_to_defense'].notna()],
                title="Distribuição do Tempo até Defesa (meses)",
                column="time_to_defense",
                bins=20
            )
        else:
            st.info("Sem dados de tempo até defesa disponíveis.")
    
    with col2:
        st.subheader("Tempo Médio por Programa")
        
        if 'time_to_defense' in df.columns and 'program' in df.columns:
            # Calculate average time to defense by program
            avg_time_by_program = df.groupby('program')['time_to_defense'].mean().reset_index()
            avg_time_by_program['time_to_defense'] = avg_time_by_program['time_to_defense'].round(1)
            avg_time_by_program = avg_time_by_program.sort_values('time_to_defense')
            
            render_bar_chart(
                avg_time_by_program,
                title="Tempo Médio até Defesa por Programa (meses)",
                x_column="program",
                y_column="time_to_defense"
            )
        else:
            st.info("Sem dados suficientes para análise por programa.")
    
    # Create a second row of visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tendência do Tempo até Defesa ao Longo do Tempo")
        
        if 'time_to_defense' in df.columns and 'enrollment_date' in df.columns:
            # Extract enrollment year
            df_with_year = df.copy()
            df_with_year['enrollment_year'] = pd.to_datetime(df_with_year['enrollment_date']).dt.year
            
            # Calculate average time to defense by enrollment year
            time_trend = df_with_year.groupby('enrollment_year')['time_to_defense'].mean().reset_index()
            time_trend['time_to_defense'] = time_trend['time_to_defense'].round(1)
            
            render_time_series_chart(
                time_trend,
                title="Evolução do Tempo Médio até Defesa por Ano de Ingresso",
                x_column="enrollment_year",
                y_column="time_to_defense"
            )
        else:
            st.info("Sem dados suficientes para análise de tendência temporal.")
    
    with col2:
        st.subheader("Tempo Médio até Defesa por Departamento")
        
        if 'time_to_defense' in df.columns and 'department' in df.columns:
            # Calculate average time to defense by department
            dept_time = df.groupby('department')['time_to_defense'].mean().reset_index()
            dept_time['time_to_defense'] = dept_time['time_to_defense'].round(1)
            dept_time = dept_time.sort_values('time_to_defense')
            
            render_bar_chart(
                dept_time,
                title="Tempo Médio até Defesa por Departamento (meses)",
                x_column="department",
                y_column="time_to_defense",
                orientation='h'
            )
        else:
            st.info("Sem dados suficientes para análise por departamento.")
            
    # Create a third row for additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Boxplot de Tempo até Defesa por Programa")
        
        if 'time_to_defense' in df.columns and 'program' in df.columns:
            # Create DataFrame for box plot
            box_df = df[df['time_to_defense'].notna()].copy()
            
            # Use a more sophisticated plotting library for boxplot
            import plotly.express as px
            fig = px.box(box_df, x='program', y='time_to_defense', 
                          title="Distribuição do Tempo até Defesa por Programa",
                          labels={"program": "Programa", "time_to_defense": "Tempo até Defesa (meses)"})
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados suficientes para análise de distribuição por programa.")
    
    with col2:
        st.subheader("Comparação com Tempo Esperado")
        
        if 'time_to_defense' in df.columns and 'program' in df.columns:
            # Create DataFrame for comparison
            compare_df = pd.DataFrame()
            
            # Calculate actual average times
            actual_times = df.groupby('program')['time_to_defense'].mean().reset_index()
            actual_times.columns = ['program', 'actual_time']
            
            # Set expected times
            expected_times = pd.DataFrame({
                'program': ['Masters', 'Doctorate'],
                'expected_time': [24, 48]
            })
            
            # Merge actual and expected
            compare_df = pd.merge(actual_times, expected_times, on='program')
            compare_df['actual_time'] = compare_df['actual_time'].round(1)
            
            # Convert to long format for grouped bar chart
            import pandas as pd
            compare_long = pd.melt(compare_df, 
                                   id_vars=['program'], 
                                   value_vars=['actual_time', 'expected_time'],
                                   var_name='type', 
                                   value_name='months')
            
            # Create more descriptive labels
            compare_long['type'] = compare_long['type'].map({
                'actual_time': 'Tempo Real', 
                'expected_time': 'Tempo Esperado'
            })
            
            # Create grouped bar chart
            import plotly.express as px
            fig = px.bar(compare_long, 
                         x='program', 
                         y='months', 
                         color='type',
                         barmode='group',
                         title="Tempo Real vs. Tempo Esperado por Programa",
                         labels={"program": "Programa", "months": "Meses", "type": "Tipo"})
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados suficientes para análise comparativa de tempos.")
    
    # Create second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolução do Tempo até Defesa")
        
        if 'time_to_defense' in df.columns and 'enrollment_date' in df.columns:
            # Calculate average time to defense by enrollment year
            df['enrollment_year'] = pd.to_datetime(df['enrollment_date']).dt.year
            time_by_year = df.groupby('enrollment_year')['time_to_defense'].mean().reset_index()
            time_by_year['time_to_defense'] = time_by_year['time_to_defense'].round(1)
            
            render_bar_chart(
                time_by_year,
                title="Tempo Médio até Defesa por Ano de Ingresso (meses)",
                x_column="enrollment_year",
                y_column="time_to_defense"
            )
        else:
            st.info("Sem dados suficientes para análise por ano.")
    
    with col2:
        st.subheader("Tempo Médio por Departamento")
        
        if 'time_to_defense' in df.columns and 'department' in df.columns:
            # Calculate average time to defense by department
            time_by_dept = df.groupby('department')['time_to_defense'].mean().reset_index()
            time_by_dept['time_to_defense'] = time_by_dept['time_to_defense'].round(1)
            time_by_dept = time_by_dept.sort_values('time_to_defense')
            
            render_bar_chart(
                time_by_dept,
                title="Tempo Médio até Defesa por Departamento (meses)",
                x_column="department",
                y_column="time_to_defense",
                orientation='h'
            )
        else:
            st.info("Sem dados suficientes para análise por departamento.")

def render_success_rate_kpi_detail(df):
    """Render detailed visualizations for success rate KPI"""
    st.header("Análise Detalhada: Taxa de Sucesso na Defesa")
    
    # Calculate defense success rate
    if 'defense_status' in df.columns:
        defense_success_rate = round(df[df['defense_status'] == 'Approved'].shape[0] / 
                                    max(1, df[df['defense_status'].notna()].shape[0]) * 100, 1)
    else:
        defense_success_rate = 0
    
    # Display the KPI
    st.metric(
        label="Taxa de Sucesso na Defesa",
        value=f"{defense_success_rate}%",
        help="Porcentagem de defesas com aprovação"
    )
    
    # Create 2-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Taxa de Sucesso por Programa")
        
        if 'defense_status' in df.columns and 'program' in df.columns:
            # Calculate success rate by program
            from utils.calculations import calculate_success_rate
            success_rate_by_program = calculate_success_rate(df, by_group='program')
            
            if not success_rate_by_program.empty:
                success_rate_by_program['success_rate'] = (success_rate_by_program['success_rate'] * 100).round(1)
                
                render_bar_chart(
                    success_rate_by_program,
                    title="Taxa de Sucesso por Programa (%)",
                    x_column="program",
                    y_column="success_rate"
                )
        else:
            st.info("Sem dados suficientes para análise por programa.")
    
    with col2:
        st.subheader("Status das Defesas")
        
        if 'defense_status' in df.columns:
            # Count defenses by status
            status_counts = df['defense_status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            render_pie_chart(
                status_counts,
                title="Distribuição de Status das Defesas",
                values_column="count",
                names_column="status"
            )
        else:
            st.info("Sem dados de status de defesa disponíveis.")
    
    # Create second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolução da Taxa de Sucesso")
        
        if 'defense_status' in df.columns and 'defense_date' in df.columns:
            # Calculate success rate by year
            df['defense_year'] = pd.to_datetime(df['defense_date']).dt.year
            
            # Group by year and calculate success rate
            def calc_success_rate(group):
                return (group == 'Approved').mean() * 100
            
            success_by_year = df.groupby('defense_year')['defense_status'].agg(calc_success_rate).reset_index()
            success_by_year.columns = ['defense_year', 'success_rate']
            success_by_year['success_rate'] = success_by_year['success_rate'].round(1)
            
            render_bar_chart(
                success_by_year,
                title="Taxa de Sucesso por Ano de Defesa (%)",
                x_column="defense_year",
                y_column="success_rate"
            )
        else:
            st.info("Sem dados suficientes para análise por ano.")
    
    with col2:
        st.subheader("Taxa de Sucesso por Tempo até Defesa")
        
        if 'defense_status' in df.columns and 'time_to_defense' in df.columns:
            # Bin time to defense
            df['time_bin'] = pd.cut(df['time_to_defense'], 
                                    bins=[0, 12, 24, 36, 48, float('inf')],
                                    labels=['0-12', '13-24', '25-36', '37-48', '48+'])
            
            # Calculate success rate by time bin
            success_by_time = df.groupby('time_bin')['defense_status'].apply(
                lambda x: (x == 'Approved').mean() * 100).reset_index()
            success_by_time.columns = ['time_bin', 'success_rate']
            success_by_time['success_rate'] = success_by_time['success_rate'].round(1)
            
            render_bar_chart(
                success_by_time,
                title="Taxa de Sucesso por Tempo até Defesa (meses)",
                x_column="time_bin",
                y_column="success_rate"
            )
        else:
            st.info("Sem dados suficientes para análise por tempo.")

def render_visualizations(df):
    """Render only the visualizations part of the overview page"""
    # Get time series data for enrollment and defenses
    from components.charts import render_time_series_chart, render_bar_chart, render_pie_chart
    from utils.calculations import calculate_success_rate
    
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
            
            if not isinstance(success_rate_by_program, float) and not success_rate_by_program.empty:
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

def render_efficiency_kpi_detail(df):
    """Render detailed visualizations for time efficiency KPI"""
    st.header("Análise Detalhada: Eficiência de Tempo")
    
    # Calculate efficiency metrics
    if 'time_to_defense' in df.columns and 'program' in df.columns:
        # Mapear programa para tempo esperado de conclusão
        df = df.copy()  # Criar cópia para evitar avisos do pandas
        df['expected_time'] = df['program'].map({'Masters': 24, 'Doctorate': 48, 'Mestrado': 24, 'Doutorado': 48})
        
        # Filtrar estudantes com dados válidos
        valid_students = df[(df['time_to_defense'].notna()) & (df['time_to_defense'] > 0) & (df['expected_time'].notna())].copy()
        
        if not valid_students.empty:
            # Calcular eficiência (tempo esperado / tempo real)
            valid_students.loc[:, 'time_efficiency'] = valid_students['expected_time'] / valid_students['time_to_defense']
            valid_students.loc[:, 'time_efficiency'] = valid_students['time_efficiency'].clip(upper=2.0)  # Limitar para 200%
            valid_students.loc[:, 'efficiency_pct'] = (valid_students['time_efficiency'] * 100).round(1)
            
            # Calcular média de eficiência
            avg_time_efficiency = round(valid_students['time_efficiency'].mean() * 100, 1)
            
            # Calcular quartis de eficiência
            q25 = round(valid_students['efficiency_pct'].quantile(0.25), 1)
            q50 = round(valid_students['efficiency_pct'].quantile(0.5), 1)
            q75 = round(valid_students['efficiency_pct'].quantile(0.75), 1)
            
            # Calcular percentual de estudantes que concluem no tempo esperado
            on_time_pct = round(100 * (valid_students['time_efficiency'] >= 1.0).mean(), 1)
            
            # Exibir métricas resumidas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Eficiência de Tempo Média",
                    value=f"{avg_time_efficiency}%",
                    help="Proporção do tempo esperado vs. tempo real (maior = mais eficiente)"
                )
            
            with col2:
                st.metric(
                    label="Eficiência Mediana",
                    value=f"{q50}%",
                    help="Valor central da eficiência de tempo"
                )
            
            with col3:
                st.metric(
                    label="Concluídos no Tempo",
                    value=f"{on_time_pct}%",
                    help="Percentual de estudantes que concluem no tempo esperado ou antes"
                )
            
            with col4:
                st.metric(
                    label="Eficiência do 3º Quartil",
                    value=f"{q75}%",
                    help="75% dos estudantes têm eficiência abaixo deste valor"
                )
            
            # Criar visualizações
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribuição da Eficiência de Tempo")
                
                # Criar bins de eficiência
                bins = [0, 50, 75, 90, 100, 125, 150, 175, 200]
                labels = ["<50%", "50-75%", "75-90%", "90-100%", "100-125%", "125-150%", "150-175%", "175-200%"]
                valid_students.loc[:, 'efficiency_bin'] = pd.cut(valid_students['efficiency_pct'], bins=bins, labels=labels)
                
                # Contar estudantes em cada bin
                efficiency_dist = valid_students['efficiency_bin'].value_counts().reset_index()
                efficiency_dist.columns = ['efficiency_range', 'count']
                efficiency_dist = efficiency_dist.sort_values('efficiency_range')
                
                # Gráfico de barras da distribuição
                render_bar_chart(
                    efficiency_dist,
                    title="Distribuição da Eficiência de Tempo dos Estudantes",
                    x_column="efficiency_range",
                    y_column="count"
                )
            
            with col2:
                st.subheader("Eficiência de Tempo por Programa")
                
                # Calcular eficiência média por programa
                efficiency_by_program = valid_students.groupby('program')['efficiency_pct'].mean().reset_index()
                efficiency_by_program['efficiency_pct'] = efficiency_by_program['efficiency_pct'].round(1)
                
                # Gráfico de barras por programa
                render_bar_chart(
                    efficiency_by_program,
                    title="Eficiência Média por Programa (%)",
                    x_column="program",
                    y_column="efficiency_pct"
                )
            
            # Segunda linha de gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Tempo Real vs. Tempo Esperado")
                
                # Calcular tempo médio por programa
                program_times = valid_students.groupby('program').agg({
                    'time_to_defense': 'mean',
                    'expected_time': 'mean'
                }).reset_index()
                
                program_times['time_to_defense'] = program_times['time_to_defense'].round(1)
                program_times['expected_time'] = program_times['expected_time'].round(1)
                
                # Converter para formato longo para gráfico de barras agrupadas
                program_times_long = pd.melt(
                    program_times, 
                    id_vars=['program'], 
                    value_vars=['time_to_defense', 'expected_time'],
                    var_name='time_type', 
                    value_name='months'
                )
                
                # Renomear para melhor legibilidade
                program_times_long['time_type'] = program_times_long['time_type'].map({
                    'time_to_defense': 'Tempo Real',
                    'expected_time': 'Tempo Esperado'
                })
                
                # Renderizar gráfico de barras agrupadas
                import plotly.express as px
                fig = px.bar(
                    program_times_long, 
                    x='program', 
                    y='months',
                    color='time_type',
                    barmode='group',
                    title="Tempo Real vs. Tempo Esperado por Programa (meses)",
                    labels={"program": "Programa", "months": "Meses", "time_type": "Tipo de Tempo"}
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                if 'advisor_name' in df.columns:
                    st.subheader("Eficiência por Orientador (Top 10)")
                    
                    # Calcular eficiência média por orientador
                    efficiency_by_advisor = valid_students.groupby('advisor_name')['efficiency_pct'].mean().reset_index()
                    efficiency_by_advisor['efficiency_pct'] = efficiency_by_advisor['efficiency_pct'].round(1)
                    efficiency_by_advisor = efficiency_by_advisor.sort_values('efficiency_pct', ascending=False).head(10)
                    
                    # Gráfico de barras por orientador
                    render_bar_chart(
                        efficiency_by_advisor,
                        title="Top 10 Orientadores por Eficiência de Tempo (%)",
                        x_column="advisor_name",
                        y_column="efficiency_pct",
                        orientation='h'
                    )
                else:
                    st.info("Sem dados de orientadores disponíveis.")
            
            # Adicionar filtros interativos
            st.subheader("Análise Detalhada com Filtros")
            
            # Criar filtro de programa
            program_options = valid_students['program'].unique().tolist()
            selected_programs = st.multiselect(
                "Filtrar por Programa", 
                options=program_options,
                default=program_options
            )
            
            # Filtrar por departamento se disponível
            department_filter = None
            if 'department' in valid_students.columns:
                department_options = valid_students['department'].unique().tolist()
                selected_departments = st.multiselect(
                    "Filtrar por Departamento", 
                    options=department_options,
                    default=department_options
                )
                department_filter = valid_students['department'].isin(selected_departments)
            
            # Aplicar filtros
            filtered_data = valid_students
            if selected_programs:
                filtered_data = filtered_data[filtered_data['program'].isin(selected_programs)]
            if department_filter is not None:
                filtered_data = filtered_data[department_filter]
            
            # Mostrar tabela de eficiência filtrada
            if not filtered_data.empty:
                st.subheader("Tabela de Eficiência (Filtrada)")
                
                display_columns = ['student_name', 'program', 'enrollment_date', 'defense_date', 
                                  'time_to_defense', 'expected_time', 'efficiency_pct']
                display_columns = [col for col in display_columns if col in filtered_data.columns]
                
                st.dataframe(
                    filtered_data[display_columns].sort_values('efficiency_pct', ascending=False),
                    use_container_width=True
                )
            else:
                st.info("Nenhum dado encontrado com os filtros selecionados.")
        else:
            st.warning("Sem dados válidos para calcular a eficiência de tempo.")
    else:
        st.warning("Dados insuficientes para análise de eficiência de tempo. São necessários tempo até defesa e programa.")

def render_completion_kpi_detail(df):
    """Render detailed visualizations for completion rate KPI"""
    st.header("Análise Detalhada: Taxa de Conclusão")
    
    # Calcular métricas de conclusão
    if 'defense_status' in df.columns:
        df = df.copy()  # Criar cópia para evitar avisos
        
        # Total de defesas concluídas
        completed_defenses = df[df['defense_status'].notna()].shape[0]
        total_students = df.shape[0]
        
        # Taxa de conclusão (alunos que defenderam / total de alunos)
        defense_completion_rate = round(completed_defenses / max(1, total_students) * 100, 1)
        
        # Exibir o KPI principal
        st.metric(
            label="Taxa de Conclusão",
            value=f"{defense_completion_rate}%",
            help="Porcentagem de alunos que concluíram a defesa"
        )
        
        # Visualizações em duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Taxa de Conclusão por Programa")
            
            if 'program' in df.columns:
                # Calcular taxa de conclusão por programa
                completion_by_program = df.groupby('program').apply(
                    lambda x: x['defense_status'].notna().mean() * 100
                ).reset_index()
                completion_by_program.columns = ['program', 'completion_rate']
                completion_by_program['completion_rate'] = completion_by_program['completion_rate'].round(1)
                
                render_bar_chart(
                    completion_by_program,
                    title="Taxa de Conclusão por Programa (%)",
                    x_column="program",
                    y_column="completion_rate"
                )
            else:
                st.info("Sem dados de programa disponíveis.")
        
        with col2:
            st.subheader("Status dos Alunos")
            
            # Calcular contagem de status
            df.loc[:, 'completion_status'] = df['defense_status'].apply(
                lambda x: 'Concluído' if pd.notna(x) else 'Em Andamento'
            )
            status_counts = df['completion_status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            render_pie_chart(
                status_counts,
                title="Distribuição de Status dos Alunos",
                values_column="count",
                names_column="status"
            )
        
        # Segunda linha de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Conclusão por Período de Ingresso")
            
            if 'enrollment_date' in df.columns:
                # Agrupar por ano de ingresso
                df.loc[:, 'enrollment_year'] = pd.to_datetime(df['enrollment_date']).dt.year
                completion_by_year = df.groupby('enrollment_year').apply(
                    lambda x: x['defense_status'].notna().mean() * 100
                ).reset_index()
                completion_by_year.columns = ['year', 'completion_rate']
                completion_by_year['completion_rate'] = completion_by_year['completion_rate'].round(1)
                
                render_time_series_chart(
                    completion_by_year,
                    title="Taxa de Conclusão por Ano de Ingresso (%)",
                    x_column="year",
                    y_column="completion_rate"
                )
            else:
                st.info("Sem dados de data de ingresso disponíveis.")
        
        with col2:
            st.subheader("Tempo Médio por Status")
            
            if 'time_to_defense' in df.columns:
                # Comparar tempos para concluídos e em andamento
                # Para alunos em andamento, calcular tempo desde o ingresso até agora
                import datetime as dt
                
                df.loc[:, 'time_elapsed'] = df['time_to_defense']
                mask_ongoing = df['defense_status'].isna()
                
                if mask_ongoing.any() and 'enrollment_date' in df.columns:
                    current_date = pd.Timestamp.now()
                    df.loc[mask_ongoing, 'time_elapsed'] = (
                        (current_date - pd.to_datetime(df.loc[mask_ongoing, 'enrollment_date'])).dt.days / 30.44
                    )
                
                df.loc[:, 'student_status'] = df['defense_status'].apply(
                    lambda x: 'Concluído' if pd.notna(x) else 'Em Andamento'
                )
                
                time_by_status = df.groupby('student_status')['time_elapsed'].mean().reset_index()
                time_by_status['time_elapsed'] = time_by_status['time_elapsed'].round(1)
                
                render_bar_chart(
                    time_by_status,
                    title="Tempo Médio por Status (meses)",
                    x_column="student_status",
                    y_column="time_elapsed"
                )
            else:
                st.info("Sem dados de tempo disponíveis.")
                
        # Adicionar filtros interativos e tabela
        st.subheader("Análise Detalhada com Filtros")
        
        # Filtro por status
        status_options = ['Concluído', 'Em Andamento']
        selected_status = st.multiselect(
            "Filtrar por Status", 
            options=status_options,
            default=status_options
        )
        
        # Filtro por programa
        program_filter = None
        if 'program' in df.columns:
            program_options = df['program'].unique().tolist()
            selected_programs = st.multiselect(
                "Filtrar por Programa", 
                options=program_options,
                default=program_options
            )
            program_filter = df['program'].isin(selected_programs)
        
        # Aplicar filtros
        filtered_data = df
        if selected_status:
            filtered_data = filtered_data[filtered_data['completion_status'].isin(selected_status)]
        if program_filter is not None:
            filtered_data = filtered_data[program_filter]
        
        # Mostrar tabela filtrada
        if not filtered_data.empty:
            st.subheader("Tabela de Alunos (Filtrada)")
            
            display_columns = ['student_name', 'program', 'enrollment_date', 'defense_date', 
                              'completion_status', 'time_elapsed']
            display_columns = [col for col in display_columns if col in filtered_data.columns]
            
            st.dataframe(
                filtered_data[display_columns].sort_values('time_elapsed', ascending=False),
                use_container_width=True
            )
        else:
            st.info("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.warning("Dados insuficientes para análise de taxa de conclusão.")

if __name__ == "__main__":
    main()
