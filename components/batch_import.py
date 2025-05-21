import streamlit as st
import pandas as pd
import datetime
from utils.database import get_connection, get_table_type_mapping, register_uploaded_file, save_df_to_database

def render_batch_import():
    """
    Render a batch import tool for Excel files with multiple sheets
    """
    st.subheader("Importação em Lote de Planilhas Excel")
    
    st.info(
        "Esta ferramenta permite importar várias planilhas de um arquivo Excel de uma só vez. "
        "O sistema tentará mapear automaticamente cada planilha para sua tabela correspondente no banco de dados."
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Selecione um arquivo Excel com múltiplas planilhas",
        type=["xlsx", "xls"]
    )
    
    if uploaded_file is not None:
        try:
            # Read all sheets from Excel file
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            
            st.success(f"Arquivo Excel carregado com sucesso! Encontradas {len(sheet_names)} planilhas.")
            
            # Get table mapping
            table_mapping = get_table_type_mapping()
            
            # Create multiselect for selecting which sheets to import
            selected_sheets = st.multiselect(
                "Selecione as planilhas que deseja importar",
                options=sheet_names,
                default=sheet_names
            )
            
            if selected_sheets:
                # Show preview of selected sheets
                for sheet_name in selected_sheets:
                    with st.expander(f"Pré-visualização: {sheet_name}"):
                        try:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, nrows=5)
                            st.dataframe(df, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erro ao ler planilha {sheet_name}: {str(e)}")
                
                # Import button
                if st.button("Importar Planilhas Selecionadas"):
                    import_results = []
                    
                    for sheet_name in selected_sheets:
                        try:
                            # Read sheet data
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                            
                            # Normalize sheet name to match table types
                            normalized_sheet_name = sheet_name
                            
                            # Find matching table type
                            matching_table_type = None
                            for table_type in table_mapping.keys():
                                if table_type.lower() == normalized_sheet_name.lower():
                                    matching_table_type = table_type
                                    break
                            
                            if matching_table_type is None:
                                import_results.append({
                                    "sheet": sheet_name,
                                    "status": "Falha",
                                    "message": "Tipo de tabela não encontrado"
                                })
                                continue
                            
                            # Register file upload
                            file_id = register_uploaded_file(
                                f"{uploaded_file.name} - {sheet_name}",
                                "excel",
                                matching_table_type
                            )
                            
                            if file_id is None:
                                import_results.append({
                                    "sheet": sheet_name,
                                    "status": "Falha",
                                    "message": "Falha ao registrar upload"
                                })
                                continue
                            
                            # Get table name for this type
                            table_name = table_mapping[matching_table_type]
                            
                            # Save data to database
                            success = save_df_to_database(df, table_name, file_id)
                            
                            if success:
                                import_results.append({
                                    "sheet": sheet_name,
                                    "status": "Sucesso",
                                    "message": f"Importado para {table_name}"
                                })
                            else:
                                import_results.append({
                                    "sheet": sheet_name,
                                    "status": "Falha",
                                    "message": "Falha ao salvar no banco de dados"
                                })
                        
                        except Exception as e:
                            import_results.append({
                                "sheet": sheet_name,
                                "status": "Erro",
                                "message": str(e)
                            })
                    
                    # Display import results
                    st.subheader("Resultados da Importação")
                    
                    # Create result dataframe
                    results_df = pd.DataFrame(import_results)
                    
                    # Style the dataframe
                    def highlight_success(val):
                        if val == 'Sucesso':
                            return 'background-color: #CCFFCC'
                        elif val == 'Falha' or val == 'Erro':
                            return 'background-color: #FFCCCC'
                        return ''
                    
                    styled_results = results_df.style.applymap(highlight_success, subset=['status'])
                    
                    # Show results
                    st.dataframe(styled_results, use_container_width=True)
                    
                    # Summary
                    success_count = results_df[results_df['status'] == 'Sucesso'].shape[0]
                    total_count = len(import_results)
                    
                    if success_count == total_count:
                        st.success(f"Todas as {total_count} planilhas foram importadas com sucesso!")
                    elif success_count > 0:
                        st.warning(f"{success_count} de {total_count} planilhas foram importadas com sucesso.")
                    else:
                        st.error(f"Falha ao importar todas as {total_count} planilhas.")
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {str(e)}")
    
    # Help information
    with st.expander("Ajuda: Como usar a importação em lote"):
        st.markdown("""
        ## Como usar a importação em lote
        
        1. Carregue um arquivo Excel que contenha múltiplas planilhas
        2. Selecione quais planilhas deseja importar
        3. Verifique a pré-visualização de cada planilha
        4. Clique em "Importar Planilhas Selecionadas"
        
        ### Importante
        
        - O nome de cada planilha no Excel deve corresponder a um dos tipos de tabela do sistema
        - Os nomes das colunas devem corresponder aos campos esperados pelo banco de dados
        - Caso contrário, você pode usar a importação individual com mapeamento de colunas
        """)

def batch_import_excel_file(excel_file):
    """
    Batch import all sheets from an Excel file
    
    Parameters:
    - excel_file: Uploaded Excel file object
    
    Returns:
    - results: List of dictionaries with import results
    """
    results = []
    
    try:
        # Read all sheets
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        
        # Get table mapping
        table_mapping = get_table_type_mapping()
        table_mapping_lower = {k.lower(): v for k, v in table_mapping.items()}
        
        # Process each sheet
        for sheet_name in sheet_names:
            try:
                # Read sheet data
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Find matching table type (case insensitive)
                matching_table_type = None
                normalized_sheet_name = sheet_name.lower()
                
                if normalized_sheet_name in table_mapping_lower:
                    # Direct match
                    table_name = table_mapping_lower[normalized_sheet_name]
                    matching_table_type = [k for k, v in table_mapping.items() if k.lower() == normalized_sheet_name][0]
                else:
                    # Try to find partial match
                    for table_type in table_mapping.keys():
                        if normalized_sheet_name in table_type.lower() or table_type.lower() in normalized_sheet_name:
                            matching_table_type = table_type
                            break
                
                if matching_table_type is None:
                    results.append({
                        "sheet": sheet_name,
                        "status": "Falha",
                        "message": "Tipo de tabela não encontrado"
                    })
                    continue
                
                # Register file upload
                file_id = register_uploaded_file(
                    f"{excel_file.name} - {sheet_name}",
                    "excel",
                    matching_table_type
                )
                
                if file_id is None:
                    results.append({
                        "sheet": sheet_name,
                        "status": "Falha",
                        "message": "Falha ao registrar upload"
                    })
                    continue
                
                # Get table name for this type
                table_name = table_mapping[matching_table_type]
                
                # Save data to database
                success = save_df_to_database(df, table_name, file_id)
                
                if success:
                    results.append({
                        "sheet": sheet_name,
                        "status": "Sucesso",
                        "message": f"Importado para {table_name}"
                    })
                else:
                    results.append({
                        "sheet": sheet_name,
                        "status": "Falha",
                        "message": "Falha ao salvar no banco de dados"
                    })
            
            except Exception as e:
                results.append({
                    "sheet": sheet_name,
                    "status": "Erro",
                    "message": str(e)
                })
    
    except Exception as e:
        results.append({
            "sheet": "Geral",
            "status": "Erro",
            "message": f"Erro ao processar arquivo Excel: {str(e)}"
        })
    
    return results