import streamlit as st
import pandas as pd
import numpy as np
from utils.kpi_calculations import calculate_kpis, get_kpi_descriptions, get_kpi_categories
import plotly.express as px
import plotly.graph_objects as go

def render_capes_kpi_dashboard():
    """
    Renderiza o dashboard de KPIs da CAPES
    """
    st.header("🎯 Dashboard de Indicadores CAPES - Engenharias IV")
    
    st.markdown("""
    <style>
    .kpi-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
    }
    .kpi-card .value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #007bff;
    }
    .kpi-card .title {
        font-size: 1rem;
        color: #495057;
    }
    .kpi-card .description {
        font-size: 0.85rem;
        color: #6c757d;
    }
    .kpi-section {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Calcular os KPIs
    with st.spinner("Calculando indicadores..."):
        kpis = calculate_kpis()
        kpi_descriptions = get_kpi_descriptions()
        kpi_categories = get_kpi_categories()
    
    # Exibição por categorias
    tabs = st.tabs(list(kpi_categories.keys()) + ["Todos os Indicadores"])
    
    # Para cada categoria, exibir os KPIs correspondentes
    for i, (category, kpi_list) in enumerate(kpi_categories.items()):
        with tabs[i]:
            render_kpi_category(category, kpi_list, kpis, kpi_descriptions)
    
    # Exibir todos os KPIs em uma única página
    with tabs[-1]:
        st.subheader("Visão Geral de Todos os Indicadores")
        
        # Criar tabela com todos os KPIs
        kpi_table = []
        for category, kpi_list in kpi_categories.items():
            for kpi in kpi_list:
                if kpi in kpis:
                    kpi_table.append({
                        "Categoria": category,
                        "Indicador": kpi,
                        "Descrição": kpi_descriptions.get(kpi, ""),
                        "Valor": kpis.get(kpi, 0)
                    })
        
        # Converter para DataFrame e exibir
        kpi_df = pd.DataFrame(kpi_table)
        st.dataframe(kpi_df, use_container_width=True, hide_index=True)
        
        # Opção para baixar como CSV
        csv = kpi_df.to_csv(index=False)
        st.download_button(
            label="Baixar Indicadores como CSV",
            data=csv,
            file_name=f"indicadores_capes_engenharias_iv.csv",
            mime="text/csv"
        )

def render_kpi_category(category, kpi_list, kpis, kpi_descriptions):
    """
    Renderiza os KPIs de uma categoria específica
    
    Parameters:
    - category: Nome da categoria
    - kpi_list: Lista de KPIs da categoria
    - kpis: Dicionário com valores de todos os KPIs
    - kpi_descriptions: Dicionário com descrições dos KPIs
    """
    st.subheader(f"{category}")
    
    # Distribuir os KPIs em colunas (3 por linha)
    rows = (len(kpi_list) + 2) // 3
    
    for row in range(rows):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            if idx < len(kpi_list):
                kpi = kpi_list[idx]
                if kpi in kpis:
                    with cols[col]:
                        render_kpi_card(kpi, kpis[kpi], kpi_descriptions.get(kpi, ""))
    
    # Adicionar visualizações específicas para a categoria
    if category == "Corpo Docente":
        render_faculty_charts(kpis)
    elif category == "Formação Discente":
        render_student_charts(kpis)
    elif category == "Egressos":
        render_alumni_charts(kpis)
    elif category == "Produção Intelectual":
        render_production_charts(kpis)
    elif category == "Disciplinas":
        render_course_charts(kpis)

def render_kpi_card(kpi, value, description):
    """
    Renderiza um card para exibir um KPI
    
    Parameters:
    - kpi: Nome do KPI
    - value: Valor do KPI
    - description: Descrição do KPI
    """
    # Formatação adequada para diferentes tipos de KPIs
    if isinstance(value, (int, np.integer)):
        formatted_value = f"{value:,}".replace(",", ".")
    elif isinstance(value, float) and kpi.endswith(('rate', 'percentage')) or kpi in ['for', 'fordt', 'ded', 'd3a', 'ade1', 'ade2', 'dpd', 'dtd', 'diep', 'dieg', 'dier', 'ader', 'disc', 'taxa_aprovacao']:
        formatted_value = f"{value:.1f}%"
    else:
        formatted_value = f"{value:.2f}"
    
    # Título mais amigável para o KPI
    kpi_titles = {
        'for_h': "Fator H",
        'for': "Bolsas PQ",
        'fordt': "Bolsas DT",
        'ded': "Dedicação Exclusiva",
        'd3a': "Envolvimento em Pesquisa",
        'ade1': "Carga Horária Colaboradores",
        'ade2': "Orientações Colaboradores",
        'ati': "Carga Horária na Pós",
        'atg1': "Carga Horária na Graduação",
        'atg2': "Orientações de IC",
        'ori': "Índice de Formação",
        'pdo': "Distribuição de Orientações",
        'dpi_docente': "Produção Docente",
        'dpi_discente_dout': "Produção Doutorandos",
        'dpi_discente_mest': "Produção Mestrandos",
        'dpd': "Distribuição da Produção",
        'dtd': "Docentes com Patentes",
        'ader': "Aderência à Área",
        'diep': "Empregabilidade",
        'dieg': "Continuidade Acadêmica",
        'dier': "Distribuição Regional",
        'disc': "Oferta de Disciplinas",
        'taxa_aprovacao': "Taxa de Aprovação",
        'total_docentes_permanentes': "Docentes Permanentes",
        'total_mestres': "Mestres Formados",
        'total_doutores': "Doutores Formados",
        'total_periodicos': "Artigos em Periódicos",
        'total_conferencias': "Artigos em Conferências"
    }
    
    title = kpi_titles.get(kpi, kpi.replace('_', ' ').title())
    
    # Criar o card
    st.markdown(f"""
    <div class="kpi-card">
        <div class="value">{formatted_value}</div>
        <div class="title">{title}</div>
        <div class="description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def render_faculty_charts(kpis):
    """
    Renderiza gráficos relacionados ao corpo docente
    
    Parameters:
    - kpis: Dicionário com valores de todos os KPIs
    """
    st.subheader("Análise do Corpo Docente")
    
    # Gráfico de barras para indicadores de qualificação docente
    qualifications = {
        "Bolsas PQ (FOR)": kpis.get('for', 0),
        "Bolsas DT (FORDT)": kpis.get('fordt', 0),
        "Dedicação Exclusiva (DED)": kpis.get('ded', 0),
        "Envolvimento em Pesquisa (D3A)": kpis.get('d3a', 0),
    }
    
    fig1 = px.bar(
        x=list(qualifications.keys()),
        y=list(qualifications.values()),
        title="Indicadores de Qualificação Docente (%)",
        labels={"x": "", "y": "Percentual (%)"},
        color=list(qualifications.keys()),
        template="plotly_white"
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico de indicadores de carga de trabalho
    col1, col2 = st.columns(2)
    
    with col1:
        workload = {
            "Na Pós-Graduação (ATI)": kpis.get('ati', 0),
            "Na Graduação (ATG1)": kpis.get('atg1', 0)
        }
        
        fig2 = px.bar(
            x=list(workload.keys()),
            y=list(workload.values()),
            title="Carga Horária Média Anual",
            labels={"x": "", "y": "Horas"},
            color=list(workload.keys()),
            template="plotly_white"
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2)
    
    with col2:
        # Gráfico de gauge para fator H
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=kpis.get('for_h', 0),
            title={"text": "Fator H Médio (FOR-H)"},
            gauge={
                'axis': {'range': [0, 20]},
                'bar': {'color': "royalblue"},
                'steps': [
                    {'range': [0, 5], 'color': "lightgray"},
                    {'range': [5, 10], 'color': "lightblue"},
                    {'range': [10, 15], 'color': "cornflowerblue"},
                    {'range': [15, 20], 'color': "royalblue"}
                ]
            }
        ))
        st.plotly_chart(fig3)

