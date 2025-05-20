import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime

def generate_excel_report(df, filename=None):
    """
    Generate an Excel report from a DataFrame
    
    Parameters:
    - df: DataFrame to export
    - filename: Name of the file (without extension)
    
    Returns:
    - download_link: Download link for the Excel file
    """
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_report_{now}"
    
    # Create a BytesIO object
    output = io.BytesIO()
    
    # Use ExcelWriter to write the DataFrame to the BytesIO object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    
    # Get the data from the BytesIO object
    excel_data = output.getvalue()
    
    # Generate download link
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Download Excel Report</a>'
    
    return href

def generate_csv_report(df, filename=None):
    """
    Generate a CSV report from a DataFrame
    
    Parameters:
    - df: DataFrame to export
    - filename: Name of the file (without extension)
    
    Returns:
    - download_link: Download link for the CSV file
    """
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_report_{now}"
    
    # Create a StringIO object
    csv_data = df.to_csv(index=False)
    
    # Generate download link
    b64 = base64.b64encode(csv_data.encode()).decode()
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">Download CSV Report</a>'
    
    return href

def generate_pdf_report(df, title, filename=None):
    """
    Generate a PDF report from a DataFrame
    
    Parameters:
    - df: DataFrame to export
    - title: Title for the report
    - filename: Name of the file (without extension)
    
    Returns:
    - download_link: Download link for the PDF file
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        st.error("ReportLab is required to generate PDF reports. Please install it with 'pip install reportlab'.")
        return None
    
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_report_{now}"
    
    # Create a BytesIO object
    output = io.BytesIO()
    
    # Create a PDF document
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {timestamp}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Add table
    data = [list(df.columns)]  # Header row
    for i, row in df.iterrows():
        data.append([str(x) for x in row.values])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the data from the BytesIO object
    pdf_data = output.getvalue()
    
    # Generate download link
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">Baixar Relatório PDF</a>'
    
    return href

def render_report_options(key_prefix="default"):
    """
    Renderiza opções para geração de relatórios
    
    Parâmetros:
    - key_prefix: Prefixo para as chaves de estado da sessão para torná-las únicas
    
    Retorna:
    - report_title: Título do relatório inserido pelo usuário
    - report_filename: Nome do arquivo inserido pelo usuário
    - report_type: Tipo de relatório selecionado
    - selected_columns: Colunas selecionadas para incluir
    """
    st.subheader("Opções de Relatório")
    
    # Título e nome do arquivo do relatório
    report_title = st.text_input(
        "Título do Relatório", 
        "Relatório KPI PPGE",
        key=f"{key_prefix}_report_title"
    )
    report_filename = st.text_input(
        "Nome do Arquivo (sem extensão)", 
        value=f"relatorio_ppge_{datetime.now().strftime('%Y%m%d')}",
        key=f"{key_prefix}_report_filename"
    )
    
    # Seleção do tipo de relatório
    report_type = st.selectbox(
        "Formato do Relatório", 
        ["Excel", "CSV", "PDF"],
        key=f"{key_prefix}_report_format"
    )
    
    # Seleção de colunas
    cols = st.session_state.get('report_columns', [])
    if cols:
        selected_columns = st.multiselect(
            "Selecione as Colunas para Incluir",
            options=cols,
            default=cols,
            key=f"{key_prefix}_selected_columns"
        )
    else:
        selected_columns = []
        st.info("Nenhuma coluna disponível. Por favor, carregue os dados primeiro.")
    
    return report_title, report_filename, report_type, selected_columns
