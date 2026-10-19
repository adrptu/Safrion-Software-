# PA-OPER F1 · Plano agronômico por operação, uma operação por vez, 19/10/2026

**Pedido do proprietário (16/10, 14:27; 18/10):** planos agronômicos seccionados por operação, com as especificidades de cada uma e foco total, uma coisa bem feita por vez.
**Especificação:** `docs/integracao/V71/PA-OPER.md` R3 (`10f37c52`, parecer favorável do Codex). Acordo da implantação: PR #47, comentário 6268255695.
**Autoria:** Claude. **Revisão e integração:** Codex. **Base:** `e32ada5e` (MAPA-REAL F2, sobre MAPA-FROTA F1). **Branch:** `claude/v44-pa-oper-f1`.

## Resultado útil
Em **Agrícola › Planos agronômicos**, o plano abre com uma faixa: **Visão geral** e as operações na ordem do ciclo, cada uma com o número de atividades e o estado em texto (✓ Pronta, • Pendente, ⚠ Com aviso, ⛔ Impedida). Um toque põe a operação em foco:
- só as atividades dela e o bloco **Parâmetros de <operação>** com as conferências;
- na Pulverização, o **volume de calda da operação** (vale para as atividades sem valor próprio) e a **calda própria** de cada atividade, editável na linha;
- o **alvo** de cada pulverização (no painel da atividade), opcional: com ele, a dose é conferida pelo uso daquele alvo na bula; sem ele, pelo uso mais permissivo, e a operação não fica "Pendente" (proprietário 19/10, desvio 8);
- **Deslocar gatilhos**: adia ou antecipa de uma vez todas as atividades da operação (K7);
- endereço próprio (`#plano=SOJA-AT&op=pulverizacao`): F5 reabre a mesma operação; Esc fecha primeiro o editor, depois o foco, depois o plano.

**Bula na versão** (base de demonstração da AG-07, por cultura × alvo): dose acima da bula, carência que termina depois da próxima colheita prevista e número de aplicações acima do máximo impedem publicar, com o motivo; unidade da bula diferente da do plano e mesmo grupo de modo de ação em sequência são só aviso.

**Rascunho e publicação** (decisão 9): toda mudança vai para o rascunho vN+1, que se guarda sozinho no cenário compartilhado, mesmo incompleto ou inválido, e reabre depois de sair ou recarregar. Publicar é ato explícito:
- com o papel de agrônomo: **Salvar e publicar vN** (o pedido de 14/10, "deixe o botão salvar", com o achado 1 do Codex: publicação explícita);
- sem o papel (PCP): o rascunho fica guardado e a nota diz "Rascunho vN guardado. O agrônomo publica ao abrir o plano."; a versão vigente segue até lá. Não há etapa de submeter nem devolver (proprietário 19/10, desvio 8);
- o segundo clique não cria vN+2; publicar o plano não aprova nem libera O.S.

**Do plano à O.S.** (transporte mínimo, decisão 10): a O.S. nova lê a calda da versão do plano em que o cultivo está e grava o **retrato** da instrução (versão do plano, calda e origem, tanque do pulverizador do conjunto no cadastro de agora). Editar o cadastro depois não muda a O.S. emitida; "Trocar conjunto" antes da execução refaz o retrato. Publicada uma versão com outra calda, a O.S. em A liberar emitida da anterior mostra "Plano vN difere: volume de calda …" e não muda sozinha.

**Ficha e app de campo** (EX-38 R10): **Vazão por bico** alvo (volume × velocidade do REND × espaçamento ÷ 600) ao lado da disponível (curva ponta × pressão, outra fonte), com a diferença em %; sem velocidade, espaçamento ou curva, "desconhecido", nunca um padrão.

**Dano evitado:** dose, carência e número de aplicações fora da bula publicados sem ver; calda digitada em quatro lugares; O.S. emitida que muda quando alguém edita o cadastro; plano que muda a O.S. sem aviso; número inventado onde falta dado.

## Serviço único (ENG-011)
`tools/prototipo/v37/gen37/operacoes.js` (no `cenario.js_prefixo()`, igual para PA, O.S., ficha e app): seções e família, herança operação → atividade, alteração de parâmetro, vazão alvo × disponível, dose por hectare, bula, pendências, estado, publicação e deslocamento de gatilhos. As cargas continuam só em `cenPreparoOrdem` (EX-38 R1, decimal); a fórmula duplicada `opCargas` foi removida.

