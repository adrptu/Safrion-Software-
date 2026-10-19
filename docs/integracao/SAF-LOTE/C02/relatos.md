# Relatos da SAF-C02 (capacidade simétrica entre safras abertas: `62b0904`, `f52fa09` e `1671671`)

Fonte: resultado do workflow `saf-c02` (run `wf_5f27fb5e-812`, concluído em 09/10 às 21:38 UTC), o mesmo texto do `journal.jsonl`.

As fases foram:
1. **autor:** `62b0904`;
2. **verificação:** três lentes sobre `62b0904` (simetria, tela e regressão). São agentes Claude separados; **não é a revisão do Codex**. A lente de regressão só concluiu na 3ª tentativa;
3. **fechamento:** as correções (`f52fa09`) e as saídas brutas (`1671671`).

Rótulos:
- **executado:** a saída está no pacote, no diff (pasta `docs/planejar-safra/verificacao-saf-c02/saidas/`, descrita no `LEIA-ME.md` dela) ou em `brutos/`;
- **relatado:** o agente diz que rodou, mas a saída não está no pacote.

## Resumo

### Achados da verificação de `62b0904` e o que o fechamento fez

| ID | Lente | Sev. | Achado | Fechamento |
|---|---|---|---|---|
| V1-1 | simetria | S4 | Com 3 ou mais safras, o percentual muda conforme a safra aberta, pela ordem da soma em ponto flutuante (anterior). Brutos: `C02-ver-simetria_*` | corrigido: soma em ordem fixa; caso mínimo dá "5 %" nas três vistas (`saidas/min-float-*.json`) |
| V1-2 | simetria | S4 | O R1 atribui ao "calendário" ocorrências que estão fora do período | corrigido: motivo do R1 pelas contagens |
| V1-3 | simetria | S4 | Com o mesmo período, as vistas mostram meses diferentes na grade | corrigido: `g_cap` com o calendário inteiro |
| V2-1 | tela | S3 (anterior, fora do diff) | PL-03 com números fixos contradiz a etapa 3 | corrigido só nas entradas: "Ver capacidade" do PL-02, PL-04 e PL-05 abre a etapa 3. A página PL-03 fica sem link; registrado em FORA-DE-ESCOPO |
| V2-2 | tela | S4 | Mesmo ponto do V1-3 | corrigido |
| V2-3 | tela | S4 | "≥" só na vista da safra dona das horas | corrigido |
| V2-4 | tela | S4 | "Tratores: 1 unidades" | corrigido |
| V3-1 | regressão | S4 | A S27SF passa de R5 (verde) a R4 (amarelo) quando a S2627 termina antes de jul/27. Brutos: `C02-ver-regressao_probe-*` | **não mudado:** é o que a decisão do Codex pede. Registrado em DECISOES, com a alternativa para o Codex decidir |
| V3-2 | regressão | S4 | `capSaf` soma em silêncio quando falta `ini`/`fim` | corrigido: contrato com erro explícito (`saidas/harness-original-na-correcao.err.txt`) |
| V3-3 | regressão | S4 | Rótulo "dados reais locais" do `montar_render` é enganoso: o dado é sintético | corrigido: "dados da Lagoa Grande: sintéticos 5/5" |

### Testes do fechamento (todos com `SAFRION_DADOS=sintetico`)

| Comando | Resultado | Rótulo |
|---|---|---|
| harness original na base `16d6734` | igual a `antes.json`: A 340 h (R2), B 140 h (R4) | executado: `saidas/harness-antes-base16d6734.json` |
| harness adaptado na correção | A e B com 140 h, R4, `same_total` true | executado: `depois.json` |
| harness original na correção | erro explícito "a safra B chegou sem o período" | executado: `saidas/harness-original-na-correcao.err.txt` |
| `capacidade_unit.py` | 101 OK · 0; os testes novos no código da `62b0904` dão 5 FALHA | executado: `saidas/capacidade_unit*.log` |
| `saf_capacidade_simetrica_test.py` (1440 e 390) | 38 ok · 0; no render da `62b0904`, 10 falhas | executado: `saidas/saf_capacidade_simetrica_test*.log` |
| `links_ocultos` 8/8, `rend_multiconjuntos_unit` 106/106 | sem falha | executado: `saidas/` |
| `camada_test.py` | 16/17: o 17 (novo) passa; o 16 (versão do cenário) já falhava na `62b0904` | executado: `saidas/camada_test*.log` |
| `saf_operacoes` 87/0, `saf_revisao` 42/0, `tabelas_saf` 24/24, `saf_cmp_continuidade` 31/0, `etapas_celular` 14/0, `acao_unica` saf e v3 10/0, `rend_multiconjuntos` 18/18, 5/5 e 9/9 | sem falha | executado: `saidas/*.log`. Rodaram sobre o build anterior à troca dos links do PL; depois só mudou `areas/planejamento.py` |
| `partest` | 46 ok · 1 falha (T1-C, vermelho conhecido) | executado: `saidas/partest.log` |
| `varredura` | 140/140 | executado: `saidas/varredura.log` (build final) |
| propriedade e simetria (2000 e 10000 sorteios, `txt_check` com 3000) | 0 falhas; 0 divergências (eram 9) | executado: `saidas/simetria-*`, `saidas/txt-3000-*`. Os scripts ficaram fora do repositório |
| `build.py` / `montar_render.py` | 0 FALHA / 140 páginas | executado: `saidas/build.log`, `saidas/montar_render.log`, `brutos/SAFC02-build.log` |

### O que o revisor confere (fila do integrador)
- **Total mensal elegível igual ao alternar A↔B com o mesmo período:**
  - cenário do Codex: 140 h nas duas vistas, com a B2 "fora da conta" nas duas;
  - controle com a B2 dentro do período: 340 h e R2 nas duas;
  - outra fazenda e safra encerrada continuam excluídas.
- **Três safras ou mais:** o percentual é igual em todas as vistas.
- **Tela, em S2627 e S27SF com 01/09/2026 a 12/07/2027:**
  - mesma ocupação de jul/27 nas duas vistas;
  - carga de fora identificada;
  - sem rolagem lateral a 1440 e a 390.
- **"Ver capacidade":** no PL-02, PL-04 e PL-05, abre `SAF.dc.html#saf=S2627&passo=operacoes`.

## autor

**Commit:** `62b0904` na branch `claude/v44-saf-c02` (worktree `<sp-safc02>`, base `16d6734`). Sem push e sem PR. São 11 arquivos, com 507 linhas acrescentadas e 25 removidas.

Apliquei a decisão proposta pelo Codex sem mudar a regra. A ocorrência de qualquer safra entra ou sai da capacidade pelo período da safra de origem, seja qual for a safra aberta. Fato, custo e datas ficam intactos. A carga de outra safra que fica fora da conta aparece no veredito, então a tela não fica verde por engano.

#### O que mudou (arquivo:linha)
- **`tools/prototipo/v37/gen37/safra.js`**
  - **:309 `capSaf`:** cada item de `outras` passa a ser `{id,nome,ini,fim,oc}`.
    - A classe das ocorrências das outras safras sai de `classeOc` com o período de cada uma; as desta safra continuam em `i.cls`. O mesmo filtro vale para as duas.
    - A carga excluída vai para `g.fora` (`{sid, cls, mi, h, n}`, com `sid` null quando é desta safra) e não entra na conta.
  - **:333 `capForaOutras`, usada em :344 `capVeredito`:** o "Fora da conta" cita a carga de outra safra nos meses e recursos em que esta safra tem demanda, com número, motivo e horas. Exemplo: "1 ocorrência da B depois do fim dela (Tratores 200,0 h)".
  - **:924 `outrasSafras`:** passa `ini` e `fim` de cada safra.
  - **:955 `e3Fora`, usada em :959 (`aria-label` da célula) e :1000 (linha do filtro):** mostra "fora da conta: Safrinha 2027 78,6 h depois do fim dela", ou "desta safra … depois do fim" quando a carga é da própria safra.
- **`dados2.py`**
  - **:753 `capacidade`:** agora espelha o `capCalc`, com o período de cada outra safra.
  - **:760 `cap_saf`:** é o núcleo puro, espelho do `capSaf`, e também guarda a carga excluída em `fora`.
  - **:736 `cap_rec`:** aceita `meses` e `dias`.
