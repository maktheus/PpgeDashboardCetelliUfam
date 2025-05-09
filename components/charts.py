import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_time_series_chart(df, title, x_column, y_column, color_column=None):
    """
    Render a time series line chart with Plotly
    
    Parameters:
    - df: DataFrame containing the data
    - title: Chart title
    - x_column: Column to use for x-axis (usually a date column)
    - y_column: Column to use for y-axis
    - color_column: Optional column to use for color differentiation
    """
    # Create figure
    if color_column:
        fig = px.line(
            df, 
            x=x_column, 
            y=y_column,
            color=color_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            markers=True
        )
    else:
        fig = px.line(
            df, 
            x=x_column, 
            y=y_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            markers=True
        )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title=x_column.replace('_', ' ').title(),
        yaxis_title=y_column.replace('_', ' ').title(),
        legend_title_text=color_column.replace('_', ' ').title() if color_column else None,
        hovermode="x unified"
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def render_bar_chart(df, title, x_column, y_column, color_column=None, orientation='v'):
    """
    Render a bar chart with Plotly
    
    Parameters:
    - df: DataFrame containing the data
    - title: Chart title
    - x_column: Column to use for x-axis
    - y_column: Column to use for y-axis
    - color_column: Optional column to use for color differentiation
    - orientation: 'v' for vertical bars, 'h' for horizontal bars
    """
    # Create figure
    if color_column:
        fig = px.bar(
            df, 
            x=x_column if orientation == 'v' else y_column,
            y=y_column if orientation == 'v' else x_column,
            color=color_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            orientation=orientation
        )
    else:
        fig = px.bar(
            df, 
            x=x_column if orientation == 'v' else y_column,
            y=y_column if orientation == 'v' else x_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            orientation=orientation
        )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title=x_column.replace('_', ' ').title() if orientation == 'v' else y_column.replace('_', ' ').title(),
        yaxis_title=y_column.replace('_', ' ').title() if orientation == 'v' else x_column.replace('_', ' ').title(),
        legend_title_text=color_column.replace('_', ' ').title() if color_column else None,
        hovermode="x unified"
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def render_pie_chart(df, title, values_column, names_column):
    """
    Render a pie chart with Plotly
    
    Parameters:
    - df: DataFrame containing the data
    - title: Chart title
    - values_column: Column to use for slice sizes
    - names_column: Column to use for slice labels
    """
    # Create figure
    fig = px.pie(
        df, 
        values=values_column,
        names=names_column,
        title=title
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        legend_title_text=names_column.replace('_', ' ').title()
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def render_scatter_plot(df, title, x_column, y_column, color_column=None, size_column=None):
    """
    Render a scatter plot with Plotly
    
    Parameters:
    - df: DataFrame containing the data
    - title: Chart title
    - x_column: Column to use for x-axis
    - y_column: Column to use for y-axis
    - color_column: Optional column to use for color differentiation
    - size_column: Optional column to use for point sizes
    """
    # Create figure
    fig = px.scatter(
        df, 
        x=x_column,
        y=y_column,
        color=color_column if color_column else None,
        size=size_column if size_column else None,
        title=title,
        labels={x_column: x_column.replace('_', ' ').title(), 
               y_column: y_column.replace('_', ' ').title()}
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title=x_column.replace('_', ' ').title(),
        yaxis_title=y_column.replace('_', ' ').title(),
        legend_title_text=color_column.replace('_', ' ').title() if color_column else None,
        hovermode="closest"
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def render_histogram(df, title, column, bins=None, color_column=None):
    """
    Render a histogram with Plotly
    
    Parameters:
    - df: DataFrame containing the data
    - title: Chart title
    - column: Column to create histogram from
    - bins: Number of bins (optional)
    - color_column: Optional column to use for color differentiation
    """
    # Create figure
    fig = px.histogram(
        df, 
        x=column,
        color=color_column if color_column else None,
        nbins=bins,
        title=title,
        labels={column: column.replace('_', ' ').title()}
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title=column.replace('_', ' ').title(),
        yaxis_title='Count',
        legend_title_text=color_column.replace('_', ' ').title() if color_column else None,
        bargap=0.1
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def render_heatmap(df, title, x_column, y_column, value_column):
    """
    Render a heatmap with Plotly
    
    Parameters:
    - df: DataFrame containing the data
    - title: Chart title
    - x_column: Column to use for x-axis
    - y_column: Column to use for y-axis
    - value_column: Column to use for color intensity
    """
    # Pivot the data
    pivot_data = df.pivot_table(
        index=y_column, 
        columns=x_column, 
        values=value_column,
        aggfunc='mean'
    )
    
    # Create figure
    fig = px.imshow(
        pivot_data,
        title=title,
        labels=dict(
            x=x_column.replace('_', ' ').title(),
            y=y_column.replace('_', ' ').title(),
            color=value_column.replace('_', ' ').title()
        )
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title=x_column.replace('_', ' ').title(),
        yaxis_title=y_column.replace('_', ' ').title()
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
