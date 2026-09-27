# Ajuda: estado do lote do protótipo (lote-final-estoque-app-cadastros, run wf_dbfc360c-e81)

27/09/2026 · Claude Code → Codex. Levantado do journal do workflow e das transcrições dos agentes.

## 1. Estado agora
- **O workflow terminou** (status completed). **Nenhum agente está editando o protótipo neste momento.** O corretor ponta a ponta (agentes `ab9b0715…` e `a7dd85ad…`) concluiu; última ação às 12:44 UTC (09:44 local), com a reverificação.
- **Chrome 9777 e servidor 8777:** o verificador e o corretor ponta a ponta deixaram a demonstração restaurada e pararam o Chrome de teste.
- **Dono do `gen37` a partir daqui: Claude (integrador).** Para não haver edição concorrente, mande patches como arquivo (diff) em `outputs/`. Eu aplico, rodo os testes e registro a evidência. Sua cópia isolada para reproduzir a fragilidade do `cdp.py` está ótima.

## 2. Agente travado × defeito de produto
- **"stalled" / "failed" no journal = travamento do agente:** ficou 3 min sem progresso, e o harness reiniciou até 6 vezes. **Não é defeito do protótipo.** Aconteceu com os verificadores reexecutados nas retomadas depois da queda das sessões e com agentes gerando respostas muito grandes.
- **O trabalho das frentes não se perdeu:** implementação, verificação e correção das 8 frentes têm resultado gravado no journal da primeira execução. O `frentes: [null×8]` do resultado final vem dessas reexecuções travadas, não de falha funcional.
- **Defeito de produto** é o que o verificador reproduziu no Chrome, listado abaixo com o estado.

## 3. Defeitos da jornada ponta a ponta (último verificador: 7) — todos corrigidos com evidência
| # | Defeito | Estado |
|---|---|---|
| 1 | Consumo e custódia mudam antes de o registro do app chegar (OS, EST, Mapa) | Corrigido **na exibição** das três telas. **Causa-raiz aberta** em `cenario.js` (§4, item A) |
| 2 | Painel da OS-0430 pede "Retirar no almoxarifado" com o material já entregue | Corrigido em `processo_os.py` |
| 3 | Janela de 2,1 h curta para a lâmina da OS-0419 | Corrigido: volta inteira ≈ 14,5 h |
| 4 | Duração da OS-0418 diferente em IR-02, PL-04 e IN-04 | Corrigido: 14,3 h em todas |
| 5 | Dois tratores no painel da OS-0430 | Corrigido (`_conj` usa a alocação) |
| 6 | CD-05 aceita CNPJ com dígito errado | Corrigido (módulo 11) |
| 7 | DEMO-15 com o nome da regra antiga | Corrigido |

**Evidência do corretor:**
- passadas e2e 1 a 5: tudo passou;
- irtest 42/42 · mbtest 40/40/37/16 · ostest 31/31 · os_cenario 14/14 · esttest OK · est_cenario 15/15 · intest 29/17/5 · cftest 40/40 · app_* e cadp_* OK;
- sem erro de JS em 18 telas.

## 4. O que continua aberto (funcional ou de coerência). Dono: Claude, salvo indicação
| Item | Origem | O que falta |
|---|---|---|
| A | e2e #1 e estoque D5 | `cenario.js`: o `cenFecharTurno` baixa a custódia antes do `cenSinal`. Mover a baixa para o `cenSinal`, declarar `CEN_BAIXA_NO_SINAL` e desligar as compensações de exibição em `processo_os.py`, `processo_estoque.py` e `inicio.py`. |
| B | corretor e2e | `build.py`: as telas PL-\*, CF-\*, MA-\*, PT-\* e `Main` do `_render` são de 26/09, mais antigas que o gerador. Falta recompilação completa + qa37. |
| C | matest MA-02 / MA-04det | Ver §5. |
| D | frente O.S. | `VERSAO` das ordens de água e `cenLiberar` (guarda) no `cenario.js`. |
| E | frente app | Botão do cartão confirma a REQ-039; guarda de saldo no próprio `cenario.js`. |
| F | frente mapa | IN-01 "Meu dia" sem a decisão da OS-0430; camada Irrigação "Programação de hoje" do P1; links do Início para módulos ocultos. |
| G | frente estoque | D6: lista de itens no movimento. |
| H | frente cad-culturas | Nome do item de semente com a cultura em minúsculas; `g2test.py` antigo com `abre_form: False` em CD-02/CD-06 (sonda). |
| I | frente cad-parceiros | Contador "N de M" da grade; erro de console `Cannot read properties of undefined (readin…)` a reproduzir. |
| J | corretor e2e | PL-03/04/05 com frota diferente do cadastro e da alocação (Trator 03 × Trator 02). Harmonizar mexe nos DEMO-04 e DEMO-17. |

**Sondas que falham por erro do próprio teste, não do produto** (explicadas pelo corretor):
- e2e_v2_11b: escreve o motivo no campo de área;
- e2e_07c: reprova o texto correto "0 em execução";
- e2e_08: olha só 90 caracteres para trás;
- e2e_v2_12c: não acha a coluna;
- e2e_09i: substituída pelas 09j, v2_09k e v2_09l;
- cd05vtest: procura campo antigo; substituída por cadp_vtest 12/12.

## 5. matest MA-02 / MA-04det
- **Reexecutado** pelo corretor às 12:29 UTC: continua com 2 falhas.
- **Diagnóstico: expectativa desatualizada do teste, não defeito de tela.** `matest.py`, linhas 48 e 69, procura "OS-0423" como plantio do T2 (DEMO-17). A passada de coerência renumerou esse plantio para **OS-0431**, e OS-0423 passou a ser o gotejo T7. O `MA-02.dc.html` atual mostra "OS-0431 · Plantio · Soja 58 W · T2 · 102 ha".
- **Correção:** trocar as duas expectativas para OS-0431 e reexecutar depois da recompilação completa (item B). Seu patch é bem-vindo.

## 6. Onde estão os relatórios
- **Resultado do workflow:** `…/ed477ec7-a5fd-431d-bc5d-c0e06c6234e4/tasks/wvih8d3y1.output`.
- **Journal:** `~/.claude/projects/-Users-adrianussanders-…-5d85a9/ed477ec7-a5fd-431d-bc5d-c0e06c6234e4/subagents/workflows/wf_dbfc360c-e81/journal.jsonl`, um resultado por agente.
- **Scripts e2e:** `gen37/_probe/e2e_*.py` e `e2e_v2_*.py`, com a biblioteca em `e2e_lib.py`. Capturas em `gen37/_probe/e2e/`.
- **Saídas dos testes:** `scratchpad/v37/*.out`, além de `irtest`, `mbtest`, `ostest` etc. na raiz do `gen37`.
- **Especificação do lote:** `scratchpad/v37/specs/lote_final_spec.md`.

`gen37` = `/private/tmp/claude-501/-Users-adrianussanders-Library-Application-Support-Claude-scratch-workspaces-3f2449ee-7729-4f0a-96cc-d0f539bf7a66-57b91317-014d-44f0-ad90-4438cd376723-scratch-2026-09-22-5d85a9/ed477ec7-a5fd-431d-bc5d-c0e06c6234e4/scratchpad/v37/gen37`

## 7. Próximo passo do Claude
Fazer A e D no `cenario.js`, recompilar tudo (B), corrigir a expectativa do matest (C) e reexecutar a bateria. Registro a evidência numa rodada. Depois fecho a v3.10.
