import streamlit as st
import pandas as pd
import numpy as np
from data.data_manager import DataManager
from components.charts import (
    render_bar_chart,
    render_histogram,
    render_scatter_plot
)
from utils.calculations import calculate_time_to_defense
from components.filters import (
    render_multi_select_filter,
    render_slider_filter,
    create_category_filter,
    create_range_filter,
    apply_filters
)

def render_page():
    """Render the Student Metrics page"""
    
    st.title("👨‍🎓 Student Metrics")
    
    # Get filtered data
    df = DataManager.get_student_metrics()
    
    # Show filter information
    st.info(
        f"Viewing data for: Year = {st.session_state.selected_year}, "
        f"Program = {st.session_state.selected_program}"
    )
    
    # Create columns for additional filters
    col1, col2 = st.columns(2)
    
    with col1:
        if 'department' in df.columns:
            departments = ["All"] + sorted(df['department'].unique().tolist())
            selected_departments = render_multi_select_filter(
                departments[1:],  # Skip "All"
                "Select Departments",
                "selected_departments",
                default=[]
            )
        else:
            selected_departments = []
            
    with col2:
        if 'research_area' in df.columns:
            research_areas = ["All"] + sorted(df['research_area'].unique().tolist())
            selected_research_areas = render_multi_select_filter(
                research_areas[1:],  # Skip "All"
                "Select Research Areas",
                "selected_research_areas",
                default=[]
            )
        else:
            selected_research_areas = []
    
    # Apply additional filters to the data
    filters = {}
    
    if selected_departments:
        filters['department'] = create_category_filter('department', selected_departments)
    
    if selected_research_areas:
        filters['research_area'] = create_category_filter('research_area', selected_research_areas)
    
    if filters:
        df = apply_filters(df, filters)
    
    # Display student count after filtering
    st.subheader(f"Showing data for {len(df)} students")
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs([
        "Time to Defense Analysis", 
        "Publication Metrics", 
        "Student Details"
    ])
    
    with tab1:
        st.subheader("Time to Defense Analysis")
        
        if 'time_to_defense' in df.columns:
            # Time to defense histogram
            render_histogram(
                df[df['time_to_defense'].notna()],
                title="Distribution of Time to Defense (months)",
                column="time_to_defense",
                bins=20,
                color_column="program" if 'program' in df.columns else None
            )
            
            # Add some statistics
            if df['time_to_defense'].notna().sum() > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Average Time (months)",
                        f"{df['time_to_defense'].mean():.1f}"
                    )
                
                with col2:
                    st.metric(
                        "Median Time (months)",
                        f"{df['time_to_defense'].median():.1f}"
                    )
                
                with col3:
                    st.metric(
                        "Std Deviation (months)",
                        f"{df['time_to_defense'].std():.1f}"
                    )
                
                # Time by department if available
                if 'department' in df.columns:
                    st.subheader("Average Time to Defense by Department")
                    
                    dept_time = df.groupby('department')['time_to_defense'].mean().reset_index()
                    dept_time = dept_time.sort_values('time_to_defense')
                    dept_time['time_to_defense'] = dept_time['time_to_defense'].round(1)
                    
                    render_bar_chart(
                        dept_time,
                        title="Average Time by Department (months)",
                        x_column="department",
                        y_column="time_to_defense",
                        orientation='h'
                    )
            else:
                st.info("No students with defense data in the current selection.")
        else:
            st.info("Time to defense data is not available.")
    
    with tab2:
        st.subheader("Publication Metrics")
        
        if 'publications' in df.columns:
            # Publications histogram
            render_histogram(
                df,
                title="Distribution of Publications per Student",
                column="publications",
                bins=10,
                color_column="program" if 'program' in df.columns else None
            )
            
            # Add some statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Average Publications",
                    f"{df['publications'].mean():.1f}"
                )
            
            with col2:
                st.metric(
                    "Median Publications",
                    f"{df['publications'].median():.1f}"
                )
            
            with col3:
                st.metric(
                    "Max Publications",
                    f"{df['publications'].max()}"
                )
            
            # If time to defense is available, show correlation
            if 'time_to_defense' in df.columns:
                st.subheader("Publications vs Time to Defense")
                
                # Filter for students who have defended
                defended_df = df[df['time_to_defense'].notna()].copy()
                
                if not defended_df.empty:
                    render_scatter_plot(
                        defended_df,
                        title="Publications vs Time to Defense",
                        x_column="time_to_defense",
                        y_column="publications",
                        color_column="program" if 'program' in df.columns else None
                    )
                    
                    # Calculate correlation
                    corr = defended_df['publications'].corr(defended_df['time_to_defense'])
                    st.info(f"Correlation coefficient: {corr:.2f}")
                else:
                    st.info("No students with both publication and defense data.")
        else:
            st.info("Publication data is not available.")
    
    with tab3:
        st.subheader("Student Details")
        
        # Display a table of student details
        if not df.empty:
            # Select columns to display
            display_cols = ['student_id', 'student_name', 'program', 'department', 
                           'research_area', 'advisor_name', 'publications']
            
            # Add time to defense if available
            if 'time_to_defense' in df.columns:
                display_cols.append('time_to_defense')
            
            # Add defense status if available
            if 'defense_status' in df.columns:
                display_cols.append('defense_status')
            
            # Filter columns that exist in the dataframe
            display_cols = [col for col in display_cols if col in df.columns]
            
            # Sort by student ID
            if 'student_id' in df.columns:
                display_df = df[display_cols].sort_values('student_id')
            else:
                display_df = df[display_cols]
            
            # Allow text search
            search_term = st.text_input("Search by Name or ID", "")
            
            if search_term:
                # Search in relevant columns
                search_cols = [col for col in ['student_id', 'student_name'] if col in display_df.columns]
                
                if search_cols:
                    search_mask = display_df[search_cols[0]].str.contains(search_term, case=False)
                    
                    for col in search_cols[1:]:
                        search_mask |= display_df[col].str.contains(search_term, case=False)
                    
                    display_df = display_df[search_mask]
            
            # Show the data table
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No student data available for the current selection.")