- **`capacidade_unit.py:202`:** 18 casos novos, com o cenário A/B, o controle, outra fazenda e safra encerrada, o cenário real, custo, paridade JS × Python e o teste de propriedade. A função `job` passa o período das outras safras.
- **`saf_capacidade_simetrica_test.py` (novo):** teste do caminho na tela, descrito abaixo.
- **`ESPECIFICACAO.md:252` e `DECISOES.md:25`:** uma linha cada com a regra e o dano evitado: o mesmo mês dar falta numa safra e folga na outra só por causa da navegação.
- **`docs/planejar-safra/verificacao-saf-c02/`:**
  - `antes.json` (sha256 `0f00e6e1…8a874`) e `depois.json` (sha256 `49eb8b9e…f9ce`).
  - `harness_original.js` e `harness_adaptado.js`.
  - `LEIA-ME.md` registra a adaptação: só a linha 14 do harness mudou, com `outras` levando `ini` e `fim` de `period[oid]`. A fixture é a mesma e a checagem de hash não foi usada, porque a fonte mudou.

#### Comandos e resultados (todos executados)
| Comando | Resultado |
|---|---|
| `CHECA_HASH=1 node harness_original.js safra.js` (base, sha256 d96875f8…) | A: 340 h, R2 vermelho. B: 140 h, R4 amarelo. `same_total: false` (defeito reproduzido) |
| `node harness_adaptado.js safra.js` (depois) | A: 140 h, R4, cita a B2 fora da conta. B: 140 h, R4. `same_total: true` |
| `capacidade_unit.py` na base, já com os testes novos | 83 OK, 11 FALHA (todas SAF-C02, como esperado) |
| `capacidade_unit.py` depois | 94 OK, 0 FALHA |
| Propriedade só com o JS (150 sorteios, 372 vistas, script no scratchpad) | Base: 138 de 150 sorteios divergem do oráculo. Depois: 0 |
| `saf_capacidade_simetrica_test.py` na base | 14 ok, 12 falhas (Tratores jul/27: 140,3 h com a S2627 aberta, 61,7 h com a S27SF) |
| `saf_capacidade_simetrica_test.py` depois | 28 ok, 0 falhas |
| `python3 build.py > /tmp/SAFC02-build.log`; `grep -c FALHA` | 0 |
| `montar_render.py` | 140 páginas |
| `varredura.py` | 140 de 140 páginas sem erro |
| `saf_operacoes_test.py` | 87 ok, 0 falhas |
| `saf_revisao_test.py` | 42 ok, 0 falhas |
| `tabelas_saf_test.py` | 24 de 24 ok |
| `saf_cmp_continuidade_test.py` | 31 ok, 0 falhas |
| `rend_multiconjuntos_unit.py` | 106 de 106 OK |
| `demanda_unica_test.py` | Não existe nesta base; é da frente CTL-4 |

**Aceite coberto nos testes:**
- **Cenário do Codex:** 140 h nas duas vistas.
- **Controle com B2 dentro do período:** 340 h nas duas, R2 nas duas.
- **Antes do início:** 250 h nas duas.
- **Outra fazenda e safra encerrada:** continuam fora (`outras_safras` e a tela).
- **Custo:** o custo de operação da S27SF (R$ 180.888,10) inclui as colheitas fora da conta.
- **Paridade JS × Python:** confere na fixture, no cenário real e nos 150 sorteios.

**Caminho na tela (1440 e 390 px):**
- Pelo botão Editar da etapa 1, as duas safras recebem o mesmo período, 01/09/2026 a 12/07/2027.
- Abre a S2627 em "Continuar → Dimensionar operações ›".
- Troca para a S27SF em "Trocar safra → Continuar → ‹ Operações e recursos".
- Tratores e Operadores e equipe de jul/27 mostram a mesma ocupação nas duas vistas, igual à do espelho Python.
- A carga de fora fica identificada no veredito, no filtro e no `aria-label`.
- Sem rolagem lateral e sem erro de JS.

#### O que ficou fora
- Não atualizei `docs/STATUS.md` nem o artefato do protótipo. Ficam para quem integrar na `claude/prototipo-v44`, para não disputar com as outras frentes.
- Não mexi em `ocupacao.*` (SAF-C01) nem na demanda (CTL-4).
- O veredito só cita a carga de outra safra nos meses e recursos em que a safra aberta tem demanda. Nos outros meses ela não muda a decisão e não é citada.
- Para a própria safra, o veredito continua mostrando só a contagem, como já era. As horas dela aparecem no filtro e no `aria-label`.
- Não rodei a bateria completa nem os vermelhos conhecidos da base. O regime do protótipo pede só os testes do módulo mexido.
- `_render/`, `project/` e `_probe/` foram gerados pelo build e testes e não entraram no commit. O build montou o `_render` com os 5 arquivos reais locais da Lagoa Grande presentes; os testes de navegador rodaram com `SAFRION_DADOS=sintetico`.
- A revisão do Codex sobre esta correção ainda está pendente.

## verificacao

Três lentes independentes (agentes Claude separados do autor; não é a revisão do Codex). Texto de cada achado como a lente registrou; "executado"/"especificado" são da própria lente.

### Lente simetria

#### simetria-1 · S4 · Com 3 ou mais safras abertas da mesma fazenda, a ocupação exibida muda conforme a safra aberta (efeito da ordem da soma em ponto flutuante)
- **reproducao:** Executado. Comando: cd <scratchpad>/safc02-simetria && node min_float.js fix_safra.js '[0.1,0.1,7]'. Cenário mínimo: A, B e C abertas, mesmo período 01 a 28/02/2027; 1 trator com 20 dias × 8 h = 160 h; uma ocorrência de cada em 10/02, com 0,1 h, 0,1 h e 7,0 h. Saída: vista A d=7.199999999999999, '4 %'; vista B d=7.199999999999999, '4 %'; vista C d=7.2, '5 %'. O valor exato é 4,5 %, que arredonda para '5 %'. O espelho Python (dados2.cap_saf + fmt_ocup) dá A '4 %', B '4 %', C '5 %': a paridade se mantém em cada vista, mas a simetria do que a pessoa lê falha. Na varredura aleatória (python3 txt_check.py fix_safra.js 3000 11) saíram 9 divergências em 117.762 células. Exemplo: cenário 2110, Tratores, '1 %' numa vista e '<1 %' nas outras, com d 7,5 contra 7,499999999999999. A base 16d6734 dá a mesma saída no caso mínimo, então o defeito é anterior à correção.
- **causa:** tools/prototipo/v37/gen37/safra.js:313 acumula a safra aberta em dThis e as outras em dOth, na ordem de 'outras'. Em safra.js:317, d=g.dThis[mi]+g.dOth[mi]. Com 3 ou mais safras, a associação muda com a safra aberta, por exemplo A+(B+C) contra B+(A+C), e o resultado difere no último bit. fmtOcup (safra.js:301, Math.round e o<1) e o espelho (dados2.py:794 e fmt_ocup:809) arredondam exatamente nessa fronteira. 'nec' e 'red' não são afetados, porque ficam protegidos pelo −1e-9 do ceil. Com 2 safras o resultado é idêntico bit a bit, pela comutatividade, por isso o cenário do Codex não pega o caso.
- **correcao:** Antes de calcular ocupação e necessárias, arredondar a demanda da célula a uma grade fixa, nos dois lados e com a mesma regra. Em JS: const d=Math.round((g.dThis[mi]+g.dOth[mi])*1e6)/1e6. Em Python: d=_math.floor((g['dThis'][mi]+g['dOth'][mi])*1e6+0.5)/1e6. Testei a versão JS em scratch (cand_arredonda.js): o caso mínimo deu '5 %' nas 3 vistas; txt_check com 3000 cenários deu 0 divergências; simetria.py com 2000 cenários deu 0 falhas. Falta a regressão em capacidade_unit.py com a fixture [0,1; 0,1; 7,0] h e 160 h, esperando '5 %' nas três vistas em JS e em Python. No software real, decimal (ENG-013) elimina a causa.

