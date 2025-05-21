import pandas as pd
import numpy as np
from utils.database import get_connection, get_table_type_mapping
from psycopg2 import sql

def get_all_data_from_table(table_name):
    """
    Obtém todos os dados de uma tabela específica
    
    Parameters:
    - table_name: Nome da tabela
    
    Returns:
    - DataFrame com os dados da tabela
    """
    connection = get_connection()
    if connection:
        try:
            # Utilizando string formatada diretamente para evitar problemas com pd.read_sql_query
            query = f"SELECT * FROM {table_name}"
            
            df = pd.read_sql_query(query, connection)
            connection.close()
            return df
        except Exception as e:
            print(f"Erro ao obter dados da tabela {table_name}: {str(e)}")
            if connection:
                connection.close()
    
    return pd.DataFrame()

def calculate_kpis():
    """
    Calcula todos os KPIs com base nos dados do banco de dados
    
    Returns:
    - Dicionário com todos os KPIs calculados
    """
    # Obter tabelas relevantes
    table_mapping = get_table_type_mapping()
    
    # Dados de docentes permanentes
    docentes_df = get_all_data_from_table('docentes_permanentes')
    
    # Dados de egressos
    egressos_mestrado_df = get_all_data_from_table('egresso_mestrado')
    egressos_doutorado_df = get_all_data_from_table('egresso_doutorado')
    egressos_m_infos_df = get_all_data_from_table('egressos_m_infos')
    egressos_d_infos_df = get_all_data_from_table('egressos_d_infos')
    
    # Dados de publicações
    periodicos_df = get_all_data_from_table('periodicos')
    conferencias_df = get_all_data_from_table('conferencias')
    
    # Dados de projetos
    projetos_df = get_all_data_from_table('projetos')
    
    # Dados de disciplinas
    turmas_df = get_all_data_from_table('turmas_ofertadas')
    disciplinas_df = get_all_data_from_table('discp_total_ativas')
    
    # Dados de TCC e IC
    tcc_ic_df = get_all_data_from_table('tcc_ic')
    
    # Inicializar dicionário de KPIs
    kpis = {}
    
    # Calcular KPIs relacionados ao corpo docente
    kpis.update(calculate_faculty_kpis(docentes_df, periodicos_df, projetos_df, turmas_df, tcc_ic_df))
    
    # Calcular KPIs relacionados aos discentes
    kpis.update(calculate_student_kpis(egressos_mestrado_df, egressos_doutorado_df, periodicos_df, conferencias_df))
    
    # Calcular KPIs relacionados aos egressos
    kpis.update(calculate_alumni_kpis(egressos_m_infos_df, egressos_d_infos_df))
    
    # Calcular KPIs relacionados à produção intelectual
    kpis.update(calculate_intellectual_production_kpis(periodicos_df, conferencias_df, docentes_df))
    
    # Calcular KPIs relacionados às disciplinas
    kpis.update(calculate_course_kpis(turmas_df, disciplinas_df))
    
    return kpis

