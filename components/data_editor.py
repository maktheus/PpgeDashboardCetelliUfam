import streamlit as st
import pandas as pd
from utils.database import get_connection, get_table_type_mapping, save_df_to_database
import psycopg2
from psycopg2 import sql

def render_data_editor(table_type=None):
    """
    Render a data editor for a specific table type
    
    Parameters:
    - table_type: Type of table to edit (optional, if None, allow selection)
    """
    # Get table mapping
    table_mapping = get_table_type_mapping()
    
    # If table_type is not provided, let the user select
    if table_type is None:
        table_types = list(table_mapping.keys())
        table_type = st.selectbox(
            "Selecione a tabela para editar",
            options=table_types
        )
    
    if table_type:
        # Get the database table name
        table_name = table_mapping[table_type]
        
        # Load data for the selected table
        df = load_table_data(table_name)
        
        if df is not None and not df.empty:
            st.subheader(f"Editor de Dados: {table_type}")
            
            # Create an editable dataframe
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                key=f"data_editor_{table_name}"
            )
            
            # Only show save button if changes were made
            if not df.equals(edited_df):
                if st.button("Salvar Alterações", key=f"save_btn_{table_name}"):
                    success = save_edited_data(edited_df, table_name, df)
                    if success:
                        st.success("Alterações salvas com sucesso!")
                    else:
                        st.error("Erro ao salvar alterações. Tente novamente.")
        else:
            st.info(f"Não há dados disponíveis para a tabela {table_type}.")
            
            # Offer to create new data
            st.write("Deseja adicionar novos dados?")
            
            # Create a template dataframe with the correct columns
            template_df = create_template_dataframe(table_name)
            
            if template_df is not None:
                # Create an editable dataframe with the template
                new_data = st.data_editor(
                    template_df,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"new_data_editor_{table_name}"
                )
                
                # Save new data button
                if st.button("Adicionar Novos Dados", key=f"add_btn_{table_name}"):
                    # Filter out empty rows
                    new_data = new_data.dropna(how='all')
                    
                    if not new_data.empty:
                        # Add upload_id as null (will be updated during save)
                        if 'upload_id' not in new_data.columns:
                            new_data['upload_id'] = None
                        
                        success = save_new_data(new_data, table_name)
                        if success:
                            st.success("Novos dados adicionados com sucesso!")
                            st.rerun()  # Refresh to show the new data
                        else:
                            st.error("Erro ao adicionar novos dados. Tente novamente.")
                    else:
                        st.warning("Não há dados válidos para adicionar.")

def load_table_data(table_name, limit=1000):
    """
    Load data from a specific table
    
    Parameters:
    - table_name: Name of the table to load data from
    - limit: Maximum number of rows to load
    
    Returns:
    - DataFrame with the table data or None if error
    """
    connection = get_connection()
    if connection:
        try:
            # Load data with columns in the correct order
            query = sql.SQL("""
            SELECT * FROM {}
            ORDER BY id DESC
            LIMIT {}
            """).format(sql.Identifier(table_name), sql.Literal(limit))
            
            df = pd.read_sql_query(query, connection)
            connection.close()
            return df
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            if connection:
                connection.close()
    
    return None

