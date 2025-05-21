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
    st.title("🎯 Dashboard de Indicadores CAPES - Engenharias IV")
    
    st.markdown("""
    <div class="help-text">
    Este dashboard exibe os principais indicadores utilizados na avaliação de programas de pós-graduação
    pela CAPES na área de Engenharias IV. Os indicadores estão organizados em 5 categorias principais.
    </div>
    """, unsafe_allow_html=True)
    
    # Adicionar explicação sobre os dados
    with st.expander("ℹ️ Sobre os Indicadores CAPES"):
        st.markdown("""
        ### Indicadores de Avaliação CAPES para Engenharias IV
        
        Os indicadores exibidos neste dashboard são baseados nos critérios de avaliação da CAPES para programas 
        de pós-graduação na área de Engenharias IV. Eles são utilizados para avaliar diferentes aspectos do programa,
        como qualidade do corpo docente, formação discente, produção intelectual e impacto social.
        
        As categorias principais são:
        - **Corpo Docente**: Avaliação da qualificação e dedicação dos docentes
        - **Formação Discente**: Métricas relacionadas à formação e produção dos alunos
        - **Egressos**: Acompanhamento da trajetória profissional e acadêmica dos ex-alunos
        - **Produção Intelectual**: Qualidade e quantidade da produção científica
        - **Disciplinas**: Oferta e aproveitamento das disciplinas
        
        Para mais informações sobre cada indicador, consulte a documentação oficial da CAPES.
        """)
        
        st.info("Os valores exibidos são calculados com base nos dados carregados no sistema. Para indicadores mais precisos, é importante manter a base de dados atualizada.")
        
    
    st.markdown("""
    <style>
    .kpi-card {
        padding: 1.25rem;
        border-radius: 0.6rem;
        margin-bottom: 1.2rem;
        background-color: #ffffff;
        border-left: 5px solid #007bff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .kpi-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 0.3rem;
    }
    .kpi-card .title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .kpi-card .description {
        font-size: 0.9rem;
        color: #6c757d;
        line-height: 1.4;
    }
    .kpi-section {
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #f8f9fa;
        border-radius: 0.8rem;
    }
    .indicator-category {
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
        color: #0066cc;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.6rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    .help-text {
        background-color: #e7f3ff;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
        border-left: 4px solid #007bff;
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
    st.markdown(f"<h3 class='indicator-category'>{category}</h3>", unsafe_allow_html=True)
    
    # Adicionar descrição para cada categoria
    category_descriptions = {
        "Corpo Docente": "Indicadores relacionados à qualificação, produtividade e dedicação do corpo docente do programa.",
        "Formação Discente": "Métricas que avaliam a formação dos alunos e sua produção científica durante o curso.",
        "Egressos": "Acompanhamento da trajetória profissional e acadêmica dos alunos após a conclusão do curso.",
        "Produção Intelectual": "Análise da quantidade e qualidade da produção científica e tecnológica do programa.",
        "Disciplinas": "Informações sobre a oferta e o aproveitamento das disciplinas do programa."
    }
    
    st.markdown(f"<div class='help-text'>{category_descriptions.get(category, '')}</div>", unsafe_allow_html=True)
    
    # Criar seção para exibição dos cards
    st.markdown("<div class='kpi-section'>", unsafe_allow_html=True)
    
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
    
    st.markdown("</div>", unsafe_allow_html=True)
    
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
    elif isinstance(value, float) and (kpi.endswith(('rate', 'percentage')) or kpi in ['for', 'fordt', 'ded', 'd3a', 'ade1', 'ade2', 'dpd', 'dtd', 'diep', 'dieg', 'dier', 'ader', 'disc', 'taxa_aprovacao']):
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
    
    # Definir cores para diferentes categorias de KPIs
    kpi_colors = {
        # Corpo Docente - Azul
        'for_h': "#1E88E5",
        'for': "#1E88E5",
        'fordt': "#1E88E5",
        'ded': "#1E88E5",
        'd3a': "#1E88E5",
        'ade1': "#1E88E5",
        'ade2': "#1E88E5",
        'ati': "#1E88E5",
        'atg1': "#1E88E5",
        'atg2': "#1E88E5",
        'dpd': "#1E88E5",
        'dtd': "#1E88E5",
        'total_docentes_permanentes': "#1E88E5",
        
        # Formação Discente - Verde
        'ori': "#26A69A",
        'pdo': "#26A69A",
        'dpi_discente_dout': "#26A69A",
        'dpi_discente_mest': "#26A69A",
        'total_mestres': "#26A69A",
        'total_doutores': "#26A69A",
        
        # Egressos - Laranja
        'diep': "#FF7043",
        'dieg': "#FF7043",
        'dier': "#FF7043",
        
        # Produção Intelectual - Roxo
        'dpi_docente': "#7E57C2",
        'ader': "#7E57C2",
        'total_periodicos': "#7E57C2",
        'total_conferencias': "#7E57C2",
        
        # Disciplinas - Amarelo
        'disc': "#F9A825",
        'taxa_aprovacao': "#F9A825"
    }
    
    # Cor padrão para KPIs não definidos
    color = kpi_colors.get(kpi, "#546E7A")
    
    # Criar o card com estilo baseado na categoria
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 5px solid {color}">
        <div class="value" style="color: {color}">{formatted_value}</div>
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
    st.markdown("<div class='chart-section'>", unsafe_allow_html=True)
    st.subheader("📊 Análise do Corpo Docente")
    
    st.markdown("""
    <div class="help-text" style="margin-bottom: 20px;">
    A análise do corpo docente considera aspectos como qualificação, dedicação e produtividade.
    Os dados apresentados abaixo refletem os principais indicadores utilizados pela CAPES para
    avaliar a qualidade e o envolvimento dos docentes permanentes do programa.
    </div>
    """, unsafe_allow_html=True)
    
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
        template="plotly_white",
        color_discrete_sequence=["#1E88E5", "#26A69A", "#FF7043", "#7E57C2"]
    )
    fig1.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        height=400,
        hovermode="x",
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico de comparação de diversos indicadores
    cols = st.columns(2)
    
    with cols[0]:
        # Gráfico de radar para comparação dos indicadores do corpo docente
        categories = ['FOR', 'FORDT', 'DED', 'D3A', 'DPD', 'DTD']
        values = [
            kpis.get('for', 0)/100, 
            kpis.get('fordt', 0)/100, 
            kpis.get('ded', 0)/100, 
            kpis.get('d3a', 0)/100, 
            kpis.get('dpd', 0)/100, 
            kpis.get('dtd', 0)/100
        ]
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Corpo Docente',
            line_color='#1E88E5',
            fillcolor='rgba(30, 136, 229, 0.3)'
        ))
        
        fig2.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Radar de Indicadores Docentes (Normalizado)",
            showlegend=False,
            height=400,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    with cols[1]:
        # Gráfico de gauge para fator H
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=kpis.get('for_h', 0),
            title={"text": "Fator H Médio (FOR-H)"},
            delta={'reference': 8.0, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 20]},
                'bar': {'color': "#1E88E5"},
                'steps': [
                    {'range': [0, 5], 'color': "rgba(30, 136, 229, 0.2)"},
                    {'range': [5, 10], 'color': "rgba(30, 136, 229, 0.4)"},
                    {'range': [10, 15], 'color': "rgba(30, 136, 229, 0.6)"},
                    {'range': [15, 20], 'color': "rgba(30, 136, 229, 0.8)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 15
                }
            }
        ))
        fig3.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Cargas horárias e orientações
    st.subheader("⏱️ Carga Horária e Orientações")
    
    cols2 = st.columns(3)
    
    with cols2[0]:
        # Gráfico de barras comparando carga horária
        workload = {
            "Na Pós-Graduação (ATI)": kpis.get('ati', 0),
            "Na Graduação (ATG1)": kpis.get('atg1', 0)
        }
        
        fig4 = px.bar(
            x=list(workload.keys()),
            y=list(workload.values()),
            title="Carga Horária Média Anual",
            labels={"x": "", "y": "Horas"},
            color=list(workload.keys()),
            template="plotly_white",
            color_discrete_sequence=["#1E88E5", "#42A5F5"]
        )
        fig4.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with cols2[1]:
        # Gráfico para ADE1 e ADE2
        colaboradores = {
            "Carga Horária (ADE1)": kpis.get('ade1', 0),
            "Orientações (ADE2)": kpis.get('ade2', 0)
        }
        
        fig5 = px.bar(
            x=list(colaboradores.keys()),
            y=list(colaboradores.values()),
            title="Atuação de Docentes Colaboradores",
            labels={"x": "", "y": "%"},
            color=list(colaboradores.keys()),
            template="plotly_white",
            color_discrete_sequence=["#5C6BC0", "#7986CB"]
        )
        fig5.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    with cols2[2]:
        # Gráfico para ATG2 (Orientações de IC)
        fig6 = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            value=kpis.get('atg2', 0),
            delta={'reference': 2, 'position': "top"},
            title={"text": "Orientações de IC por Docente (ATG2)"},
            gauge={
                'shape': "bullet",
                'axis': {'range': [None, 6]},
                'threshold': {
                    'line': {'color': "green", 'width': 2},
                    'thickness': 0.75,
                    'value': 3
                },
                'steps': [
                    {'range': [0, 2], 'color': "lightgray"},
                    {'range': [2, 4], 'color': "gray"},
                    {'range': [4, 6], 'color': "darkgray"}
                ],
                'bar': {'color': "#1E88E5"}
            }
        ))
        fig6.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig6, use_container_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("📑 Explicação Detalhada dos Indicadores do Corpo Docente"):
        st.markdown("""
        ### Principais Indicadores do Corpo Docente

        **FOR-H (Fator H Ampliado)**: Representa o valor médio do fator H ampliado dos docentes permanentes, medido pelas plataformas SCOPUS/WebOfScience. É calculado com base no valor do último ano coletado, normalizado pelo número de anos desde a obtenção do doutorado.

        **FOR (Bolsas PQ)**: Percentual de docentes permanentes que são detentores de bolsa de Produtividade em Pesquisa do CNPq. Estima a maturidade científica do corpo docente.

        **FORDT (Bolsas DT)**: Percentual de docentes permanentes que são detentores de bolsa de Produtividade em Desenvolvimento Tecnológico e Extensão Inovadora do CNPq. Mede a maturidade do corpo docente na produção, desenvolvimento e inovação tecnológica.

        **DED (Dedicação Exclusiva)**: Mede o percentual de docentes permanentes do programa que possuem dedicação exclusiva ao programa.

        **D3A (Envolvimento em Pesquisa)**: Quantifica a porcentagem de docentes permanentes intensamente envolvidos em atividades de pesquisa.

        **ADE1 (Carga Horária Colaboradores)**: Percentual da carga horária anual de disciplinas oferecidas pelo PPG que é atribuída a docentes colaboradores ou visitantes.

        **ADE2 (Orientações Colaboradores)**: Percentual das teses de doutorado e/ou dissertações de mestrado concluídas que têm orientação atribuída a docentes colaboradores ou visitantes.

        **ATI (Carga Horária na Pós-Graduação)**: Carga horária anual média de disciplinas ministradas na pós-graduação pelos docentes permanentes.

        **ATG1 (Carga Horária na Graduação)**: Carga horária anual média de disciplinas ministradas na graduação pelos docentes permanentes.

        **ATG2 (Orientações de IC)**: Número médio de alunos de iniciação científica da graduação orientados pelos docentes permanentes.

        **DPD (Distribuição da Produção)**: Porcentagem do corpo docente permanente que contribuiu com produção científica qualificada.

        **DTD (Docentes com Patentes)**: Porcentagem do corpo docente permanente que contribuiu com a autoria de patentes depositadas ou concedidas.
        """)
    

def render_student_charts(kpis):
    """
    Renderiza gráficos relacionados à formação discente
    
    Parameters:
    - kpis: Dicionário com valores de todos os KPIs
    """
    st.markdown("<div class='chart-section'>", unsafe_allow_html=True)
    st.subheader("📚 Análise da Formação Discente")
    
    st.markdown("""
    <div class="help-text" style="margin-bottom: 20px;">
    A análise da formação discente avalia a capacidade do programa em formar mestres e doutores com qualidade, 
    considerando aspectos como tempo de titulação, produção científica dos alunos e distribuição das orientações.
    Os indicadores abaixo refletem o desempenho do programa nestes quesitos.
    </div>
    """, unsafe_allow_html=True)
    
    # Visão geral de titulados
    total_titulados = kpis.get('total_mestres', 0) + kpis.get('total_doutores', 0)
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="font-size: 1.8rem; margin-bottom: 0.5rem;">Total de Titulados: {total_titulados}</h3>
            <p style="font-size: 1.1rem; color: #555;">
                Mestres: <span style="color: #26A69A; font-weight: bold;">{kpis.get('total_mestres', 0)}</span> | 
                Doutores: <span style="color: #1E88E5; font-weight: bold;">{kpis.get('total_doutores', 0)}</span>
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    cols1 = st.columns(2)
    
    with cols1[0]:
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
            template="plotly_white",
            color_discrete_sequence=["#26A69A", "#1E88E5"]
        )
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with cols1[1]:
        # Gráfico de gauge para índice ORI
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=kpis.get('ori', 0),
            title={"text": "Índice de Formação (ORI)"},
            delta={'reference': 2.5, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 5]},
                'bar': {'color': "#26A69A"},
                'steps': [
                    {'range': [0, 1], 'color': "rgba(38, 166, 154, 0.2)"},
                    {'range': [1, 2], 'color': "rgba(38, 166, 154, 0.4)"},
                    {'range': [2, 3], 'color': "rgba(38, 166, 154, 0.6)"},
                    {'range': [3, 5], 'color': "rgba(38, 166, 154, 0.8)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 4
                }
            }
        ))
        fig3.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Seção de produção intelectual discente
    st.subheader("📝 Produção Intelectual Discente")
    
    cols2 = st.columns([1, 2])
    
    with cols2[0]:
        # Radar para comparação de indicadores de produção discente
        categories = ['DPI_Dout', 'DPI_Mest', 'PDO']
        values = [
            kpis.get('dpi_discente_dout', 0) / 3,  # Normalizado para 0-1 (assumindo máx 3)
            kpis.get('dpi_discente_mest', 0) / 2,  # Normalizado para 0-1 (assumindo máx 2)
            kpis.get('pdo', 0) / 100              # Já está em percentual (0-100)
        ]
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Indicadores Discentes',
            line_color='#26A69A',
            fillcolor='rgba(38, 166, 154, 0.3)'
        ))
        
        fig4.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Radar de Indicadores Discentes (Normalizado)",
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig4, use_container_width=True)
    
    with cols2[1]:
        # Gráfico de barras para produção discente
        production_data = {
            'Indicador': ['Produção Doutorandos (DPI_disc_Dout)', 'Produção Mestrandos (DPI_disc_Mest)', 'Distribuição das Orientações (PDO)'],
            'Valor': [kpis.get('dpi_discente_dout', 0), kpis.get('dpi_discente_mest', 0), kpis.get('pdo', 0)],
            'Meta': [1.5, 0.8, 70],
            'Unidade': ['Índice', 'Índice', '%']
        }
        
        # Criar DataFrame com metas para comparação
        import pandas as pd
        prod_df = pd.DataFrame(production_data)
        
        # Gráfico de barras com metas
        fig5 = go.Figure()
        
        # Adicionar barras para valores reais
        fig5.add_trace(go.Bar(
            x=prod_df['Indicador'],
            y=prod_df['Valor'],
            name='Valor Atual',
            marker_color=['#1E88E5', '#26A69A', '#FF7043'],
            text=prod_df.apply(lambda row: f"{row['Valor']:.1f} {row['Unidade']}", axis=1),
            textposition='auto'
        ))
        
        # Adicionar linhas para as metas
        for i, row in prod_df.iterrows():
            fig5.add_shape(type="line",
                line=dict(dash="dash", color="red", width=2),
                x0=i-0.4, x1=i+0.4, y0=row['Meta'], y1=row['Meta'],
                xref="x", yref="y"
            )
            
            # Texto para a meta
            fig5.add_annotation(
                x=i,
                y=row['Meta'] * 1.1,
                text=f"Meta: {row['Meta']}{row['Unidade']}",
                showarrow=False,
                font=dict(size=10, color="red")
            )
        
        fig5.update_layout(
            title="Indicadores de Produção Discente vs. Metas",
            xaxis_title="",
            yaxis_title="",
            template="plotly_white",
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("📑 Explicação Detalhada dos Indicadores de Formação Discente"):
        st.markdown("""
        ### Principais Indicadores de Formação Discente

        **ORI (Índice de Formação)**: Avalia a intensidade da formação de recursos humanos de alto nível, por meio do número de orientações de dissertações e de teses de doutorado concluídas. Calculado pela fórmula:
        ORI = (nº de Mestres titulados × 1 + nº de Doutores titulados × 3) / nº de docentes permanentes

        **PDO (Distribuição das Orientações)**: Quantifica a distribuição das orientações de dissertações e de teses de doutorado entre os docentes. É calculado pela porcentagem de docentes permanentes que participam da orientação de dissertações ou teses defendidas.

        **DPI_discente_Dout (Produção Doutorandos)**: Estima o volume e a qualidade da produção intelectual originada pelo corpo discente em programas de Doutorado. É calculado pela soma ponderada da produção em termos dos estratos do Qualis Periódicos que possuem autores discentes ou egressos, dividida pelo número de titulados.

        **DPI_discente_Mest (Produção Mestrandos)**: Similar ao DPI_discente_Dout, mas para programas de Mestrado. Inclui trabalhos completos em eventos relevantes com participação discente.
        """)
    

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