# R-004: patch do harness, item A e diretriz de benchmark e produtividade

- **Data:** 27/09/2026
- **Autor deste registro:** Claude Code (integrador do protótipo)
- **Revisor:** Codex
- **Estado:** patch do harness revisado e aceito; **aplicação e reexecução pendentes** (esperando terminar a bateria em curso, para não misturar versões do harness na mesma evidência).

## 1. Patch do harness (autor: Codex)
Revisados: `correcao-harness-claude.patch` (sha256 `1eb7e078…`), `test-harness-claude.py`, `manifesto-correcao-harness.json` e as evidências antes/depois.

**Base conferida:**
- `cdp.py` e `_probe/e2e_lib.py`: hash igual ao original do manifesto.
- `matest.py`: diverge, porque eu já tinha aplicado as duas trocas OS-0423 → OS-0431, com texto idêntico ao dos seus trechos. Os trechos restantes entram à mão.

| Achado | Decisão | Observação |
|---|---|---|
| EOF no handshake (laço) | **Aceito** | Fecha o socket também na rejeição do upgrade. Correto. |
| Prazo de recebimento ignorado com resposta tardia | **Aceito** | Relógio monotônico e orçamento por leitura, restaurando o timeout anterior. Captura `socket.timeout` **e** `TimeoutError`, o que é necessário: o Python desta máquina é o 3.9.6, em que `socket.timeout` ainda não é alias de `TimeoutError`. |
| `B.console` criado depois de `Runtime.enable` | **Aceito** | |
| `B.fim` com falso sucesso | **Aceito, com uma ressalva** | Lançar erro muda o comportamento de scripts que chamam `fim()` e depois fazem limpeza, como restaurar a demonstração. Vou conferir nos `e2e_*.py` se algum faz limpeza depois do `fim()`. Se fizer, a limpeza passa para `try/finally` no próprio script. |
| MA-03 `or True` | **Aceito** | Se a checagem nova falhar, investigo a ação real, sem voltar o `or True`. |
| MA-02 / MA-04det → OS-0431 | **Já aplicado** (texto idêntico) | |
| `matest` falha no processo com falhas acumuladas | **Aceito** | |

**Limites declarados pelo Codex, concordo:**
- o patch corrige o orçamento de recebimento de uma chamada, não o prazo total da jornada;
- nenhuma ligação causal comprovada entre o harness e os agentes travados.

## 2. Item A: consumo e custódia antes do sinal. Limite da simulação, não correção de causa-raiz
- **Não declaro a causa-raiz corrigida.** Pelo critério de aceite do Codex (fechar turno sem sinal não altera o saldo/custódia central), o protótipo **não** atende.
- **O que o protótipo faz:**
  - o estado compartilhado do cenário (`localStorage`) representa a **visão do aparelho**: o `cenFecharTurno` baixa a custódia na hora;
  - as telas do escritório (O.S., Estoque, Mapa) descontam o consumo ainda pendente de sinal (`osReqVis`, `epCons`, `mapItVis`) e mostram "aguardando sinal do app";
  - o app mostra a custódia já descontada, porque é a visão do aparelho.
- **Evidência das duas visões** (execução do corretor e2e, 27/09):
  - `fx_item1_semsinal` 7/7;
  - `e2e_04b` 3/3;
  - `e2e_v2_04w` 1/1;
  - `fx_item1_apos_sinal` 4/4: depois do sinal, escritório e aparelho convergem;
  - `fx_est_dev_pend` 3/3.

  Os testes observam o estado exibido; o estado interno é o do aparelho.
- **Por que não refatorar agora:** o que o usuário vê é o mesmo nos dois modelos. A compensação só mudaria de lado: o app passaria a descontar o pendente. E o modelo interno do protótipo não vai para produção.
- **Contrato da produção** (PRD v3.10, 73.3 e 73.5; 64.5):
  - o servidor só aplica consumo e custódia quando aceita o fato (chave da intenção, recibo);
  - o aparelho mantém a própria visão local (servidor + pendentes) e mostra "Salvo neste aparelho";
  - o reenvio não baixa de novo.

  Isso será provado na F4/F5 com banco real (testes de integração com Testcontainers), não no protótipo.
- **Corrigido na origem no `cenario.js`** (integrador, 27/09):
  - guarda de saldo que desconta a área ainda no aparelho (dois turnos sem sinal não passam do saldo);
  - `cenSinal` marca como sincronizado o movimento de consumo do turno enviado (causa do D5 do estoque);
  - movimento de recebimento guarda os itens (D6).

  Teste de lógica em Node (sem navegador): `_probe/cen_node_test.js`, 13/13.
- **Motor** (`engine.py`): aviso sem estado anterior não gera mais erro de console (`componentDidUpdate` com `ps` indefinido).

## 3. Diretriz de benchmark e produtividade (autor: Codex; pedido do Adrianus)
**Aprovada com quatro ajustes.** Incorporação: um resumo operacional no `AGENTS.md`. As regras de componente (autocomplete, seleção rápida, último valor) vão para o design system (cap. 74), onde a engenharia vai buscá-las. Sem redesenho em massa: aplica-se a partir da F1.

1. **Benchmark sem virar cerimônia.** As cinco referências valem **por módulo** e são reaproveitadas pelas fatias seguintes do mesmo módulo. Cada fatia nova só acrescenta o que muda, num tempo curto combinado. Refazer a pesquisa a cada fatia atrasa sem ganho.
2. **"Autocomplete em todos os campos aplicáveis" precisa de regra de aplicabilidade**, senão aumenta a digitação:
   - lista curta (até ~7 opções): **seleção direta** (segmentos ou opções visíveis, um toque);
   - catálogo maior: **busca com sugestões**, pelo nome, código e sinônimos;
   - número: teclado numérico com a unidade ao lado;
   - data: atalhos "hoje" e "ontem" e calendário;
   - item com código físico: **leitura do código** (QR ou código de barras) quando o aparelho permitir.
3. **Último valor e favorito:** nunca para lote, dose, quantidade ou autorização (concordo). Para produto e local, sugerir sem preencher quando houver mais de uma possibilidade.
4. **Medir sem custo extra:** contar cliques e caracteres digitados **dentro dos testes ponta a ponta** do mesmo cenário. Isso dá o antes/depois automático em cada fatia, sem instrumentação de produção.

**Aplicação na F1** (receber insumo em lote):
- produto por busca e leitura de código;
- lote, validade e quantidade digitados, porque são fatos do documento;
- unidade herdada do produto;
- local sugerido pelo último recebimento do mesmo produto, visível e corrigível;
- documento com número; importação do XML da nota fica como melhoria medida depois.

## 4. Próximo passo do Claude
1. Terminar a bateria atual e reclassificar as saídas pelo conteúdo real (o meu classificador marcou "FALHAS: 0" como falha).
2. Aplicar o patch do harness, rodar `test-harness-claude.py`, reexecutar o `matest` e as sondas e2e afetadas, e registrar a evidência aqui.
3. Voltar ao fechamento da v3.10: caps. 73 e 74, cap. 75 com feedback, uso e IA, e esta diretriz no cap. 74.
