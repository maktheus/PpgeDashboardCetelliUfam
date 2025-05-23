import pyotp
import base64
import os
import json
from datetime import datetime, timedelta

# Chave secreta para geração de OTP - em produção, deve ser armazenada de forma segura
# Aqui usamos uma chave fixa para demonstração, mas em produção deve ser armazenada em variáveis de ambiente
SECRET_KEY = os.environ.get("OTP_SECRET_KEY", "PPGEEDASHBOARD2023")

def generate_totp_secret():
    """Gera uma chave secreta para TOTP"""
    return pyotp.random_base32()

def get_totp_uri(name, issuer_name="PPGEE Dashboard"):
    """Retorna a URI para configuração do TOTP"""
    secret = base64.b32encode(SECRET_KEY.encode()).decode('utf-8')
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=name, issuer_name=issuer_name)

def verify_totp(token):
    """Verifica se o token TOTP é válido"""
    try:
        # Usando a mesma chave secreta que foi usada para gerar o QR code
        secret = base64.b32encode(SECRET_KEY.encode()).decode('utf-8')
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    except:
        return False

def get_current_totp():
    """Retorna o TOTP atual para fins de depuração"""
    secret = base64.b32encode(SECRET_KEY.encode()).decode('utf-8')
    totp = pyotp.TOTP(secret)
    return totp.now()

def is_authenticated():
    """Verifica se o usuário está autenticado"""
    import streamlit as st
    return st.session_state.get('authenticated', False)

def authenticate():
    """Define o estado de autenticação como verdadeiro"""
    import streamlit as st
    st.session_state.authenticated = True
    st.session_state.auth_time = datetime.now()

def logout():
    """Remove o estado de autenticação"""
    import streamlit as st
    st.session_state.authenticated = False
    if 'auth_time' in st.session_state:
        del st.session_state.auth_time

def check_auth_expiry(expiry_minutes=30):
    """Verifica se a autenticação expirou"""
    import streamlit as st
    if not is_authenticated():
        return False
    
    auth_time = st.session_state.get('auth_time')
    if not auth_time:
        logout()
        return False
    
    # Verificar se passou o tempo de expiração
    if datetime.now() > auth_time + timedelta(minutes=expiry_minutes):
        logout()
        return False
    
    return True

def require_authentication(page_function):
    """Decorator para páginas que requerem autenticação"""
    def wrapper(*args, **kwargs):
        import streamlit as st
        
        if not check_auth_expiry():
            show_auth_screen()
        else:
            # Exibe opção de logout
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.sidebar.info("Autenticado como Administrador")
            with col2:
                if st.sidebar.button("Logout"):
                    logout()
                    st.rerun()
            
            # Renderiza a página protegida
            page_function(*args, **kwargs)
    
    return wrapper

def show_auth_screen():
    """Exibe tela de autenticação com TOTP"""
    import streamlit as st
    import qrcode
    from io import BytesIO
    from PIL import Image
    
    st.title("🔐 Acesso Restrito: Gerenciamento de Dados")
    
    st.write("Esta seção é restrita e requer autenticação por código de verificação.")
    
    # Exibir instruções
    with st.expander("Instruções para Autenticação", expanded=True):
        st.write("""
        1. Para acessar esta página, você precisa ter um aplicativo de autenticação como Google Authenticator, 
           Authy ou Microsoft Authenticator.
        2. Escaneie o QR Code abaixo OU configure manualmente usando a chave secreta.
        3. Digite o código de 6 dígitos fornecido pelo aplicativo para acessar a página.
        """)
        
        # Gerar QR Code
        totp_uri = get_totp_uri("PPGE Dashboard Admin", "PPGE Dashboard")
        
        # Criar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Converter para imagem
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter PIL Image para bytes
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Exibir QR Code
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img_buffer, caption="QR Code para configurar autenticador", width=250)
        
        st.markdown("---")
        
        # Chave para configuração manual
        totp_key = base64.b32encode(SECRET_KEY.encode()).decode('utf-8')
        st.markdown(f"""
        #### Configuração Manual (caso não consiga escanear o QR Code):
        
        **Chave Secreta para inserir manualmente:**
        
        ```
        {totp_key}
        ```
        
        **Links para Download dos Aplicativos:**
        - [Google Authenticator (Android)](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)
        - [Google Authenticator (iOS)](https://apps.apple.com/app/google-authenticator/id388497605)
        - [Microsoft Authenticator](https://www.microsoft.com/pt-br/security/mobile-authenticator-app)
        - [Authy](https://authy.com/download/)
        """)
    
    # Formulário de autenticação
    with st.form("auth_form"):
        token = st.text_input("Código de Verificação (6 dígitos)", max_chars=6, placeholder="000000")
        submitted = st.form_submit_button("🔓 Verificar Código", use_container_width=True)
        
        if submitted:
            if verify_totp(token):
                authenticate()
                st.success("Autenticação bem sucedida! Redirecionando...")
                st.rerun()
            else:
                st.error("Código inválido. Tente novamente.")
    
    # Para fins de teste/depuração - exibir código atual
    if st.checkbox("Exibir código atual para testes"):
        current_code = get_current_totp()
        st.code(f"Código atual: {current_code}")
        st.warning("Esta opção deve ser removida em ambiente de produção!")