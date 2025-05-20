import pandas as pd

def analyze_excel_structure(file_path):
    """
    Analisa a estrutura de um arquivo Excel e lista todas as planilhas
    
    Parameters:
    - file_path: Caminho para o arquivo Excel
    """
    try:
        # Ler o arquivo Excel
        xls = pd.ExcelFile(file_path)
        
        # Listar todas as planilhas
        sheet_names = xls.sheet_names
        print(f"O arquivo Excel possui {len(sheet_names)} planilhas:")
        for i, sheet_name in enumerate(sheet_names, 1):
            print(f"{i}. {sheet_name}")
            
            # Ler algumas linhas da planilha para entender sua estrutura
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
                print(f"   Colunas: {list(df.columns)}")
                print(f"   Linhas: {len(df)}")
                print("   Primeiras linhas:")
                print(df.head(2))
                print("")
            except Exception as e:
                print(f"   Erro ao ler planilha: {str(e)}")
                print("")
                
    except Exception as e:
        print(f"Erro ao analisar o arquivo Excel: {str(e)}")

if __name__ == "__main__":
    # Substitua pelo caminho do seu arquivo
    file_path = "attached_assets/00-MAIN-DATA-SUCUPIRA-v14.xlsx"
    analyze_excel_structure(file_path)