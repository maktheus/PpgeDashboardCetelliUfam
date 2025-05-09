import pandas as pd
import numpy as np

def calculate_time_to_defense(df):
    """
    Calculate time to defense for each student
    
    Parameters:
    - df: DataFrame with enrollment_date and defense_date columns
    
    Returns:
    - DataFrame with time_to_defense column added (in months)
    """
    if 'enrollment_date' in df.columns and 'defense_date' in df.columns:
        df = df.copy()
        
        # Ensure dates are datetime objects
        df['enrollment_date'] = pd.to_datetime(df['enrollment_date'])
        df['defense_date'] = pd.to_datetime(df['defense_date'])
        
        # Calculate time difference in months
        df['time_to_defense'] = (df['defense_date'] - df['enrollment_date']).dt.days / 30.44
        
        return df
    
    return df

def calculate_completion_rate(df, by_group=None):
    """
    Calculate completion rate (percentage of students who have defended)
    
    Parameters:
    - df: DataFrame with defense_status column
    - by_group: Column name to group by (optional)
    
    Returns:
    - If by_group is None: completion rate as a float
    - If by_group is specified: DataFrame with completion rates by group
    """
    if 'defense_status' not in df.columns:
        return 0.0 if by_group is None else pd.DataFrame()
    
    df = df.copy()
    
    # Function to calculate completion rate for a group
    def calc_rate(group):
        total = len(group)
        completed = group['defense_status'].notna().sum()
        return (completed / total) if total > 0 else 0
    
    if by_group:
        if by_group not in df.columns:
            return pd.DataFrame()
        
        # Group by the specified column and calculate rates
        result = df.groupby(by_group).apply(calc_rate).reset_index()
        result.columns = [by_group, 'completion_rate']
        
        return result
    else:
        # Calculate overall completion rate
        total = len(df)
        completed = df['defense_status'].notna().sum()
        
        return (completed / total) if total > 0 else 0

def calculate_success_rate(df, by_group=None):
    """
    Calculate success rate (percentage of defenses that were approved)
    
    Parameters:
    - df: DataFrame with defense_status column
    - by_group: Column name to group by (optional)
    
    Returns:
    - If by_group is None: success rate as a float
    - If by_group is specified: DataFrame with success rates by group
    """
    if 'defense_status' not in df.columns:
        return 0.0 if by_group is None else pd.DataFrame()
    
    df = df.copy()
    
    # Function to calculate success rate for a group
    def calc_rate(group):
        defenses = group['defense_status'].notna().sum()
        successful = (group['defense_status'] == 'Approved').sum()
        return (successful / defenses) if defenses > 0 else 0
    
    if by_group:
        if by_group not in df.columns:
            return pd.DataFrame()
        
        # Group by the specified column and calculate rates
        result = df.groupby(by_group).apply(calc_rate).reset_index()
        result.columns = [by_group, 'success_rate']
        
        return result
    else:
        # Calculate overall success rate
        defenses = df['defense_status'].notna().sum()
        successful = (df['defense_status'] == 'Approved').sum()
        
        return (successful / defenses) if defenses > 0 else 0

def calculate_productivity_metrics(df):
    """
    Calculate productivity metrics (publications per student, etc.)
    
    Parameters:
    - df: DataFrame with publications column
    
    Returns:
    - Dictionary of productivity metrics
    """
    if 'publications' not in df.columns:
        return {}
    
    df = df.copy()
    
    metrics = {
        'avg_publications': df['publications'].mean(),
        'median_publications': df['publications'].median(),
        'max_publications': df['publications'].max(),
        'total_publications': df['publications'].sum()
    }
    
    # Calculate by program if available
    if 'program' in df.columns:
        by_program = df.groupby('program')['publications'].agg(['mean', 'median', 'max', 'sum'])
        
        for program in by_program.index:
            metrics[f'{program.lower()}_avg_publications'] = by_program.loc[program, 'mean']
            metrics[f'{program.lower()}_total_publications'] = by_program.loc[program, 'sum']
    
    return metrics

def calculate_advisor_metrics(df):
    """
    Calculate metrics related to advisors
    
    Parameters:
    - df: DataFrame with advisor_id and related columns
    
    Returns:
    - DataFrame with advisor metrics
    """
    if 'advisor_id' not in df.columns:
        return pd.DataFrame()
    
    df = df.copy()
    
    # Group by advisor
    advisor_metrics = df.groupby('advisor_id').agg({
        'student_id': 'count',
        'publications': 'sum' if 'publications' in df.columns else 'size'
    }).reset_index()
    
    advisor_metrics.rename(columns={
        'student_id': 'total_students',
        'publications': 'total_publications'
    }, inplace=True)
    
    # Add advisor names if available
    if 'advisor_name' in df.columns:
        advisor_names = df[['advisor_id', 'advisor_name']].drop_duplicates()
        advisor_metrics = advisor_metrics.merge(advisor_names, on='advisor_id')
    
    # Calculate success rates if defense data is available
    if 'defense_status' in df.columns:
        success_rates = calculate_success_rate(df, by_group='advisor_id')
        
        if not success_rates.empty:
            advisor_metrics = advisor_metrics.merge(success_rates, on='advisor_id')
    
    # Calculate average time to defense if available
    if 'enrollment_date' in df.columns and 'defense_date' in df.columns:
        df_with_time = calculate_time_to_defense(df)
        
        avg_time = df_with_time.groupby('advisor_id')['time_to_defense'].mean().reset_index()
        avg_time.rename(columns={'time_to_defense': 'avg_time_to_defense'}, inplace=True)
        
        advisor_metrics = advisor_metrics.merge(avg_time, on='advisor_id')
    
    return advisor_metrics

def calculate_trending_metrics(df, date_column='enrollment_date', freq='M'):
    """
    Calculate metrics over time to show trends
    
    Parameters:
    - df: DataFrame with date column
    - date_column: Column containing dates
    - freq: Frequency for grouping ('D' for daily, 'W' for weekly, 'M' for monthly, 'Y' for yearly)
    
    Returns:
    - DataFrame with metrics over time
    """
    if date_column not in df.columns:
        return pd.DataFrame()
    
    df = df.copy()
    
    # Ensure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Group by time period
    df['period'] = df[date_column].dt.to_period(freq)
    
    # Calculate metrics per period
    period_metrics = df.groupby('period').agg({
        'student_id': 'count'
    }).reset_index()
    
    # Convert period back to datetime for plotting
    period_metrics['period'] = period_metrics['period'].dt.to_timestamp()
    
    period_metrics.rename(columns={
        'student_id': 'count',
        'period': 'date'
    }, inplace=True)
    
    return period_metrics
