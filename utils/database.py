import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import streamlit as st

# Get database connection parameters from environment variables
DB_HOST = os.environ.get('PGHOST')
DB_PORT = os.environ.get('PGPORT')
DB_NAME = os.environ.get('PGDATABASE')
DB_USER = os.environ.get('PGUSER')
DB_PASSWORD = os.environ.get('PGPASSWORD')
DB_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """
    Get a connection to the PostgreSQL database
    
    Returns:
    - Connection object
    """
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def init_database():
    """
    Initialize database tables if they don't exist
    """
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create table for tracking uploaded files
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                table_type TEXT NOT NULL,
                upload_timestamp TIMESTAMP NOT NULL DEFAULT NOW()
            )
            """)
            
            # Create tables for all identified data types from the Excel file
            
            # Infos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS infos (
                id SERIAL PRIMARY KEY,
                info_text TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # EGRESSO-MESTRADO
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egresso_mestrado (
                id SERIAL PRIMARY KEY,
                ata TEXT,
                aluno TEXT,
                ano_ingresso TEXT,
                defesa TEXT,
                orientador TEXT,
                titulo_defesa TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # EGRESSOS-M-INFOS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egressos_m_infos (
                id SERIAL PRIMARY KEY,
                orientando TEXT,
                orientador TEXT,
                defesa TEXT,
                cursando_doutorado TEXT,
                trabalhando TEXT,
                trabalhando_outro_estado TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # EGRESSO-DOUTORADO
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egresso_doutorado (
                id SERIAL PRIMARY KEY,
                ata TEXT,
                aluno TEXT,
                ano_ingresso TEXT,
                defesa TEXT,
                orientador TEXT,
                titulo_defesa TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # EGRESSOS-D-INFOS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egressos_d_infos (
                id SERIAL PRIMARY KEY,
                orientando TEXT,
                orientador TEXT,
                defesa TEXT,
                cursando_doutorado TEXT,
                trabalhando TEXT,
                trabalhando_outro_estado TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # OFERTA-DEMANDA
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS oferta_demanda (
                id SERIAL PRIMARY KEY,
                descricao TEXT,
                ano_2021 INTEGER,
                ano_2022 INTEGER,
                ano_2023 INTEGER,
                ano_2024 INTEGER,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # PROJETOS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS projetos (
                id SERIAL PRIMARY KEY,
                numero INTEGER,
                titulo TEXT,
                natureza TEXT,
                coordenador TEXT,
                financiador TEXT,
                projetos_nao_academicos TEXT,
                resumo TEXT,
                valor_financiado TEXT,
                atuacao TEXT,
                alunos_envolvidos TEXT,
                ano_inicio TEXT,
                ano_fim TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # DOCENTES-PERMANENTES
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS docentes_permanentes (
                id SERIAL PRIMARY KEY,
                docente TEXT,
                categoria TEXT,
                ano INTEGER,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # PERIODICOS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS periodicos (
                id SERIAL PRIMARY KEY,
                numero INTEGER,
                titulo TEXT,
                periodico TEXT,
                autor TEXT,
                ano INTEGER,
                tem_discente_egresso TEXT,
                tem_docente_ppgee TEXT,
                titulo_tese_dissertacao TEXT,
                cont INTEGER,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # CONFERENCIAS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conferencias (
                id SERIAL PRIMARY KEY,
                numero INTEGER,
                titulo TEXT,
                autor TEXT,
                ano INTEGER,
                titulo_tese_dissertacao TEXT,
                cont INTEGER,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # TCC-IC
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tcc_ic (
                id SERIAL PRIMARY KEY,
                docente TEXT,
                tcc_1 TEXT,
                tcc_2 TEXT,
                tcc_3 TEXT,
                tcc_4 TEXT,
                coluna5 TEXT,
                ic_1 TEXT,
                ic_2 TEXT,
                ic_3 TEXT,
                ic_4 TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # DOCENTES-DISC-N-CH
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS docentes_disc_n_ch (
                id SERIAL PRIMARY KEY,
                docente TEXT,
                dppg_1 TEXT,
                dppg_2 TEXT,
                dppg_3 TEXT,
                dppg_4 TEXT,
                coluna5 TEXT,
                dg_ch_1 TEXT,
                dg_ch_2 TEXT,
                dg_ch_3 TEXT,
                dg_ch_4 TEXT,
                disc_grad_5 TEXT,
                dg_n_1 TEXT,
                dg_n_2 TEXT,
                dg_n_3 TEXT,
                dg_n_4 TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # REVISOR-EDITOR
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS revisor_editor (
                id SERIAL PRIMARY KEY,
                nome_docente TEXT,
                nome_evento TEXT,
                ano INTEGER,
                nacional_internacional TEXT,
                funcao_desempenhada TEXT,
                sucupira TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Eventos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id SERIAL PRIMARY KEY,
                proposta TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # TURMAS-OFERTADAS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas_ofertadas (
                id SERIAL PRIMARY KEY,
                unidade TEXT,
                ano INTEGER,
                periodo TEXT,
                cod_disciplina TEXT,
                disciplina TEXT,
                sigla_disciplina TEXT,
                cod_turma TEXT,
                cod_curso TEXT,
                curso TEXT,
                situacao TEXT,
                docente TEXT,
                vagas_oferecidas INTEGER,
                vagas_aumentadas INTEGER,
                qtd_matriculado INTEGER,
                qtd_aprovados INTEGER,
                qtd_reprovado_nota INTEGER,
                qtd_reprovado_freq INTEGER,
                qtd_trancados INTEGER,
                horario TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # DISCP-TOTAL-ATIVAS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS discp_total_ativas (
                id SERIAL PRIMARY KEY,
                disciplina TEXT,
                curso TEXT,
                cr TEXT,
                curso2 TEXT,
                data_ini TEXT,
                data_fim TEXT,
                ativo TEXT,
                unnamed_7 TEXT,
                unnamed_8 TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Melhores-Teses
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS melhores_teses (
                id SERIAL PRIMARY KEY,
                aluno TEXT,
                titulo TEXT,
                defesa TEXT,
                orientador TEXT,
                justificativa TEXT,
                nota_originalidade NUMERIC,
                nota_relevancia NUMERIC,
                potencial_inovacao NUMERIC,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Melhores-Dissertacoes
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS melhores_dissertacoes (
                id SERIAL PRIMARY KEY,
                aluno TEXT,
                titulo TEXT,
                defesa TEXT,
                orientador TEXT,
                justificativa TEXT,
                nota_originalidade NUMERIC,
                nota_relevancia NUMERIC,
                potencial_inovacao NUMERIC,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
            connection.close()
            return False
    
    return False

def save_df_to_database(df, table_name, file_id):
    """
    Save a DataFrame to the specified database table
    
    Parameters:
    - df: DataFrame to save
    - table_name: Name of the table to save to
    - file_id: ID of the uploaded file record
    
    Returns:
    - Boolean indicating if save was successful
    """
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Add upload_id to DataFrame
            df['upload_id'] = file_id
            
            # Removing rows that are completely NaN
            df = df.dropna(how='all')
            
            # Handle empty DataFrame
            if df.empty:
                st.warning(f"Nenhum dado válido encontrado para importar na tabela {table_name}")
                connection.close()
                return False
            
            # Get column names from DataFrame
            columns = df.columns.tolist()
            
            # Check if table exists
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                st.error(f"Tabela {table_name} não existe no banco de dados")
                connection.close()
                return False
            
            # Get columns of the table
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            table_columns = [row[0] for row in cursor.fetchall()]
            
            # Filter DataFrame to include only columns that exist in the table
            valid_columns = [col for col in columns if col.lower() in [c.lower() for c in table_columns]]
            
            if not valid_columns:
                st.error(f"Nenhuma coluna válida encontrada para importar na tabela {table_name}")
                connection.close()
                return False
            
            # Filter DataFrame to include only valid columns
            df_filtered = df[valid_columns].copy()
            
            # Create insert statement
            insert_stmt = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, valid_columns))
            )
            
            # Convert DataFrame to list of tuples
            values = [tuple(row) for row in df_filtered.values]
            
            # Execute insert
            execute_values(cursor, insert_stmt, values)
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            st.error(f"Database save error: {str(e)}")
            connection.close()
            return False
    
    return False

def get_table_type_mapping():
    """
    Get mapping of table types to database table names
    
    Returns:
    - Dictionary with table type to table name mapping
    """
    return {
        "Infos": "infos",
        "EGRESSO-MESTRADO": "egresso_mestrado",
        "EGRESSOS-M-INFOS": "egressos_m_infos",
        "EGRESSO-DOUTORADO": "egresso_doutorado",
        "EGRESSOS-D-INFOS": "egressos_d_infos",
        "OFERTA-DEMANDA": "oferta_demanda",
        "PROJETOS": "projetos",
        "DOCENTES-PERMANENTES": "docentes_permanentes",
        "PERIODICOS": "periodicos",
        "CONFERENCIAS": "conferencias",
        "TCC-IC": "tcc_ic",
        "DOCENTES-DISC-N-CH": "docentes_disc_n_ch",
        "REVISOR-EDITOR": "revisor_editor",
        "Eventos": "eventos",
        "TURMAS-OFERTADAS": "turmas_ofertadas",
        "DISCP-TOTAL-ATIVAS": "discp_total_ativas",
        "Melhores-Teses": "melhores_teses",
        "Melhores-Dissertacoes": "melhores_dissertacoes"
    }

def register_uploaded_file(filename, file_type, table_type):
    """
    Register an uploaded file in the database
    
    Parameters:
    - filename: Name of the uploaded file
    - file_type: Type of file (csv, excel, etc.)
    - table_type: Type of table the data belongs to
    
    Returns:
    - ID of the created record or None if failed
    """
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            cursor.execute("""
            INSERT INTO uploaded_files (filename, file_type, table_type)
            VALUES (%s, %s, %s) RETURNING id
            """, (filename, file_type, table_type))
            
            result = cursor.fetchone()
            file_id = result[0] if result else None
            
            connection.commit()
            cursor.close()
            connection.close()
            return file_id
        except Exception as e:
            st.error(f"File registration error: {str(e)}")
            connection.close()
            return None
    
    return None

def get_uploaded_files():
    """
    Get list of all uploaded files
    
    Returns:
    - DataFrame with uploaded files information
    """
    connection = get_connection()
    if connection:
        try:
            query = """
            SELECT id, filename, file_type, table_type, upload_timestamp
            FROM uploaded_files
            ORDER BY upload_timestamp DESC
            """
            
            df = pd.read_sql_query(query, connection)
            connection.close()
            return df
        except Exception as e:
            st.error(f"Error retrieving uploaded files: {str(e)}")
            connection.close()
            return pd.DataFrame()
    
    return pd.DataFrame()

def get_data_by_table_type(table_type):
    """
    Get data from database by table type
    
    Parameters:
    - table_type: Type of table to get data from
    
    Returns:
    - DataFrame with data from the specified table type
    """
    table_mapping = get_table_type_mapping()
    
    if table_type not in table_mapping:
        st.error(f"Unknown table type: {table_type}")
        return pd.DataFrame()
    
    table_name = table_mapping[table_type]
    
    connection = get_connection()
    if connection:
        try:
            query = sql.SQL("""
            SELECT * FROM {}
            ORDER BY id DESC
            """).format(sql.Identifier(table_name))
            
            df = pd.read_sql_query(query, connection)
            connection.close()
            return df
        except Exception as e:
            st.error(f"Error retrieving data: {str(e)}")
            connection.close()
            return pd.DataFrame()
    
    return pd.DataFrame()