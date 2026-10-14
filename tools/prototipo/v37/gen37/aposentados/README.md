# Testes aposentados (vermelho antigo de teste obsoleto)

Movidos para cá em 14/10/2026 (AGENTS §3.6: "vermelho antigo é corrigido, distinguindo defeito do produto, teste obsoleto e falha da
ferramenta"). Não rodam na bateria. A regra que cobriam continua protegida pelos testes indicados.

| Teste | Por que saiu | Onde a regra continua (executado em 14/10) |
|---|---|---|
| `saftest.py` | Roteiro sem asserção (só imprime), que marcava caixas de seleção da etapa 2. As caixas saíram na v58 (proprietário, 13/10/2026). | `saf_revisao_test.py` 42 ok; `saf_fazendas_test.py` 14/14 |
| `saf38test.py` | Revisão v3.8 de 26/09; lê a 2ª tabela visível da etapa 3, que deixou de existir com a etapa única 3-4-5. Vermelho registrado desde então em `docs/planejar-safra/etapa-unica-3-4-5/ESPECIFICACAO.md` (linha "continuam vermelhos pelo motivo antigo; regras recriadas em O14, O15 e P8"). | `saf_operacoes_test.py` O14, O15 e P8: 87 ok · 0 falhas |
| `psfix38test.py` | Mesmo motivo e mesmo registro do `saf38test.py`. | `saf_operacoes_test.py` O14, O15 e P8 |
| `plano_referencia_nav.py` | Abria o painel "Comparar versões do plano" pelo botão da faixa do Planejar safra. A entrada saiu a pedido do proprietário (14/10/2026: "tire comparar versões do plano"). | As regras do painel (CONTROLE-02 F2, autoria Codex) seguem no código e nos testes de unidade `plano_referencia_unit_test.py` e `plano_referencia_comando_test.py`. Se a entrada voltar em outro lugar, o teste volta com ela. |
| `plano_referencia_publicar_nav.py` | Mesmo motivo: publicava a referência pelo mesmo botão. | Idem. |