def save_edited_data(edited_df, table_name, original_df):
    """
    Save edited data back to the database
    
    Parameters:
    - edited_df: DataFrame with the edited data
    - table_name: Name of the table to save to
    - original_df: Original DataFrame for comparison
    
    Returns:
    - Boolean indicating if save was successful
    """
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Identify new rows (rows without an ID)
            new_rows = edited_df[edited_df['id'].isna()].copy()
            
            # Identify updated rows (rows with an ID that have changed)
            updated_rows = edited_df[~edited_df['id'].isna()].copy()
            if not original_df.empty:
                # Convert IDs to same type for comparison
                updated_rows['id'] = updated_rows['id'].astype(int)
                original_df['id'] = original_df['id'].astype(int)
                
                # Get list of IDs to compare
                ids_to_compare = updated_rows['id'].tolist()
                
                # Filter original_df to only include rows with these IDs
                original_filtered = original_df[original_df['id'].isin(ids_to_compare)].copy()
                
                # Set index for easy comparison
                updated_rows.set_index('id', inplace=True)
                original_filtered.set_index('id', inplace=True)
                
                # Find rows that changed by comparing with original data
                changed_rows = []
                for idx in updated_rows.index:
                    if idx in original_filtered.index:
                        # Compare row with original
                        original_row = original_filtered.loc[idx]
                        updated_row = updated_rows.loc[idx]
                        
                        # Check if any values changed
                        if not all(original_row == updated_row):
                            changed_rows.append(updated_row)
                
                if changed_rows:
                    # Convert list of series to DataFrame
                    changed_df = pd.DataFrame(changed_rows)
                    # Reset index to get ID back as a column
                    changed_df = changed_df.reset_index()
                    updated_rows = changed_df.copy()
                else:
                    # No changes found
                    updated_rows = pd.DataFrame()
            
            # Handle new rows (INSERT)
            if not new_rows.empty:
                # Remove the empty ID column and any other unnecessary columns
                if 'id' in new_rows.columns:
                    new_rows = new_rows.drop(columns=['id'])
                
                # Set a default upload_id if needed
                if 'upload_id' in new_rows.columns:
                    new_rows.loc[new_rows['upload_id'].isna(), 'upload_id'] = 0
                
                # Filter out empty rows
                new_rows = new_rows.dropna(how='all')
                
                if not new_rows.empty:
                    # Get column names
                    columns = new_rows.columns.tolist()
                    
                    # Create insert statement
                    insert_stmt = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                        sql.Identifier(table_name),
                        sql.SQL(', ').join(map(sql.Identifier, columns))
                    )
                    
                    # Convert to list of tuples
                    values = [tuple(row) for row in new_rows.values]
                    
                    # Execute insert
                    from psycopg2.extras import execute_values
                    execute_values(cursor, insert_stmt, values)
            
            # Handle updated rows (UPDATE)
            if not updated_rows.empty:
                # Update each row individually
                for idx, row in updated_rows.iterrows():
                    # Convert to python int to avoid numpy int which causes issues
                    row_id = int(row['id']) if not pd.isna(row['id']) else None
                    
                    if row_id is None:
                        continue  # Skip if no valid ID
                        
                    # Create a dictionary of values to update, excluding id
                    update_values = {}
                    for col in row.index:
                        if col != 'id' and not pd.isna(row[col]):
                            # Convert numpy/pandas types to Python native types
                            val = row[col]
                            if isinstance(val, (pd.Timestamp, pd.Timedelta)):
                                val = val.to_pydatetime()
                            elif hasattr(val, 'item'):  # For numpy scalar types
                                val = val.item()
                            update_values[col] = val
                    
                    if update_values:
                        # Create update statement
                        set_clause = sql.SQL(", ").join([
                            sql.SQL("{} = {}").format(
                                sql.Identifier(col),
                                sql.Literal(val)
                            ) for col, val in update_values.items()
                        ])
                        
                        update_stmt = sql.SQL("UPDATE {} SET {} WHERE id = {}").format(
                            sql.Identifier(table_name),
                            set_clause,
                            sql.Literal(row_id)
                        )
                        
                        # Execute update
                        cursor.execute(update_stmt)
            
            # Commit changes
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar alterações: {str(e)}")
            if connection:
                connection.close()
    
    return False

def create_template_dataframe(table_name):
    """
    Create a template DataFrame with the correct columns for a table
    
    Parameters:
    - table_name: Name of the table
    
    Returns:
    - Empty DataFrame with the correct columns or None if error
    """
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Get the table columns and types
            cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            
            # Create a dictionary to store column types
            column_types = {}
            column_names = []
            
            for col, dtype in columns:
                # Skip the ID column for new data
                if col.lower() == 'id':
                    continue
                
                column_names.append(col)
                
                # Map SQL types to Python types
                if dtype in ('integer', 'bigint', 'smallint'):
                    column_types[col] = 'int64'
                elif dtype in ('numeric', 'decimal', 'real', 'double precision'):
                    column_types[col] = 'float64'
                elif dtype.startswith('timestamp') or dtype == 'date':
                    column_types[col] = 'datetime64[ns]'
                else:
                    column_types[col] = 'object'
            
            # Create an empty DataFrame with the correct columns and one empty row
            template_data = {col: [None] for col in column_names}
            template_df = pd.DataFrame(template_data)
            
            # Set the column types
            for col, dtype in column_types.items():
                try:
                    template_df[col] = template_df[col].astype(dtype)
                except:
                    # If type conversion fails for empty values, keep as is
                    pass
            
            cursor.close()
            connection.close()
            
            return template_df
        except Exception as e:
            st.error(f"Erro ao criar template: {str(e)}")
            if connection:
                connection.close()
    
    return None

def save_new_data(new_data, table_name):
    """
    Save new data to the database
    
    Parameters:
    - new_data: DataFrame with the new data
    - table_name: Name of the table to save to
    
    Returns:
    - Boolean indicating if save was successful
    """
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Register a new file upload
            cursor.execute("""
            INSERT INTO uploaded_files (filename, file_type, table_type)
            VALUES ('Adicionado manualmente', 'manual', 'Manual')
            RETURNING id
            """)
            
            upload_id = cursor.fetchone()[0]
            
            # Set the upload_id
            new_data['upload_id'] = upload_id
            
            # Filter out any empty rows
            new_data = new_data.dropna(how='all')
            
            if not new_data.empty:
                # Get column names
                columns = new_data.columns.tolist()
                
                # Create insert statement
                insert_stmt = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                )
                
                # Convert to list of tuples
                values = [tuple(row) for row in new_data.values]
                
                # Execute insert
                from psycopg2.extras import execute_values
                execute_values(cursor, insert_stmt, values)
                
                connection.commit()
                cursor.close()
                connection.close()
                return True
            else:
                st.warning("Não há dados válidos para adicionar.")
                connection.close()
                return False
                
        except Exception as e:
            st.error(f"Erro ao salvar novos dados: {str(e)}")
            if connection:
                connection.close()
    
    return False