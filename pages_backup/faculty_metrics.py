import streamlit as st
import pandas as pd
import numpy as np
from data.data_manager import DataManager
from components.charts import (
    render_bar_chart,
    render_scatter_plot,
    render_pie_chart
)
from utils.calculations import calculate_advisor_metrics

def render_page():
    """Render the Faculty Metrics page"""
    
    st.title("👨‍🏫 Faculty Metrics")
    
    # Get filtered data
    df = DataManager.get_data()
    
    # Show filter information
    st.info(
        f"Viewing data for: Year = {st.session_state.selected_year}, "
        f"Program = {st.session_state.selected_program}"
    )
    
    # Calculate advisor metrics
    advisor_metrics = calculate_advisor_metrics(df)
    
    if advisor_metrics.empty:
        st.warning("No faculty data available.")
        return
    
    # Top advisors metrics
    st.subheader("Top Faculty Members")
    
    # Create three columns for top metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### By Number of Students")
        
        top_by_students = advisor_metrics.sort_values('total_students', ascending=False).head(5)
        
        render_bar_chart(
            top_by_students,
            title="Faculty with Most Students",
            x_column="advisor_name" if "advisor_name" in top_by_students.columns else "advisor_id",
            y_column="total_students",
            orientation='h'
        )
    
    with col2:
        st.markdown("### By Success Rate")
        
        if 'success_rate' in advisor_metrics.columns:
            # Filter advisors with at least 3 students
            min_students = 3
            success_advisors = advisor_metrics[advisor_metrics['total_students'] >= min_students].copy()
            
            if not success_advisors.empty:
                success_advisors['success_rate_pct'] = (success_advisors['success_rate'] * 100).round(1)
                success_advisors = success_advisors.sort_values('success_rate_pct', ascending=False).head(5)
                
                render_bar_chart(
                    success_advisors,
                    title=f"Faculty with Highest Success Rate (min {min_students} students)",
                    x_column="advisor_name" if "advisor_name" in success_advisors.columns else "advisor_id",
                    y_column="success_rate_pct",
                    orientation='h'
                )
            else:
                st.info(f"No faculty with at least {min_students} students.")
        else:
            st.info("Success rate data not available.")
    
    with col3:
        st.markdown("### By Time to Defense")
        
        if 'avg_time_to_defense' in advisor_metrics.columns:
            # Filter advisors with at least 3 students
            min_students = 3
            time_advisors = advisor_metrics[advisor_metrics['total_students'] >= min_students].copy()
            
            if not time_advisors.empty:
                time_advisors['avg_time_to_defense'] = time_advisors['avg_time_to_defense'].round(1)
                time_advisors = time_advisors.sort_values('avg_time_to_defense').head(5)
                
                render_bar_chart(
                    time_advisors,
                    title=f"Faculty with Fastest Time to Defense (min {min_students} students)",
                    x_column="advisor_name" if "advisor_name" in time_advisors.columns else "advisor_id",
                    y_column="avg_time_to_defense",
                    orientation='h'
                )
            else:
                st.info(f"No faculty with at least {min_students} students and time to defense data.")
        else:
            st.info("Time to defense data not available.")
    
    # Faculty workload analysis
    st.divider()
    st.subheader("Faculty Workload Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Workload distribution
        advisor_metrics['students_binned'] = pd.cut(
            advisor_metrics['total_students'],
            bins=[0, 1, 3, 5, 10, 100],
            labels=['1 student', '2-3 students', '4-5 students', '6-10 students', '10+ students']
        )
        
        workload_dist = advisor_metrics.groupby('students_binned').size().reset_index(name='count')
        
        render_pie_chart(
            workload_dist,
            title="Faculty Workload Distribution",
            values_column="count",
            names_column="students_binned"
        )
    
    with col2:
        # Department distribution if department data is available
        if 'department' in df.columns:
            faculty_by_dept = df.groupby('advisor_id').first().reset_index()
            dept_dist = faculty_by_dept.groupby('department').size().reset_index(name='count')
            
            render_pie_chart(
                dept_dist,
                title="Faculty by Department",
                values_column="count",
                names_column="department"
            )
        else:
            st.info("Department data not available.")
    
    # Faculty details table
    st.divider()
    st.subheader("Faculty Details Table")
    
    # Prepare the table
    table_cols = ['advisor_id', 'advisor_name', 'total_students']
    
    if 'success_rate' in advisor_metrics.columns:
        advisor_metrics['success_rate_pct'] = (advisor_metrics['success_rate'] * 100).round(1)
        table_cols.append('success_rate_pct')
    
    if 'avg_time_to_defense' in advisor_metrics.columns:
        advisor_metrics['avg_time_to_defense'] = advisor_metrics['avg_time_to_defense'].round(1)
        table_cols.append('avg_time_to_defense')
    
    if 'total_publications' in advisor_metrics.columns:
        table_cols.append('total_publications')
    
    # Filter columns that exist in the dataframe
    table_cols = [col for col in table_cols if col in advisor_metrics.columns]
    
    # Sort by number of students
    display_df = advisor_metrics[table_cols].sort_values('total_students', ascending=False)
    
    # Rename columns for better display
    column_renames = {
        'advisor_id': 'Advisor ID',
        'advisor_name': 'Advisor Name',
        'total_students': 'Total Students',
        'success_rate_pct': 'Success Rate (%)',
        'avg_time_to_defense': 'Avg Time to Defense (months)',
        'total_publications': 'Total Publications'
    }
    
    display_df = display_df.rename(columns={col: column_renames.get(col, col) for col in table_cols})
    
    # Display the table
    st.dataframe(display_df, use_container_width=True)
    
    # Add a search option
    if 'advisor_name' in advisor_metrics.columns:
        st.subheader("Search Faculty Member")
        
        search_term = st.text_input("Enter name to search", "")
        
        if search_term:
            # Search by name
            search_result = advisor_metrics[
                advisor_metrics['advisor_name'].str.contains(search_term, case=False)
            ]
            
            if not search_result.empty:
                search_cols = [col for col in table_cols if col in search_result.columns]
                search_display = search_result[search_cols].rename(
                    columns={col: column_renames.get(col, col) for col in search_cols}
                )
                
                st.dataframe(search_display, use_container_width=True)
            else:
                st.info(f"No faculty member found with name containing '{search_term}'.")
