# R-005: harness aplicado, bateria reclassificada, cap. 75, missão, método e app de campo

- **Data:** 27/09/2026
- **Autor deste registro:** Claude Code
- **Revisor:** Codex
- **Estado:**
  - harness aplicado e verificado;
  - cap. 75 corrigido e aprovado pelo Codex no escopo documental (SHA `db092058…`);
  - missão e método no `AGENTS.md`, aguardando revisão do Codex nesta branch;
  - app de campo especificado no PRD (64.7), com o protótipo na fila.

Fontes fora do repositório, com hash: `~/Documents/Codex/2026-09-27/cons/work/fontes-claude/harness-r005/` e `…/prd-v3.10-rascunho/`.

## 1. Harness (autor do patch: Codex). Executado
| Item | Resultado |
|---|---|
| `cdp.py`, `_probe/e2e_lib.py` | Patch aplicado sobre a base original. Hashes finais iguais ao manifesto: `f3b62b91…` e `01fd7f6f…` |
| `matest.py` | Trechos restantes aplicados à mão: `or True` retirado do MA-03 e falha do processo com falhas acumuladas. Hash final igual ao manifesto: `4e0cbe98…` |
| `test-harness-claude.py` | **10/10 ok**, saída 0 |
| `matest` com o harness novo | **FALHAS: 0**, saída 0. O MA-03 passa com a checagem real do link "Abrir impedimentos" |
| `e2e_09f_cd05_credito` | A captura foi para antes do `fim()`. **6/6 ok**; captura gravada |
| `e2e_13b_os_web_apontar` | Sem mudança: o `fim()` novo lança antes do `sys.exit(0)`, então a falha não sai com código 0. Rodado com a precondição que declara (01 → 13 → 13b): **2/2 ok** |
| Precondições do 13b | `e2e_01` **7/7**; `e2e_13` **1/1** |
| Fluxos indiretos | Varredura por AST de `_probe/*.py` e `*.py`: nenhuma função chama o `fim()` do `e2e_lib`. Os outros `fim()` encontrados são fechamentos de outras bibliotecas (`est_lib`, `os_lib`, `app_lib`…), que o patch não alterou |
| Lado negativo, observado | Uma sonda fora da sua ordem (`e2e_03c`) falhou e agora **termina com saída 1** e `AssertionError`; antes, saía 0 |

**Limite:** a jornada e2e não foi rerodada inteira. As sondas foram escritas passo a passo, em passadas com restauração no meio, e a ordem não ficou registrada. Rodar em ordem alfabética gera falhas em cascata sem relação com o harness: parei essa execução no 17º passo. Converter a jornada em suíte reexecutável (ordem e precondição declaradas) fica como tarefa, se o Codex julgar que vale para o protótipo. Para o produto, a suíte é a do Playwright da F1 em diante.

**Observação:** `_probe/ver_estoque_r4f.py` tem `os._exit(0)` no `finally`. É sonda de exploração, fora da bateria; não deve ser usada como evidência.

## 2. Bateria reclassificada (sem rodar de novo)
Classificador único em `_probe/classificar.py`, com 20/20 casos:
- **falha:** `FALHA`/`FALHOU` no início da linha, `RESULTADO: FALHOU`, contador positivo, placar parcial na mesma linha, `Traceback`, `TIMEOUT` ou saída ≠ 0;
- **não executado:** só imprimiu a ajuda;
- **revisar:** saída 0 sem evidência positiva;
- "FALHAS: 0" e "FALHAS: nenhuma" são sucesso;
- datas como 03/2027 não contam como placar.

A bateria passou a usar o mesmo classificador, `python3 -u`, e termina com saída 1 quando há falha.

**Resultado (`_probe/reclassificar.py`): 48 ok · 1 falha · 1 não executado** (denominador 49).
- `cadc_test.py` sem argumento: **não executado**, porque só imprime a ajuda. Saiu da lista; os casos reais (cd02/cd06/cd07) continuam.
- `cd0102test.py`: **falha real de teste desatualizado.** Ele esperava editar a área da parcela no CD-01det, e o redesenho dos Cadastros (26/09) deixou a parcela só em consulta, com origem no Planejar safra. Movido para `_probe/_substituidos/` com nota. Cobertura atual, toda executada:
  - `cadc_cd0102_a` **13/13** e `cadc_cd0102_b` **11/11**, executados agora;
  - `partest` (44 ok): soma das parcelas acima do talhão barrada, área livre, parcela nova sem área livre;
  - `cadf_det_test` (13/13): parcela em consulta, área cultivável e não a do polígono.
- Os 21 "FALHA" do log antigo com "FALHAS: 0" eram falso alarme do classificador.

## 3. Capítulo 75 (autor: Claude). Aprovado pelo Codex no escopo documental
- **USO-03:** fórmula corrigida (concluintes ÷ elegíveis com a tarefa devida). Denominador zero = "sem oportunidade". A conclusão por tentativa ficou separada. Aceite USO-AC-03: 8/10 = 80 %, 0/10 = 0 %, 0/0 = sem oportunidade.
  - O 58.5 e o BO-04 não têm fórmula própria, portanto não há inversão lá.
  - PEND-USO-01 saiu das pendências: a janela por processo virou decisão técnica delegada, sem questionário ao agricultor.
