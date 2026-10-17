# EX47 — ações da linha independentes de Excluir
Autor Codex; revisor/integrador Claude. Base PR89 2f22375dcd61673f55f363eee0d69001474b8bb6. Contrato PR47/6228331140; inclui engine.py para alinhar trilhas, cabeçalho e total ao runtime.

Quando menu_linha/rmenu estava ativo sem dele/del, o motor retirava ações da célula mas não construía o menu. Agora cria o menu com as ações existentes, sem adicionar Excluir. A linha sem ações preserva apenas célula estrutural de alinhamento, sem botão vazio. Guarda de confirmação não reaproveita cf obsoleto para linha sem exclusão. Com rmenu, linha ro/fora/livre/nosel sem ações não cai na lixeira legada. Atalhos de navegação continuam na célula.
Não liga rmenu globalmente nem altera autorizações ou comandos de domínio. Caminho sem rmenu preservado.

Executado Node24.19: rmenu_unit.js sobre g2lib completo, sem mocks de funções: ações/chamada parametrizada/navegação/colunas/confirmacao obsoleta/exclusão/quatro guardas/caminho legado OK. Contraprova mesmo teste na base falha no primeiro rm ausente.
Executado Python3: rmenu_generator_test.py, 8 combinações menu/exclusão/seleção no gerador real; cabeçalho, total e trilhas alinhados; del preservado.
Fontes auxiliares catalogo_operacoes.py, visoes.py e visoes_marcas.py recuperadas da base exata, sem alterações.
Browser não executado: bloqueio Codex preservado. Claude deve conferir Tabela/Cartões em1440/390, teclado abre/fecha menu e retorno de foco, ação selecionada e total; retarget após89/88 antes da integração. Nenhum auto-merge nem publicação própria.
