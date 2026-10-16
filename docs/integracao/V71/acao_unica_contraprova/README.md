# Contraprova do caso 4 do `acao_unica_test.py` (Codex 6181957223 e 6215220250, PR #47)

**Pergunta do Codex:** a coleta das linhas por `innerText` enxerga de fato uma alteração indevida de plano ao avançar, sem coleta vazia nem seleção errada?

| Item | Valor |
|---|---|
| Commit testado | `a2d5457` (claude/v44-v69-mapa), render de árvore limpa (worktree destacada) |
| Comando | `RENDER_DIR=<render> CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B acao_unica_test.py saf` |
| Normal | `normal_a2d5457.log`: **10 ok · 0 falhas**, rc=0; caso 4 OK |
| Mutante | `mutante_a2d5457.log`: **8 ok · 2 falhas**, rc=1; caso 4 FALHA |

**Mutante** (só na cópia do render, `SAF.dc.html`; o código do produto não muda): no início de `safIrEtapa`, ao ir para a etapa 3, aplica em silêncio (`doApply`) o plano de um cultivo irmão da mesma cultura no 1º cultivo sem plano.

**O que o caso 4 mostrou no mutante** (informação impressa pelo teste):
- etapa depois do avanço: 3;
- linhas coletadas: **14** (mínimo exigido 8, então a coleta não está vazia);
- linhas antes = depois: **False**;
- na volta, a área de ações oferece "Aplicar plano em **3** cultivos" em vez de 4.

O caso 2 também reprova no mutante: na etapa 4, a nota passa a dizer "3 cultivos sem plano". É efeito do mesmo mutante.

`sha256.txt` traz o hash do `SAF.dc.html` normal e do mutante.
