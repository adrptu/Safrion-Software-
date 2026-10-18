# EX51 N-1/B-3 — candidata para revisão cruzada

Base 31680412b515d34ae7fa958969a652c3d1060ffb; contrato PR47 6241763475, interface final 6241782009. Autor Codex; revisor/integrador Claude.

A emissão agora grava OS, DIA, REC/RA, decisão e recibo em uma única escrita estrita do cenário. O legado MIP é preservado e migrado apenas junto à primeira operação bem-sucedida. Dados ilegíveis/incompatíveis e ausência do cenário recusam escrita. A interface exige ator, chave e dver no terceiro argumento; a autorização precede a recuperação do recibo. Histórico de decisão e receitas canceladas são preservados.

As portas osc_aprovar e osc_liberar recusam receita ausente/divergente/cancelada, antes de aprovação ou reserva. Guardam produto, unidade, dose, área e total; ordens sem origem MIP e erradicação sem receita mantêm as regras existentes. osReceitaErro(c,o) fica disponível para a UI do Claude. Ordens MIP antigas sem c.mip precisam da migração pelo fluxo MIP; não são aprovadas silenciosamente.

Validação local executada: 6 testes do adaptador, 8 de emissão/recibo/histórico, 22 das guardas; sintaxe JS e compilação Python. Executar `node n1_adapter_test.cjs`, `node n1_emission_test.cjs`, `node n1_recipe_test.cjs` neste diretório. Os testes de emissão usam persistência e alocação de IDs reais, mas simulam agronomia e construção da OS. Guardas usam funções reais com permissão/regra legal/efeito de reserva simulados. Isso não comprova navegador, estoque real, teclado, celular ou E2E.

Pendências impeditivas de publicação: composição por Claude dos chamadores AG-01 com ator/chave/dver e MB-06 com cenário; revisão crítica; testes reais da composição e da guarda pelo grupo; recuperação visual de dados ilegíveis. Não publicar a candidata isolada: chamadas antigas recusam. Aceite de concorrência multiaba explicitamente pendente; comparar a string/revisão observada não é exclusão mútua. Não há alegação de transação de servidor ou HML.
