import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SST OS Pro", page_icon="🛡️", layout="wide")

# --- ESTADO GLOBAL (Persistência na Sessão) ---
if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False,
        'user_nome': '',
        'nivel': 0,
        'config_url': '',
        'config_id': '',
        'ai_key': ''
    })

# --- FUNÇÃO DE LOGIN ---
def login_sistema():
    with st.sidebar:
        st.title("🔐 Acesso SST")
        u_input = st.text_input("Usuário")
        p_input = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            # Credenciais definidas conforme conversamos
            usuarios = {
                "desenvolvedor": {"senha": "Mm88918675@@", "nivel": 3, "nome": "Desenvolvedor"},
                "tst01": {"senha": "123", "nivel": 2, "nome": "Técnico de Campo"},
                "gestor": {"senha": "999", "nivel": 1, "nome": "Gerente Geral"}
            }
            
            if u_input in usuarios and usuarios[u_input]["senha"] == p_input:
                st.session_state.update({
                    'autenticado': True,
                    'user_nome': usuarios[u_input]["nome"],
                    'nivel': usuarios[u_input]["nivel"]
                })
                st.rerun()
            else:
                st.error("Usuário/Senha inválidos")

if not st.session_state.autenticado:
    login_sistema()
    st.info("Acesse com seu usuário para liberar o sistema.")
    st.stop()

# --- NAVEGAÇÃO DINÂMICA ---
opcoes = ["🏠 Home"]
if st.session_state.nivel >= 2:
    opcoes.extend(["📝 Inspeções (NRs)", "📦 Entrega de EPI"])
if st.session_state.nivel == 3:
    opcoes.append("🛠️ Configurações Dev")

with st.sidebar:
    st.write(f"👤 **{st.session_state.user_nome}**")
    escolha = st.radio("Navegar", opcoes)
    st.divider()
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- FUNÇÃO DE GRAVAÇÃO (SEM GOOGLE CLOUD / PEM) ---
def salvar_registro(aba, dados_dicionario):
    if not st.session_state.config_url:
        st.error("Erro: Configure a URL da Planilha no painel Dev primeiro!")
        return
    try:
        # Conexão simplificada para planilha pública (Editor)
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_atual = conn.read(spreadsheet=st.session_state.config_url, worksheet=aba)
        df_novo = pd.concat([df_atual, pd.DataFrame([dados_dicionario])], ignore_index=True)
        conn.update(spreadsheet=st.session_state.config_url, worksheet=aba, data=df_novo)
        st.success("✅ Registro enviado para a planilha!")
        st.balloons()
    except Exception as e:
        st.error(f"Falha na conexão: {e}. Verifique se a planilha está como 'Editor' para qualquer pessoa com o link.")

# --- TELAS ---

# 1. HOME
if escolha == "🏠 Home":
    st.title(f"Olá, {st.session_state.user_nome}!")
    st.write("Sistema de Gestão de Segurança do Trabalho - Visão Geral")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Status do Banco", "✅ OK" if st.session_state.config_id else "⚠️ Pendente")
    with c2:
        st.metric("Nível de Acesso", f"Lvl {st.session_state.nivel}")
    with c3:
        st.metric("IA Engine", "Ativa" if st.session_state.ai_key else "Inativa")

# 2. INSPEÇÕES COM PLANO DE AÇÃO
elif escolha == "📝 Inspeções (NRs)":
    st.title("📝 Inspeção e Plano de Ação")
    
    with st.form("form_inspecao"):
        col1, col2 = st.columns(2)
        id_i = col1.text_input("ID", placeholder="I01", max_chars=4)
        local = col2.text_input("Local da Inspeção")
        status = st.selectbox("Status de Conformidade", ["C", "N"], help="C=Conforme / N=Não Conforme")
        
        st.divider()
        st.subheader("📋 Detalhes e Plano de Ação")
        obs = st.text_area("Descreva a situação encontrada")
        
        # Só exibe campos de plano de ação se houver Não Conformidade
        plano = ""
        prazo = ""
        if status == "N":
            st.warning("⚠️ Atenção: Descreva as medidas corretivas abaixo.")
            plano = st.text_input("Plano de Ação (O que fazer?)")
            prazo = st.date_input("Prazo para correção")
        
        if st.form_submit_button("Finalizar e Gravar"):
            dados = {
                "id": id_i,
                "dt": pd.Timestamp.now().strftime('%d/%m/%Y'),
                "lc": local,
                "st": status,
                "ob": f"{obs} | Plano: {plano} | Prazo: {prazo}" if status == "N" else obs
            }
            salvar_registro("T_INS", dados)

# 3. ENTREGA DE EPI
elif escolha == "📦 Entrega de EPI":
    st.title("📦 Registro de Entrega (NR-06)")
    with st.form("form_epi"):
        id_e = st.text_input("Cód. Entrega", placeholder="E01")
        colab = st.text_input("Nome do Colaborador")
        ca = st.text_input("Número do CA")
        if st.form_submit_button("Registrar Entrega"):
            dados_epi = {
                "id": id_e,
                "cb": colab,
                "ca": ca,
                "de": pd.Timestamp.now().strftime('%d/%m/%Y')
            }
            salvar_registro("T_EPI", dados_epi)

# 4. CONFIGURAÇÕES DEV (Com Botão de Salvar)
elif escolha == "🛠️ Configurações Dev":
    st.title("🛠️ Painel de Configurações Técnicas")
    st.info("Insira os dados abaixo para vincular o app à sua planilha.")
    
    with st.form("form_config"):
        url_input = st.text_input("URL da Planilha Google (Modo Editor)", value=st.session_state.config_url)
        id_input = st.text_input("ID da Planilha (opcional para log)", value=st.session_state.config_id)
        ia_input = st.text_input("Chave API da IA", value=st.session_state.ai_key, type="password")
        
        if st.form_submit_button("💾 Salvar Configurações"):
            st.session_state.config_url = url_input
            st.session_state.config_id = id_input
            st.session_state.ai_key = ia_input
            st.success("Configurações salvas com sucesso para esta sessão!")
            st.rerun()

    st.divider()
    st.subheader("📂 Estrutura SQL (Apps Script)")
    st.code("""
function setupSST() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tabelas = {
    "T_USR": ["id", "nm", "lg", "sh", "nv"],
    "T_INS": ["id", "dt", "lc", "st", "ob"],
    "T_EPI": ["id", "cb", "ca", "de"]
  };
  for (var n in tabelas) {
    var aba = ss.getSheetByName(n) || ss.insertSheet(n);
    aba.getRange(1, 1, 1, tabelas[n].length).setValues([tabelas[n]]);
  }
}
    """, language="javascript")