## Comandos e resultados (executados em 19/10, árvore desta branch, dados sintéticos)
Todos em `tools/prototipo/v37/gen37`. Testes de navegador com `CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico` sobre o `_render` do build sintético desta árvore.

| Comando | Resultado | Bruto |
|---|---|---|
| `node pa_oper_unit.js` (serviço: seções, herança, vazão, dose, bula, estado, publicação, K7; mutantes m1–m3) | **42/42** | `pa_oper_unit.log` |
| `python3 -B pa_oper_cen_test.py` (P4 cargas na fonte única, P19 retrato) | **7/7** | `pa_oper_cen.log` |
| `python3 -B pa_oper_p15_test.py` (P15: demanda das 4 safras, impressão digital dos 8 planos, c2, campos novos; mutante M1) | **5/5** | `pa_oper_p15.log` |
| `python3 -B pa_oper_test.py` (P1–P3, P7, P12, P13, P15e/f, P16, P17, P18, P19, P19b, K2, K3, K5, K7) | **24/24**; cliques medidos: K2 4 · K3 3 · K5 5 · K7 5 (tetos 4, 4, 6, 6) | `pa_oper_test.log` |
| `pa_lista_test.py` (K1: 4 cliques e 5 teclas, igual ao antes) | 24/24 | `reg_pa_lista_test.log` |
| `pa_regras_test.py` | 18/18 | `reg_pa_regras_test.log` |
| `ds_1610_test.py` | 16/16 | `reg_ds_1610_test.log` |
| `paginas_scan_test.py` | 5/5 (147 páginas) | `reg_paginas_scan_test.log` |
| `os_cenario_test.py` · `carencia_test.py` · `demanda_unica_test.py` · `demanda_unica_nav_test.py` | 22/22 · 90/90 · 71/71 · 29/29 | `reg_*.log` |
| `alocacao_unit_test.py` · `cen_grava_test.py` · `ficha_pivo_unit_test.py` · `ficha_pivo_test.py` · `mapa_frota_test.py` | 21/21 · 10/10 · 23/23 · 21/21 · 20/20 | `reg_*.log` |
| `ex38_test.py` | 16/17, **igual à base** (P3, ver desvio 6) | `reg_ex38_test.log`, `reg_ex38_test_BASE.log` |
| `saf_operacoes_test.py` | 85/87, **igual à base** (N6 e P4 do Planejar safra, não tocados aqui) | `reg_saf_operacoes_test.log`, `…_BASE.log` |
| `mbtest.py` | MB-02 "excesso 220 px", **igual à base** (já registrado na Base verde 2) | `reg_mbtest.log`, `reg_mbtest_BASE.log` |

Os testes que abrem a tela de planos (`pa_oper_test`, `pa_lista`, `ds_1610`, `paginas_scan`) rodaram no build final, já com o K7 e os alvos de 44 px. Os demais rodaram no build anterior ao K7. A diferença entre os dois builds está só em `processo_planos.py` e numa função nova, `opDeslocar`, que só a tela de planos chama.

**Fotos** em 1440 e 390 px (visão geral, Pulverização em foco, MILHO-SF com calda "Pendente", ficha da OS-0424, editor do K7) foram conferidas. Elas ficam fora do repositório. Na foto de 390 px, o campo de dias do K7 tinha 28 px de altura. Foi corrigido para 44 px, e o P16 agora mede também o campo, o Aplicar e o Cancelar.

## Contraprova
Rodada na ponta antes da F1, `e32ada5e` (`ANTES=<_render dessa ponta>`, árvore limpa, dados sintéticos):
- `pa_oper_test.py`: **1 ok · 18 falhas** (`contraprova_base_pa_oper_test.log`).
  - Não há na base: faixa com estado, foco, calda, bula na versão, publicação explícita, rascunho guardado, transporte da versão para a O.S., retrato, vazão por bico, migração "Pendente", deslocar.
  - O roteiro K para no K7, porque "Deslocar gatilhos" não existe na base. Numa rodada anterior, o K5 (percorrer as operações pelos chips) passou também na base: é comportamento que já existia, e só não pode piorar.
  - O único ok é "sem erro de JavaScript".
