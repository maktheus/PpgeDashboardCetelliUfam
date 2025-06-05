import streamlit as st
import pandas as pd
from datetime import datetime

def render_date_range_filter(label="Date Range", key_prefix="date"):
    """
    Render a date range filter with start and end date inputs
    
    Parameters:
    - label: Label to display above the filter
    - key_prefix: Prefix for the session state keys
    
    Returns:
    - start_date: Selected start date
    - end_date: Selected end date
    """
    st.subheader(label)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get min date from session state or use default
        min_date = datetime(2018, 1, 1)
        max_date = datetime.now()
        
        start_key = f"{key_prefix}_start"
        if start_key not in st.session_state:
            st.session_state[start_key] = min_date
            
        start_date = st.date_input(
            "Start Date",
            value=st.session_state[start_key],
            min_value=min_date,
            max_value=max_date,
            key=start_key
        )
        st.session_state[start_key] = start_date
        
    with col2:
        end_key = f"{key_prefix}_end"
        if end_key not in st.session_state:
            st.session_state[end_key] = max_date
            
        end_date = st.date_input(
            "End Date",
            value=st.session_state[end_key],
            min_value=min_date,
            max_value=max_date,
            key=end_key
        )
        st.session_state[end_key] = end_date
    
    return start_date, end_date

def render_multi_select_filter(options, label, key, default=None):
    """
    Render a multi-select filter
    
    Parameters:
    - options: List of options to select from
    - label: Label to display above the filter
    - key: Key for the session state
    - default: Default selected values
    
    Returns:
    - selected: List of selected options
    """
    if key not in st.session_state:
        st.session_state[key] = default if default is not None else []
        
    selected = st.multiselect(
        label,
        options=options,
        default=st.session_state[key]
    )
    
    st.session_state[key] = selected
    return selected

def render_slider_filter(min_val, max_val, label, key, default=None, step=1, format=None):
    """
    Render a slider filter
    
    Parameters:
    - min_val: Minimum value
    - max_val: Maximum value
    - label: Label to display above the filter
    - key: Key for the session state
    - default: Default selected range (tuple of min, max)
    - step: Slider step size
    - format: Format string for the values
    
    Returns:
    - selected: Tuple of selected min and max values
    """
    if key not in st.session_state:
        st.session_state[key] = default if default is not None else (min_val, max_val)
        
    selected = st.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=st.session_state[key],
        step=step,
        format=format
    )
    
    st.session_state[key] = selected
    return selected

def apply_filters(df, filters):
    """
    Apply multiple filters to a dataframe
    
    Parameters:
    - df: DataFrame to filter
    - filters: Dictionary where keys are column names and values are filter functions
              that take a dataframe and return a boolean mask
    
    Returns:
    - filtered_df: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, filter_func in filters.items():
        mask = filter_func(filtered_df)
        filtered_df = filtered_df[mask]
    
    return filtered_df

def create_date_filter(column, start_date, end_date):
    """
    Create a date filter function
    
    Parameters:
    - column: Column name containing dates
    - start_date: Start date for filtering
    - end_date: End date for filtering
    
    Returns:
    - filter_func: Function that takes a dataframe and returns a boolean mask
    """
    def filter_func(df):
        if column not in df.columns:
            return pd.Series([True] * len(df))
        
        df_copy = df.copy()
        if df_copy[column].dtype != 'datetime64[ns]':
            df_copy[column] = pd.to_datetime(df_copy[column])
            
        return (df_copy[column] >= pd.Timestamp(start_date)) & (df_copy[column] <= pd.Timestamp(end_date))
    
    return filter_func

def create_category_filter(column, selected_values):
    """
    Create a category filter function
    
    Parameters:
    - column: Column name containing categories
    - selected_values: List of values to include
    
    Returns:
    - filter_func: Function that takes a dataframe and returns a boolean mask
    """
    def filter_func(df):
        if column not in df.columns or not selected_values:
            return pd.Series([True] * len(df))
            
        return df[column].isin(selected_values)
    
    return filter_func

def create_range_filter(column, min_val, max_val):
    """
    Create a range filter function
    
    Parameters:
    - column: Column name containing numeric values
    - min_val: Minimum value to include
    - max_val: Maximum value to include
    
    Returns:
    - filter_func: Function that takes a dataframe and returns a boolean mask
    """
    def filter_func(df):
        if column not in df.columns:
            return pd.Series([True] * len(df))
            
        return (df[column] >= min_val) & (df[column] <= max_val)
    
    return filter_func
