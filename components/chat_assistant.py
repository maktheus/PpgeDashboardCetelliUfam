import streamlit as st
import pandas as pd
import json
import requests
from typing import Dict, List, Any
import time

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
    
    # Data summary for context
    data_summary = generate_data_summary(df)
    
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
                response = generate_llm_response(prompt, data_summary, df)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.chat_messages = []
        st.rerun()

def generate_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
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
        "basic_stats": {}
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
    
    return summary

def generate_llm_response(user_question: str, data_summary: Dict[str, Any], df: pd.DataFrame) -> str:
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
        # First, try to answer with local data analysis
        local_response = analyze_question_locally(user_question, data_summary, df)
        
        if local_response:
            return local_response
        
        # If local analysis isn't sufficient, try external LLM
        return call_free_llm_api(user_question, data_summary)
        
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}. Tente reformular sua pergunta ou verifique se os dados estão carregados corretamente."

def analyze_question_locally(user_question: str, data_summary: Dict[str, Any], df: pd.DataFrame) -> str:
    """
    Analyze simple questions using local data processing
    
    Parameters:
    - user_question: User's question
    - data_summary: Summary of the current dataset
    - df: DataFrame containing the data
    
    Returns:
    - response: Local analysis response or None if question is too complex
    """
    question_lower = user_question.lower()
    
    # Basic statistics questions
    if any(word in question_lower for word in ['quantos', 'total', 'número', 'count']):
        if 'estudantes' in question_lower or 'alunos' in question_lower:
            total_students = len(df)
            return f"Existem **{total_students}** registros de estudantes no dataset atual."
        
        if 'professores' in question_lower or 'docentes' in question_lower:
            if 'advisor_name' in df.columns:
                unique_advisors = df['advisor_name'].nunique()
                return f"Existem **{unique_advisors}** orientadores únicos no dataset."
        
        if 'programas' in question_lower:
            if 'program' in df.columns:
                unique_programs = df['program'].nunique()
                programs_list = df['program'].unique().tolist()
                return f"Existem **{unique_programs}** programas: {', '.join(programs_list)}"
    
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
    
    return None

def call_free_llm_api(user_question: str, data_summary: Dict[str, Any]) -> str:
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
            return call_huggingface_api(user_question, data_summary, st.secrets["HUGGINGFACE_API_KEY"])
    except:
        pass
    
    # Option 2: Try using a free public endpoint (no API key required)
    try:
        return call_free_public_llm(user_question, data_summary)
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

def call_huggingface_api(user_question: str, data_summary: Dict[str, Any], api_key: str) -> str:
    """Call Hugging Face API with the provided API key"""
    try:
        # Prepare context
        context = f"""
        Contexto dos dados:
        - Total de registros: {data_summary['total_records']}
        - Colunas disponíveis: {', '.join(data_summary['columns'])}
        - Colunas numéricas: {', '.join(data_summary['numeric_columns'])}
        - Colunas categóricas: {', '.join(data_summary['categorical_columns'])}
        """
        
        # Prepare prompt
        prompt = f"""
        Você é um assistente especializado em análise de dados acadêmicos de programas de pós-graduação.
        
        {context}
        
        Pergunta do usuário: {user_question}
        
        Responda de forma clara e objetiva em português, focando nos dados disponíveis.
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

def call_free_public_llm(user_question: str, data_summary: Dict[str, Any]) -> str:
    """Try to call a free public LLM endpoint (no API key required)"""
    # For now, this will use enhanced local analysis
    # In the future, this could connect to other free services
    return generate_enhanced_local_response(user_question, data_summary)

def generate_enhanced_local_response(user_question: str, data_summary: Dict[str, Any]) -> str:
    """Generate an enhanced response using local analysis"""
    question_lower = user_question.lower()
    
    # More sophisticated pattern matching
    response_parts = []
    
    # Check for data overview questions
    if any(word in question_lower for word in ['visão geral', 'overview', 'resumo', 'summary']):
        response_parts.append(f"**Visão Geral dos Dados:**")
        response_parts.append(f"• Total de registros: {data_summary['total_records']}")
        response_parts.append(f"• Campos disponíveis: {len(data_summary['columns'])}")
        response_parts.append(f"• Dados numéricos: {len(data_summary['numeric_columns'])} campos")
        response_parts.append(f"• Dados categóricos: {len(data_summary['categorical_columns'])} campos")
    
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
    
    # Fallback to suggesting specific questions
    return """
    Posso ajudá-lo a analisar seus dados! Aqui estão algumas perguntas que posso responder:
    
    **Informações básicas:**
    • "Quantos registros temos?"
    • "Que dados estão disponíveis?"
    • "Qual é o período dos dados?"
    
    **Análises específicas:**
    • "Quantos estudantes temos?"
    • "Qual a média de tempo para defesa?"
    • "Quantos orientadores únicos existem?"
    
    Faça uma pergunta específica sobre seus dados!
    """

def render_chat_help():
    """
    Render help section for the chat assistant
    """
    with st.expander("💡 Como usar o Assistente de Dados"):
        st.markdown("""
        **Exemplos de perguntas que você pode fazer:**
        
        📊 **Estatísticas básicas:**
        - "Quantos estudantes temos no total?"
        - "Qual é a média de tempo para defesa?"
        - "Quantas publicações os estudantes têm em média?"
        
        📈 **Tendências e comparações:**
        - "Qual programa tem melhor taxa de conclusão?"
        - "Como está evoluindo o número de defesas ao longo dos anos?"
        - "Quais são os orientadores mais produtivos?"
        
        🔍 **Informações dos dados:**
        - "Que dados estão disponíveis?"
        - "Qual é o período coberto pelos dados?"
        - "Quantos programas diferentes temos?"
        
        **Dicas:**
        - Seja específico em suas perguntas
        - Use termos relacionados aos seus dados
        - Se não entender a resposta, reformule a pergunta
        """)