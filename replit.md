# replit.md

## Overview

This is a Streamlit-based KPI Dashboard for PPGEE (Programa de Pós-Graduação em Engenharias Elétricas), designed to analyze and visualize key performance indicators for graduate programs according to CAPES evaluation criteria for Engineering IV programs. The application provides comprehensive data management, visualization, and reporting capabilities for academic program assessment.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **UI Components**: Multi-page application with tabbed interfaces
- **Visualization**: Plotly charts and graphs for data presentation
- **Language Support**: Portuguese and English translations
- **Authentication**: TOTP-based authentication system with QR code generation

### Backend Architecture
- **Data Processing**: Pandas-based data manipulation and analysis
- **Database**: PostgreSQL for persistent data storage
- **File Processing**: Support for Excel (.xlsx), CSV, and JSON file imports
- **Batch Processing**: Multi-sheet Excel import capabilities

### Data Flow
1. **Data Import**: Users upload Excel/CSV files through web interface
2. **Data Processing**: Files are parsed and mapped to appropriate database tables
3. **Data Storage**: Processed data is stored in PostgreSQL tables
4. **Data Analysis**: KPI calculations are performed on stored data
5. **Visualization**: Results are displayed through interactive charts and metrics

## Key Components

### Data Management
- **DataManager Class**: Central data management with session state integration
- **Sample Data Generator**: Creates synthetic data for testing and demonstration
- **Database Integration**: PostgreSQL connection management and table operations
- **File Import System**: Support for multiple file formats with automatic mapping

### KPI Calculation Engine
- **CAPES Indicators**: Implementation of 20+ CAPES evaluation indicators
- **Student Metrics**: Time to defense, completion rates, success rates
- **Faculty Metrics**: Advisor distribution, productivity measures
- **Program Performance**: Trend analysis and comparative metrics

### Visualization Components
- **Interactive Charts**: Plotly-based time series, bar charts, pie charts, histograms
- **KPI Cards**: Metric display cards with delta comparisons
- **Dashboard Views**: Overview, detailed metrics, and comparative analysis

### Authentication System
- **TOTP Authentication**: Time-based one-time password system
- **QR Code Generation**: For mobile authenticator app setup
- **Session Management**: Secure session state handling

### Multi-language Support
- **Translation System**: Portuguese/English language switching
- **Localized Content**: All UI elements and help text translated

## External Dependencies

### Core Dependencies
- **streamlit**: Web application framework (v1.45.0)
- **pandas**: Data manipulation and analysis (v2.2.3)
- **plotly**: Interactive visualization library (v6.0.1)
- **psycopg2-binary**: PostgreSQL database adapter (v2.9.10)
- **openpyxl**: Excel file processing (v3.1.5)

### Authentication & Security
- **pyotp**: TOTP implementation (v2.9.0)
- **qrcode**: QR code generation (v8.2)

### Additional Libraries
- **numpy**: Numerical computing (v2.2.5)
- **requests**: HTTP library (v2.32.3)
- **reportlab**: PDF generation (v4.4.0)
- **google-auth**: Google authentication (v2.40.1)
- **twilio**: SMS notifications (v9.6.1)

## Deployment Strategy

### Environment Configuration
- **Platform**: Replit with Python 3.11 and PostgreSQL 16
- **Health Check**: Integrated health check server on port 8080
- **Scaling**: Autoscale deployment target
- **Port Configuration**: Main app on port 5000, health check on port 8080

### Database Setup
- **PostgreSQL**: Version 16 with automatic table initialization
- **Connection Management**: Environment variable-based configuration
- **Data Persistence**: Structured tables for students, faculty, and program data

### File Structure
- Modular architecture with separate components, utils, and data modules
- Page-based navigation with backup page implementations
- Asset management for Excel templates and reference data

## Changelog
- June 24, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.