#### simetria-2 · S4 · O veredito R1 atribui ao 'calendário do protótipo' ocorrências que estão no calendário, mas fora do período da safra; a outra vista dá outro motivo para as mesmas ocorrências
- **reproducao:** Executado. Comando: python3 <scratchpad>/safc02-simetria/r1_texto.py, sobre uma cópia limpa do commit 62b0904 com dados sintéticos e a S27SF com período 01 a 31/08/2027. Saída: as ocorrências caem em fev–jul/27 e nenhuma está fora do calendário; cls={antes:14, cal:0}. Veredito: R1, 'Capacidade não calculada: as 14 ocorrências desta safra ficam fora do calendário do protótipo (set/26 – ago/27).' Na vista da S2627, depois da correção, as mesmas ocorrências aparecem como 'antes do início dela'. Caso mínimo sintético, do encolhimento: uma safra com período 24/01 a 21/03/2027, calendário jan/27 e uma ocorrência em 08/01/2027. Resultado: R1 'a ocorrência desta safra fica fora do calendário do protótipo (jan/27 – jan/27)'.
- **causa:** tools/prototipo/v37/gen37/safra.js:348: o R1 dispara com !x.cls.cal, o que inclui 'antes' e 'depois', mas o texto supõe sempre 'fora do calendário'. Também devolve antes de foraTxt, então a contagem 'antes do início' some. A ESPECIFICACAO.md:199 define o R1 como 'nenhuma ocorrência desta safra no calendário', e o código diverge da especificação. O defeito é anterior à SAF-C02 e fica fora do escopo estrito dela, mas agora as duas vistas explicam a mesma carga de formas diferentes.
- **correcao:** No ramo R1, montar o texto a partir de x.cls. Manter o texto atual só quando x.cls.fora===oc.length. Nos outros casos, usar algo como 'Capacidade não calculada: nenhuma ocorrência desta safra cai no período dela (dd/mm/aaaa a dd/mm/aaaa).', seguido de foraTxt com as contagens 'antes do início' e 'depois do fim'. Ajustar a ESPECIFICACAO §3.1 (R1). Regressão em capacidade_unit.py: S27SF com período em ago/27, esperando o novo texto.

#### simetria-3 · S4 · Com o mesmo período, as duas vistas mostram conjuntos de meses diferentes na 'Capacidade por mês' (a grade da safra fixa não cresce quando o período aumenta)
- **reproducao:** Executado. Comando: env UI_COPIA=copia CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 ui_grade.py, no diretório de scratch, com 1440 px. Pela tela, a S2627 e a S27SF receberam o período 01/09/2026 a 12/07/2027. A vista S2627 mostra 11 meses (set/26–jul/27). A vista S27SF mostra só fev/27–jul/27. Os números dos 36 recursos × meses em comum são iguais. Não reproduzi o caso em que a safra tem demanda própria num mês acrescentado: com os dados atuais a S27SF não tem demanda em set/26–jan/27.
- **causa:** tools/prototipo/v37/gen37/areas/processo_safra.py:191-194: CAP_MIS gera as colunas de cada g_cap fixa pelo período original de D2.SAFRAS. safra.js:985: capMeses só filtra gc._c0 e não acrescenta coluna. É anterior à SAF-C02 (commit 8a08de9).
- **correcao:** Gerar todas as colunas do calendário para todas as g_cap fixas, como já acontece com a g_cap_NOVA, e deixar capMeses recortar em tempo de execução. Regressão no navegador: editar o período e conferir que as colunas acompanham.

**O que a lente tentou e não quebrou**
- (a) Simetria entre vistas, pelo gerador próprio simetria.py (semente fixa; 2 a 4 safras de F1 e F2, abertas e encerradas; períodos iguais, encaixados, contidos, disjuntos, parciais e abertos; ocorrências antes, dentro, depois e fora do calendário e nas bordas exatas; recursos compartilhados e 'xnaocomp'; un=0; dias=0; 2 a 6 meses). Rodadas de 2000 cenários (semente 20261009, 35.735 células comparadas aos pares), 5000 (semente 42) e 10000 (semente 777, 167.082 células aos pares, 3.345 com período igual e carga excluída). Comparei d, nec, red, ocup e cap: 0 falhas.
- (a) Oráculo independente, com elegibilidade pela safra de origem e só o conjunto que a vista enxerga: 62.269 células com 2000 cenários e 299.009 com 10000. 0 falhas.
- (b) Conservação por fonte e recurso (Σ elegível + Σ fora da conta = Σ carga no calendário; 32.661 conferências com 2000 cenários e 158.452 com 10000): 0 falhas. capSaf não altera a entrada (comparei o JSON antes e depois), então ocorrência, data e custo ficam intactos. O custo da S27SF (R$ 180.888,10) inclui as colheitas fora da conta, conferido na tela.
- (c) Veredito: 402 grupos (safra, motivo) de outra safra fora da conta em células com demanda desta safra (2000 cenários) e 2.018 (10000) aparecem com número, motivo e horas por recurso corretos, sem grupo sobrando. Nunca sai R5 verde com carga excluída numa célula própria. O aria-label da célula (e3Fora + e3CelAria, parte de tela) passou em 853 grupos, incluindo 'desta safra': 0 falhas.
- (d) Outra fazenda e safra encerrada nunca entram: 1.120 vistas de safra encerrada e 2.243 vistas com outra fazenda no cenário (2000 cenários), 0 falhas. Nos dados sintéticos, a LG2627 e a S2526 também não entram (real_py.py e ui_grade.py).
- (e) Paridade entre JS e o espelho Python dados2.cap_saf, célula a célula (d, dThis, dOth, cap, ocup, nec, red, soma, own), fora, oth, max, reds, necMax e horas: 62.269 células (2000 cenários) e 299.009 (10000). 0 falhas.
- O gerador detecta defeitos de verdade. Na base 16d6734, 986 de 2000 cenários ficam assimétricos, 296 deles com o MESMO período nas duas vistas. Cenário mínimo, mesmo período: S1 e S2 de 24/01 a 21/03/2027, uma ocorrência da S2 em 08/01/2027 com 30 h de Operadores. Vista S1: 30 h; vista S2: 0 h. Na correção, 0 h nas duas. Também derrubou os 5 mutantes: m1, outras sem etiqueta (falhas a, c, e); m2, veredito sem as outras (falhas c-ausente e c-verde); m3, fora da conta não registrada (falhas b, c, e); m4, veredito sem o filtro de célula (falhas c-sobra, c-n, c-horas); m5, espelho Python ignorando o fim (falhas e-*).
- Harness do Codex: o original roda na base com CHECA_HASH=1 (sha d96875f8…) e dá A 340 h R2, B 140 h R4, same_total false. O adaptado roda na correção e dá A 140 h R4 citando a B2 com 200,0 h, B 140 h R4, same_total true. A única mudança é a linha 14, como diz o LEIA-ME, e os sha256 de harness_*.js, antes.json e depois.json conferem com ele.
- capacidade_unit.py numa cópia limpa (git archive 62b0904, SAFRION_DADOS=sintetico): 94 OK, 0 FALHA. Com a safra.js e a dados2.py da base: 83 OK, 11 FALHA, todas SAF-C02, como o autor relatou.
- O teste de navegador do autor (saf_capacidade_simetrica_test.py), rodado na cópia limpa com o build próprio (build.py com 0 FALHA e montar_render com 140 páginas), deu 28 ok e 0 falhas em 1440 e 390 px.
- O teste ui_grade.py olha a grade inteira, não só jul/27: 6 recursos × 6 meses comuns, em dois estados (períodos do cadastro e mesmo período), mesma ocupação e mesmas horas nas duas vistas, tela igual ao espelho Python, sem erro de JS. Correção: 10 ok. Base: falha com o mesmo período (Tratores jul/27 140,3 h na S2627 contra 61,7 h na S27SF; Colhedoras jul/27 56 % contra 16 %).
- Espelho Python sobre os dados sintéticos do protótipo, S2627 × S27SF em 32 pares de período (cadastro, igual e sorteados): 2.304 células, 0 divergências, 2.196 cargas de outra safra fora da conta.
- Com 2 safras abertas, o d é idêntico bit a bit nas duas vistas, por comutatividade; a divergência de exibição do achado 1 só aparece com 3 ou mais.
- Ponto latente, sem defeito hoje: capSaf usa i.cls que o chamador põe nas ocorrências da safra aberta, enquanto as outras são etiquetadas dentro dele. Os dois chamadores atuais (capCalc em safra.js:927 e dados2.capacidade:757) etiquetam. Um chamador novo que esqueça essa etiqueta trará a assimetria de volta.

**Comandos registrados pela lente**

