import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px # Biblioteca para gráficos profissionais

# --- CONFIGURAÇÃO AVANÇADA ---
st.set_page_config(page_title="SST MANAGEMENT SYSTEM", page_icon="🛡️", layout="wide")

# --- ESTILO CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_value=True)

# --- PERSISTÊNCIA DE DADOS ---
if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False, 'user_nome': '', 'nivel': 0,
        'config_url': '', 'ai_key': ''
    })

# --- SISTEMA DE LOGIN ---
def login():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1063/1063302.png", width=80)
        st.title("Portal de Acesso")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar Sistema"):
            usuarios = {
                "dev": {"senha": "adm", "nivel": 3, "nome": "Engenheiro de Dados"},
                "tst01": {"senha": "123", "nivel": 2, "nome": "Técnico SST"},
                "fiscal": {"senha": "999", "nivel": 1, "nome": "Auditoria/Gestão"}
            }
            if u in usuarios and usuarios[u]["senha"] == p:
                st.session_state.update({'autenticado': True, 'user_nome': usuarios[u]["nome"], 'nivel': usuarios[u]["nivel"]})
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

if not st.session_state.autenticado:
    login()
    st.stop()

# --- HELPER: CONEXÃO COM PLANILHA ---
def get_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except:
        st.error("Erro ao conectar ao banco de dados.")
        return None

# --- MENU LATERAL ---
with st.sidebar:
    st.write(f"💼 **{st.session_state.user_nome}**")
    menu = st.radio("Módulos de Gestão", ["📊 Dashboard Executivo", "📋 Inspeções Técnicas", "📦 Gestão de EPIs", "🎓 Treinamentos", "🛠️ Configurações"])
    if st.button("Encerrar Sessão"):
        st.session_state.autenticado = False
        st.rerun()

# --- TELAS ---

if menu == "📊 Dashboard Executivo":
    st.title("📊 Painel de Indicadores SST")
    
    # Dados fictícios para simulação enquanto não há registros
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Taxa de Conformidade", "85%", "+2%")
    c2.metric("Pendências NR-18", "12", "-3")
    c3.metric("EPIs Entregues/Mês", "145")
    c4.metric("Treinamentos Ativos", "92%")

    st.subheader("Tendência de Irregularidades")
    # Exemplo de gráfico Plotly
    df_fake = pd.DataFrame({'Mês': ['Jan', 'Fev', 'Mar'], 'Não Conformidades': [15, 10, 8]})
    fig = px.line(df_fake, x='Mês', y='Não Conformidades', markers=True, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📋 Inspeções Técnicas":
    st.title("📋 Checklist e Inspeção de Campo")
    
    with st.expander("Informações da Área", expanded=True):
        col1, col2, col3 = st.columns(3)
        id_i = col1.text_input("ID do Laudo", "INS-2024-001")
        local = col2.selectbox("Frente de Trabalho", ["Canteiro Norte", "Almoxarifado Central", "Oficina Mecânica"])
        nr_ref = col3.multiselect("NRs Referência", ["NR-01", "NR-06", "NR-10", "NR-12", "NR-18", "NR-35"])

    with st.container():
        st.subheader("Itens de Verificação")
        status = st.radio("O ambiente está em conformidade?", ["Conforme", "Não Conforme"], horizontal=True)
        obs = st.text_area("Evidências e Observações Técnicas")
        
        if status == "Não Conforme":
            st.error("### ⚠️ PLANO DE AÇÃO (5W2H)")
            c1, c2 = st.columns(2)
            oque = c1.text_input("O que deve ser feito?")
            quem = c2.text_input("Responsável pela Correção")
            prazo = st.date_input("Prazo Limite")
            gravidade = st.select_slider("Gravidade do Risco", options=["Baixo", "Médio", "Alto", "Crítico"])

    if st.button("💾 Finalizar Relatório de Inspeção"):
        # Lógica de gravação concatenando dados técnicos
        st.success("Relatório gerado e enviado para a base de dados.")

elif menu == "📦 Gestão de EPIs":
    st.title("📦 Controle de Equipamentos (NR-06)")
    tab1, tab2 = st.tabs(["Nova Entrega", "Inventário"])
    
    with tab1:
        with st.form("epi"):
            col1, col2 = st.columns(2)
            col1.text_input("Nome do Funcionário")
            col1.text_input("Matrícula")
            col2.selectbox("Equipamento", ["Capacete de Segurança", "Bota de PVC", "Protetor Auricular", "Cinto de Segurança"])
            col2.text_input("Número do CA (Certificado de Aprovação)")
            st.checkbox("O colaborador recebeu treinamento para o uso deste EPI?")
            if st.form_submit_button("Gerar Ficha de Entrega Digital"):
                st.info("Ficha processada.")

elif menu == "🛠️ Configurações":
    if st.session_state.nivel < 3:
        st.error("Acesso negado.")
    else:
        st.title("⚙️ Configurações do Sistema")
        with st.form("cfg"):
            st.session_state.config_url = st.text_input("URL Database (Google Sheets)", value=st.session_state.config_url)
            st.session_state.ai_key = st.text_input("Chave Gemini AI (Análise de Riscos)", value=st.session_state.ai_key, type="password")
            if st.form_submit_button("Atualizar Parâmetros"):
                st.success("Sistema atualizado.")