def render_student_charts(kpis):
    """
    Renderiza gráficos relacionados à formação discente
    
    Parameters:
    - kpis: Dicionário com valores de todos os KPIs
    """
    st.subheader("Análise da Formação Discente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza para distribuição de titulados
        titulados = {
            "Mestres": kpis.get('total_mestres', 0),
            "Doutores": kpis.get('total_doutores', 0)
        }
        
        fig1 = px.pie(
            values=list(titulados.values()),
            names=list(titulados.keys()),
            title="Distribuição de Titulados",
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig1)
    
    with col2:
        # Gráfico de barras para produção discente
        production = {
            "Doutorandos (DPI_disc_Dout)": kpis.get('dpi_discente_dout', 0),
            "Mestrandos (DPI_disc_Mest)": kpis.get('dpi_discente_mest', 0)
        }
        
        fig2 = px.bar(
            x=list(production.keys()),
            y=list(production.values()),
            title="Produção Intelectual Discente",
            labels={"x": "", "y": "Índice DPI"},
            color=list(production.keys()),
            template="plotly_white"
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2)
    
    # Gauge para índice ORI
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kpis.get('ori', 0),
        title={"text": "Índice de Formação (ORI)"},
        gauge={
            'axis': {'range': [0, 5]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 1], 'color': "lightgray"},
                {'range': [1, 2], 'color': "lightgreen"},
                {'range': [2, 3], 'color': "mediumseagreen"},
                {'range': [3, 5], 'color': "green"}
            ]
        }
    ))
    st.plotly_chart(fig3, use_container_width=True)