| Comando | Resultado |
|---|---|
| `git -C <sp-safc02> show 16d6734:tools/prototipo/v37/gen37/safra.js > scratchpad/safc02-simetria/base_safra.js; git show 62b0904:…/safra.js > fix_safra.js; sha256sum` | base d96875f8…e9677, igual ao hash do Codex; fix 1f18e705…cd56a, igual ao arquivo da worktree |
| `cd scratchpad/safc02-simetria && CHECA_HASH=1 node <sp-safc02>/docs/planejar-safra/verificacao-saf-c02/harness_original.js base_safra.js; node …/harness_adaptado.js fix_safra.js` | Base: A 340 h, nec 3, R2; B 140 h, R4; same_total False. Correção: A 140 h, R4, 'Fora da conta: 1 ocorrência da B depois do fim dela (Tratores 200,0 h)'; B 140 h, R4; same_total True |
| `python3 simetria.py base_safra.js 2000 20261009 --sem-py --base` | Falhas a-oraculo e a-simetria em 986 cenários (3.964 e 3.970 ocorrências). Mínimo em minimos_base.json: uma ocorrência de 190 h antes do início da S1 entra na vista da S3 e não na da S1 |
| `python3 simetria.py fix_safra.js 2000 20261009  (com espelho Python e (c))` | falhas {} · cobertura a_oraculo 62.269, a_pares 35.735, mesmo período com fora 673, b 32.661, c_grupos 402, d fechadas 1.120, d outra fazenda 2.243, e 62.269 células |
| `python3 simetria.py fix_safra.js 5000 42` | falhas {} |
| `python3 simetria.py fix_safra.js 10000 777` | falhas {} · a_oraculo 299.009, a_pares 167.082, c_grupos 2.018, e 299.009; R2 13.095, R4 4.697, R5 1.454, R1 8.501, R3 716, R0 1.533 |
| `python3 simetria.py m1_outras_sem_etiqueta.js\|m2_veredito_sem_outras.js\|m3_fora_nao_registrada.js\|m4_veredito_sem_filtro_celula.js 400 20261009; SIM_MUT_PY=1 python3 simetria.py fix_safra.js 400 20261009` | Os 5 mutantes foram derrubados: m1 (a-oraculo em 208 cenários, e-*, c-ausente), m2 (c-ausente em 67, c-verde em 3), m3 (b-conserva em 254, e-fora, c), m4 (c-sobra em 121, c-n, c-horas), m5 Python (e-celula em 92, e-fora, e-oth etc.) |
| `python3 (script inline) contagem de assimetrias com o mesmo período, 2000 cenários, base × correção; encolhimento` | Base: 986 cenários, 296 com o mesmo período. Correção: 0 e 0. Mínimo da base com o mesmo período: S2 com 30 h em 08/01/2027, período de 24/01 a 21/03 nas duas; vista S1 30 h, vista S2 0 h. Correção: 0 h nas duas |
| `python3 aria_check.py fix_safra.js 2000 20261009` | grupos_conferidos 853, falhas 0 |
| `python3 txt_check.py fix_safra.js 3000 11 ; python3 txt_check.py cand_arredonda.js 3000 11` | Correção: 9 divergências de texto em 117.762 células (por exemplo, '1 %' contra '<1 %', '4 %' contra '5 %'). Candidata com arredondamento a 1e-6: 0 divergências |
| `node min_float.js fix_safra.js '[0.1,0.1,7]' ; node min_float.js base_safra.js '[0.1,0.1,7]' ; node min_float.js cand_arredonda.js '[0.1,0.1,7]' ; espelho Python inline` | Correção e base: A '4 %', B '4 %', C '5 %'. Espelho Python: o mesmo resultado. Candidata: '5 %' nas três vistas |
| `python3 simetria.py cand_arredonda.js 2000 20261009 --sem-py` | falhas {} |
| `SAFRION_DADOS=sintetico python3 real_py.py` | 32 pares de período, 2.304 células, 2.196 cargas de outra safra fora da conta, 0 falhas; a LG2627 e a S2526 não entram |
| `git archive 62b0904 tools/prototipo \| tar -x -C scratchpad/…/copia; cd copia/…/gen37 && SAFRION_DADOS=sintetico python3 capacidade_unit.py` | RESULTADO: 94 OK · 0 FALHA |
| `copia_base com a safra.js e a dados2.py de 16d6734 e o capacidade_unit.py novo: SAFRION_DADOS=sintetico python3 capacidade_unit.py` | RESULTADO: 83 OK · 11 FALHA (todas SAF-C02) |
| `copia (62b0904): SAFRION_DADOS=sintetico python3 build.py > build_copia.log; grep -c FALHA; python3 montar_render.py` | build rc 0, FALHA 0; _render com 140 páginas e 20 arquivos (a contagem 'dados reais locais 5/5' se refere à pasta sintética, porque SAFRION_DADOS=sintetico) |
| `cd copia/…/gen37 && env CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 saf_capacidade_simetrica_test.py` | RESULTADO: 28 ok · 0 falhas (1440 e 390 px) |
| `git archive 16d6734 tools/prototipo → copia_base; build.py; montar_render.py` | build rc 0, FALHA 0; 140 páginas |
| `env UI_COPIA=copia\|copia_base CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 ui_grade.py` | Correção: 10 ok, 0 falhas; 36 células comuns em cada estado, igual ao espelho. Base: 9 ok, 1 falha com o mesmo período (Tratores jul/27 140,3 h contra 61,7 h; Colhedoras 56 % contra 16 %). Nas duas: S2627 com 11 meses e S27SF com 6, mesmo com o período igual (achado 3) |
| `python3 r1_texto.py` | S27SF com período em ago/27: cls antes=14, cal=0, nenhuma ocorrência fora do calendário; R1 'as 14 ocorrências desta safra ficam fora do calendário do protótipo (set/26 – ago/27)' (achado 2) |
| `git -C <sp-safc02> rev-parse --short HEAD; git status --short` | HEAD 62b0904; nenhum arquivo versionado alterado. Observação: simetria.py, real_py.py e o espelho inline importam a dados2.py da worktree, o que grava .pyc no __pycache__/ dela; essa pasta não é versionada e já aparecia como não rastreada. Todo o resto ficou em <scratchpad>/safc02-simetria/ |

### Lente tela

