// Função para inicializar a estrutura da planilha (O "SQL" de criação)
function inicializarBancoSST() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // Definição das tabelas e colunas (IDs reduzidos)
  var tabelas = {
    "T_USR": ["id", "nm", "lg", "sh", "nv"], // Usuários: id, nome, login, senha, nivel
    "T_INS": ["id", "dt", "lc", "st", "ob"], // Inspeções: id, data, local, status, obs
    "T_EPI": ["id", "cb", "ca", "de"],       // EPI: id, colab, ca, dt_entrega
    "T_CFG": ["chave", "valor"]              // Configurações do Sistema
  };
  
  for (var nome in tabelas) {
    var aba = ss.getSheetByName(nome) || ss.insertSheet(nome);
    aba.getRange(1, 1, 1, tabelas[nome].length).setValues([tabelas[nome]]);
    aba.setFrozenRows(1); // Congela o cabeçalho
  }
}

// Exemplo de como você chamaria uma "Query" para inserir dados
function inserirRegistro(nomeTabela, dados) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(nomeTabela);
  sheet.appendRow(dados);
}
