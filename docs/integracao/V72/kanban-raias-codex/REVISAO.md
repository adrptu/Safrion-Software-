# AGR-02 — recolher raias do Kanban

Autor Codex; revisor/integrador Claude. Contratos6223477051 e6224284837. Base6dfa09c190cf55ff16da841561d5739b138b7646 doPR88; entrega empilhada, depende da integração88 e da composiçãoDS87. Não integrar isoladamente nem autoaprovar.

O cabeçalho nativo da raia agora recolhe/expande, com▸/▾ antes do nome (TAB-09), rótulo pelo objetivo e aria-expanded. Recolher não modifica a trilha, filtro, seleção, cartões nem dados de domínio. A memória local da tela separa perfil, fazenda, safra, dimensão, caminho e grupo; trocar visão/filtro e voltar conserva a expansão. Continua um quadro só quando não há agrupamento ou o recorte já chega ao último nível; não há trilha (AGR-02). A mesma O.S. de dois talhões mantém os dois vínculos e a indicação da repetição.

## Provas executadas

kanban_raias_test.py monta as grades e oJavaScript pelo build real da O.S.; executa PREVALS/EXTRAVALS e os callbacks reais emNode com dados sintéticos.9/9: abertura, recolha sem mutação, duplo acionamento, volta de visão/seleção, filtro, fazenda, perfil, quadro único eO.S. em duas raias. Mesmos casos sobre6dfa09c:0/9 (gesto/estado novo ausente). Brutos anexos. AST3/3; buildreal e compilaçãoJS efetivamente executados pelo runner. Não é prova de DOM, foco, toque nem teclado.

visoes2_formas_test.py foi adaptado ao pedido novo de recolher. Os antigosF2–F4 exigiam “Descer em”, portanto não podiam permanecer como aceite desse gesto. Foram preservadas as contraprovas de trilha explícita, Calendário/Carga, filtro de talhão e recortePainel; adicionadas ativaçãoEnter/Espaço, aria-expanded, foco no cabeçalho, volta entre visões e toque390. Não executado peloCodex: navegador continua bloqueado. Claude deve rodar a navegação atualizada, tabelas_os e os_cenario sobre a composição identificada, comparando vermelhos preexistentes sem ocultá-los.

## Integração

Delta de produto restrito ao helperosKbRaia, construção kb_raias e _kanban_raias. Nenhuma alteração deOS-LOTE/alocacao/inicio.py. A composiçãoDS87 moveu a seta antiga para antes do nome; ao integrar, conservar a nova seta dinâmica antes do nome, sem recuperar “Descer em”. SePR88 receber correção, atualizar esta pilha preservando a autoria e retestar só o afetado antes de integrar.

Aplicado: listagem/detalhe existentes, contexto e próximo gesto explícitos, estado acessível e alvo44px no toque. Fora: mudanças em cálculos, agenda, composição de operações, preferências persistentes e novos menus. Cortado: navegação inesperada ao tocar o cabeçalho; não há trilha desde a AGR-02, e um endereço antigo com trilha não recorta. Nenhuma publicação ou conclusão do conjunto é declarada.