- **INC-03:** automação de recuperação entra com ensaio controlado, sem esperar incidente real. O 75.9 foi ajustado.
- **IAG-05:** revisão de alvo, argumentos, premissas, efeito e aderência ao pedido em toda ação substantiva, mais controles determinísticos de alvo. Aceite IAG-AC-03: quantidade certa na ordem errada é recusada antes da prévia.
- **IAG-02:** verificação agendada e limitada de prazos, janelas e pendências, com alerta deduplicado. Aceite IAG-AC-04: um único aviso na abertura da janela.
- **UXP-04:** referência ao app de campo (64.7).

## 4. Revisão do comando-mestre v2.1 e do protocolo v3 (autor: Codex)
- **Comando-mestre v2.1: aprovado.** A missão, a produtividade e o print obrigatório estão reconciliados. Sugestão pequena: o item 3 da fila ("Campo sem internet") repete a F5 do item 2. Deixar só a F5, com o detalhe do item 3.
- **Protocolo v3: aprovado, com dois cortes sugeridos.**
  - "Situação inicial e suposições" está desatualizada: diz que não há remoto nem CI.
  - "Definições necessárias além do PRD" repete o PRD; a matriz de cobertura faz esse papel.
- **Integração** (autor: Claude; revisor: Codex; branch `docs/r005-missao-metodo`):
  - `AGENTS.md` §0, missão: valor medido por esforço poupado, erros evitados e resultado verificado;
  - `AGENTS.md` §3.4, método: acordo curto de tarefa, uma solução por problema, revisão por contraexemplo, destravar sem repetir, conferir o resultado real, corte do supérfluo;
  - `docs/parceria/protocolo.md` passa a apontar para o `AGENTS.md` e para as rodadas, sem caminho absoluto externo;
  - `STATUS.md`: "publicado em 27/09; verificado pelo Codex", e a CI remota não executou por bloqueio da conta. Não marcar CI verde nem mexer em plano ou cobrança.

## 5. App de campo: Meu dia, registro rápido e retorno (pedido do Adrianus)
**Crítica da seção do Codex na diretriz.** Aceita no mérito, com ajustes para não criar vocabulário nem regra paralela:
1. **Palavras:**
   - "Salvando / Salvo no aparelho / Enviado / Precisa corrigir" passam às da tabela única 74.4.3: Enviando → Salvo neste aparelho / Aguardando envio → Sincronizado (Ver recibo); Conflito (Revisar).
   - "Enviado" foi retirado de propósito: sugeria aceite central sem recibo.
   - "Precisa corrigir" é erro de campo, não situação de envio.
2. **Nome único:** a aba "Hoje" (64.1) e o MB-01 "Hoje no campo" passam a **Meu dia**, o mesmo nome do IN-01 na web.
3. **Três blocos com nome:** Agora / Depois / Impedidas. O impedimento usa o formato "{pendência} · {dono}" já existente no cap. 74, sem botão de execução.
4. **Som com limites:**
   - dois sons: salvo e precisa de atenção;
   - só em resposta a uma ação da pessoa, nunca na sincronização de fundo, no máximo um por ação;
   - ligado por padrão (o proprietário pediu) e desligável;
   - segue o modo silencioso quando a plataforma permite;
   - tudo funciona sem som.
5. **Estimativa:** identificada como "estimado", nunca preenchida como fato. Isso bate com o 64.2 e com "último valor nunca para quantidade".
6. **Aviso e impedimento separados**, com exemplos: hectares por hora acima do rendimento só avisam; área acima do saldo impede.

**Integração no PRD v3.10** (`edits/app_campo_64.json`, 5 edições com âncora única na v3.9):
- 64.7 novo, com aceites CAMPO-11 a CAMPO-16;
- 64.1 e CAMPO-02 renomeados;
- MB-01 com a rota `/app/meu-dia`;
- linha de rastreio.

Os componentes são os do cap. 74 (74.5.27 a 74.5.29 e 74.6.7). As regras de som entram no 74.5.29 quando o redator do 74b terminar, para não disputar o arquivo.

**Protótipo** (MB-01 com Agora/Depois/Impedidas, operador e almoxarife sobre o mesmo cenário, motivo da posição e som): **não iniciado.** Segui a prioridade do Codex de não abrir frente nova antes do harness. Proponho fazer em seguida, por ser o mesmo fluxo MB do lote atual. Se o Codex preferir fechar antes a v3.10, fica depois dela.

## 6. Próximo passo do Claude
1. O Codex revisa esta branch e integra (não integro o próprio trabalho).
2. Fechar a v3.10: os workflows dos caps. 73 e 74b ainda estão em execução; depois vêm a reconciliação por região, a montagem e a verificação.
3. Meu dia no protótipo (item 5), conforme a ordem acordada.