#### tela-1 · S3 (existia antes, fora do diff da SAF-C02, não bloqueia) · PL-03 "Capacidade e recursos" mostra carga × capacidade fixa no código, sem a regra do capSaf, e contradiz a etapa 3 do Planejar safra
- **reproducao:** Executado: env CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 600 python3 <scratchpad>/safc02-ui/pl03.py. Caminho do gestor: Meu dia (IN-01) → "Reprogramar saldo" leva à /PL-05.dc.html → "Ver cenário" leva à /PL-03.dc.html. A PL-03 mostra "CARGA OUT/26 2.410 h · CAPACIDADE LÍQUIDA 2.640 h · DÉFICIT 270 h tratores 150+ cv" e a linha "Tratores 150+ cv · Plantio soja 910 ha · 1.180 h · 910 h · … · 270 h". No mesmo protótipo, a etapa 3 da S2627 (SAF.dc.html#saf=S2627&passo=operacoes) dá para Tratores em out/26 d=73,79 h, cap=809,6 h, ocupação 9 %, precisa de 1, sem falta. O espelho dados2.capacidade dá o mesmo valor da etapa 3. Captura: shot_PL03.png.
- **causa:** tools/prototipo/v37/gen37/areas/planejamento.py:311-374: a PL-03 é maquete estática, com a lista CAP e a g_cap "Carga out/26" escritas à mão, e não chama capCalc nem capSaf. Os links continuam ativos: planejamento.py:252 ("Ver capacidade" na PL-02), :439 ("Ver quadro completo") e :475 ("Ver cenário" na PL-05, que se alcança pelo IN-01). É o único outro lugar que mostra capacidade de recurso. Mapa (IN-04), Compras (CMP, SU-*) e Portal (PT-*) não mostram capacidade de máquina nem de pessoa; o grep de capSaf, capCalc, capVeredito e outrasSafras só encontra safra.js e o espelho dados2.
- **correcao:** Deixar uma fonte só (ENG-011). Trocar os três links (planejamento.py:252, 439 e 475) por SAF.dc.html#saf=<safra>&passo=operacoes, a etapa 3, que já aplica a regra da SAF-C02. Depois, retirar a PL-03 da navegação ou montá-la a partir do capCalc. Combinar com a frente NAV (#44), que está enxugando telas redundantes, e registrar como item separado, não dentro da SAF-C02.

#### tela-2 · S4 (existia antes, fora do diff; aparece no próprio cenário da SAF-C02) · Com o mesmo período gravado pela tela, a g_cap da S27SF mostra menos meses que a da S2627: as colunas foram fixadas no build pelo período original
- **reproducao:** Executado: walk.py, cenário P1 (as duas safras com 01/09/2026 a 12/07/2027 gravados pelo Editar da etapa 1), em 1440 e em 390 px. Colunas da g_cap na S2627: set/26 … jul/27. Na S27SF: só fev/27 … jul/27. A mesma diferença aparece no P4. Os totais por célula batem (demanda, capacidade, ocupação, necessárias e falta iguais em todas as células); faltam na tela da S27SF set/26 a jan/27, que estão dentro do período dela. Nos dados sintéticos a S27SF não tem demanda própria nesses meses, porque o plantio fica preso à colheita da soja. Por isso o efeito hoje é só de exibição: some a carga "(x %)" da outra safra.
- **causa:** tools/prototipo/v37/gen37/areas/processo_safra.py:191-194: CAP_MIS dimensiona g_cap_S2627 e g_cap_S27SF pelos períodos fixos de D2.SAFRAS. Em execução, safra.js:931 (capMeses) e o filtro gc._c0 em safra.js:985 só conseguem reduzir as colunas, nunca acrescentar. A g_cap_NOVA já nasce com o calendário inteiro.
- **correcao:** Em processo_safra.py:194, gerar toda g_cap_<k> com list(range(len(meses))), como a NOVA, e deixar o capMeses recortar em execução. Acrescentar ao saf_capacidade_simetrica_test.py a verificação de que os cabeçalhos de mês da g_cap são iguais nas duas vistas com o mesmo período. Conferir em 390 px que não aparece rolagem lateral, porque a rolagem horizontal da grade já existe.

#### tela-3 · S4 (existia antes, fora do diff; não consegui alcançar pela tela com os dados sintéticos) · A marca "≥" (horas não calculáveis) da carga de outra safra só aparece na vista dessa safra
- **reproducao:** Executado: node <scratchpad>/safc02-ui/semh.js <sp-safc02>/tools/prototipo/v37/gen37/safra.js. Fixture do Codex com B1 tendo falta.semHoras=50. Vista A: d=140, ocupação 87,5, ge=false, o que vira o texto "88 %". Vista B: d=140, ocupação 87,5, ge=true, o que vira "≥ 88 %". O total é o mesmo e a marca de piso depende da navegação. Pela tela não alcancei: o Rendimento é obrigatório (processo_safra.py:155, req=True) e nenhuma ocorrência sintética tem semHoras.
- **causa:** safra.js:315 (capSaf) soma semH só quando own. Por isso e3CelTxt e e3CelAria (safra.js:953-960) só marcam "≥" na vista da safra que tem as horas não calculáveis. pendSR e e3Incompleto também contam só a própria safra.
- **correcao:** Item separado, de baixa prioridade. Acumular semH também para as ocorrências elegíveis (cal) das outras safras, ou num semHOth, para a célula mostrar "≥" nas duas vistas. Espelhar em dados2.cap_saf e incluir no teste de propriedade.

#### tela-4 · S4 (cosmético, existia antes) · Aviso depois de salvar o recurso diz "Tratores: 1 unidades"
- **reproducao:** Executado: walk.py, cenário P4. Formulário Recurso dos Tratores com un=1 e jornada=4, depois Salvar. O aviso mostrado é "Tratores: 1 unidades, jornada de 4 h. Tratores fev/27: 27 % → 271 %." (shot_P4_390_S2627.png).
- **causa:** safra.js:1147 (recAfter): nfa(r.v.un)+' unidades' sem tratar o singular.
- **correcao:** Usar 'unidade' quando un==1 (e 'pessoa' para g_recp_pes).

**O que a lente tentou e não quebrou**
- Não consegui refutar a correção SAF-C02 pelo caminho de tela. Passei por Editar o período na etapa 1 → Continuar → avanço ou retorno até a etapa 3 → "Trocar safra" → Continuar na outra safra → etapa 3 → de volta à primeira. Em 4 cenários e duas larguras (1440×900 e 390×844 com toque), demanda, capacidade, ocupação, necessárias e falta deram iguais nas duas vistas em TODAS as células recurso × mês, os 6 recursos e os 12 meses, e bateram com o espelho dados2.capacidade com o mesmo período.
- P1, as duas com 01/09/2026 a 12/07/2027 (o cenário do autor, agora em todas as células): Tratores jul/27 dá 61,7 h nas duas. As duas vistas ficam em R4 amarelo. Na S2627, o veredito cita "2 ocorrências da Safrinha 2027 depois do fim dela (Tratores 78,6 h e Operadores e equipe 157,2 h)". O filtro e o aria-label de cada célula com demanda trazem "fora da conta: Safrinha 2027 … depois do fim dela" na S2627 e "desta safra … depois do fim" na S27SF.
- P2, as duas com 15/02/2027 a 31/07/2027, para testar "antes do início" num mês mostrado: Tratores fev/27 dá 97,7 h nas duas. A S27SF cita "2 ocorrências da Safra 2026/27 antes do início dela (Tratores 91,6 h e Operadores e equipe 183,2 h)". A S2627 diz "29 ocorrências antes do início da safra" e o filtro mostra "desta safra 91,6 h antes do início".
- P3, só a Safrinha editada (01/02 a 12/07/2027), com períodos diferentes: os totais continuam iguais, porque a elegibilidade vem da origem, e a carga de fora fica identificada nas duas vistas.
- P4, o P1 com Tratores 1 unidade e jornada 4 h pelo formulário Recurso, para testar falta e necessárias: as duas vistas dão R2 vermelho, "Tratores precisam de 3 em fev/27 e você tem 1". Na S27SF aparece "somando a Safra 2026/27 (122,0 h)". Tratores jul/27 dá 61,7 h, precisa de 1, sem falta, nas duas. Na base a vista da S2627 somaria 140,3 h e pediria 2. A prévia do formulário ("Maior uso: 27 % → 271 % (fev/27) · precisa de 3, tem 1") bate com o resultado gravado.
- Ida e volta S2627 → S27SF → S2627: a vista da S2627 volta idêntica (G e veredito), sem estado residual. Nenhuma vista com carga de outra safra fora da conta numa célula com demanda própria ficou verde.
- Outra fazenda (LG2627) e safra encerrada (S2526) ficam fora: a lista outras de cada vista tem só a outra safra aberta da Santa Rita. O custo de operação continua o mesmo em todos os cenários: S27SF R$ 180.888,10, que inclui as colheitas fora da conta, e S2627 R$ 264.617,07, que no P2 inclui R$ 197.815,54 de antes de 15/02/2027.
- Em todas as vistas não houve rolagem lateral nem erro de JS. A 390 px o veredito longo e a linha do filtro quebram linha sem cortar texto (capturas shot_*_390_*.png).
- Teste de propriedade próprio com 3 safras abertas, períodos aleatórios e diferentes (30 % das vezes com o mesmo período), ocorrências fora do calendário, 2 recursos e 4 meses, contra um oráculo independente que soma por elegibilidade da origem: 400 sorteios e 1.200 vistas sem nenhuma falha, com 3.197 cargas de fora conferidas. O mesmo script na base 16d6734 deu 5.066 falhas (controle).
- Harness adaptado do Codex com a fixture original: same_total=true. A dá 140 h, R4, e cita "1 ocorrência da B depois do fim dela (Tratores 200,0 h)". B dá 140 h, R4.
- Outros lugares que mostram capacidade: o grep de capSaf, capCalc, capVeredito e outrasSafras encontra só safra.js (etapa3, e3Diff, recPrev e recLive, que passam todos pelo capCalc e por isso leem a mesma regra) e o espelho dados2. Mapa (IN-04), Compras (CMP, SU-*), Portal (PT-*) e manutenção (MA-*) não mostram capacidade de recurso de máquina nem de pessoa. A única exceção é a PL-03 estática (achado S3).
- A worktree não foi alterada: git status sem arquivo versionado modificado. Os scripts e as saídas estão em <scratchpad>/safc02-ui/.

**Comandos registrados pela lente**

| Comando | Resultado |
|---|---|
| `python3 (comparação linha a linha de safra.js com _render/SAF.dc.html)` | 1.278 linhas de código e 0 ausentes: o _render da worktree (11:47) embute o safra.js do commit 62b0904, então não foi preciso refazer o build |
| `cd <sp-safc02>/tools/prototipo/v37/gen37 && env CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 saf_capacidade_simetrica_test.py` | 28 ok, 0 falhas (teste do autor reproduzido) |
| `env PYTHONDONTWRITEBYTECODE=1 CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 scratchpad/safc02-ui/walk.py P1` | 22 ok, 2 falhas. As 2 falhas são as colunas da g_cap diferentes com o mesmo período (achado S4); todas as células, o espelho, o veredito, o filtro e o aria-label estão OK |
| `... walk.py P2 P3` | 44 ok, 2 falhas. As falhas são as colunas diferentes no P3, esperado porque os períodos são diferentes; o P2 passou inteiro |
| `... walk.py P4 (depois de passar os recursos modificados ao espelho)` | 22 ok, 2 falhas (só as colunas da g_cap). As duas vistas dão R2 com 'Tratores precisam de 3 em fev/27 e você tem 1'; Tratores jul/27 dá 61,7 h, nec 1, red false nas duas |
| `env ... timeout 600 python3 scratchpad/safc02-ui/pl03.py` | IN-01 → /PL-05.dc.html → /PL-03.dc.html. A PL-03 mostra o déficit de 270 h de Tratores em out/26, fixo no código; a etapa 3 e o espelho dão Tratores out/26 73,79 h de 809,6 h (9 %), cabe |
| `node docs/planejar-safra/verificacao-saf-c02/harness_adaptado.js tools/prototipo/v37/gen37/safra.js` | same_total true. A: d 140, nec 1, R4, cita a B fora da conta. B: d 140, nec 1, R4 |
| `SAFRION_DADOS=sintetico python3 -B capacidade_unit.py` | 94 OK, 0 FALHA |
| `node scratchpad/safc02-ui/prop3.js <safra.js da worktree> e <safra.js da 16d6734>` | Correção: 400 sorteios, 1.200 vistas, 0 falhas, 3.197 cargas de fora conferidas. Base: 5.066 falhas (controle) |
| `node scratchpad/safc02-ui/semh.js tools/prototipo/v37/gen37/safra.js` | A tem ge=false e B tem ge=true na mesma célula (d=140): o '≥' só aparece na vista da safra dona das horas não calculáveis (achado S4, existia antes) |
| `grep capSaf\|capCalc\|capVeredito\|outrasSafras e grep -i capacidade em _render (CMP, IN-04, MA-*, SU-*, PL-*, PT-*)` | Consumidores só em safra.js e dados2. Exibição de capacidade de recurso fora do SAF só na PL-03 estática |
| `git -C <sp-safc02> status --short \| grep -v '^??'` | vazio: nenhum arquivo versionado alterado na worktree |

### Lente regressao

#### regressao-1 · S4 · Mudança de veredito pretendida: S27SF passa de R5 verde para R4 amarelo quando a S2627 termina antes de jul/27, embora a carga excluída não mude a conclusão
- **reproducao:** Executado. Sonda de navegador <scratchpad>/safc02-r3/probe_ui_r3.py, cenário Y: só a S2627 é editada pela tela para 01/09/2026 a 30/06/2027; depois abre a S27SF na etapa 3. Na base 16d6734: R5, 'Na estimativa mensal, cabe com o que você tem.', Tratores jul/27 = 140,33 h. No HEAD 62b0904: R4, '...cabe nos 553 ha com plano. Fora da conta: 1 ocorrência da Safra 2026/27 depois do fim dela (Tratores 25,3 h e Operadores e equipe 25,3 h).', Tratores jul/27 = 115,0 h. A S2627 aberta mostra 115,0 h nas duas versões. O espelho Python e o JS (py_xy.py) dão os mesmos números. Mesmo somando os 25,3 h excluídos, cabe: 140,3 h de 920 h, com 4 tratores e necessidade de 1.
- **causa:** safra.js:333-336 (capForaOutras) cita toda carga excluída de outra safra num recurso × mês com demanda desta safra; em safra.js:344, essa citação entra em 'fora' e safra.js:360 transforma qualquer 'fora' em R4. A decisão do Codex pede isso de forma expressa ('revela também a carga excluída pertinente'), e é a mesma regra que a ocorrência fora da própria safra já seguia (Regra A). Não é defeito de implementação. A mudança é pretendida, mas na tela passa a aparecer amarelo onde antes era verde.
- **correcao:** Nenhuma obrigatória. Se o Codex achar que é ruído, uma opção: só considerar 'pertinente' (e só tirar do verde) quando somar a carga excluída tornaria a célula vermelha, ou seja, quando nc(d + carga excluída) > un. Nos outros casos, citar só no filtro e no aria-label. A decisão de produto fica com o Codex. Se mantiver como está, registrar em DECISOES.md que R5 → R4 nesse caso é esperado.

#### regressao-2 · S4 · capSaf conta tudo em silêncio quando o item de 'outras' chega sem ini/fim, e volta ao resultado que depende da navegação
- **reproducao:** Executado: node docs/planejar-safra/verificacao-saf-c02/harness_original.js tools/prototipo/v37/gen37/safra.js, harness sem ini/fim em 'outras', contra o HEAD 62b0904. Resultado: A 340 h R2, B 140 h R4, same_total:false (saída em scratchpad/safc02-r3/h-orig-head.json). Com o harness adaptado, que passa ini/fim, o resultado é 140/140, same_total:true.
- **causa:** safra.js:311: cl = classeOc(i.dt, i.mi, s.ini, s.fim). Sem s.ini e s.fim, classeOc (safra.js:300) devolve 'cal' e a ocorrência da outra safra entra na conta. Hoje o único chamador, outrasSafras (safra.js:924), passa o período, então a tela não é afetada. O dados2.cap_saf (dados2.py:772) faz o mesmo com s.get('ini').
- **correcao:** Opcional, para proteger o porte ao software real: tornar o contrato explícito, com um teste unitário de que outrasSafras e dados2.capacidade sempre entregam ini/fim, ou um aviso ou registro quando 'outras' chega sem período. Não é preciso mudar o cálculo.

#### regressao-3 · S4 · O relato do autor diz que o _render foi montado com 'arquivos reais locais da Lagoa Grande', mas são os sintéticos (rótulo enganoso de montar_render.py, que já existia)
- **reproducao:** Executado: SAFRION_DADOS=sintetico python3 montar_render.py imprime 'dados reais locais: 5/5'. Mas python3 -c 'import dados_lagoa_fonte as F; print(F.REAL, F.DIR)', rodado na worktree sem a variável, dá 'REAL False .../dados_lagoa_sintetico/saida', e não existe dados_lagoa/ nem dados_lagoa_kml.py em <sp-safc02>.
- **causa:** tools/prototipo/v37/gen37/montar_render.py:14-18 conta os arquivos de dados_lagoa_fonte.DIR, que na camada sintética aponta para dados_lagoa_sintetico/saida, e mesmo assim os chama de 'reais'. O código é anterior a esta correção (commit abc00a4). O relato do SAF-C02 repetiu o rótulo e passou a impressão de dado real no artefato (ENG-017), o que não aconteceu.
- **correcao:** Fora do escopo do SAF-C02: no relato, trocar por 'camada sintética (REAL=False)'. Em tarefa separada, montar_render.py pode imprimir 'dados da Lagoa Grande: sintéticos 5/5' ou 'reais 5/5' conforme dados_lagoa_fonte.REAL.

**O que a lente tentou e não quebrou**
- Bateria de navegador, base 16d6734 × HEAD 62b0904, com SAFRION_DADOS=sintetico e _render montado nas duas: o log inteiro é IDÊNTICO depois de normalizar tempos e caminhos em saf_operacoes_test (87 ok/0), saf_revisao_test (42/0), tabelas_saf_test (24/24), saf_cmp_continuidade_test (31/0), etapas_celular_test (14/0), partest (46 ok/1 falha nas duas: 'T1-C copia ajuste do T1-B', vermelho conhecido), acao_unica_test saf (10/0), acao_unica_test v3 (10/0), rend_multiconjuntos_test fluxo (18/18), telas (5/5), bordas (9/9) e varredura (140/140 páginas sem erro).
- Testes puros: capacidade_unit.py dá 94 OK/0 no HEAD e 76 OK/0 na base. Os 76 antigos continuam passando no HEAD e o diff do teste só acrescenta casos; job() passa a levar ini/fim, e nenhuma expectativa antiga mudou. rend_multiconjuntos_unit.py dá 106/106 nas duas.
- Os testes novos discriminam: capacidade_unit.py do HEAD rodado sobre o código da base dá 83 OK/11 FALHA, todas SAF-C02, o que confere com o relato. saf_capacidade_simetrica_test.py dá 28 ok/0 no HEAD e 16 ok/12 falhas contra o _render da base. O autor relatou 14 ok/12 falhas: as 12 falhas conferem e o número de ok difere em 2.
- Seed sem nenhuma mudança: nas 4 safras (S2627, S27SF, S2526, LG2627), o JS (capSaf + capVeredito) e o Python (capacidade) dão células e veredito idênticos na base e no HEAD. S2627 fica R4, S27SF R5, S2526 R1 e LG2627 (Lagoa Grande) R2 'Operadores e equipe precisam de 127 em nov/26... 75 ocorrências antes do início'. g.fora fica vazio em todas, porque as 75 'antes' da LG2627 têm mi<0. A LG2627 é a única safra da fazenda dela, então nada muda ali.
- Regra A conservada pela tela, cenários X (só a S27SF termina em 12/07/2027) e Y (só a S2627 termina em 30/06/2027): o custo de operação fica igual na base e no HEAD (S2627 R$ 264.617,07; S27SF R$ 180.888,10). As colheitas fora do período continuam em oc com cls 'depois' e custo (T2 15/07 R$ 68.301,60; P1 14/07 R$ 21.774,00), e as datas não mudam.
- Simetria pela tela (sonda própria, 1440 px): no HEAD, X dá Tratores jul/27 = 61,73 h com a S2627 e com a S27SF abertas, e Y dá 115,0 h nas duas. Na base, X dava 140,33 × 61,73 e Y dava 115,0 × 140,33, o que reproduz o defeito também com UMA só safra editada. Sem erro de JS. Os números conferem com o espelho Python e o JS (py_xy.py).
- Harness do Codex: CHECA_HASH=1 na base (fonte d96875f8…) dá A 340 R2 e B 140 R4, same_total false. O adaptado no HEAD dá 140/140, same_total true. As saídas são byte a byte iguais a antes.json e depois.json, e os sha256 de antes.json (0f00e6e1…), depois.json (49eb8b9e…), harness_original (bc141473…), harness_adaptado (7bcf243e…) e safra.js (1f18e705…) conferem com o LEIA-ME.
- Propriedade adversarial própria (prop_r3.js, 400 sorteios, 998 vistas, 2 ou 3 safras, 2 recursos, 3 meses), no HEAD: conservação (contada + g.fora = toda carga no calendário) com 0 falhas; nenhum R5 verde nas 204 vistas com carga excluída pertinente de outra safra; o número de ocorrências citadas no veredito é igual ao das pertinentes (0 falhas); a demanda é igual em todas as vistas (0 falhas).
- Os consumidores da capacidade passam todos por capCalc: veredito, células da g_cap, atalhos e aria-label (e3CelAria), filtro, e3Diff (antes → depois ao salvar), recPrev/recLive (prévia do formulário Recurso) e e3Op (naConta). capSaf não tem outro chamador. No Python, D2.capacidade é chamado só por testes, com assinatura inalterada.
- Outra fazenda e safra encerrada continuam fora: a filtragem fica em outrasSafras e outras_safras, que não mudaram além de passar ini/fim, e isso foi confirmado pela tela no teste novo (Mamão e 2025/26 ausentes).
- Escopo: das 165 páginas do _render, só SAF.dc.html muda entre base e HEAD. ocupacao.js e ocupacao.py não foram tocados. O diff fica nos 11 arquivos declarados.
- Paridade Python: a mudança em cap_rec (pes = r['pes'] se existir) não altera RECURSOS, que não têm 'pes', e os números da seed são idênticos.

**Comandos registrados pela lente**

| Comando | Resultado |
|---|---|
| `git worktree add (já existia, limpa, em 16d6734: scratchpad/safc02-base, branch tmp/safc02-base; reaproveitada) + SAFRION_DADOS=sintetico python3 build.py; python3 montar_render.py (base e HEAD)` | As duas com rc=0, 140 artboards, 0 FALHA no log, _render com 140 páginas. Montei com SAFRION_DADOS=sintetico nas duas; a worktree não tem dado real, então REAL=False de qualquer jeito. |
| `diff -rq _render HEAD × base` | Só SAF.dc.html difere, de 165 arquivos |
| `SAFRION_DADOS=sintetico python3 capacidade_unit.py (HEAD \| base)` | 94 OK · 0 FALHA \| 76 OK · 0 FALHA |
| `capacidade_unit.py do HEAD sobre o código da base (pasta mista com symlinks)` | 83 OK · 11 FALHA, todas SAF-C02 |
| `SAFRION_DADOS=sintetico python3 rend_multiconjuntos_unit.py (HEAD \| base)` | 106/106 OK \| 106/106 OK |
| `CHECA_HASH=1 node harness_original.js <base>/safra.js; node harness_adaptado.js <HEAD>/safra.js; node harness_original.js <HEAD>/safra.js` | Base A 340 R2 / B 140 R4, same_total false (= antes.json byte a byte). HEAD adaptado 140/140, same_total true (= depois.json). HEAD sem período nas outras: 340/140, false (achado S4 de fail-open). |
| `sha256sum docs/planejar-safra/verificacao-saf-c02/* safra.js` | Todos conferem com o LEIA-ME |
| `python3 seed_cmp.py (JS capSaf+capVeredito e Python capacidade nas 4 safras da seed, base × HEAD)` | Idênticos. S2627 R4, S27SF R5, S2526 R1, LG2627 R2. g.fora vazio. |
| `node prop_r3.js <HEAD>/safra.js (400 sorteios, 998 vistas)` | conservação 0, verde enganoso 0 (204 vistas de risco), citação 0, simetria 0 falhas |
| `python3 py_xy.py (cenários X e Y pelo espelho, base × HEAD)` | X: S2627 jul/27 Tratores 140,33 → 61,73 h, veredito com a Safrinha citada. Y: S27SF 140,33 → 115,0 h, R5 → R4. JS = Python. |
| `env CHROME_BIN=<chrome> flock /tmp/cdpE.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 probe_ui_r3.py (HEAD \| base)` | rc=0 nas duas. Simetria no HEAD (61,73/61,73; 115/115), assimetria na base. Custo igual nas duas. Sem erro de JS. |
| `mesmo prefixo de navegador: saf_operacoes_test.py (HEAD \| base)` | 87 ok · 0 \| 87 ok · 0, log idêntico |
| `saf_revisao_test.py` | 42/0 \| 42/0, log idêntico |
| `tabelas_saf_test.py` | 24/24 \| 24/24, log idêntico |
| `saf_cmp_continuidade_test.py` | 31/0 \| 31/0, log idêntico |
| `etapas_celular_test.py` | 14/0 \| 14/0, log idêntico |
| `partest.py` | 46 ok · 1 falha \| 46 ok · 1 falha (T1-C copia ajuste do T1-B, vermelho conhecido), log idêntico |
| `acao_unica_test.py saf` | 10/0 \| 10/0, log idêntico |
| `acao_unica_test.py v3` | 10/0 \| 10/0, log idêntico |
| `rend_multiconjuntos_test.py fluxo \| telas \| bordas` | 18/18, 5/5 e 9/9 nas duas, logs idênticos |
| `varredura.py` | 140/140 páginas sem erro \| 140/140, idêntico |
| `saf_capacidade_simetrica_test.py (HEAD; e HEAD com RENDER_DIR=<base>/_render)` | 28 ok · 0 falhas \| 16 ok · 12 falhas (teste discrimina o defeito) |
| `git worktree remove --force scratchpad/safc02-base; git branch -D tmp/safc02-base; git worktree prune` | Removidas. A worktree scratchpad/safc02-base-reg (branch tmp/safc02-base-reg, de uma execução anterior, não criada por mim) ficou intacta. Nenhum arquivo versionado de <sp-safc02> foi alterado; HEAD continua 62b0904. Logs em scratchpad/safc02-r3/. |

## fechamento

Corrigi todos os achados das três verificações: o S3 e os S4 baratos, cada um com teste de regressão. A capacidade continua igual nas duas safras, ao alternar uma e outra com o mesmo período. O R5 → R4 não mudei: é o comportamento que a decisão do Codex pede, e ficou registrado. Os commits estão na branch `claude/v44-saf-c02` (worktree `<sp-safc02>`), sem push e sem PR. A revisão do Codex ainda não foi feita.

#### Commits
- `f52fa09` SAF-C02: correções da verificação (11 arquivos, +162 −32)
- `1671671` SAF-C02: saídas brutas da verificação (36 arquivos, em `docs/planejar-safra/verificacao-saf-c02/`)

#### O que mudou (arquivo:linha)
- **`safra.js`**
  - `:312 capContrato`: o cálculo agora recusa com erro explícito quando falta o período de outra safra (`ini`/`fim`) ou a etiqueta `cls` desta. Antes somava tudo em silêncio.
  - `:322`: a célula soma a parte de cada safra sempre na mesma ordem, do menor para o maior valor.
  - `:320`: o "≥" (área sem horas calculáveis) vale para ocorrência de qualquer safra que entra na conta.
  - `:354`: o motivo do R1 sai das contagens (antes do início, depois do fim, fora do calendário).
  - `:1154`: singular no aviso ("1 unidade", "1 pessoa").
- **`dados2.py`** (espelho Python, igual ao JS)
  - `:768`: `ValueError` nos mesmos casos do `capContrato`.
  - `:791`: o mesmo "≥".
  - `:801`: a mesma ordem de soma.
- **`areas/processo_safra.py:193`**: toda `g_cap` nasce com o calendário inteiro, e `capMeses` recorta pelo período gravado.
- **`areas/planejamento.py:254`, `:441` e `:477`**: "Ver capacidade" no PL-02, PL-04 e PL-05 abre a etapa 3 do Planejar safra (`SAF.dc.html#saf=S2627&passo=operacoes`). Antes abria o PL-03. A docstring registra a mudança.
- **`montar_render.py:19`**: o rótulo agora diz "dados da Lagoa Grande: sintéticos" ou "reais", conforme a fonte (`F.REAL`).
- **Testes**
  - `capacidade_unit.py:341–395`: casos V1-1, V1-2 (dois), V2-3, V3-2 (dois) e V3-1.
  - `saf_capacidade_simetrica_test.py`: meses iguais nas duas vistas (`:40`), singular (`:103`), R1 pela tela (`:109`) e o caminho do PL na tela (`:112`).
  - `dados_lagoa_sintetico/camada_test.py:226`: caso 17, rótulo do `montar_render`.
- **Documentos**
  - `ESPECIFICACAO.md`: R1, meses da `g_cap`, "≥", ordem da soma e contrato.
  - `DECISOES.md`: meses da `g_cap` e "R5 → R4 é esperado".
  - `FORA-DE-ESCOPO.md`: o PL-03 fica sem entrada pelas telas.

#### Comandos e resultados (todos executados, com `SAFRION_DADOS=sintetico`)
| Comando | Resultado |
|---|---|
| `CHECA_HASH=1 node harness_original.js` na safra.js da base 16d6734 | Igual a `antes.json` byte a byte: A 340 h (R2), B 140 h (R4) |
| `node harness_adaptado.js safra.js` → `depois.json` | A e B com 140 h, R4, `same_total` true. Só o `source_hash` mudou (9e329c43…) |
| `node harness_original.js` na correção | Erro explícito "a safra B chegou sem o período", em vez de 340 h em silêncio |
| `python3 build.py > /tmp/SAFC02-build.log`; `grep -c FALHA` | 0 FALHA, 140 páginas |
| `montar_render.py` | 140 páginas, "dados da Lagoa Grande: sintéticos 5/5" |
| `varredura.py` (build final) | 140 de 140 páginas sem erro |
| `capacidade_unit.py` | 101 OK, 0 FALHA. Os testes novos no código da 62b0904 dão 5 FALHA |
| `saf_capacidade_simetrica_test.py` (1440 e 390 px) | 38 ok, 0 falhas. No render da 62b0904: 10 falhas, só nos casos novos |
| `links_ocultos_test.py` | 8 de 8 |
| `rend_multiconjuntos_unit.py` | 106 de 106 |
| `camada_test.py` | 16 de 17. O 17 (novo) passa; o 16 (versão do cenário: 4 em vez de 3) já falhava na 62b0904 |
| Bateria do navegador (`saf_operacoes` 87/0, `saf_revisao` 42/0, `tabelas_saf` 24/24, `saf_cmp_continuidade` 31/0, `etapas_celular` 14/0, `acao_unica` saf 10/0 e v3 10/0, `rend_multiconjuntos` 18/18, 5/5 e 9/9, `partest` 46/1) | Log inteiro igual ao da 62b0904, já normalizado. A falha do `partest` (T1-C) é vermelho conhecido |
| Testes de propriedade (scripts dos verificadores) | 2000 e 10000 sorteios com o espelho Python: 0 falhas. `txt_check` com 3000: 0 divergências (eram 9). Caso mínimo com 3 safras: "5 %" nas três vistas (antes "4 %", "4 %", "5 %"). `prop3`, `prop_r3` e "≥": 0 falhas |

#### Achados
**Aceitos e corrigidos:**
- **V2-1 (S3), PL-03.** Corrigi só as três entradas. A página PL-03 continua no build sem nenhum link para ela. Derivar a página da etapa 3 ou removê-la fica como tarefa própria, já registrada em FORA-DE-ESCOPO.
- **V1-1 (S4):** ordem da soma com 3 ou mais safras.
- **V1-2 (S4):** texto do R1.
- **V1-3 e V2-2 (S4):** colunas da `g_cap`.
- **V2-3 (S4):** "≥" nas duas vistas.
- **V2-4 (S4):** "1 unidades".
- **V3-2 (S4):** contrato. Período nulo (`ini`/`fim` null) continua aceito e significa "sem período".
- **V3-3 (S4):** rótulo do `montar_render`. O relato anterior também estava errado: o `_render` foi montado com a camada **sintética**, e não com dado real da Lagoa Grande.

**Não mudei:**
- **V3-1 (S4), R5 → R4.** É o que a decisão do Codex pede, e é a mesma regra da ocorrência fora da própria safra. Ficou registrado em DECISOES.md, com a alternativa ("só tira o verde se a carga somada desse falta") para o Codex decidir.

#### Limites da prova
- O PL-03 continua com números fixos. Só não tem mais entrada pelas telas.
- Os testes do SAF da bateria rodaram sobre o build de 18:03, antes da troca dos links. Entre esse build e o final só mudou `planejamento.py`. A varredura, o teste de simetria e o `links_ocultos` rodaram de novo sobre o build final.
- Os scripts de propriedade (`simetria.py`, `txt_check.py` e outros) ficaram no scratchpad e não estão no repositório. Só as saídas foram versionadas.
- Não rodei a bateria completa nem os outros vermelhos conhecidos.
- Não atualizei `docs/STATUS.md` nem o artefato. Ficam para quem integrar na `claude/prototipo-v44`, que avançou para 3374b65, mas sem mudar `safra.js`, `dados2.py`, `processo_safra.py` nem `planejamento.py`.
- O `planejamento.py` também é alterado pelas frentes SUP (`:253`, linha vizinha à `:254`) e PCM. Na integração pode surgir um conflito de linha adjacente, simples de resolver.

#### O que conferir na tela
1. **Mesmo período.** Em Planejar safra, edite a Safra 2026/27 e a Safrinha 2027 para 01/09/2026 a 12/07/2027. Na etapa 3 de cada uma:
   - Tratores em jul/27 mostram 61,7 h nas duas;
   - as duas grades têm os mesmos 11 meses (set/26 a jul/27);
   - o veredito da S2627 cita "2 ocorrências da Safrinha 2027 depois do fim dela".
2. **Recurso com 1 unidade.** Salve Tratores com 1 unidade. O aviso diz "1 unidade".
3. **Safrinha em ago/27.** Mude o período da Safrinha para 01 a 31/08/2027. O R1 diz "nenhuma ocorrência desta safra cai no período dela" com as 14 ocorrências antes do início, e não "fora do calendário".
4. **Caminho do PL.** Em Meu dia → Reprogramar saldo → Ver capacidade, abre a etapa 3 da Safra 2026/27, e não o PL-03.

O resumo das saídas brutas está em `<sp-safc02>/docs/planejar-safra/verificacao-saf-c02/LEIA-ME.md`, e os arquivos em `<sp-safc02>/docs/planejar-safra/verificacao-saf-c02/saidas/`.
