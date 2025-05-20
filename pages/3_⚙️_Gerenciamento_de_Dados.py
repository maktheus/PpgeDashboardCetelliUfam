import streamlit as st
import pandas as pd
import datetime
from utils.database import init_database, get_uploaded_files, get_data_by_table_type, get_table_type_mapping
from components.data_import import render_file_uploader, process_uploaded_file, render_data_mapping_tool, save_imported_data

st.set_page_config(
    page_title="Gerenciamento de Dados - PPGE KPI Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# Initialize database tables if they don't exist
init_database()

def render_page():
    """Render the Data Management page"""
    st.title("Gerenciamento de Dados")
    
    tabs = st.tabs(["Importar Dados", "Visualizar Dados", "Histórico de Uploads"])
    
    with tabs[0]:
        render_import_section()
    
    with tabs[1]:
        render_view_export_section()
    
    with tabs[2]:
        render_upload_history_section()

def render_import_section():
    """Render the Import Data section"""
    
    st.header("Importação de Dados")
    
    # Info card about data import
    st.info(
        "Importe dados de arquivos Excel, CSV ou JSON. O sistema ajudará a mapear "
        "os campos para o formato necessário para o Dashboard PPGE."
    )
    
    # File uploader with table type selection
    uploaded_file, file_type, table_type = render_file_uploader()
    
    if uploaded_file is not None:
        # Store selected table type in session state for use in the mapping tool
        if table_type:
            st.session_state['selected_table_type'] = table_type
        
        # Process uploaded file
        imported_df, error_message = process_uploaded_file(uploaded_file, file_type)
        
        if error_message:
            st.error(error_message)
            return
        
        if imported_df is not None:
            st.success(f"Arquivo processado com sucesso! Encontrados {len(imported_df)} registros.")
            
            # Show data preview
            st.subheader("Pré-visualização dos Dados")
            st.dataframe(imported_df.head(5), use_container_width=True)
            
            # Data mapping
            mapped_df, mapping_applied = render_data_mapping_tool(imported_df)
            
            if mapping_applied:
                # Save button
                if st.button("Salvar Dados Importados"):
                    # Get filename for reference
                    file_name = uploaded_file.name if uploaded_file else "Dados Importados"
                    
                    # Save the data to PostgreSQL
                    success = save_imported_data(
                        mapped_df, 
                        file_name, 
                        file_type, 
                        table_type
                    )
                    
                    if success:
                        st.success("Dados importados e salvos com sucesso no banco de dados PostgreSQL!")
                    else:
                        st.error("Falha ao salvar os dados importados no banco de dados.")

def render_view_export_section():
    """Render the View & Export Data section"""
    
    st.header("Visualizar e Exportar Dados")
    
    # Get table types
    table_types = list(get_table_type_mapping().keys())
    
    # Table type selection
    selected_table = st.selectbox(
        "Selecionar tipo de tabela para visualizar:",
        table_types
    )
    
    if selected_table:
        # Load data for selected table type
        df = get_data_by_table_type(selected_table)
        
        if df.empty:
            st.info(f"Nenhum dado encontrado para a tabela {selected_table}.")
        else:
            st.success(f"Dados carregados com sucesso! Encontrados {len(df)} registros.")
            
            # Show data
            st.subheader(f"Dados da tabela: {selected_table}")
            st.dataframe(df, use_container_width=True)
            
            # Export options
            st.subheader("Exportar Dados")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Exportar para CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Baixar CSV",
                        data=csv,
                        file_name=f"{selected_table}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("Exportar para Excel"):
                    # Convert to Excel
                    output = pd.ExcelWriter(f"{selected_table}.xlsx", engine="openpyxl")
                    df.to_excel(output, index=False, sheet_name=selected_table)
                    output.close()
                    
                    with open(f"{selected_table}.xlsx", "rb") as f:
                        excel_data = f.read()
                    
                    st.download_button(
                        label="Baixar Excel",
                        data=excel_data,
                        file_name=f"{selected_table}_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

def render_upload_history_section():
    """Render the Upload History section"""
    
    st.header("Histórico de Uploads")
    
    # Get upload history
    uploads_df = get_uploaded_files()
    
    if uploads_df.empty:
        st.info("Nenhum upload registrado no histórico.")
    else:
        st.success(f"Encontrados {len(uploads_df)} uploads no histórico.")
        
        # Format timestamp for display
        if 'upload_timestamp' in uploads_df.columns:
            uploads_df['upload_timestamp'] = pd.to_datetime(uploads_df['upload_timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        # Display upload history
        st.dataframe(uploads_df, use_container_width=True)

def protected_render_page():
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        render_page()
    else:
        st.warning("Você precisa estar autenticado para acessar esta página.")
        
        # Add login form
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                # Simple authentication (in production, use a more secure approach)
                if username == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

if __name__ == "__main__":
    protected_render_page()