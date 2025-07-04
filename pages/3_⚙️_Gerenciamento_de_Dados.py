import streamlit as st
import pandas as pd
import datetime
from utils.database import init_database, get_uploaded_files, get_data_by_table_type, get_table_type_mapping
from components.data_import import render_file_uploader, process_uploaded_file, render_data_mapping_tool, save_imported_data
from components.batch_import import render_batch_import
from components.data_editor import render_data_editor
from utils.auth import require_authentication

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
    
    tabs = st.tabs(["Importação em Lote", "Importação Individual", "Editar Dados", "Visualizar Dados", "Histórico de Uploads"])
    
    with tabs[0]:
        render_batch_import_section()
    
    with tabs[1]:
        render_individual_import_section()
    
    with tabs[2]:
        render_edit_data_section()
    
    with tabs[3]:
        render_view_export_section()
    
    with tabs[4]:
        render_upload_history_section()

def render_batch_import_section():
    """Render the Batch Import section for multiple tables from Excel"""
    
    st.header("Importação em Lote")
    
    # Info card about batch import
    st.info(
        "Importe múltiplas tabelas de um arquivo Excel de uma só vez. "
        "Cada planilha será mapeada para a tabela correspondente no banco de dados."
    )
    
    # Render batch import component
    render_batch_import()

def render_individual_import_section():
    """Render the Individual Import Data section"""
    
    st.header("Importação Individual")
    
    # Info card about data import
    st.info(
        "Importe dados individuais de arquivos Excel, CSV ou JSON. "
        "Você poderá mapear as colunas do arquivo para o formato necessário do banco de dados."
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

def render_edit_data_section():
    """Render the Edit Data section"""
    
    st.header("Editar Dados")
    
    # Info card about data editing
    st.info(
        "Aqui você pode editar dados existentes ou adicionar novos registros nas tabelas. "
        "As alterações serão salvas diretamente no banco de dados."
    )
    
    # Get table types
    table_types = list(get_table_type_mapping().keys())
    
    # Table type selection
    selected_table = st.selectbox(
        "Selecionar tabela para editar:",
        table_types,
        key="edit_table_select"
    )
    
    if selected_table:
        # Render data editor for the selected table
        render_data_editor(selected_table)
        
        st.markdown("---")
        st.markdown("""
        ### Instruções de Edição
        
        1. **Editar células**: Clique diretamente na célula para editar seu conteúdo.
        2. **Adicionar linhas**: Clique no botão '+' no final da tabela para adicionar novas linhas.
        3. **Salvar alterações**: Clique no botão 'Salvar Alterações' após fazer modificações.
        
        **Observações importantes**:
        - Algumas colunas podem ter restrições de tipo (números, datas, etc.).
        - O campo 'id' não pode ser editado por ser a chave primária.
        - Após salvar, a tabela será atualizada automaticamente.
        """)

def render_view_export_section():
    """Render the View & Export Data section"""
    
    st.header("Visualizar e Exportar Dados")
    
    # Get table types
    table_types = list(get_table_type_mapping().keys())
    
    # Table type selection
    selected_table = st.selectbox(
        "Selecionar tipo de tabela para visualizar:",
        table_types,
        key="view_table_select"
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

@require_authentication
def protected_render_page():
    """Render the protected data management page with OTP authentication"""
    render_page()

if __name__ == "__main__":
    protected_render_page()