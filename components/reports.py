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
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">Download PDF Report</a>'
    
    return href

def render_report_options(key_prefix="default"):
    """
    Render report generation options
    
    Parameters:
    - key_prefix: Prefix for the session state keys to make them unique
    
    Returns:
    - report_title: User inputted report title
    - report_filename: User inputted filename
    - report_type: Selected report type
    - selected_columns: Selected columns to include
    """
    st.subheader("Report Options")
    
    # Report title and filename
    report_title = st.text_input(
        "Report Title", 
        "PPGE KPI Report",
        key=f"{key_prefix}_report_title"
    )
    report_filename = st.text_input(
        "Filename (without extension)", 
        value=f"ppge_report_{datetime.now().strftime('%Y%m%d')}",
        key=f"{key_prefix}_report_filename"
    )
    
    # Report type selection
    report_type = st.selectbox(
        "Report Format", 
        ["Excel", "CSV", "PDF"],
        key=f"{key_prefix}_report_format"
    )
    
    # Column selection
    cols = st.session_state.get('report_columns', [])
    if cols:
        selected_columns = st.multiselect(
            "Select Columns to Include",
            options=cols,
            default=cols,
            key=f"{key_prefix}_selected_columns"
        )
    else:
        selected_columns = []
        st.info("No columns available. Please load data first.")
    
    return report_title, report_filename, report_type, selected_columns
