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
            
            # Create tables for different data types
            
            # Table for EGRESSOS-M-INFOS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egressos_m_infos (
                id SERIAL PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                degree_type TEXT,
                continuation_level TEXT,
                employment_status TEXT,
                geographic_region TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Table for EGRESSOS-D-INFOS
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egressos_d_infos (
                id SERIAL PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                degree_type TEXT,
                continuation_level TEXT,
                employment_status TEXT,
                geographic_region TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Table for EGRESSOS-MESTRADO
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egressos_mestrado (
                id SERIAL PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                enrollment_date DATE,
                defense_date DATE,
                advisor_name TEXT,
                program TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Table for EGRESSOS-DOUTORADO
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS egressos_doutorado (
                id SERIAL PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                enrollment_date DATE,
                defense_date DATE,
                advisor_name TEXT,
                program TEXT,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Table for Melhores-Teses
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS melhores_teses (
                id SERIAL PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                title TEXT,
                defense_date DATE,
                advisor_name TEXT,
                justification TEXT,
                originality_score NUMERIC,
                relevance_score NUMERIC,
                innovation_potential NUMERIC,
                upload_id INTEGER REFERENCES uploaded_files(id)
            )
            """)
            
            # Table for Melhores-Dissertacoes
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS melhores_dissertacoes (
                id SERIAL PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                title TEXT,
                defense_date DATE,
                advisor_name TEXT,
                justification TEXT,
                originality_score NUMERIC,
                relevance_score NUMERIC,
                innovation_potential NUMERIC,
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
            
            # Get column names from DataFrame
            columns = df.columns.tolist()
            
            # Create insert statement
            insert_stmt = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns))
            )
            
            # Convert DataFrame to list of tuples
            values = [tuple(row) for row in df.values]
            
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
        "EGRESSOS-M-INFOS": "egressos_m_infos",
        "EGRESSOS-D-INFOS": "egressos_d_infos",
        "EGRESSOS-MESTRADO": "egressos_mestrado",
        "EGRESSOS-DOUTORADO": "egressos_doutorado",
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