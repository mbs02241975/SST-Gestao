import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="SST OS Pro", page_icon="🛡️", layout="wide")

# Inicialização do estado de sessão para evitar erros de "KeyError"
for key in ['autenticado', 'user_nome', 'nivel', 'config_url', 'config_id']:
    if key not in st.session_state:
        st.session_state[key] = False if key == 'autenticado' else "" if key != 'nivel' else 0

# --- LOGIN ---
def login():
    with st.sidebar:
        st.title("🔐 Acesso")
        u = st.text_input("Usuário", key="user_login")
        p = st.text_input("Senha", type="password", key="pass_login")
        if st.button("Entrar"):
            usuarios = {
                "dev": {"senha": "adm", "nivel": 3, "nome": "Administrador"},
                "tst01": {"senha": "123", "nivel": 2, "nome": "Técnico SST"}
            }
            if u in usuarios and usuarios[u]["senha"] == p:
                st.session_state.update({'autenticado': True, 'user_nome': usuarios[u]["nome"], 'nivel': usuarios[u]["nivel"]})
                st.rerun()
            else:
                st.error("Credenciais incorretas.")

if not st.session_state.autenticado:
    login()
    st.info("Faça login para começar.")
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.write(f"👤 {st.session_state.user_nome}")
    # Menu só aparece se houver URL configurada, caso contrário, força Configurações
    if not st.session_state.config_url:
        st.warning("⚠️ Configure a Planilha")
        escolha = "🛠️ Configurações"
    else:
        escolha = st.radio("Menu", ["📊 Dashboard", "📝 Inspeções", "📦 EPIs", "🛠️ Configurações"])
    
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- FUNÇÃO DE CONEXÃO ---
def salvar_no_banco(aba, dados):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_atual = conn.read(spreadsheet=st.session_state.config_url, worksheet=aba)
        df_novo = pd.concat([df_atual, pd.DataFrame([dados])], ignore_index=True)
        conn.update(spreadsheet=st.session_state.config_url, worksheet=aba, data=df_novo)
        st.success("✅ Gravado com sucesso!")
        st.balloons()
    except Exception as e:
        st.error(f"Erro de conexão: {e}. Verifique se a planilha está como 'Editor'.")

# --- TELAS ---

if escolha == "📊 Dashboard":
    st.title("📊 Indicadores de Segurança")
    # Gráfico simples para garantir que a tela não fique branca
    data = {'Status': ['Conforme', 'Não Conforme'], 'Qtd': [10, 2]}
    fig = px.pie(data, values='Qtd', names='Status', title="Visão Geral de Conformidade")
    st.plotly_chart(fig)

elif escolha == "📝 Inspeções":
    st.title("📝 Nova Inspeção Técnica")
    with st.form("form_ins"):
        c1, c2 = st.columns(2)
        id_i = c1.text_input("Cód. Inspeção", placeholder="INS-01")
        local = c2.text_input("Setor/Local")
        status = st.selectbox("Status", ["C", "N"], help="C=Conforme / N=Não Conforme")
        obs = st.text_area("Observações e Plano de Ação")
        if st.form_submit_button("Salvar Registro"):
            salvar_no_banco("T_INS", {"id": id_i, "dt": pd.Timestamp.now().strftime('%d/%m/%Y'), "lc": local, "st": status, "ob": obs})

elif escolha == "📦 EPIs":
    st.title("📦 Entrega de Equipamentos (NR-06)")
    with st.form("form_epi"):
        c1, c2 = st.columns(2)
        colab = c1.text_input("Nome do Colaborador")
        id_e = c2.text_input("ID Entrega", placeholder="EPI-01")
        ca = st.text_input("Certificado de Aprovação (CA)")
        equip = st.selectbox("Equipamento", ["Capacete", "Luva", "Bota", "Óculos", "Protetor Auricular"])
        if st.form_submit_button("Registrar Entrega"):
            salvar_no_banco("T_EPI", {"id": id_e, "cb": colab, "eq": equip, "ca": ca, "de": pd.Timestamp.now().strftime('%d/%m/%Y')})

elif escolha == "🛠️ Configurações":
    st.title("🛠️ Configurações do Sistema")
    st.markdown("---")
    with st.form("form_cfg"):
        st.subheader("Vincular Google Sheets")
        url_input = st.text_input("URL da Planilha", value=st.session_state.config_url, help="Cole a URL completa do navegador")
        id_input = st.text_input("ID da Planilha (GID)", value=st.session_state.config_id, help="Opcional: ID para logs")
        
        if st.form_submit_button("💾 Salvar e Ativar Sistema"):
            if "docs.google.com/spreadsheets" in url_input:
                st.session_state.config_url = url_input
                st.session_state.config_id = id_input
                st.success("Configurações aplicadas! O menu foi liberado.")
                st.rerun()
            else:
                st.error("URL inválida. Certifique-se de que é um link do Google Sheets.")
