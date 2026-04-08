import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SST OS Pro", page_icon="🛡️", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False, 'user_nome': '', 'nivel': 0,
        'config_url': '', 'ai_key': ''
    })

# --- FUNÇÃO DE LOGIN ---
def login():
    with st.sidebar:
        st.title("🔐 Acesso SST")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            usuarios = {
                "dev": {"senha": "adm", "nivel": 3, "nome": "Eng. Segurança"},
                "tst01": {"senha": "123", "nivel": 2, "nome": "Técnico SST"},
                "gestor": {"senha": "999", "nivel": 1, "nome": "Gestor"}
            }
            if u in usuarios and usuarios[u]["senha"] == p:
                st.session_state.update({'autenticado': True, 'user_nome': usuarios[u]["nome"], 'nivel': usuarios[u]["nivel"]})
                st.rerun()

if not st.session_state.autenticado:
    login()
    st.info("Aguardando autenticação...")
    st.stop()

# --- NAVEGAÇÃO ---
opcoes = ["📊 Dashboard", "📝 Inspeções", "📦 EPIs", "🛠️ Configurações"]
escolha = st.sidebar.radio("Menu", opcoes)

# --- FUNÇÃO DE SALVAMENTO ---
def salvar_registro(aba, dados):
    if not st.session_state.config_url:
        st.error("URL da planilha não configurada!")
        return
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_atual = conn.read(spreadsheet=st.session_state.config_url, worksheet=aba)
        df_novo = pd.concat([df_atual, pd.DataFrame([dados])], ignore_index=True)
        conn.update(spreadsheet=st.session_state.config_url, worksheet=aba, data=df_novo)
        st.success("✅ Gravado com sucesso!")
    except Exception as e:
        st.error(f"Erro: {e}")

# --- TELAS ---
if escolha == "📊 Dashboard":
    st.title(f"Bem-vindo, {st.session_state.user_nome}")
    # Gráfico simples para testar o Plotly (Evita o erro de ModuleNotFound)
    df_grafico = pd.DataFrame({'Setor': ['Canteiro', 'Oficina', 'ADM'], 'N-Conformidades': [5, 2, 1]})
    fig = px.bar(df_grafico, x='Setor', y='N-Conformidades', title="Irregularidades por Setor")
    st.plotly_chart(fig)

elif escolha == "📝 Inspeções":
    st.title("Relatório de Inspeção")
    with st.form("ins"):
        col1, col2 = st.columns(2)
        id_i = col1.text_input("ID")
        local = col2.text_input("Local")
        st_conf = st.selectbox("Conformidade", ["C", "N"])
        obs = st.text_area("Observações / Plano de Ação")
        if st.form_submit_button("Salvar"):
            salvar_registro("T_INS", {"id": id_i, "dt": "08/04/2026", "lc": local, "st": st_conf, "ob": obs})

elif escolha == "🛠️ Configurações":
    st.title("Configurações do Desenvolvedor")
    with st.form("cfg"):
        url = st.text_input("URL da Planilha", value=st.session_state.config_url)
        if st.form_submit_button("Salvar Configurações"):
            st.session_state.config_url = url
            st.success("Configuração salva!")
