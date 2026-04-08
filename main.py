import streamlit as st
import pandas as pd

# --- ESTADO DA SESSÃO ---
if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False,
        'nivel': 0,
        'config_id': '',
        'config_url': '',
        'ai_key': ''
    })

# --- FUNÇÃO DE LOGIN ---
def realizar_login():
    st.sidebar.title("🔐 Acesso SST")
    usuario = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")
    
    if st.sidebar.button("Entrar"):
        # Lógica de exemplo (Pode ser validada via Google Sheets depois)
        if usuario == "dev" and senha == "suasenha":
            st.session_state.autenticado = True
            st.session_state.nivel = 3 # Nível Desenvolvedor
            st.success("Bem-vindo, Desenvolvedor!")
        elif usuario == "tst" and senha == "123":
            st.session_state.autenticado = True
            st.session_state.nivel = 2 # Nível Técnico
        st.rerun()

if not st.session_state.autenticado:
    realizar_login()
    st.stop()

# --- MENU LATERAL ---
menu = ["Home", "Inspeções (NRs)", "Entrega de EPI"]
if st.session_state.nivel == 3:
    menu.append("🛠️ Configurações Dev")

escolha = st.sidebar.radio("Navegar", menu)

# --- TELA: CONFIGURAÇÕES DEV ---
if escolha == "🛠️ Configurações Dev":
    st.header("Painel de Controle do Desenvolvedor")
    
    with st.expander("🔗 Configuração de Conexão (Google Sheets)", expanded=True):
        st.session_state.config_url = st.text_input("URL da Planilha", value=st.session_state.config_url)
        st.session_state.config_id = st.text_input("ID da Planilha", value=st.session_state.config_id)
        
    with st.expander("🤖 Inteligência Artificial", expanded=True):
        st.session_state.ai_key = st.text_input("API KEY (IA)", value=st.session_state.ai_key, type="password")

    with st.expander("📄 Estrutura SQL (Apps Script)", expanded=False):
        st.info("Copie este código para a extensão Apps Script da sua planilha:")
        sql_template = f"""
/* Criação das tabelas com IDs reduzidos 
T_USR (id, nm, lg, sh, nv)
T_INS (id, dt, lc, st, ob)
*/
function setup() {{
  // Script gerado para URL: {st.session_state.config_url}
  // Execute a função inicializarBancoSST() no console do Google.
}}
        """
        st.code(sql_template, language="javascript")
    
    if st.button("Aplicar Alterações"):
        st.toast("Configurações atualizadas com sucesso!")

# --- TELA: INSPEÇÕES ---
elif escolha == "Inspeções (NRs)":
    st.header("Registro de Inspeção Diária")
    col1, col2 = st.columns(2)
    
    with col1:
        # IDs reduzidos para economizar espaço
        id_ins = st.text_input("Cód. Inspeção", max_chars=4, placeholder="I01")
        local = st.selectbox("Local", ["Canteiro A", "Almoxarifado", "Escritório"])
        
    with col2:
        status = st.radio("Status de Conformidade", ["C", "N"]) # C: Conforme / N: Não Conforme
        data = st.date_input("Data")

    obs = st.text_area("Observações (Breve)")
    
    if st.button("Salvar na Planilha"):
        # Aqui entra a lógica st.connection utilizando as variáveis do estado da sessão
        st.success(f"Registro {id_ins} enviado para {st.session_state.config_id}")