- `pa_oper_cen_test.py` na base: `contraprova_base_pa_oper_cen.log`.
- P15 (migração) passa nas duas versões quanto à demanda, como a especificação pede. O mutante obrigatório M1, que preenche a calda por código em todos os planos, reprova o P15d.
- Mutantes de cálculo da especificação que valem para a F1 têm um caso que os reprova:
  - última carga cheia: `pa_oper_cen` P4d (41.5: 500 + 500 + 200 L, 24 L de produto);
  - velocidade padrão quando falta: `pa_oper_unit` P18b;
  - calda pendente que vira padrão: `pa_oper_unit` P3c.
  - Os mutantes não foram rodados de novo como código separado nesta entrega.

## Desvios do aceite e decisões de implementação
1. **Colunas da família.** O P2 pede "as colunas da família" na operação em foco. Implementado como uma linha de informação na atividade (alvo, calda e origem, carência), nos Cartões e na Tabela, e não como colunas novas da Tabela. Motivo: a Tabela é do motor comum (TAB-11/DS); coluna por família pede mudança no motor, que fica para a F2 com o Codex.
2. **Oráculos antigos atualizados, com o motivo na docstring:** `pa_regras_test.py` e `pa_lista_test.py` editavam doses que agora passam da bula (0,6 → 0,45 L/ha no Fungicida A; Glifosato 6 → 2,5 L/ha, máximo 3) e liam "Salvar alterações" / "Publicado · vN" (agora "Salvar e publicar vN" / "Publicada vN"). L18: o plano novo persiste no F5 (decisão 9). L1: a palavra "impedida" do estado da operação deixa de reprovar. K1 medido: 4 cliques e 5 teclas, igual ao antes.
3. **Semente de demonstração:** só SOJA-AT v6 · Pulverização · 100 L/ha, marcada "demonstração", para a OS-0421 manter os números de hoje (PA-OPER §Migração). Os outros 7 planos ficam "Pendente" (P15d, P15f).
4. **Curva da ponta:** a05 ganhou espaçamento 0,5 m, ponta leque 110-015 a 3 bar e uma curva de catálogo (0,59 L/min), marcada "catálogo de ponta (demonstração)". Não é medição da fazenda.
5. **Achados de dados da semente (para o Codex e o RT):**
   - CAFE-AR · Fungicida C 0,8 L/ha > máximo de 0,75 → ⛔ (o plano café abre "Impedida" na Pulverização);
   - MAMAO-PROD · Abamectina: carência termina 6 dias depois da colheita prevista → ⛔;
   - SOJA-AT · Fungicida 2ª: mesmo grupo de modo de ação da aplicação anterior → ⚠;
   - SOJA-AT e MILHO-SF · Inseticida B: bula em kg/ha × plano em L/ha → ⚠ "dose não conferida".