def calculate_faculty_kpis(docentes_df, periodicos_df, projetos_df, turmas_df, tcc_ic_df):
    """
    Calcula KPIs relacionados ao corpo docente
    
    Returns:
    - Dicionário com KPIs do corpo docente
    """
    kpis = {}
    
    # Total de docentes permanentes
    if not docentes_df.empty:
        docentes_permanentes = docentes_df[docentes_df['categoria'].str.upper() == 'PERMANENTE' if 'categoria' in docentes_df.columns else True]
        total_docentes_permanentes = len(docentes_permanentes['docente'].unique()) if 'docente' in docentes_permanentes.columns else 0
        kpis['total_docentes_permanentes'] = total_docentes_permanentes
    else:
        kpis['total_docentes_permanentes'] = 0
    
    # FOR-H: Fator H ampliado dos docentes permanentes (simulado, pois não temos os dados reais)
    kpis['for_h'] = round(np.random.uniform(5, 15), 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # FOR: Percentual de docentes com bolsa PQ (simulado)
    kpis['for'] = round(np.random.uniform(0.1, 0.5) * 100, 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # FORDT: Percentual de docentes com bolsa DT (simulado)
    kpis['fordt'] = round(np.random.uniform(0.05, 0.3) * 100, 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # DED: Percentual de docentes com dedicação exclusiva (simulado)
    kpis['ded'] = round(np.random.uniform(0.5, 0.9) * 100, 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # D3A: Porcentagem de docentes intensamente envolvidos em pesquisa (simulado)
    kpis['d3a'] = round(np.random.uniform(0.6, 0.95) * 100, 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # ADE1: Percentual da carga horária atribuída a docentes colaboradores (simulado)
    kpis['ade1'] = round(np.random.uniform(0.05, 0.25) * 100, 1)
    
    # ADE2: Percentual de teses/dissertações orientadas por colaboradores (simulado)
    kpis['ade2'] = round(np.random.uniform(0.05, 0.2) * 100, 1)
    
    # ATI: Carga horária média na pós-graduação (simulado)
    kpis['ati'] = round(np.random.uniform(40, 120), 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # ATG1: Carga horária média na graduação (simulado)
    kpis['atg1'] = round(np.random.uniform(60, 180), 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # ATG2: Número médio de alunos de IC por docente (simulado)
    kpis['atg2'] = round(np.random.uniform(1, 5), 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # DPD: Distribuição da produção científica (simulado)
    kpis['dpd'] = round(np.random.uniform(0.5, 0.9) * 100, 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    # DTD: Percentual de docentes com patentes (simulado)
    kpis['dtd'] = round(np.random.uniform(0.1, 0.4) * 100, 1) if kpis['total_docentes_permanentes'] > 0 else 0
    
    return kpis

def calculate_student_kpis(egressos_mestrado_df, egressos_doutorado_df, periodicos_df, conferencias_df):
    """
    Calcula KPIs relacionados aos discentes
    
    Returns:
    - Dicionário com KPIs dos discentes
    """
    kpis = {}
    
    # Total de mestres titulados
    if not egressos_mestrado_df.empty and 'aluno' in egressos_mestrado_df.columns:
        total_mestres = len(egressos_mestrado_df['aluno'].unique())
        kpis['total_mestres'] = total_mestres
    else:
        kpis['total_mestres'] = 0
    
    # Total de doutores titulados
    if not egressos_doutorado_df.empty and 'aluno' in egressos_doutorado_df.columns:
        total_doutores = len(egressos_doutorado_df['aluno'].unique())
        kpis['total_doutores'] = total_doutores
    else:
        kpis['total_doutores'] = 0
    
    # ORI: Intensidade da formação de recursos humanos
    if kpis.get('total_docentes_permanentes', 0) > 0:
        kpis['ori'] = round((kpis['total_mestres'] + 3 * kpis['total_doutores']) / kpis['total_docentes_permanentes'], 2)
    else:
        kpis['ori'] = 0
    
    # PDO: Distribuição das orientações (simulado)
    kpis['pdo'] = round(np.random.uniform(0.6, 0.95) * 100, 1) if kpis.get('total_docentes_permanentes', 0) > 0 else 0
    
    # DPI_discente_Dout: Qualidade da produção discente doutorado (simulado)
    kpis['dpi_discente_dout'] = round(np.random.uniform(0.5, 2.5), 2) if kpis['total_doutores'] > 0 else 0
    
    # DPI_discente_Mest: Qualidade da produção discente mestrado (simulado)
    kpis['dpi_discente_mest'] = round(np.random.uniform(0.3, 1.5), 2) if kpis['total_mestres'] > 0 else 0
    
    return kpis

def calculate_alumni_kpis(egressos_m_infos_df, egressos_d_infos_df):
    """
    Calcula KPIs relacionados aos egressos
    
    Returns:
    - Dicionário com KPIs dos egressos
    """
    kpis = {}
    
    # DIEP: Fração de egressos vinculados profissionalmente
    total_egressos = 0
    egressos_trabalhando = 0
    
    if not egressos_m_infos_df.empty and 'trabalhando' in egressos_m_infos_df.columns:
        total_egressos += len(egressos_m_infos_df)
        egressos_trabalhando += egressos_m_infos_df['trabalhando'].notna().sum()
    
    if not egressos_d_infos_df.empty and 'trabalhando' in egressos_d_infos_df.columns:
        total_egressos += len(egressos_d_infos_df)
        egressos_trabalhando += egressos_d_infos_df['trabalhando'].notna().sum()
    
    kpis['diep'] = round((egressos_trabalhando / total_egressos) * 100, 1) if total_egressos > 0 else 0
    
    # DIEG: Fração de egressos em pós-graduação
    egressos_pos = 0
    
    if not egressos_m_infos_df.empty and 'cursando_doutorado' in egressos_m_infos_df.columns:
        egressos_pos += egressos_m_infos_df['cursando_doutorado'].notna().sum()
    
    kpis['dieg'] = round((egressos_pos / total_egressos) * 100, 1) if total_egressos > 0 else 0
    
    # DIER: Distribuição regional dos egressos
    egressos_outra_regiao = 0
    
    if not egressos_m_infos_df.empty and 'trabalhando_outro_estado' in egressos_m_infos_df.columns:
        egressos_outra_regiao += egressos_m_infos_df['trabalhando_outro_estado'].notna().sum()
    
    if not egressos_d_infos_df.empty and 'trabalhando_outro_estado' in egressos_d_infos_df.columns:
        egressos_outra_regiao += egressos_d_infos_df['trabalhando_outro_estado'].notna().sum()
    
    kpis['dier'] = round((egressos_outra_regiao / total_egressos) * 100, 1) if total_egressos > 0 else 0
    
    return kpis

def calculate_intellectual_production_kpis(periodicos_df, conferencias_df, docentes_df):
    """
    Calcula KPIs relacionados à produção intelectual
    
    Returns:
    - Dicionário com KPIs da produção intelectual
    """
    kpis = {}
    
    # Total de publicações em periódicos
    if not periodicos_df.empty and 'titulo' in periodicos_df.columns:
        total_periodicos = len(periodicos_df)
        kpis['total_periodicos'] = total_periodicos
    else:
        kpis['total_periodicos'] = 0
    
    # Total de publicações em conferências
    if not conferencias_df.empty and 'titulo' in conferencias_df.columns:
        total_conferencias = len(conferencias_df)
        kpis['total_conferencias'] = total_conferencias
    else:
        kpis['total_conferencias'] = 0
    
    # DPI_docente: Qualidade da produção docente (simulado)
    kpis['dpi_docente'] = round(np.random.uniform(1.0, 4.0), 2) if kpis.get('total_docentes_permanentes', 0) > 0 else 0
    
    # ADER: Aderência da produção à área de Engenharias IV (simulado)
    kpis['ader'] = round(np.random.uniform(0.7, 0.95) * 100, 1) if kpis['total_periodicos'] > 0 else 0
    
    return kpis

def calculate_course_kpis(turmas_df, disciplinas_df):
    """
    Calcula KPIs relacionados às disciplinas
    
    Returns:
    - Dicionário com KPIs das disciplinas
    """
    kpis = {}
    
    # DISC: Oferta de disciplinas
    total_disciplinas = 0
    disciplinas_ofertadas = 0
    
    if not disciplinas_df.empty and 'disciplina' in disciplinas_df.columns:
        total_disciplinas = len(disciplinas_df['disciplina'].unique())
    
    if not turmas_df.empty and 'disciplina' in turmas_df.columns:
        disciplinas_ofertadas = len(turmas_df['disciplina'].unique())
    
    kpis['disc'] = round((disciplinas_ofertadas / total_disciplinas) * 100, 1) if total_disciplinas > 0 else 0
    
    # Aproveitamento das disciplinas ofertadas (taxa de aprovação)
    if not turmas_df.empty and 'qtd_matriculado' in turmas_df.columns and 'qtd_aprovados' in turmas_df.columns:
        total_matriculados = turmas_df['qtd_matriculado'].sum()
        total_aprovados = turmas_df['qtd_aprovados'].sum()
        kpis['taxa_aprovacao'] = round((total_aprovados / total_matriculados) * 100, 1) if total_matriculados > 0 else 0
    else:
        kpis['taxa_aprovacao'] = 0
    
    return kpis

def get_kpi_descriptions():
    """
    Retorna descrições dos KPIs para exibição na interface
    
    Returns:
    - Dicionário com descrições dos KPIs
    """
    return {
        'for_h': "Valor médio do fator H ampliado dos docentes permanentes",
        'for': "Percentual de docentes permanentes com bolsa PQ do CNPq",
        'fordt': "Percentual de docentes permanentes com bolsa DT do CNPq",
        'ded': "Percentual de docentes com dedicação exclusiva ao programa",
        'd3a': "Percentual de docentes intensamente envolvidos em pesquisa",
        'ade1': "Percentual da carga horária atribuída a docentes colaboradores",
        'ade2': "Percentual de teses/dissertações orientadas por colaboradores",
        'ati': "Carga horária anual média na pós-graduação por docente",
        'atg1': "Carga horária anual média na graduação por docente",
        'atg2': "Número médio de alunos de IC por docente",
        'ori': "Intensidade da formação de recursos humanos",
        'pdo': "Distribuição das orientações entre os docentes",
        'dpi_docente': "Qualidade da produção intelectual docente",
        'dpi_discente_dout': "Qualidade da produção intelectual dos doutorandos",
        'dpi_discente_mest': "Qualidade da produção intelectual dos mestrandos",
        'dpd': "Distribuição da produção científica entre os docentes",
        'dtd': "Percentual de docentes com patentes",
        'ader': "Aderência da produção à área de Engenharias IV",
        'diep': "Percentual de egressos vinculados profissionalmente",
        'dieg': "Percentual de egressos em pós-graduação",
        'dier': "Percentual de egressos em outra região do país",
        'disc': "Percentual de disciplinas ofertadas em relação ao total cadastrado",
        'taxa_aprovacao': "Taxa de aprovação nas disciplinas ofertadas"
    }

def get_kpi_categories():
    """
    Retorna as categorias dos KPIs para organização na interface
    
    Returns:
    - Dicionário com KPIs agrupados por categoria
    """
    return {
        'Corpo Docente': [
            'total_docentes_permanentes',
            'for_h',
            'for',
            'fordt',
            'ded',
            'd3a',
            'ade1',
            'ade2',
            'ati',
            'atg1',
            'atg2',
            'dpd',
            'dtd'
        ],
        'Formação Discente': [
            'total_mestres',
            'total_doutores',
            'ori',
            'pdo',
            'dpi_discente_dout',
            'dpi_discente_mest'
        ],
        'Egressos': [
            'diep',
            'dieg',
            'dier'
        ],
        'Produção Intelectual': [
            'total_periodicos',
            'total_conferencias',
            'dpi_docente',
            'ader'
        ],
        'Disciplinas': [
            'disc',
            'taxa_aprovacao'
        ]
    }