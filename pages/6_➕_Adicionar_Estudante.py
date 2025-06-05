import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, date

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the page configuration
st.set_page_config(
    page_title="Adicionar Estudante | PPGEE KPI Dashboard",
    page_icon="➕",
    layout="wide",
)

# Initialize session state for filters if not already done
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = 'All'

if 'selected_program' not in st.session_state:
    st.session_state.selected_program = 'All'

# Import our modules
from data.data_manager import DataManager
from utils.database import get_db_connection
import psycopg2

def get_available_advisors():
    """Get list of available advisors from current data"""
    try:
        df = DataManager.get_data()
        if 'advisor_name' in df.columns:
            advisors = sorted(df['advisor_name'].dropna().unique().tolist())
            return advisors
        else:
            return []
    except:
        return []

def add_student_to_database(student_data):
    """Add new student to the database"""
    try:
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate new student ID
        cursor.execute("SELECT COALESCE(MAX(student_id), 0) + 1 FROM students")
        new_student_id = cursor.fetchone()[0]
        
        # Get advisor_id from advisor_name
        cursor.execute("SELECT advisor_id FROM advisors WHERE advisor_name = %s", (student_data['advisor_name'],))
        advisor_result = cursor.fetchone()
        
        if not advisor_result:
            # Create new advisor if doesn't exist
            cursor.execute("SELECT COALESCE(MAX(advisor_id), 0) + 1 FROM advisors")
            new_advisor_id = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT INTO advisors (advisor_id, advisor_name) VALUES (%s, %s)",
                (new_advisor_id, student_data['advisor_name'])
            )
            advisor_id = new_advisor_id
        else:
            advisor_id = advisor_result[0]
        
        # Insert new student
        insert_query = """
        INSERT INTO students (
            student_id, student_name, program, department, 
            enrollment_date, defense_date, defense_status,
            advisor_id, advisor_name, research_area, publications
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            new_student_id,
            student_data['student_name'],
            student_data['program'],
            student_data['department'],
            student_data['enrollment_date'],
            student_data['defense_date'],
            student_data['defense_status'],
            advisor_id,
            student_data['advisor_name'],
            student_data.get('research_area', 'Educação'),
            student_data.get('publications', 0)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Clear session state data to force refresh
        if 'data' in st.session_state:
            del st.session_state['data']
        
        return True, f"Estudante {student_data['student_name']} adicionado com sucesso!"
        
    except Exception as e:
        return False, f"Erro ao adicionar estudante: {str(e)}"

def render_add_student_form():
    """Render the form to add a new student"""
    
    st.title("➕ Adicionar Novo Estudante")
    st.markdown("---")
    
    # Get available advisors
    available_advisors = get_available_advisors()
    
    with st.form("add_student_form"):
        st.subheader("Dados do Estudante")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input(
                "Nome do Estudante *",
                placeholder="Digite o nome completo do estudante",
                help="Nome completo do estudante"
            )
            
            program = st.selectbox(
                "Programa *",
                options=["Mestrado", "Doutorado"],
                help="Selecione o tipo de programa"
            )
            
            department = st.text_input(
                "Departamento *",
                value="PPGE",
                disabled=True,
                help="Departamento fixo: PPGE"
            )
            
            enrollment_date = st.date_input(
                "Data de Matrícula *",
                value=date.today(),
                min_value=date(2015, 1, 1),
                max_value=date.today(),
                help="Data de matrícula do estudante"
            )
        
        with col2:
            defense_date = st.date_input(
                "Data de Defesa",
                value=None,
                min_value=date(2015, 1, 1),
                max_value=date(2030, 12, 31),
                help="Data da defesa (deixe vazio se ainda não defendeu)"
            )
            
            defense_status = st.selectbox(
                "Status da Defesa *",
                options=["Pending", "Approved", "Rejected"],
                index=0,
                help="Status atual da defesa"
            )
            
            if available_advisors:
                advisor_name = st.selectbox(
                    "Nome do Orientador *",
                    options=available_advisors,
                    help="Selecione o orientador"
                )
            else:
                advisor_name = st.text_input(
                    "Nome do Orientador *",
                    placeholder="Digite o nome do orientador",
                    help="Nome do orientador"
                )
            
            research_area = st.text_input(
                "Área de Pesquisa",
                value="Educação",
                help="Área de pesquisa do estudante"
            )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "Adicionar Estudante",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validate required fields
            if not student_name.strip():
                st.error("Nome do estudante é obrigatório")
                return
            
            if not advisor_name.strip():
                st.error("Nome do orientador é obrigatório")
                return
            
            # Prepare student data
            student_data = {
                'student_name': student_name.strip(),
                'program': program,
                'department': department,
                'enrollment_date': enrollment_date,
                'defense_date': defense_date if defense_date else None,
                'defense_status': defense_status,
                'advisor_name': advisor_name.strip(),
                'research_area': research_area.strip() if research_area.strip() else 'Educação',
                'publications': 0
            }
            
            # Add student to database
            success, message = add_student_to_database(student_data)
            
            if success:
                st.success(message)
                st.balloons()
                
                # Show success message and option to add another
                st.info("Você pode visualizar o novo estudante na página de Gerador de Relatórios.")
                
                if st.button("Adicionar Outro Estudante", type="secondary"):
                    st.rerun()
            else:
                st.error(message)

def render_recent_students():
    """Show recently added students"""
    st.subheader("Estudantes Recentemente Adicionados")
    
    try:
        df = DataManager.get_data()
        
        if not df.empty:
            # Get the 5 most recent students by enrollment date
            recent_students = df.nlargest(5, 'enrollment_date')[
                ['student_name', 'program', 'enrollment_date', 'defense_status', 'advisor_name']
            ]
            
            st.dataframe(
                recent_students,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "student_name": "Nome",
                    "program": "Programa", 
                    "enrollment_date": "Data de Matrícula",
                    "defense_status": "Status da Defesa",
                    "advisor_name": "Orientador"
                }
            )
        else:
            st.info("Nenhum estudante encontrado na base de dados.")
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Main page content
def main():
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_add_student_form()
    
    with col2:
        render_recent_students()

if __name__ == "__main__":
    main()