6. **ex38_test P3** está vermelho já na base (16/17, mesmo motivo, log em `brutos/`): o teste exige 1e-12 contra a quantidade arredondada aos centésimos por `cenQtdTrecho`. Não vem desta frente. O retrato também anula a variação de `CEN_PREP_ATIVOS` que o P3 faz na OS-0421; proposta ao Codex: o P3 variar `instrucao.tanque`.
7. **390 px:** a faixa quebra em uma operação por linha (6 linhas no SOJA-AT). A base já quebrava assim (foto conferida); fica como melhoria possível de padrão (faixa com rolagem horizontal), fora desta fatia.
8. **Leve e fluido (proprietário, 19/10: "Não quero um sistema travado e burocrático, quero leve e fluido").** Aplicado o AGENTS §4 (trava só onde protege algo concreto):
   - **Saiu o ciclo submeter → em revisão → devolver** (decisão 9 e telas da PA-OPER §Revisão, item 1, na parte do AG-05 "revisão"). Era uma etapa a mais entre editar e publicar, sem dano concreto que só ela evitasse: a bula continua impedindo publicar, e publicar continua sendo de quem tem o papel. O serviço `opPublicar` só conhece "publicar"; "submeter" volta "ato desconhecido" e não cria versão.
   - **O alvo deixou de ser pendência no plano.** Pendência nunca impediu publicar; só pintava a operação de "Pendente". A conferência da bula sem alvo já usava o uso mais permissivo. A lista do foco mostra só ⛔ e ⚠ e, sem alvo, uma linha cinza que explica a conferência.
   - **Saiu o "clique de novo" (R1 da revisão NAV-1).** Antes, com a dose aberta no campo, "Salvar e publicar" ficava desabilitado; e o clique que gravava a dose pela saída do campo não publicava, pedindo um 2º clique. Agora a dose aberta e válida entra no mesmo clique, a bula é conferida com ela e o aviso diz "inclui <produto>: a → b L/ha". Dose inválida não publica e o erro fica no campo (R2). Dose acima da bula entra no rascunho e não publica, com o ⛔ no aviso.
   - **Quem não tem o papel** vê a nota "Rascunho vN guardado. O agrônomo publica ao abrir o plano." à vista (sem ela, a barra ficava vazia).
   - **Continua travado, com o dano:** dose, carência e número de aplicações fora da bula impedem publicar (lei e resultado técnico); publicar é do papel de agrônomo (AG-05, CMD-02); a O.S. segue com aprovação agronômica individual (PRD 41/73.9). A PA-OPER §Pulverização pede "receituário sem alvo" travado na aprovação da O.S.; essa conferência ainda não existe no protótipo, nem antes desta mudança, e fica registrada para a O.S.
   - **Oráculos trocados, com motivo:** `pa_oper_test` P1 (Pulverização do SOJA-AT passa de "• Pendente" a "⚠ Com aviso": restam os avisos de grupo de modo de ação e de unidade da bula), P12a (Caio sem primária e sem "Submeter") e P12b (Ana publica, sem "Devolver"); `pa_oper_unit` E4 (só a calda é pendência), P12d (submeter é recusado) e P12e (publicar segue a numeração da última publicada); `pa_lista_test` L14a/b/c (um clique publica com a dose aberta; dose 0 não publica); `pa_regras_test` U5 (dose aberta não desabilita) e U14 (publicar com a dose aberta, válida, inválida e acima da bula).

## Rodada "leve" (19/10, executada no build de `cbe4cd38`: PA leve + MAPA-REAL F2 + correção K4, dados sintéticos)
Brutos em `brutos/leve/` (`resumo.txt` e um log por teste).

| Teste | Resultado |
|---|---|
| `pa_oper_unit.js` | 42/42 |
| `pa_regras_test.py` | 18/18; contraprova na `ccda8c8d` 16/18 (U5 e U14 reprovam) |
| `pa_oper_test.py` | 24/24; contraprova no build da `ccda8c8d` 22/24 (P1 e P12a reprovam) |
| `pa_lista_test.py` | 24/24 (L14 com o publicar num clique) |
| `pa_oper_p15_test.py` · `pa_oper_cen_test.py` | 5/5 · 7/7 |
| `ds_1610_test.py` · `paginas_scan_test.py` | 16/16 · 5/5 (147 páginas) |
| `frota_unit.js` · `mapa_frota_test.py` (K4 juntado) | 57/57 · 23/23 |
| `mapa_real_semdado_test.py` · `tools/geo` (`s2_l2a_test` e `s2_l2a_montagem_test`) | 3/3 · 18/18 |

## Fora desta fatia (PA-OPER decisão 10)
F2: Plantio e Tratamento de sementes (população, PMS, germinação), etapa 2 do Planejar safra com o resumo por operação e o ajuste por talhão, aplicar a vN nova ao cultivo. F3: Adubação e correção, fertirrigação. F4: Colheita, tratos, poda e preparo.

## Artefato (executado)
**v148**, versões 166 e 167 (`1792425796-a2a8` e `1792425816-955b`).
- Publicadas as 60 páginas que mudam com esta frente: o `operacoes.js` entra no prefixo comum. A lista saiu da comparação do render da base com o desta branch.
- As páginas foram montadas da árvore com os dados reais da Lagoa Grande, fora do Git, como na v147. A varredura nessa árvore deu 5/5 nas 147 páginas.
- As 60 foram lidas de volta e são idênticas, byte a byte, às enviadas.

## Brutos
`brutos/`: saídas completas dos comandos acima e da contraprova.
