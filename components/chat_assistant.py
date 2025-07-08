import streamlit as st
import pandas as pd
import json
import requests
from typing import Dict, List, Any
import time
import psycopg2
import os

def render_chat_assistant():
    """
    Render a chat assistant component that allows users to interact with their data
    using a free LLM API
    """
    st.subheader("💬 Assistente de Dados")
    st.markdown("Converse com seus dados! Faça perguntas sobre os indicadores, estatísticas e tendências.")
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Get current data for context
    from data.data_manager import DataManager
    df = DataManager.get_data()
    
    if df.empty:
        st.warning("Nenhum dado disponível. Importe dados primeiro para usar o assistente de chat.")
        return
    
    # Enhanced data summary for better context
    data_summary = generate_enhanced_data_summary(df)
    
    # Get faculty-student relationships for specialized queries
    faculty_data = get_faculty_student_data()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Faça uma pergunta sobre seus dados..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analisando seus dados..."):
                response = generate_llm_response(prompt, data_summary, df, faculty_data)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.chat_messages = []
        st.rerun()

def generate_enhanced_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a summary of the current dataset for context
    
    Parameters:
    - df: DataFrame containing the data
    
    Returns:
    - summary: Dictionary with data summary information
    """
    summary = {
        "total_records": len(df),
        "columns": list(df.columns),
        "date_range": {},
        "numeric_columns": [],
        "categorical_columns": [],
        "basic_stats": {},
        "faculty_info": {},
        "program_info": {},
        "student_info": {}
    }
    
    # Identify numeric and categorical columns
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            summary["numeric_columns"].append(col)
            col_data = df[col].dropna()
            if len(col_data) > 0:
                summary["basic_stats"][col] = {
                    "mean": float(col_data.mean()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "count": int(col_data.count())
                }
            else:
                summary["basic_stats"][col] = {
                    "mean": 0, "min": 0, "max": 0, "count": 0
                }
        else:
            summary["categorical_columns"].append(col)
            if df[col].dtype == 'object':
                unique_vals = df[col].dropna().unique()
                summary["basic_stats"][col] = {
                    "unique_count": len(unique_vals),
                    "top_values": list(unique_vals[:5]) if len(unique_vals) > 0 else []
                }
    
    # Check for date columns
    for col in df.columns:
        if 'date' in col.lower():
            try:
                date_series = pd.to_datetime(df[col], errors='coerce')
                if not date_series.isna().all():
                    summary["date_range"][col] = {
                        "start": str(date_series.min()),
                        "end": str(date_series.max())
                    }
            except:
                pass
    
    # Enhanced faculty information
    if 'advisor_name' in df.columns:
        faculty_counts = df['advisor_name'].value_counts()
        summary["faculty_info"] = {
            "total_advisors": len(faculty_counts),
            "advisor_student_counts": faculty_counts.to_dict(),
            "top_advisors": faculty_counts.head(5).to_dict(),
            "avg_students_per_advisor": faculty_counts.mean()
        }
    
    # Program information
    if 'program' in df.columns:
        program_counts = df['program'].value_counts()
        summary["program_info"] = {
            "total_programs": len(program_counts),
            "program_student_counts": program_counts.to_dict(),
            "programs_list": program_counts.index.tolist()
        }
    
    # Student information
    summary["student_info"] = {
        "total_students": len(df),
        "completed_defenses": len(df[df['defense_status'] == 'Approved']) if 'defense_status' in df.columns else 0,
        "pending_defenses": len(df[df['defense_status'] != 'Approved']) if 'defense_status' in df.columns else 0
    }
    
    return summary

def generate_llm_response(user_question: str, data_summary: Dict[str, Any], df: pd.DataFrame, faculty_data: Dict[str, Any] = None) -> str:
    """
    Generate a response using a free LLM API based on the user's question and data
    
    Parameters:
    - user_question: User's question
    - data_summary: Summary of the current dataset
    - df: DataFrame containing the data
    
    Returns:
    - response: Generated response from the LLM
    """
    try:
        # Build conversation context from chat history
        conversation_context = build_conversation_context()
        
        # First, try to answer with enhanced local data analysis (with context)
        local_response = analyze_question_locally_enhanced(user_question, data_summary, df, faculty_data, conversation_context)
        
        if local_response:
            return local_response
        
        # If local analysis isn't sufficient, try external LLM with enhanced context
        return call_free_llm_api_enhanced(user_question, data_summary, faculty_data, conversation_context)
        
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}. Tente reformular sua pergunta ou verifique se os dados estão carregados corretamente."

def get_faculty_student_data() -> Dict[str, Any]:
    """
    Get detailed faculty-student relationships from the database
    
    Returns:
    - Dictionary with faculty data and student counts
    """
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return {}
        
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()
        
        # Get faculty data from multiple tables
        faculty_data = {}
        
        # Try to get data from students table
        try:
            cursor.execute("""
                SELECT advisor_name, COUNT(*) as student_count 
                FROM students 
                WHERE advisor_name IS NOT NULL 
                GROUP BY advisor_name 
                ORDER BY student_count DESC
            """)
            
            results = cursor.fetchall()
            faculty_data['advisor_student_counts'] = {row[0]: row[1] for row in results}
            
        except Exception:
            # Table might not exist, continue
            pass
        
        # Try to get data from docentes_permanentes table
        try:
            cursor.execute("SELECT * FROM docentes_permanentes LIMIT 10")
            results = cursor.fetchall()
            if results:
                faculty_data['permanent_faculty'] = len(results)
        except Exception:
            pass
        
        # Try to get data from advisors table
        try:
            cursor.execute("SELECT advisor_name FROM advisors")
            results = cursor.fetchall()
            if results:
                faculty_data['registered_advisors'] = [row[0] for row in results]
        except Exception:
            pass
        
        cursor.close()
        connection.close()
        
        return faculty_data
        
    except Exception as e:
        return {}

def build_conversation_context() -> str:
    """
    Build conversation context from chat history
    
    Returns:
    - String with formatted conversation context
    """
    if "chat_messages" not in st.session_state or not st.session_state.chat_messages:
        return ""
    
    # Get the last 6 messages (3 exchanges) to avoid too much context
    recent_messages = st.session_state.chat_messages[-6:]
    
    context_parts = ["**Contexto da conversa anterior:**"]
    
    for i, message in enumerate(recent_messages):
        role = "Usuário" if message["role"] == "user" else "Assistente"
        content = message["content"]
        
        # Truncate very long messages
        if len(content) > 200:
            content = content[:200] + "..."
        
        context_parts.append(f"{role}: {content}")
    
    return "\n".join(context_parts) + "\n\n"

def analyze_question_locally_enhanced(user_question: str, data_summary: Dict[str, Any], df: pd.DataFrame, faculty_data: Dict[str, Any] = None, conversation_context: str = "") -> str:
    """
    Analyze simple questions using local data processing with conversation context
    
    Parameters:
    - user_question: User's question
    - data_summary: Summary of the current dataset
    - df: DataFrame containing the data
    - faculty_data: Additional faculty data from database
    - conversation_context: Context from previous conversation
    
    Returns:
    - response: Local analysis response or None if question is too complex
    """
    question_lower = user_question.lower()
    
    # Check for contextual references (pronouns, demonstratives)
    contextual_response = handle_contextual_questions(user_question, conversation_context, df, data_summary)
    if contextual_response:
        return contextual_response
    
    # Enhanced professor/advisor questions
    if any(word in question_lower for word in ['professor', 'orientador', 'docente', 'advisor']):
        # Check if asking for specific professor's student count
        if any(word in question_lower for word in ['quantos', 'total', 'número', 'alunos', 'estudantes']):
            
            # Try to extract professor name from question
            professor_name = extract_professor_name_from_question(user_question, df)
            
            if professor_name:
                # Get specific professor's student count
                if 'advisor_name' in df.columns:
                    student_count = len(df[df['advisor_name'].str.contains(professor_name, case=False, na=False)])
                    
                    if student_count > 0:
                        # Get details about the students
                        professor_students = df[df['advisor_name'].str.contains(professor_name, case=False, na=False)]
                        
                        response = f"**Professor {professor_name}** tem **{student_count}** aluno(s) orientado(s).\n\n"
                        
                        # Add more details if available
                        if 'defense_status' in df.columns:
                            approved = len(professor_students[professor_students['defense_status'] == 'Approved'])
                            pending = len(professor_students[professor_students['defense_status'] != 'Approved'])
                            response += f"• **{approved}** defesas aprovadas\n"
                            response += f"• **{pending}** defesas pendentes\n"
                        
                        if 'program' in df.columns:
                            programs = professor_students['program'].value_counts().to_dict()
                            response += f"• **Programas**: {', '.join([f'{prog}: {count}' for prog, count in programs.items()])}\n"
                        
                        return response
                    else:
                        return f"Não encontrei alunos orientados pelo professor **{professor_name}** no dataset atual."
            
            # General faculty statistics
            if 'advisor_name' in df.columns:
                faculty_stats = data_summary.get('faculty_info', {})
                
                if faculty_stats:
                    response = f"**Estatísticas dos Orientadores:**\n"
                    response += f"• Total de orientadores: **{faculty_stats.get('total_advisors', 0)}**\n"
                    response += f"• Média de alunos por orientador: **{faculty_stats.get('avg_students_per_advisor', 0):.1f}**\n\n"
                    
                    response += "**Top 5 Orientadores com mais alunos:**\n"
                    for advisor, count in faculty_stats.get('top_advisors', {}).items():
                        response += f"• {advisor}: **{count}** alunos\n"
                    
                    return response
    
    # Basic statistics questions
    if any(word in question_lower for word in ['quantos', 'total', 'número', 'count']):
        if 'estudantes' in question_lower or 'alunos' in question_lower:
            total_students = len(df)
            student_info = data_summary.get('student_info', {})
            
            response = f"**Total de estudantes:** {total_students}\n"
            if student_info:
                response += f"• Defesas aprovadas: **{student_info.get('completed_defenses', 0)}**\n"
                response += f"• Defesas pendentes: **{student_info.get('pending_defenses', 0)}**\n"
            
            return response
        
        if 'professores' in question_lower or 'docentes' in question_lower:
            if 'advisor_name' in df.columns:
                unique_advisors = df['advisor_name'].nunique()
                return f"Existem **{unique_advisors}** orientadores únicos no dataset."
        
        if 'programas' in question_lower:
            program_info = data_summary.get('program_info', {})
            if program_info:
                response = f"**Total de programas:** {program_info.get('total_programs', 0)}\n"
                response += "**Programas disponíveis:**\n"
                for program, count in program_info.get('program_student_counts', {}).items():
                    response += f"• {program}: **{count}** alunos\n"
                return response
    
    # Average/mean questions
    if any(word in question_lower for word in ['média', 'average', 'mean']):
        if 'tempo' in question_lower and 'defesa' in question_lower:
            if 'time_to_defense_days' in df.columns:
                avg_time = df['time_to_defense_days'].mean()
                if not pd.isna(avg_time):
                    return f"O tempo médio para defesa é de **{avg_time:.1f} dias** (aproximadamente {avg_time/365:.1f} anos)."
        
        if 'publicações' in question_lower or 'publications' in question_lower:
            if 'publications' in df.columns:
                avg_pubs = df['publications'].mean()
                if not pd.isna(avg_pubs):
                    return f"O número médio de publicações por estudante é **{avg_pubs:.1f}**."
    
    # Range/period questions
    if any(word in question_lower for word in ['período', 'range', 'anos']):
        date_info = []
        for col, date_range in data_summary.get("date_range", {}).items():
            date_info.append(f"**{col}**: {date_range['start']} até {date_range['end']}")
        
        if date_info:
            return f"Períodos dos dados:\n" + "\n".join(date_info)
    
    # Column information
    if any(word in question_lower for word in ['colunas', 'campos', 'dados disponíveis']):
        columns = data_summary.get("columns", [])
        return f"**Dados disponíveis ({len(columns)} campos):**\n" + "\n".join([f"• {col}" for col in columns])
    
    # Enhanced program and trend analysis
    if any(word in question_lower for word in ['programa', 'program', 'curso']):
        program_info = data_summary.get('program_info', {})
        if program_info and 'qual' in question_lower:
            response = "**Análise dos Programas:**\n"
            
            # Find program with most students
            program_counts = program_info.get('program_student_counts', {})
            if program_counts:
                max_program = max(program_counts, key=program_counts.get)
                response += f"• Programa com mais alunos: **{max_program}** ({program_counts[max_program]} alunos)\n"
                
                # Calculate success rates if available
                if 'defense_status' in df.columns and 'program' in df.columns:
                    for program in program_counts.keys():
                        program_data = df[df['program'] == program]
                        if len(program_data) > 0:
                            success_rate = len(program_data[program_data['defense_status'] == 'Approved']) / len(program_data) * 100
                            response += f"• {program}: Taxa de sucesso **{success_rate:.1f}%**\n"
            
            return response
    
    # List all advisors question
    if any(word in question_lower for word in ['lista', 'todos', 'orientadores', 'professores']):
        if 'advisor_name' in df.columns:
            faculty_info = data_summary.get('faculty_info', {})
            advisor_counts = faculty_info.get('advisor_student_counts', {})
            
            if advisor_counts:
                response = "**Lista de Orientadores e seus Alunos:**\n"
                # Sort by student count (descending)
                sorted_advisors = sorted(advisor_counts.items(), key=lambda x: x[1], reverse=True)
                
                for advisor, count in sorted_advisors:
                    response += f"• **{advisor}**: {count} aluno(s)\n"
                
                return response
    
    return None

def handle_contextual_questions(user_question: str, conversation_context: str, df: pd.DataFrame, data_summary: Dict[str, Any]) -> str:
    """
    Handle questions that reference previous conversation context
    
    Parameters:
    - user_question: Current user's question
    - conversation_context: Context from previous messages
    - df: DataFrame containing the data
    - data_summary: Summary of the current dataset
    
    Returns:
    - Contextual response or None if not applicable
    """
    question_lower = user_question.lower()
    
    # Check for pronouns and references
    contextual_indicators = [
        'ele', 'ela', 'dele', 'dela', 'desse', 'dessa', 'deste', 'desta',
        'esse', 'essa', 'este', 'esta', 'aquele', 'aquela', 'mesmo',
        'mesma', 'anterior', 'mencionado', 'citado', 'falou', 'disse'
    ]
    
    if any(indicator in question_lower for indicator in contextual_indicators):
        
        # Extract professor names mentioned in previous context
        if conversation_context and any(word in question_lower for word in ['quantos', 'alunos', 'estudantes', 'orientandos']):
            
            # Look for professor names in conversation context
            import re
            professor_pattern = r'[Pp]rofessor\s+([A-ZÁÊÇÕ][a-záêçõ\s]+)'
            matches = re.findall(professor_pattern, conversation_context)
            
            if matches:
                professor_name = matches[-1].strip()  # Get the most recent mention
                
                # Get information about this professor
                if 'advisor_name' in df.columns:
                    professor_students = df[df['advisor_name'].str.contains(professor_name, case=False, na=False)]
                    
                    if len(professor_students) > 0:
                        student_count = len(professor_students)
                        response = f"Baseado na conversa anterior sobre o **Professor {professor_name}**, ele tem **{student_count}** aluno(s) orientado(s).\n\n"
                        
                        # Add additional context based on the specific question
                        if 'programa' in question_lower or 'curso' in question_lower:
                            if 'program' in df.columns:
                                programs = professor_students['program'].value_counts().to_dict()
                                response += f"**Distribuição por programa:**\n"
                                for prog, count in programs.items():
                                    response += f"• {prog}: {count} aluno(s)\n"
                        
                        elif 'defesa' in question_lower or 'aprovad' in question_lower:
                            if 'defense_status' in df.columns:
                                approved = len(professor_students[professor_students['defense_status'] == 'Approved'])
                                pending = len(professor_students[professor_students['defense_status'] != 'Approved'])
                                response += f"**Status das defesas:**\n"
                                response += f"• Aprovadas: {approved}\n"
                                response += f"• Pendentes: {pending}\n"
                        
                        elif 'tempo' in question_lower:
                            if 'time_to_defense_days' in df.columns:
                                avg_time = professor_students['time_to_defense_days'].mean()
                                if not pd.isna(avg_time):
                                    response += f"**Tempo médio para defesa:** {avg_time:.1f} dias ({avg_time/365:.1f} anos)\n"
                        
                        return response
    
    # Handle comparative questions referring to previous responses
    if any(word in question_lower for word in ['comparar', 'diferença', 'melhor', 'pior', 'maior', 'menor']):
        if conversation_context:
            # Look for multiple professors mentioned in context
            import re
            professor_pattern = r'[Pp]rofessor\s+([A-ZÁÊÇÕ][a-záêçõ\s]+)'
            matches = re.findall(professor_pattern, conversation_context)
            
            if len(matches) >= 2:
                # Compare the professors mentioned
                prof1, prof2 = matches[-2].strip(), matches[-1].strip()
                
                if 'advisor_name' in df.columns:
                    prof1_count = len(df[df['advisor_name'].str.contains(prof1, case=False, na=False)])
                    prof2_count = len(df[df['advisor_name'].str.contains(prof2, case=False, na=False)])
                    
                    response = f"**Comparação entre os professores mencionados:**\n"
                    response += f"• Professor {prof1}: **{prof1_count}** alunos\n"
                    response += f"• Professor {prof2}: **{prof2_count}** alunos\n\n"
                    
                    if prof1_count > prof2_count:
                        response += f"O Professor {prof1} orienta mais alunos ({prof1_count - prof2_count} a mais)."
                    elif prof2_count > prof1_count:
                        response += f"O Professor {prof2} orienta mais alunos ({prof2_count - prof1_count} a mais)."
                    else:
                        response += "Ambos orientam o mesmo número de alunos."
                    
                    return response
    
    # Handle follow-up questions about data mentioned before
    if any(word in question_lower for word in ['detalhe', 'detalhes', 'mais', 'específico', 'completo']):
        if conversation_context and ('orientador' in conversation_context.lower() or 'professor' in conversation_context.lower()):
            return "Com base na conversa anterior, que tipo de detalhes específicos você gostaria de saber? Posso fornecer informações sobre:\n• Distribuição por programas\n• Status das defesas\n• Tempo médio para defesa\n• Comparações com outros orientadores\n\nPor favor, seja mais específico sobre o que deseja saber."
    
    return None

def extract_professor_name_from_question(question: str, df: pd.DataFrame) -> str:
    """
    Try to extract a professor name from the user's question
    
    Parameters:
    - question: User's question
    - df: DataFrame containing the data
    
    Returns:
    - Professor name if found, otherwise None
    """
    if 'advisor_name' not in df.columns:
        return None
    
    # Get all advisor names
    advisor_names = df['advisor_name'].dropna().unique()
    
    # Try to find advisor name in question
    question_lower = question.lower()
    
    # Check for direct matches or partial matches
    for advisor in advisor_names:
        if advisor and len(advisor) > 2:  # Avoid very short names
            # Check if advisor name (or significant part) is in question
            advisor_parts = advisor.lower().split()
            
            # Check for last name matches (usually more distinctive)
            for part in advisor_parts:
                if len(part) > 3 and part in question_lower:
                    return advisor
    
    return None

def call_free_llm_api_enhanced(user_question: str, data_summary: Dict[str, Any], faculty_data: Dict[str, Any] = None, conversation_context: str = "") -> str:
    """
    Call a free LLM API to generate a response
    
    Parameters:
    - user_question: User's question
    - data_summary: Summary of the current dataset
    
    Returns:
    - response: Response from the LLM API
    """
    # Try multiple free API options
    
    # Option 1: Try Hugging Face if API key is available
    try:
        if hasattr(st, 'secrets') and 'HUGGINGFACE_API_KEY' in st.secrets:
            return call_huggingface_api_enhanced(user_question, data_summary, faculty_data, conversation_context, st.secrets["HUGGINGFACE_API_KEY"])
    except:
        pass
    
    # Option 2: Try using a free public endpoint (no API key required)
    try:
        return call_free_public_llm_enhanced(user_question, data_summary, faculty_data, conversation_context)
    except:
        pass
    
    # Fallback: Provide information about setting up API access
    return """
    Para usar o assistente avançado de IA, você pode configurar uma das seguintes opções gratuitas:
    
    **Opção 1 - Hugging Face (Recomendado):**
    1. Acesse https://huggingface.co/
    2. Crie uma conta gratuita
    3. Vá em Settings > Access Tokens
    4. Crie um novo token
    5. Configure HUGGINGFACE_API_KEY nos secrets do Streamlit
    
    **Opção 2 - OpenAI (Gratuito com limitações):**
    1. Acesse https://platform.openai.com/
    2. Crie uma conta e obtenha créditos gratuitos
    3. Configure OPENAI_API_KEY nos secrets
    
    **Enquanto isso, posso responder perguntas básicas sobre seus dados usando análise local.**
    Exemplos: "Quantos estudantes temos?", "Qual a média de tempo para defesa?", "Que dados estão disponíveis?"
    """

def call_huggingface_api_enhanced(user_question: str, data_summary: Dict[str, Any], faculty_data: Dict[str, Any], conversation_context: str, api_key: str) -> str:
    """Call Hugging Face API with the provided API key"""
    try:
        # Prepare enhanced context
        context = f"""
        Contexto detalhado dos dados acadêmicos:
        - Total de registros de estudantes: {data_summary['total_records']}
        - Colunas disponíveis: {', '.join(data_summary['columns'])}
        - Colunas numéricas: {', '.join(data_summary['numeric_columns'])}
        - Colunas categóricas: {', '.join(data_summary['categorical_columns'])}
        
        Informações dos orientadores:
        - Total de orientadores: {data_summary.get('faculty_info', {}).get('total_advisors', 0)}
        - Media de alunos por orientador: {data_summary.get('faculty_info', {}).get('avg_students_per_advisor', 0):.1f}
        - Top orientadores: {data_summary.get('faculty_info', {}).get('top_advisors', {})}
        
        Informações dos programas:
        - Total de programas: {data_summary.get('program_info', {}).get('total_programs', 0)}
        - Distribuição por programa: {data_summary.get('program_info', {}).get('program_student_counts', {})}
        
        Informações dos estudantes:
        - Defesas aprovadas: {data_summary.get('student_info', {}).get('completed_defenses', 0)}
        - Defesas pendentes: {data_summary.get('student_info', {}).get('pending_defenses', 0)}
        """
        
        if faculty_data:
            context += f"""
        
        Dados adicionais dos orientadores:
        - Contagem de alunos por orientador: {faculty_data.get('advisor_student_counts', {})}
        """
        
        # Prepare prompt with conversation context
        prompt = f"""
        Você é um assistente especializado em análise de dados acadêmicos de programas de pós-graduação.
        
        {context}
        
        {conversation_context}
        
        Pergunta atual do usuário: {user_question}
        
        Responda de forma clara e objetiva em português, considerando o contexto da conversa anterior e focando nos dados disponíveis. Se a pergunta fizer referência a informações mencionadas anteriormente, conecte com o contexto da conversa.
        """
        
        # Call Hugging Face API
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "Desculpe, não consegui gerar uma resposta adequada.")
            else:
                return "Desculpe, não consegui gerar uma resposta adequada."
        else:
            return f"Erro na API: {response.status_code}. Tente novamente em alguns momentos."
            
    except requests.exceptions.Timeout:
        return "A consulta está demorando muito. Tente fazer uma pergunta mais específica."
    except Exception as e:
        return f"Erro ao conectar com o serviço de IA: {str(e)}"

def call_free_public_llm_enhanced(user_question: str, data_summary: Dict[str, Any], faculty_data: Dict[str, Any] = None, conversation_context: str = "") -> str:
    """Try to call a free public LLM endpoint (no API key required)"""
    # For now, this will use enhanced local analysis
    # In the future, this could connect to other free services
    return generate_enhanced_local_response_v2(user_question, data_summary, faculty_data, conversation_context)

def generate_enhanced_local_response_v2(user_question: str, data_summary: Dict[str, Any], faculty_data: Dict[str, Any] = None, conversation_context: str = "") -> str:
    """Generate an enhanced response using local analysis"""
    question_lower = user_question.lower()
    
    # More sophisticated pattern matching
    response_parts = []
    
    # Check for data overview questions
    if any(word in question_lower for word in ['visão geral', 'overview', 'resumo', 'summary']):
        response_parts.append(f"**Visão Geral dos Dados Acadêmicos:**")
        response_parts.append(f"• Total de estudantes: {data_summary['total_records']}")
        response_parts.append(f"• Campos disponíveis: {len(data_summary['columns'])}")
        response_parts.append(f"• Dados numéricos: {len(data_summary['numeric_columns'])} campos")
        response_parts.append(f"• Dados categóricos: {len(data_summary['categorical_columns'])} campos")
        
        # Add faculty overview
        faculty_info = data_summary.get('faculty_info', {})
        if faculty_info:
            response_parts.append(f"• Total de orientadores: {faculty_info.get('total_advisors', 0)}")
            response_parts.append(f"• Média de alunos por orientador: {faculty_info.get('avg_students_per_advisor', 0):.1f}")
        
        # Add program overview
        program_info = data_summary.get('program_info', {})
        if program_info:
            response_parts.append(f"• Total de programas: {program_info.get('total_programs', 0)}")
        
        # Add student status overview
        student_info = data_summary.get('student_info', {})
        if student_info:
            response_parts.append(f"• Defesas aprovadas: {student_info.get('completed_defenses', 0)}")
            response_parts.append(f"• Defesas pendentes: {student_info.get('pending_defenses', 0)}")
    
    # Check for statistical questions
    if any(word in question_lower for word in ['estatísticas', 'statistics', 'números', 'dados']):
        if data_summary['basic_stats']:
            response_parts.append("**Estatísticas Principais:**")
            for col, stats in data_summary['basic_stats'].items():
                if col in data_summary['numeric_columns']:
                    response_parts.append(f"• {col}: média={stats.get('mean', 0):.2f}, min={stats.get('min', 0)}, max={stats.get('max', 0)}")
                elif 'unique_count' in stats:
                    response_parts.append(f"• {col}: {stats['unique_count']} valores únicos")
    
    # Check for date range questions
    if any(word in question_lower for word in ['período', 'range', 'datas', 'tempo']):
        if data_summary.get('date_range'):
            response_parts.append("**Períodos dos Dados:**")
            for col, date_range in data_summary['date_range'].items():
                response_parts.append(f"• {col}: {date_range['start']} até {date_range['end']}")
    
    if response_parts:
        return "\n".join(response_parts)
    
    # Enhanced fallback with faculty-specific examples
    base_examples = """
    Posso ajudá-lo a analisar seus dados acadêmicos! Aqui estão algumas perguntas que posso responder:
    
    **Informações sobre orientadores:**
    • "Quantos alunos o professor [nome] tem?"
    • "Qual orientador tem mais alunos?"
    • "Lista todos os orientadores"
    • "Quantos orientadores temos?"
    
    **Informações sobre estudantes:**
    • "Quantos estudantes temos no total?"
    • "Quantas defesas foram aprovadas?"
    • "Qual a média de tempo para defesa?"
    
    **Informações sobre programas:**
    • "Quantos programas temos?"
    • "Qual programa tem mais alunos?"
    • "Como estão distribuídos os alunos por programa?"
    
    **Análises gerais:**
    • "Dê uma visão geral dos dados"
    • "Que dados estão disponíveis?"
    • "Qual é o período dos dados?"
    
    **Perguntas contextuais (baseadas na conversa):**
    • "E ele?" (referindo-se ao último professor mencionado)
    • "Compare com o anterior"
    • "Dê mais detalhes"
    • "Qual a diferença?"
    
    **Exemplo específico:** "Quantos alunos o professor Silva tem?"
    """
    
    # Add contextual suggestions if there's conversation history
    if conversation_context:
        contextual_addition = "\n**💡 Dica:** Como temos uma conversa em andamento, você pode fazer perguntas de acompanhamento como 'E os outros professores?', 'Compare com ele', ou 'Dê mais detalhes sobre isso'."
        return base_examples + contextual_addition
    
    return base_examples

def render_chat_help():
    """
    Render help section for the chat assistant
    """
    with st.expander("💡 Como usar o Assistente de Dados"):
        st.markdown("""
        **Exemplos de perguntas que você pode fazer:**
        
        👨‍🏫 **Perguntas sobre orientadores:**
        - "Quantos alunos o professor [nome] tem?"
        - "Qual orientador tem mais alunos?"
        - "Lista todos os orientadores e seus alunos"
        - "Quantos orientadores temos no total?"
        
        📊 **Estatísticas básicas:**
        - "Quantos estudantes temos no total?"
        - "Qual é a média de tempo para defesa?"
        - "Quantas defesas foram aprovadas?"
        - "Quantas defesas estão pendentes?"
        
        📈 **Análises por programa:**
        - "Qual programa tem mais alunos?"
        - "Como estão distribuídos os alunos por programa?"
        - "Qual programa tem melhor taxa de conclusão?"
        
        🔍 **Informações gerais:**
        - "Dê uma visão geral dos dados"
        - "Que dados estão disponíveis?"
        - "Qual é o período coberto pelos dados?"
        
        **💬 Conversas contextuais:**
        - "E ele?" (referindo-se ao último professor mencionado)
        - "Compare com o anterior"
        - "Dê mais detalhes sobre isso"
        - "Qual a diferença entre eles?"
        
        **Dicas:**
        - Para perguntas sobre professores específicos, use o nome do professor
        - Você pode fazer perguntas de acompanhamento baseadas nas respostas anteriores
        - Use pronomes como "ele", "ela", "esse", "essa" para se referir a informações anteriores
        - Seja específico em suas perguntas
        
        **Exemplos:**
        - "Quantos alunos o professor Silva tem?"
        - "E o professor Santos?" (após perguntar sobre Silva)
        - "Compare os dois professores"
        """)