import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SST OS Pro", page_icon="🛡️", layout="wide")

# --- ESTADO GLOBAL ---
if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False,
        'nivel': 0,
        'config_url': '',
        'config_id': '',
        'ai_key': ''
    })

# --- LOGIN (Sidebar) ---
with st.sidebar:
    if not st.session_state.autenticado:
        st.title("🔐 Acesso")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "dev" and p == "admin": # Altere aqui suas credenciais
                st.session_state.update({'autenticado': True, 'nivel': 3})
                st.rerun()
    else:
        st.write(f"Usuário logado (Nível {st.session_state.nivel})")
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()

if not st.session_state.autenticado:
    st.warning("Acesse com seu usuário e senha na lateral.")
    st.stop()

# --- MENU ---
menu = ["Home", "Inspeções (NRs)", "Entrega de EPI"]
if st.session_state.nivel == 3:
    menu.append("🛠️ Configurações Dev")

escolha = st.sidebar.radio("Navegar", menu)

# --- FUNÇÃO PARA SALVAR (SQL-Like) ---
def salvar_dados(aba, nova_linha):
    if not st.session_state.config_url:
        st.error("Erro: URL da planilha não configurada no Painel Dev!")
        return
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Lê dados atuais
        df_antigo = conn.read(spreadsheet=st.session_state.config_url, worksheet=aba)
        # Adiciona nova linha
        df_novo = pd.concat([df_antigo, pd.DataFrame([nova_linha])], ignore_index=True)
        # Atualiza a planilha
        conn.update(spreadsheet=st.session_state.config_url, worksheet=aba, data=df_novo)
        st.success("Dados enviados com sucesso para a planilha!")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

# --- TELAS ---

if escolha == "Home":
    st.title("🏠 Painel de Controle SST")
    st.markdown(f"""
    Bem-vindo ao sistema de gestão.
    * **Status da Conexão:** {"✅ Conectado" if st.session_state.config_id else "❌ Não Configurado"}
    * **ID da Planilha:** `{st.session_state.config_id}`
    """)
    
    col1, col2 = st.columns(2)
    col1.metric("Inspeções este mês", "0")
    col2.metric("EPIs Pendentes", "0")

elif escolha == "Inspeções (NRs)":
    st.title("📝 Registro de Inspeções")
    with st.form("form_ins"):
        c1, c2 = st.columns(2)
        id_i = c1.text_input("ID", placeholder="I01")
        local = c2.text_input("Local/Setor")
        status = st.selectbox("Status", ["C", "N"], help="C=Conforme, N=Não Conforme")
        obs = st.text_area("Observações")
        if st.form_submit_button("Gravar Inspeção"):
            salvar_dados("T_INS", {"id": id_i, "dt": pd.Timestamp.now().strftime('%d/%m/%Y'), "lc": local, "st": status, "ob": obs})

elif escolha == "Entrega de EPI":
    st.title("📦 Controle de Entrega de EPI")
    with st.form("form_epi"):
        c1, c2 = st.columns(2)
        id_e = c1.text_input("ID Registro", placeholder="E01")
        colab = c2.text_input("Nome do Colaborador")
        ca = st.text_input("CA do Equipamento")
        if st.form_submit_button("Confirmar Entrega"):
            salvar_dados("T_EPI", {"id": id_e, "cb": colab, "ca": ca, "de": pd.Timestamp.now().strftime('%d/%m/%Y')})

elif escolha == "🛠️ Configurações Dev":
    st.title("🛠️ Configurações do Sistema")
    st.session_state.config_url = st.text_input("URL completa da Planilha", value=st.session_state.config_url)
    st.session_state.config_id = st.text_input("ID da Planilha", value=st.session_state.config_id)
    st.session_state.ai_key = st.text_input("Chave API IA", value=st.session_state.ai_key, type="password")
    st.info("As configurações acima são mantidas enquanto o app estiver aberto.")
