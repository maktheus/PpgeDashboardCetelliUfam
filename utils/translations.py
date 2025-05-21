"""
Utility module for language translations
"""

# Dictionary containing translations for all text in the application
translations = {
    # General UI elements
    "page_title": {
        "pt": "PPGEE KPI Dashboard",
        "en": "PPGEE KPI Dashboard"
    },
    "title": {
        "pt": "📊 PPGEE KPI Dashboard",
        "en": "📊 PPGEE KPI Dashboard"
    },
    "filters": {
        "pt": "Filtros",
        "en": "Filters"
    },
    "navigation": {
        "pt": "Navegação",
        "en": "Navigation"
    },
    "view_selection": {
        "pt": "Escolher Visualização",
        "en": "Choose View"
    },
    "current_filter_info": {
        "pt": "Visualizando dados para: Ano = {}, Programa = {}",
        "en": "Viewing data for: Year = {}, Program = {}"
    },
    "back_button": {
        "pt": "← Voltar para KPI Dashboard",
        "en": "← Back to KPI Dashboard"
    },
    "copyright": {
        "pt": "© 2023-2025 PPGE Dashboard",
        "en": "© 2023-2025 PPGE Dashboard"
    },
    "last_update": {
        "pt": "Atualizado em: {}",
        "en": "Last updated: {}"
    },
    "version": {
        "pt": "Versão 1.1.0",
        "en": "Version 1.1.0"
    },
    "year_filter": {
        "pt": "Ano Acadêmico",
        "en": "Academic Year"
    },
    "program_filter": {
        "pt": "Programa",
        "en": "Program"
    },
    "language_selector": {
        "pt": "Idioma",
        "en": "Language"
    },
    
    # Tab Names
    "overview_tab": {
        "pt": "📊 Visão Geral",
        "en": "📊 Overview"
    },
    "capes_indicators_tab": {
        "pt": "🎯 Indicadores CAPES",
        "en": "🎯 CAPES Indicators"
    },
    "detailed_analysis_tab": {
        "pt": "📈 Análises Detalhadas",
        "en": "📈 Detailed Analysis"
    },
    
    # Sidebar navigation
    "overview_nav": {
        "pt": "📊 Visão Geral",
        "en": "📊 Overview"
    },
    "student_metrics_nav": {
        "pt": "👨‍🎓 Métricas dos Estudantes",
        "en": "👨‍🎓 Student Metrics"
    },
    "faculty_metrics_nav": {
        "pt": "👨‍🏫 Métricas dos Docentes",
        "en": "👨‍🏫 Faculty Metrics"
    },
    "program_performance_nav": {
        "pt": "🏫 Desempenho do Programa",
        "en": "🏫 Program Performance"
    },
    "report_generator_nav": {
        "pt": "📝 Gerador de Relatórios",
        "en": "📝 Report Generator"
    },
    "data_management_nav": {
        "pt": "⚙️ Gerenciamento de Dados",
        "en": "⚙️ Data Management"
    },
    
    # KPI Dashboard Section
    "main_kpi_title": {
        "pt": "Principais Indicadores de Desempenho (KPIs)",
        "en": "Key Performance Indicators (KPIs)"
    },
    "kpi_click_instruction": {
        "pt": "Clique em um KPI para visualizar gráficos e análises detalhadas",
        "en": "Click on a KPI to view detailed charts and analysis"
    },
    "time_metrics": {
        "pt": "Métricas de Tempo",
        "en": "Time Metrics"
    },
    "efficiency_metrics": {
        "pt": "Métricas de Eficiência",
        "en": "Efficiency Metrics"
    },
    "view_details": {
        "pt": "Ver Detalhes",
        "en": "View Details"
    },
    
    # KPI Cards
    "total_students": {
        "pt": "Total de Alunos",
        "en": "Total Students"
    },
    "total_faculty": {
        "pt": "Total de Docentes",
        "en": "Total Faculty"
    },
    "avg_defense_time": {
        "pt": "Tempo Médio até Defesa",
        "en": "Average Time to Defense"
    },
    "defense_success_rate": {
        "pt": "Taxa de Sucesso na Defesa",
        "en": "Defense Success Rate"
    },
    "median_defense_time": {
        "pt": "Mediana do Tempo até Defesa",
        "en": "Median Time to Defense"
    },
    "masters_avg_time": {
        "pt": "Mestrado (Tempo Médio)",
        "en": "Masters (Average Time)"
    },
    "doctorate_avg_time": {
        "pt": "Doutorado (Tempo Médio)",
        "en": "Doctorate (Average Time)"
    },
    "time_variation": {
        "pt": "Variação do Tempo (Desvio)",
        "en": "Time Variation (Std Dev)"
    },
    "time_efficiency": {
        "pt": "Eficiência de Tempo",
        "en": "Time Efficiency"
    },
    "min_time": {
        "pt": "Tempo Mínimo",
        "en": "Minimum Time"
    },
    "max_time": {
        "pt": "Tempo Máximo",
        "en": "Maximum Time"
    },
    "completion_rate": {
        "pt": "Taxa de Conclusão",
        "en": "Completion Rate"
    },
    
    # Card tooltips
    "students_help": {
        "pt": "Número total de alunos no programa",
        "en": "Total number of students in the program"
    },
    "faculty_help": {
        "pt": "Número total de docentes orientando alunos",
        "en": "Total number of faculty advising students"
    },
    "defense_time_help": {
        "pt": "Tempo médio desde o ingresso até a defesa",
        "en": "Average time from enrollment to defense"
    },
    "success_rate_help": {
        "pt": "Porcentagem de defesas com aprovação",
        "en": "Percentage of defenses with approval"
    },
    "median_time_help": {
        "pt": "Mediana do tempo desde o ingresso até a defesa (valor central)",
        "en": "Median time from enrollment to defense (central value)"
    },
    "masters_time_help": {
        "pt": "Tempo médio até a defesa para alunos de Mestrado",
        "en": "Average time to defense for Masters students"
    },
    "doctorate_time_help": {
        "pt": "Tempo médio até a defesa para alunos de Doutorado",
        "en": "Average time to defense for Doctorate students"
    },
    "time_variation_help": {
        "pt": "Desvio padrão do tempo até a defesa (medida de variabilidade)",
        "en": "Standard deviation of time to defense (measure of variability)"
    },
    "efficiency_help": {
        "pt": "Proporção do tempo esperado vs. tempo real (maior = mais eficiente)",
        "en": "Ratio of expected time vs. actual time (higher = more efficient)"
    },
    "min_time_help": {
        "pt": "Menor tempo registrado para conclusão",
        "en": "Lowest recorded time for completion"
    },
    "max_time_help": {
        "pt": "Maior tempo registrado para conclusão",
        "en": "Highest recorded time for completion"
    },
    "completion_help": {
        "pt": "Porcentagem de alunos que concluíram a defesa",
        "en": "Percentage of students who completed their defense"
    },
    
    # Common units and suffixes
    "months": {
        "pt": "meses",
        "en": "months"
    },
    "percent": {
        "pt": "%",
        "en": "%"
    },
    
    # Translations for program names
    "masters": {
        "pt": "Mestrado",
        "en": "Masters"
    },
    "doctorate": {
        "pt": "Doutorado",
        "en": "Doctorate"
    },
    "all": {
        "pt": "Todos",
        "en": "All"
    },
    "All": {
        "pt": "Todos",
        "en": "All"
    },
    "Todos": {
        "pt": "Todos",
        "en": "All"
    },
    
    # Languages
    "pt_language": {
        "pt": "Português",
        "en": "Portuguese"
    },
    "en_language": {
        "pt": "Inglês",
        "en": "English"
    }
}

def get_translation(key, lang="pt"):
    """
    Get a translated text for a specific key in the specified language
    
    Parameters:
    - key: The translation key
    - lang: The language code ('pt' or 'en')
    
    Returns:
    - The translated text or the key itself if translation is not found
    """
    if key in translations:
        if lang in translations[key]:
            return translations[key][lang]
    
    # Return the key itself if translation not found
    return key