def render_alumni_charts(kpis):
    """
    Renderiza gráficos relacionados aos egressos
    
    Parameters:
    - kpis: Dicionário com valores de todos os KPIs
    """
    st.subheader("Análise dos Egressos")
    
    # Gráfico de barras para indicadores de egressos
    alumni = {
        "Empregabilidade (DIEP)": kpis.get('diep', 0),
        "Continuidade Acadêmica (DIEG)": kpis.get('dieg', 0),
        "Distribuição Regional (DIER)": kpis.get('dier', 0)
    }
    
    fig = px.bar(
        x=list(alumni.keys()),
        y=list(alumni.values()),
        title="Indicadores de Egressos (%)",
        labels={"x": "", "y": "Percentual (%)"},
        color=list(alumni.keys()),
        template="plotly_white"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def render_production_charts(kpis):
    """
    Renderiza gráficos relacionados à produção intelectual
    
    Parameters:
    - kpis: Dicionário com valores de todos os KPIs
    """
    st.subheader("Análise da Produção Intelectual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza para distribuição de publicações
        publications = {
            "Periódicos": kpis.get('total_periodicos', 0),
            "Conferências": kpis.get('total_conferencias', 0)
        }
        
        fig1 = px.pie(
            values=list(publications.values()),
            names=list(publications.keys()),
            title="Distribuição de Publicações",
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig1)
    
    with col2:
        # Gráfico de gauge para aderência à área
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=kpis.get('ader', 0),
            title={"text": "Aderência à Área (ADER)"},
            delta={'reference': 80, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "lightskyblue"},
                    {'range': [75, 100], 'color': "royalblue"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        st.plotly_chart(fig2)
    
    # Gráfico de barras para indicadores de produção
    production = {
        "Produção Docente (DPI_docente)": kpis.get('dpi_docente', 0),
        "Distribuição da Produção (DPD)": kpis.get('dpd', 0) / 100 * kpis.get('dpi_docente', 0),
        "Docentes com Patentes (DTD)": kpis.get('dtd', 0) / 100 * kpis.get('dpi_docente', 0)
    }
    
    fig3 = px.bar(
        x=list(production.keys()),
        y=list(production.values()),
        title="Indicadores de Produção",
        labels={"x": "", "y": "Valor"},
        color=list(production.keys()),
        template="plotly_white"
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

def render_course_charts(kpis):
    """
    Renderiza gráficos relacionados às disciplinas
    
    Parameters:
    - kpis: Dicionário com valores de todos os KPIs
    """
    st.subheader("Análise das Disciplinas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de gauge para oferta de disciplinas
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=kpis.get('disc', 0),
            title={"text": "Oferta de Disciplinas (DISC)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "lightgreen"},
                    {'range': [75, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        st.plotly_chart(fig1)
    
    with col2:
        # Gráfico de gauge para taxa de aprovação
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=kpis.get('taxa_aprovacao', 0),
            title={"text": "Taxa de Aprovação"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 85], 'color': "lightskyblue"},
                    {'range': [85, 100], 'color': "royalblue"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        st.plotly_chart(fig2)

def render_kpi_table(kpis):
    """
    Renderiza uma tabela com todos os KPIs
    
    Parameters:
    - kpis: Dicionário com valores dos KPIs
    """
    st.subheader("Tabela de Indicadores")
    
    # Criar DataFrame para exibição
    kpi_descriptions = get_kpi_descriptions()
    kpi_categories = get_kpi_categories()
    
    data = []
    for category, kpi_list in kpi_categories.items():
        for kpi in kpi_list:
            if kpi in kpis:
                data.append({
                    "Categoria": category,
                    "Indicador": kpi,
                    "Descrição": kpi_descriptions.get(kpi, ""),
                    "Valor": kpis[kpi]
                })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)