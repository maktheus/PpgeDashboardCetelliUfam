import pandas as pd
import os

# Mostrar informações sobre os arquivos
print("Arquivos disponíveis:")
print("1. 00-MAIN-DATA-SUCUPIRA-dash.xlsx")
print("2. professores.xlsx")

# Analisar 00-MAIN-DATA-SUCUPIRA-dash.xlsx
try:
    print("\n=== Analisando o arquivo MAIN-DATA-SUCUPIRA ===")
    sucupira_file = 'attached_assets/00-MAIN-DATA-SUCUPIRA-dash.xlsx'
    
    # Listar sheets
    print("\nPlanilhas disponíveis:")
    sheets = pd.ExcelFile(sucupira_file).sheet_names
    print(sheets)
    
    # Analisar cada planilha
    for sheet in sheets:
        print(f"\n--- Planilha: {sheet} ---")
        df = pd.read_excel(sucupira_file, sheet_name=sheet)
        print(f"Número de linhas: {len(df)}")
        print(f"Colunas: {df.columns.tolist()}")
        print("\nPrimeiras 2 linhas:")
        print(df.head(2).to_string())
        
        # Verificar tipos de dados
        print("\nTipos de dados:")
        print(df.dtypes)
except Exception as e:
    print(f"Erro ao analisar o arquivo MAIN-DATA-SUCUPIRA: {str(e)}")

# Analisar professores.xlsx
try:
    print("\n\n=== Analisando o arquivo PROFESSORES ===")
    prof_file = 'attached_assets/professores.xlsx'
    
    # Listar sheets
    print("\nPlanilhas disponíveis:")
    sheets = pd.ExcelFile(prof_file).sheet_names
    print(sheets)
    
    # Analisar cada planilha
    for sheet in sheets:
        print(f"\n--- Planilha: {sheet} ---")
        df = pd.read_excel(prof_file, sheet_name=sheet)
        print(f"Número de linhas: {len(df)}")
        print(f"Colunas: {df.columns.tolist()}")
        print("\nPrimeiras 2 linhas:")
        print(df.head(2).to_string())
        
        # Verificar tipos de dados
        print("\nTipos de dados:")
        print(df.dtypes)
except Exception as e:
    print(f"Erro ao analisar o arquivo PROFESSORES: {str(e)}")