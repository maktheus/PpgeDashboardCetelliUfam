import streamlit as st
import pandas as pd
import numpy as np
from data.data_manager import DataManager
from components.charts import (
    render_time_series_chart,
    render_bar_chart,
    render_pie_chart,
    render_heatmap
)
from utils.calculations import (
    calculate_time_to_defense,
    calculate_completion_rate,
    calculate_success_rate,
    calculate_trending_metrics
)

def render_page():
    """Render the Program Performance page"""
    
    st.title("🏫 Program Performance Metrics")
    
    # Get filtered data
    df = DataManager.get_data()
    
    # Show filter information
    st.info(
        f"Viewing data for: Year = {st.session_state.selected_year}, "
        f"Program = {st.session_state.selected_program}"
    )
    
    # Program overview metrics
    program_metrics = DataManager.get_program_metrics()
    
    if program_metrics.empty:
        st.warning("No program data available.")
        return
    
    # KPI dashboard for programs
    st.subheader("Program KPI Dashboard")
    
    # Create columns for KPIs
    cols = st.columns(len(program_metrics))
    
    for i, (_, row) in enumerate(program_metrics.iterrows()):
        with cols[i]:
            program_name = row['program']
            
            st.metric(
                label=f"{program_name} Program",
                value=f"{int(row['total_students'])} students"
            )
            
            if 'success_rate' in row:
                st.metric(
                    label="Success Rate",
                    value=f"{row['success_rate']*100:.1f}%"
                )
            
            if 'time_to_defense' in row:
                st.metric(
                    label="Avg Time to Defense",
                    value=f"{row['time_to_defense']:.1f} months"
                )
    
    # Trends over time
    st.divider()
    st.subheader("Program Trends Over Time")
    
    # Student enrollment trends
    if 'enrollment_date' in df.columns:
        enrollment_trends = calculate_trending_metrics(df, date_column='enrollment_date', freq='Y')
        
        if not enrollment_trends.empty:
            enrollment_trends['year'] = enrollment_trends['date'].dt.year
            
            # If program is available, calculate enrollment by program and year
            if 'program' in df.columns:
                df['enrollment_year'] = pd.to_datetime(df['enrollment_date']).dt.year
                program_trends = df.groupby(['enrollment_year', 'program']).size().reset_index(name='count')
                
                # Create a pivot table for program trends
                program_pivot = program_trends.pivot(
                    index='enrollment_year',
                    columns='program',
                    values='count'
                ).reset_index()
                
                # Fill NaN values with 0
                program_pivot = program_pivot.fillna(0)
                
                # Convert numeric columns to integers
                for col in program_pivot.columns:
                    if col != 'enrollment_year':
                        program_pivot[col] = program_pivot[col].astype(int)
                
                # Display program trends
                st.subheader("Enrollments by Program Over Time")
                st.dataframe(program_pivot, use_container_width=True)
                
                # Create stacked bar chart
                st.subheader("Enrollment Distribution by Program")
                
                render_bar_chart(
                    program_trends,
                    title="Enrollments by Program and Year",
                    x_column="enrollment_year",
                    y_column="count",
                    color_column="program"
                )
            else:
                # Display simple enrollment trends
                st.subheader("Yearly Enrollments")
                
                render_bar_chart(
                    enrollment_trends,
                    title="Student Enrollments by Year",
                    x_column="year",
                    y_column="count"
                )
        else:
            st.info("No enrollment trend data available.")
    else:
        st.info("Enrollment date data not available.")
    
    # Defense trends if defense data is available
    if 'defense_date' in df.columns and 'defense_status' in df.columns:
        st.divider()
        st.subheader("Defense Trends")
        
        df_with_defense = df[df['defense_status'].notna()].copy()
        
        if not df_with_defense.empty:
            # Calculate defense year
            df_with_defense['defense_year'] = pd.to_datetime(df_with_defense['defense_date']).dt.year
            
            # Count defenses by year and status
            defense_trends = df_with_defense.groupby(['defense_year', 'defense_status']).size().reset_index(name='count')
            
            # Display defense trends
            render_bar_chart(
                defense_trends,
                title="Defenses by Year and Status",
                x_column="defense_year",
                y_column="count",
                color_column="defense_status"
            )
            
            # Calculate success rate by year
            success_by_year = df_with_defense.groupby('defense_year').apply(
                lambda x: (x['defense_status'] == 'Approved').mean()
            ).reset_index(name='success_rate')
            
            success_by_year['success_rate'] = (success_by_year['success_rate'] * 100).round(1)
            
            # Display success rate trend
            st.subheader("Defense Success Rate by Year")
            
            render_bar_chart(
                success_by_year,
                title="Defense Success Rate Trend (%)",
                x_column="defense_year",
                y_column="success_rate"
            )
        else:
            st.info("No defense data available.")
    else:
        st.info("Defense data not available.")
    
    # Department and research area analysis
    if 'department' in df.columns or 'research_area' in df.columns:
        st.divider()
        st.subheader("Department and Research Area Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'department' in df.columns:
                # Department distribution
                dept_dist = df.groupby('department').size().reset_index(name='count')
                dept_dist = dept_dist.sort_values('count', ascending=False)
                
                render_bar_chart(
                    dept_dist,
                    title="Student Distribution by Department",
                    x_column="department",
                    y_column="count",
                    orientation='h'
                )
            else:
                st.info("Department data not available.")
        
        with col2:
            if 'research_area' in df.columns:
                # Research area distribution
                area_dist = df.groupby('research_area').size().reset_index(name='count')
                area_dist = area_dist.sort_values('count', ascending=False).head(10)
                
                render_bar_chart(
                    area_dist,
                    title="Top 10 Research Areas",
                    x_column="research_area",
                    y_column="count",
                    orientation='h'
                )
            else:
                st.info("Research area data not available.")
        
        # If both department and research area are available, show heatmap
        if 'department' in df.columns and 'research_area' in df.columns:
            # Create heatmap of department vs research area
            dept_area = df.groupby(['department', 'research_area']).size().reset_index(name='count')
            
            # Only include combinations with at least 2 students
            dept_area = dept_area[dept_area['count'] >= 2]
            
            if not dept_area.empty:
                st.subheader("Department vs Research Area Distribution")
                
                render_heatmap(
                    dept_area,
                    title="Student Distribution by Department and Research Area",
                    x_column="research_area",
                    y_column="department",
                    value_column="count"
                )
    
    # Publication analysis
    if 'publications' in df.columns:
        st.divider()
        st.subheader("Publication Analysis")
        
        # Calculate publication metrics
        total_publications = df['publications'].sum()
        avg_publications = df['publications'].mean()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Total Publications",
                value=int(total_publications)
            )
        
        with col2:
            st.metric(
                label="Average Publications per Student",
                value=f"{avg_publications:.2f}"
            )
        
        # Show publications by program if available
        if 'program' in df.columns:
            pubs_by_program = df.groupby('program').agg({
                'publications': ['sum', 'mean', 'median']
            }).reset_index()
            
            pubs_by_program.columns = ['Program', 'Total Publications', 'Avg Publications', 'Median Publications']
            pubs_by_program['Avg Publications'] = pubs_by_program['Avg Publications'].round(2)
            
            st.subheader("Publications by Program")
            st.dataframe(pubs_by_program, use_container_width=True)
            
            # Show publication comparison chart
            pub_compare = df.groupby('program')['publications'].mean().reset_index()
            pub_compare['publications'] = pub_compare['publications'].round(2)
            
            render_bar_chart(
                pub_compare,
                title="Average Publications by Program",
                x_column="program",
                y_column="publications"
            )
