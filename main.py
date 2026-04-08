import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SST OS Pro", page_icon="🛡️", layout="wide")

# --- ESTADO GLOBAL ---
if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False,
        'user_nome': '',
        'nivel': 0,
        'config_url': '',
        'config_id': '',
        'ai_key': ''
    })

# --- FUNÇÃO DE LOGIN MELHORADA ---
def login_sistema():
    st.sidebar.title("🔐 Acesso ao Sistema")
    u_input = st.sidebar.text_input("Usuário")
    p_input = st.sidebar.text_input("Senha", type="password")
    
    if st.sidebar.button("Entrar"):
        # Dicionário de usuários (Posteriormente você pode ler da aba T_USR)
        usuarios = {
            "desenvolvedor": {"senha": "Mm88918675@@", "nivel": 3, "nome": "Desenvolvedor"},
            "tst01": {"senha": "123", "nivel": 2, "nome": "Técnico de Campo"},
            "gestor": {"senha": "999", "nivel": 1, "nome": "Gerente de Operações"}
        }
        
        if u_input in usuarios and usuarios[u_input]["senha"] == p_input:
            st.session_state.update({
                'autenticado': True,
                'user_nome': usuarios[u_input]["nome"],
                'nivel': usuarios[u_input]["nivel"]
            })
            st.sidebar.success(f"Logado como {usuarios[u_input]['nome']}")
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

# Execução do Login
if not st.session_state.autenticado:
    login_sistema()
    st.info("Por favor, faça login na barra lateral para acessar as ferramentas de segurança.")
    st.stop()

# --- MENU DINÂMICO POR NÍVEL ---
# Nível 1 vê apenas Home. Nível 2 vê Home, Inspeções e EPI. Nível 3 vê tudo.
opcoes = ["🏠 Home"]
if st.session_state.nivel >= 2:
    opcoes.extend(["📝 Inspeções", "📦 Entrega de EPI"])
if st.session_state.nivel == 3:
    opcoes.append("🛠️ Configurações Dev")

escolha = st.sidebar.radio("Navegar", opcoes)
st.sidebar.divider()
if st.sidebar.button("Sair"):
    st.session_state.autenticado = False
    st.rerun()

# --- FUNÇÃO DE PERSISTÊNCIA ---
def salvar_dados(aba, nova_linha):
    if not st.session_state.config_url:
        st.error("Configurações de banco de dados ausentes.")
        return
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_antigo = conn.read(spreadsheet=st.session_state.config_url, worksheet=aba)
        df_novo = pd.concat([df_antigo, pd.DataFrame([nova_linha])], ignore_index=True)
        conn.update(spreadsheet=st.session_state.config_url, worksheet=aba, data=df_novo)
        st.balloons()
        st.success("Dados registrados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# --- TELAS ---

if escolha == "🏠 Home":
    st.title(f"Bem-vindo, {st.session_state.user_nome}!")
    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Status do Sistema", "ONLINE")
    c2.metric("Sua Permissão", f"Nível {st.session_state.nivel}")
    c3.metric("Banco de Dados", "Conectado" if st.session_state.config_id else "Pendente")

elif escolha == "📝 Inspeções":
    st.title("Inspeções de Segurança")
    if st.session_state.nivel < 2:
        st.error("Seu nível não permite registros.")
    else:
        with st.form("ins_form"):
            c1, c2 = st.columns(2)
            id_i = c1.text_input("Cód", placeholder="I01")
            local = c2.text_input("Setor")
            status = st.radio("Conformidade", ["C", "N"])
            obs = st.text_area("Observações")
            if st.form_submit_button("Salvar Registro"):
                salvar_dados("T_INS", {"id": id_i, "dt": pd.Timestamp.now().strftime('%d/%m/%Y'), "lc": local, "st": status, "ob": obs})

elif escolha == "📦 Entrega de EPI":
    st.title("Controle de EPIs")
    if st.session_state.nivel < 2:
        st.error("Acesso restrito.")
    else:
        with st.form("epi_form"):
            id_e = st.text_input("ID", placeholder="E01")
            colab = st.text_input("Colaborador")
            ca = st.text_input("CA")
            if st.form_submit_button("Registrar Entrega"):
                salvar_dados("T_EPI", {"id": id_e, "cb": colab, "ca": ca, "de": pd.Timestamp.now().strftime('%d/%m/%Y')})

elif escolha == "🛠️ Configurações Dev":
    st.title("Painel Administrativo")
    st.session_state.config_url = st.text_input("URL da Planilha", value=st.session_state.config_url)
    st.session_state.config_id = st.text_input("ID da Planilha", value=st.session_state.config_id)
    st.session_state.ai_key = st.text_input("Chave API IA", value=st.session_state.ai_key, type="password")
