import pandas as pd
import streamlit as st
import io
import base64
from datetime import datetime

def export_to_excel(df, filename=None):
    """
    Export DataFrame to Excel file
    
    Parameters:
    - df: DataFrame to export
    - filename: Filename (without extension)
    
    Returns:
    - download_link: HTML link for downloading the file
    """
    # Generate filename if not provided
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_data_{now}"
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    # Get binary data
    excel_data = output.getvalue()
    
    # Create download link
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Download Excel File</a>'
    
    return href

def export_to_csv(df, filename=None):
    """
    Export DataFrame to CSV file
    
    Parameters:
    - df: DataFrame to export
    - filename: Filename (without extension)
    
    Returns:
    - download_link: HTML link for downloading the file
    """
    # Generate filename if not provided
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_data_{now}"
    
    # Create CSV string
    csv = df.to_csv(index=False)
    
    # Create download link
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">Download CSV File</a>'
    
    return href

def export_to_pdf(df, title, filename=None):
    """
    Export DataFrame to PDF file
    
    Parameters:
    - df: DataFrame to export
    - title: Report title
    - filename: Filename (without extension)
    
    Returns:
    - download_link: HTML link for downloading the file
    """
    # This requires the ReportLab library
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    # Generate filename if not provided
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_report_{now}"
    
    # Create buffer
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    
    # Create story (content)
    story = []
    
    # Add title
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_style = styles['Normal']
    story.append(Paragraph(f"Generated on: {timestamp}", date_style))
    story.append(Spacer(1, 20))
    
    # Prepare data for table
    data = [list(df.columns)]  # Add header row
    
    # Add data rows
    for i, row in df.iterrows():
        data.append([str(x) for x in row.values])
    
    # Create table
    table = Table(data)
    
    # Style table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(table_style)
    story.append(table)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create download link
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">Download PDF File</a>'
    
    return href

def generate_report(df, title, format='excel', filename=None, selected_columns=None):
    """
    Generate a report in the specified format
    
    Parameters:
    - df: DataFrame to export
    - title: Report title
    - format: 'excel', 'csv', or 'pdf'
    - filename: Filename (without extension)
    - selected_columns: List of columns to include (if None, all columns are included)
    
    Returns:
    - download_link: HTML link for downloading the file
    """
    # Filter columns if specified
    if selected_columns:
        df = df[selected_columns].copy()
    
    # Generate filename if not provided
    if filename is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppge_report_{now}"
    
    # Export based on format
    if format.lower() == 'excel':
        return export_to_excel(df, filename)
    elif format.lower() == 'csv':
        return export_to_csv(df, filename)
    elif format.lower() == 'pdf':
        return export_to_pdf(df, title, filename)
    else:
        st.error(f"Unsupported format: {format}")
        return ""
