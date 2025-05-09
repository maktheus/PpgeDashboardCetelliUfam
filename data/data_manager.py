import pandas as pd
import streamlit as st
import os
import numpy as np
from data.sample_data import generate_sample_data

class DataManager:
    """Class for managing data in the PPGE KPI Dashboard"""
    
    @staticmethod
    def get_data():
        """
        Get the current data for the dashboard
        
        Returns:
        - DataFrame with the current data
        """
        # Check if data is in session state
        if 'data' not in st.session_state:
            # Se existir os arquivos de planilha, tenta importá-los
            sucupira_file = 'attached_assets/00-MAIN-DATA-SUCUPIRA-dash.xlsx'
            professores_file = 'attached_assets/professores.xlsx'
            
            if os.path.exists(sucupira_file) and os.path.exists(professores_file):
                st.session_state['data'] = DataManager.import_from_sucupira_data(
                    sucupira_file, professores_file
                )
            else:
                # Initialize with sample data
                st.session_state['data'] = generate_sample_data()
        
        # Apply filters based on sidebar selections
        return DataManager.apply_global_filters(st.session_state['data'])
    
    @staticmethod
    def import_from_sucupira_data(sucupira_file, professores_file):
        """
        Importa os dados das planilhas da SUCUPIRA
        
        Parameters:
        - sucupira_file: Caminho para o arquivo de dados da SUCUPIRA
        - professores_file: Caminho para o arquivo de professores
        
        Returns:
        - DataFrame com os dados processados
        """
        try:
            # Importar dados de mestrado
            df_mestrado = pd.read_excel(sucupira_file, sheet_name='EGRESSO-MESTRADO')
            df_mestrado['PROGRAMA'] = 'Mestrado'
            
            # Importar dados de doutorado
            df_doutorado = pd.read_excel(sucupira_file, sheet_name='EGRESSO-DOUTORADO')
            df_doutorado['PROGRAMA'] = 'Doutorado'
            
            # Juntar os dois DataFrames
            df_combined = pd.concat([df_mestrado, df_doutorado], ignore_index=True)
            
            # Renomear colunas para o formato esperado pelo dashboard
            df_combined = df_combined.rename(columns={
                'ALUNOS': 'student_name',
                'ANO DE INGRESSO': 'enrollment_date',
                'DEFESA': 'defense_date',
                'ORIENTADOR': 'advisor_name',
                'PROGRAMA': 'program'
            })
            
            # Criar IDs para estudantes
            df_combined['student_id'] = range(1, len(df_combined) + 1)
            
            # Importar dados de professores
            df_professores = pd.read_excel(professores_file, sheet_name='PROFESSORES')
            
            # Verificar se o formato está correto
            if len(df_professores.columns) == 1:
                professores_list = df_professores.iloc[:, 0].tolist()
                
                # Criar um DataFrame de professores no formato necessário
                professores_data = []
                for i, nome in enumerate(professores_list):
                    if pd.notna(nome) and nome.strip():
                        professores_data.append({
                            'advisor_id': i + 1,
                            'advisor_name': nome.strip()
                        })
                
                df_professores_clean = pd.DataFrame(professores_data)
                
                # Mapear advisor_id para o dataset principal
                advisor_id_map = {row['advisor_name']: row['advisor_id'] 
                                  for _, row in df_professores_clean.iterrows()}
                
                # Adicionar advisor_id baseado no advisor_name
                df_combined['advisor_id'] = df_combined['advisor_name'].map(
                    lambda x: advisor_id_map.get(x, None)
                )
            
            # Adicionar status de defesa
            df_combined['defense_status'] = df_combined['defense_date'].apply(
                lambda x: 'Approved' if pd.notna(x) else 'Pending'
            )
            
            # Adicionar departamento (usando um valor padrão)
            df_combined['department'] = 'PPGE'
            
            # Adicionar área de pesquisa (vazio por enquanto)
            df_combined['research_area'] = 'Educação'
            
            # Adicionar número de publicações (aleatório por enquanto)
            df_combined['publications'] = np.random.randint(0, 5, size=len(df_combined))
            
            # Converter datas para o formato correto
            for col in ['enrollment_date', 'defense_date']:
                if col in df_combined.columns:
                    # Tratar valores problemáticos antes da conversão
                    df_combined[col] = df_combined[col].apply(
                        lambda x: pd.NaT if isinstance(x, str) and 'Q' in x else x
                    )
                    # Converter para datetime com tratamento de erros
                    df_combined[col] = pd.to_datetime(df_combined[col], errors='coerce')
            
            return df_combined
            
        except Exception as e:
            st.error(f"Erro ao importar dados SUCUPIRA: {str(e)}")
            # Em caso de erro, usar dados de amostra
            return generate_sample_data()
    
    @staticmethod
    def apply_global_filters(df):
        """
        Apply global filters from sidebar to the data
        
        Parameters:
        - df: DataFrame to filter
        
        Returns:
        - Filtered DataFrame
        """
        filtered_df = df.copy()
        
        # Apply year filter if not "All"
        if 'selected_year' in st.session_state and st.session_state.selected_year != "All":
            year = int(st.session_state.selected_year)
            
            # Filter enrollment_date by year
            if 'enrollment_date' in filtered_df.columns:
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['enrollment_date']).dt.year == year)
                ]
        
        # Apply program filter if not "All"
        if 'selected_program' in st.session_state and st.session_state.selected_program != "All":
            program = st.session_state.selected_program
            
            # Filter program column
            if 'program' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['program'] == program]
        
        return filtered_df
    
    @staticmethod
    def update_data(new_data):
        """
        Update the data in session state
        
        Parameters:
        - new_data: New DataFrame to store
        
        Returns:
        - Boolean indicating if update was successful
        """
        try:
            st.session_state['data'] = new_data
            return True
        except Exception as e:
            st.error(f"Failed to update data: {str(e)}")
            return False
    
    @staticmethod
    def import_data(df, file_name=None):
        """
        Import data from uploaded file and store with timestamp
        
        Parameters:
        - df: DataFrame from imported file
        - file_name: Name of the imported file (optional)
        
        Returns:
        - Boolean indicating if import was successful
        """
        try:
            # Initialize 'data_history' if it doesn't exist
            if 'data_history' not in st.session_state:
                st.session_state['data_history'] = []
            
            # Create a timestamp for this import
            import_timestamp = pd.Timestamp.now()
            
            # Store the current data in history
            data_entry = {
                'timestamp': import_timestamp,
                'data': df.copy(),
                'file_name': file_name or f"Data Import {import_timestamp.strftime('%Y-%m-%d %H:%M')}"
            }
            
            # Add to history
            st.session_state['data_history'].append(data_entry)
            
            # Limit history size to prevent memory issues (keep last 10 imports)
            if len(st.session_state['data_history']) > 10:
                st.session_state['data_history'] = st.session_state['data_history'][-10:]
            
            # Set the most recent import as the current dataset
            st.session_state['data'] = df
            st.session_state['current_data_timestamp'] = import_timestamp
            
            return True
        except Exception as e:
            st.error(f"Failed to import data: {str(e)}")
            return False
    
    @staticmethod
    def get_student_metrics():
        """
        Get student-specific metrics
        
        Returns:
        - DataFrame with student metrics
        """
        df = DataManager.get_data()
        
        # Ensure we have student data
        if 'student_id' not in df.columns:
            return pd.DataFrame()
        
        # Process student metrics
        if 'enrollment_date' in df.columns and 'defense_date' in df.columns:
            # Calculate time to defense for each student
            # Converter as datas com tratamento de erros
            enrollment_dates = pd.to_datetime(df['enrollment_date'], errors='coerce')
            defense_dates = pd.to_datetime(df['defense_date'], errors='coerce')
            
            # Calcular tempo até a defesa (apenas para casos onde ambas as datas são válidas)
            time_to_defense = (defense_dates - enrollment_dates).dt.days / 30.44  # Média de dias por mês
            df['time_to_defense'] = time_to_defense
        
        return df
    
    @staticmethod
    def get_faculty_metrics():
        """
        Get faculty-specific metrics
        
        Returns:
        - DataFrame with faculty metrics
        """
        df = DataManager.get_data()
        
        # Ensure we have faculty data
        if 'advisor_id' not in df.columns:
            return pd.DataFrame()
        
        # Group by advisor to get metrics per faculty
        if 'advisor_name' in df.columns:
            faculty_metrics = df.groupby(['advisor_id', 'advisor_name']).agg({
                'student_id': 'count',
                'defense_status': lambda x: (x == 'Approved').mean() if 'defense_status' in df.columns else 0
            }).reset_index()
            
            faculty_metrics.rename(columns={
                'student_id': 'total_students',
                'defense_status': 'success_rate'
            }, inplace=True)
            
            # Calculate additional metrics if data is available
            if 'time_to_defense' in df.columns:
                advisor_avg_time = df.groupby(['advisor_id', 'advisor_name'])['time_to_defense'].mean().reset_index()
                faculty_metrics = faculty_metrics.merge(advisor_avg_time, on=['advisor_id', 'advisor_name'])
            
            return faculty_metrics
        
        return pd.DataFrame()
    
    @staticmethod
    def get_program_metrics():
        """
        Get program-level metrics
        
        Returns:
        - DataFrame with program metrics
        """
        df = DataManager.get_data()
        
        # Ensure we have program data
        if 'program' not in df.columns:
            return pd.DataFrame()
        
        # Group by program to get metrics
        program_metrics = df.groupby('program').agg({
            'student_id': 'count',
            'defense_status': lambda x: (x == 'Approved').mean() if 'defense_status' in df.columns else 0
        }).reset_index()
        
        program_metrics.rename(columns={
            'student_id': 'total_students',
            'defense_status': 'success_rate'
        }, inplace=True)
        
        # Calculate additional metrics if data is available
        if 'time_to_defense' in df.columns:
            program_avg_time = df.groupby('program')['time_to_defense'].mean().reset_index()
            program_metrics = program_metrics.merge(program_avg_time, on='program')
        
        return program_metrics
    
    @staticmethod
    def get_time_series_data():
        """
        Get time series data for trend analysis
        
        Returns:
        - DataFrame with time series data
        """
        df = DataManager.get_data()
        
        # Ensure we have date data
        if 'enrollment_date' not in df.columns:
            return pd.DataFrame()
        
        # Convert enrollment_date to datetime if needed
        if df['enrollment_date'].dtype != 'datetime64[ns]':
            df['enrollment_date'] = pd.to_datetime(df['enrollment_date'], errors='coerce')
        
        # Group by year and month
        df['year_month'] = df['enrollment_date'].dt.to_period('M')
        
        time_series = df.groupby(['year_month']).size().reset_index(name='enrollments')
        time_series['year_month'] = time_series['year_month'].dt.to_timestamp()
        
        # If defense date is available, add defenses over time
        if 'defense_date' in df.columns:
            if df['defense_date'].dtype != 'datetime64[ns]':
                df['defense_date'] = pd.to_datetime(df['defense_date'], errors='coerce')
            
            df['defense_year_month'] = df['defense_date'].dt.to_period('M')
            defenses = df.groupby(['defense_year_month']).size().reset_index(name='defenses')
            defenses['defense_year_month'] = defenses['defense_year_month'].dt.to_timestamp()
            
            # Rename to merge
            defenses.rename(columns={'defense_year_month': 'year_month'}, inplace=True)
            
            # Merge enrollments and defenses
            time_series = time_series.merge(defenses, on='year_month', how='outer').fillna(0)
        
        return time_series.sort_values('year_month')
        
    @staticmethod
    def get_data_history():
        """
        Get the history of imported data
        
        Returns:
        - List of dictionaries with historical data entries
        """
        if 'data_history' not in st.session_state:
            st.session_state['data_history'] = []
            
        return st.session_state['data_history']
    
    @staticmethod
    def get_data_by_timestamp(timestamp):
        """
        Get data from a specific historical import by timestamp
        
        Parameters:
        - timestamp: The timestamp of the import to retrieve
        
        Returns:
        - DataFrame or None if not found
        """
        if 'data_history' not in st.session_state:
            return None
            
        for entry in st.session_state['data_history']:
            if entry['timestamp'] == timestamp:
                return entry['data']
                
        return None
    
    @staticmethod
    def compare_datasets(timestamp1, timestamp2, metrics=None):
        """
        Compare two datasets from the history
        
        Parameters:
        - timestamp1: Timestamp of the first dataset
        - timestamp2: Timestamp of the second dataset
        - metrics: List of metrics to compare (optional)
        
        Returns:
        - Dictionary with comparison results
        """
        df1 = DataManager.get_data_by_timestamp(timestamp1)
        df2 = DataManager.get_data_by_timestamp(timestamp2)
        
        if df1 is None or df2 is None:
            return None
            
        # Default metrics to compare if none provided
        if metrics is None:
            metrics = ['total_records', 'avg_time_to_defense', 'success_rate']
            
        results = {
            'dataset1_name': next((e['file_name'] for e in st.session_state['data_history'] 
                                if e['timestamp'] == timestamp1), "Dataset 1"),
            'dataset2_name': next((e['file_name'] for e in st.session_state['data_history'] 
                                if e['timestamp'] == timestamp2), "Dataset 2"),
            'metrics': {}
        }
        
        # Total records comparison
        if 'total_records' in metrics:
            results['metrics']['total_records'] = {
                'dataset1': len(df1),
                'dataset2': len(df2),
                'difference': len(df2) - len(df1),
                'percent_change': (len(df2) - len(df1)) / len(df1) * 100 if len(df1) > 0 else float('inf')
            }
            
        # Time to defense comparison
        if 'avg_time_to_defense' in metrics and 'enrollment_date' in df1.columns and 'defense_date' in df1.columns:
            # Calculate for dataset 1
            df1_copy = df1.copy()
            # Tratar valores problemáticos antes da conversão
            df1_copy['defense_date'] = df1_copy['defense_date'].apply(
                lambda x: pd.NaT if isinstance(x, str) and 'Q' in x else x
            )
            df1_copy['enrollment_date'] = df1_copy['enrollment_date'].apply(
                lambda x: pd.NaT if isinstance(x, str) and 'Q' in x else x
            )
            # Converter para datetime com tratamento de erros
            defense_dates1 = pd.to_datetime(df1_copy['defense_date'], errors='coerce')
            enrollment_dates1 = pd.to_datetime(df1_copy['enrollment_date'], errors='coerce')
            df1_copy['time_to_defense'] = (defense_dates1 - enrollment_dates1).dt.days / 30.44
            avg1 = df1_copy['time_to_defense'].mean()
            
            # Calculate for dataset 2
            df2_copy = df2.copy()
            # Tratar valores problemáticos antes da conversão
            df2_copy['defense_date'] = df2_copy['defense_date'].apply(
                lambda x: pd.NaT if isinstance(x, str) and 'Q' in x else x
            )
            df2_copy['enrollment_date'] = df2_copy['enrollment_date'].apply(
                lambda x: pd.NaT if isinstance(x, str) and 'Q' in x else x
            )
            # Converter para datetime com tratamento de erros
            defense_dates2 = pd.to_datetime(df2_copy['defense_date'], errors='coerce')
            enrollment_dates2 = pd.to_datetime(df2_copy['enrollment_date'], errors='coerce')
            df2_copy['time_to_defense'] = (defense_dates2 - enrollment_dates2).dt.days / 30.44
            avg2 = df2_copy['time_to_defense'].mean()
            
            results['metrics']['avg_time_to_defense'] = {
                'dataset1': avg1,
                'dataset2': avg2,
                'difference': avg2 - avg1,
                'percent_change': (avg2 - avg1) / avg1 * 100 if avg1 > 0 else float('inf')
            }
            
        # Success rate comparison
        if 'success_rate' in metrics and 'defense_status' in df1.columns:
            # Calculate for dataset 1
            success_rate1 = (df1['defense_status'] == 'Approved').mean() if 'defense_status' in df1.columns else 0
            
            # Calculate for dataset 2
            success_rate2 = (df2['defense_status'] == 'Approved').mean() if 'defense_status' in df2.columns else 0
            
            results['metrics']['success_rate'] = {
                'dataset1': success_rate1,
                'dataset2': success_rate2,
                'difference': success_rate2 - success_rate1,
                'percent_change': (success_rate2 - success_rate1) / success_rate1 * 100 if success_rate1 > 0 else float('inf')
            }
            
        # Program distribution comparison
        if 'program_distribution' in metrics and 'program' in df1.columns:
            # Calculate for dataset 1
            prog_dist1 = df1.groupby('program').size().reset_index(name='count')
            prog_dist1['percentage'] = prog_dist1['count'] / prog_dist1['count'].sum() * 100
            
            # Calculate for dataset 2
            prog_dist2 = df2.groupby('program').size().reset_index(name='count')
            prog_dist2['percentage'] = prog_dist2['count'] / prog_dist2['count'].sum() * 100
            
            results['metrics']['program_distribution'] = {
                'dataset1': prog_dist1.to_dict('records'),
                'dataset2': prog_dist2.to_dict('records')
            }
            
        return results
