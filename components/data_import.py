import streamlit as st
import pandas as pd
import io
import datetime
import json

def render_file_uploader():
    """
    Render file uploader for importing data
    
    Returns:
    - uploaded_file: File object or None if no file was uploaded
    - file_type: Detected file type or None
    """
    st.subheader("Import Data")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a file (Excel, CSV, or JSON)",
        type=["xlsx", "csv", "json"]
    )
    
    file_type = None
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'xlsx':
            file_type = 'excel'
        elif file_extension == 'csv':
            file_type = 'csv'
        elif file_extension == 'json':
            file_type = 'json'
    
    return uploaded_file, file_type

def process_uploaded_file(uploaded_file, file_type):
    """
    Process uploaded file and convert to DataFrame
    
    Parameters:
    - uploaded_file: Uploaded file object
    - file_type: Type of file ('excel', 'csv', or 'json')
    
    Returns:
    - df: Processed DataFrame or None if processing failed
    - error_message: Error message or None if processing succeeded
    """
    try:
        if file_type == 'excel':
            df = pd.read_excel(uploaded_file)
        elif file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'json':
            # For JSON, try to load as records
            json_data = json.load(uploaded_file)
            
            # If it's a list of records, convert directly
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            # If it's a dict with nested data, try flattening
            elif isinstance(json_data, dict):
                # Check if it has a top-level key that contains the data
                data_keys = [k for k in json_data.keys() if isinstance(json_data[k], list)]
                
                if data_keys:
                    # Use the first key that contains a list
                    df = pd.DataFrame(json_data[data_keys[0]])
                else:
                    # Treat as a single record
                    df = pd.DataFrame([json_data])
            else:
                return None, "Invalid JSON format"
        else:
            return None, "Unsupported file type"
        
        # Process date columns
        for col in df.columns:
            # Check if column name suggests it's a date
            if any(date_hint in col.lower() for date_hint in ['date', 'time', 'day', 'month', 'year']):
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    # If conversion fails, leave as is
                    pass
        
        return df, None
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def render_data_mapping_tool(df):
    """
    Render a tool for mapping columns in the imported data
    
    Parameters:
    - df: Imported DataFrame
    
    Returns:
    - mapped_df: DataFrame with mapped columns
    - mapping_applied: Boolean indicating if mapping was applied
    """
    st.subheader("Map Data Columns")
    
    # Define expected columns for the PPGE KPI dashboard
    expected_columns = {
        'student_id': 'Student ID',
        'student_name': 'Student Name',
        'program': 'Program (Masters/Doctorate)',
        'enrollment_date': 'Enrollment Date',
        'defense_date': 'Defense Date',
        'defense_status': 'Defense Status (Approved/Failed)',
        'advisor_id': 'Advisor ID',
        'advisor_name': 'Advisor Name',
        'department': 'Department',
        'research_area': 'Research Area',
        'publications': 'Number of Publications'
    }
    
    # Create mapping UI
    st.write("Map your data columns to the expected format:")
    
    mapping = {}
    cols = st.columns(2)
    
    for i, (expected_col, description) in enumerate(expected_columns.items()):
        col_idx = i % 2
        with cols[col_idx]:
            mapping[expected_col] = st.selectbox(
                f"{description}",
                options=["-- Ignore --"] + list(df.columns),
                key=f"map_{expected_col}"
            )
    
    # Apply mapping button
    apply_mapping = st.button("Apply Mapping")
    mapping_applied = False
    mapped_df = df.copy()
    
    if apply_mapping:
        # Create a new DataFrame with the mapped columns
        new_df = pd.DataFrame()
        
        for expected_col, source_col in mapping.items():
            if source_col != "-- Ignore --":
                new_df[expected_col] = df[source_col]
        
        # Display preview of mapped data
        st.subheader("Mapped Data Preview")
        st.dataframe(new_df.head())
        
        # Update the mapped DataFrame
        mapped_df = new_df
        mapping_applied = True
        
        # Confirmation message
        st.success("Column mapping applied successfully!")
    
    return mapped_df, mapping_applied

def save_imported_data(df):
    """
    Save imported and processed data
    
    Parameters:
    - df: DataFrame to save
    
    Returns:
    - success: Boolean indicating if the save was successful
    """
    # In a real application, this would save to a database
    # For this Streamlit app, we'll store in session state
    
    # Store the DataFrame in session state
    st.session_state['imported_data'] = df
    
    # Store the import timestamp
    st.session_state['data_import_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return True
