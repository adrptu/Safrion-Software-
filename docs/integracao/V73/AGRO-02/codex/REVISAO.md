# AGRO-02 — escolha explícita de produto e dose
Autor Codex; revisor/integrador Claude. Contrato PR47/6228584304.
Base d995dedf1f94f6f0819b3c873f74fabe2439b57f.

Abrir Decidir controle preenchia o primeiro produto sem trava e sua dose mínima; se todos tinham trava, escolhia o primeiro mesmo assim. Escolher produto também sobrescrevia a dose pela mínima, inclusive ao clicar no produto já selecionado.

Agora produto/dose começam vazios. Escolher outro produto limpa a dose; clicar no mesmo preserva exatamente a entrada, inclusive vírgula, zero e texto incompleto para validação. Área/data/contexto e guardas de emissão existentes permanecem. O foco inicial usa o destino pan_x existente para formulário sem seleção.

## Evidência executada
Node 24.19: agro02_selecao_unit.js — 7 passaram na candidata; na fonte base, 1 passou e 6 falharam pelo preenchimento automático. Executa as expressões reais de transição de estado da UI com contexto pré-calculado sintético, não simula validações agronômicas.
Python AST e node --check do JS extraído passaram.
Nenhum navegador, teclado, celular ou E2E executado pelo Codex nesta fatia: ferramenta bloqueada no registro anterior. Claude deve conferir abertura, seleção, troca/reclicagem, foco e emissão bloqueada sem dose em 1440/390 antes de integrar/publicar.

## Limites e pendências existentes
Não fecha AGRO-02 integralmente. Prévia de selos dos produtos não selecionados ainda usa dose mínima para classificação; cobertura por local/múltiplos lotes e compra continuam nos achados anteriores. Não altera estoque, cálculo, receituário, permissões ou liberação.
Não declara registro legal dos produtos de demonstração nem prescreve dose.

Aplicado: entrada explícita e preservação do rascunho no mesmo produto.
Deixado fora: cobertura/compra e classificação de prévias, por autoria/escopo separado.
Cortado: seleção automática/fallback e dose mínima automática, pois faixa de bula não é prescrição.
