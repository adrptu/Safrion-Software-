# PLANO DE EXECUÇÃO · CONTROLE-01

**Pedido.** Adrianus, 05/10/2026: "execute a melhor recomendação" da auditoria `pce/verificada.md` §5.

**Base.** `claude/v44-tabelas-05` @ `884620c`. É a ponta da cadeia de PRs em rascunho #36→#37→#39→…→#44, conferida com `gh api …/pulls`. A branch `claude/v44-controle-01` já existe em `884620c`, na worktree `/home/user/sp-ctl`, sem commits.

**Abreviações.** `gen37/` = `tools/prototipo/v37/gen37` · `ctl/` = `scratchpad/ctl`

**O que rodei para consolidar (executado):**
- `git` (branches, worktrees e ancestralidade);
- `gh api` (estado dos PRs);
- `diff -U0` das cópias B (`ctl/b_cet/v37q`) e F (`ctl/fFc/v37`), e leitura de `ctl/d_cet/frente_d_corrigida.diff`, para achar os trechos que mudam;
- conferência das linhas citadas;
- levantamento dos vermelhos da bateria-base.

Os números de teste de cada frente vêm das execuções dos desenhos em `ctl/`. **Não rodei esses testes de novo.** Nenhum arquivo do repositório foi editado e nenhum navegador foi aberto.

---

## 1. Ordem dos PRs (pilha sobre #44)

**Critérios, nesta ordem:**
1. **Severidade.** O pedido diz "S2 primeiro", mas há dois S1 (F item 1 e E1). Por isso: S1 e S2 antes de S3.
2. **Mesmos arquivos juntos:**
   - liberação: F e E1;
   - execução: B, D, A e ATOR;
   - plano: C1 e C2;
   - irrigação: E3;
   - agronomia: E2.
3. **Maturidade.** Diff já executado em cópia vem antes de desenho só especificado.

| PR | Branch (base = PR anterior) | Frentes / regras | Sev. | Ponto de partida | Tamanho do produto |
|---|---|---|---|---|---|
| CTL-1 | `claude/v44-controle-01` (base #44) | F: liberar = aprovar e liberar (CMD-42 + CMD-06) e elos ocultos · F-R1..R5 | S1 + S3 | diffs em `ctl/fFc/*.diff`; build com 144 quadros | +48 −44 |
| CTL-2 | `claude/v44-controle-02` | E1: trava legal única na liberação e no ajuste · RL-E1, RL-E2 | S1 | patch em memória `ctl/e2/proposta_e2.py` | ≈ +76 −17 |
| CTL-3 | `…-03` | E3: outorga com fonte única · RL-E4 | S2 | idem | ≈ +37 −13 |
| CTL-4 | `…-04` | B: início com entrega parcial · R1–R5, R4b | S2 | cópia `ctl/b_cet/v37q` | +27 −11 |
| CTL-5 | `…-05` | D: aprova quem decide · R-D0..R-D5 | S2 (D4 é S3) | `ctl/d_cet/frente_d_corrigida.diff` | +111 −64 |
| CTL-6 | `…-06` | A: apontamento único web × app · AP-01..AP-09 | S2 | núcleo em sobreposição (`ctl/cetA`); tela especificada | ≈ +140 líquidas |
| CTL-7 | `…-07` | **ATOR (novo, desta consolidação):** CMD-42/06 e CMD-09 com o perfil de quem age | S1 (proposta; o Codex classifica) | a especificar (§2) | a medir no desenho |
| CTL-8 | `…-08` | C1: demanda única por fazenda (SAF etapa 6 = CMP etapa 2) · DEM-01..04, 06..08 | S2 | só espelho (`ctl/fc_cet/impl3.py`, `dem_js_v2.js`) | ≈ +110 −4 |
| CTL-9 | `…-09` | C2: Mapa › Insumos lê a mesma demanda · DEM-05 | S2 | idem | ≈ +15 −41 |
| CTL-10 | `…-10` | E2: AG-07 vira consulta; receituário só gravado · RL-E3 | S3 | patch em memória | +5 −80 |

**Portões fora da pilha.** Todos bloqueiam a homologação, mas não o início.

- **G1 · OS-0424 (S1 de dado, E §7.1).**
  - O problema: Fungicida A em milho, sem registro, já Liberadas e executável. Pela regra, é a única ordem da semente que falha (E §1.1).
  - Quem decide a correção da semente é o Codex. A base demonstrativa não tem fungicida foliar para milho, então ninguém inventa uso.
  - O Claude aplica num PR mínimo, o CTL-2b, **antes do CTL-8**: a C usa a OS-0424 na DEM-04 e no N13.
  - Prova: `osUsoErro` sobre todas as ordens da semente = 0.
  - Observação: a B não traz `osUsoErro` no Iniciar. Além disso, as páginas do app não carregam o CARD (E, recusada 2). Por isso o portão é o dado, e não uma trava nova.
- **G2 · possível dado real (ENG-017).**
  - Onde: `dados_irrigacao.py:43` (texto de observação da captação LG-PAR; o proprietário confirmou em 05/10/2026 que não era dado real; trocado por texto demonstrativo em `3c9daf1`), presente desde a raiz `e8d780d`, conferido com `git grep`.
  - O CTL-3 tira o texto do HEAD, mas o histórico continua.
  - O Codex confere com o proprietário antes de qualquer publicação.
- **G3 · B-R8.** Fechamento com dose efetiva abaixo da aprovada. Carrega o resto do dano da B e está "severidade a classificar". Se o Codex classificar como S2, vira o CTL-11, antes da homologação.
- **G4 · CTL-7.** Precisa estar integrado antes da homologação (motivo no §2, CTL-7).

**Regra de pilha:**
- Cada PR abre em rascunho, com base no PR anterior.
- Nenhum é integrado antes da cadeia #36–#44.
- Achado de revisão num PR de baixo exige rebase dos de cima e nova rodada da bateria.
- Ninguém integra o próprio PR: integrador é o Codex.

**Homologação** (depois do CTL-10, de G1 a G4 e do parecer dos dois agentes). O proprietário recebe link, versão e uma tarefa curta (proposta):
1. "Libere a OS-0430 e veja na Origem quem aprovou e quem liberou".
2. "No app, tente iniciar a OS-0430 sem retirar os insumos".
3. "Aponte o mesmo dia na web e no app e decida como Paula".
4. "Na Compra, confira que o Fungicida A não pede mais 145,2 L".

Limitações a declarar:
- o perfil de demonstração não é segurança (D);
- a trilha tem hora sem data (F §8);
- a capacidade não desconta o realizado;
- SAF, CMP e Mapa leem a semente estática (C, risco 1).

---

## 2. Cada PR

### Verificação comum a todos os PRs ("verde")

```sh
W=<worktree da PR>; G=$W/tools/prototipo/v37/gen37; cd $G
python3 build.py && python3 montar_render.py                       # 144 quadros
CHROME_BIN=/tmp/cloudchrome/chrome python3 varredura.py            # 144/144 sem erro
python3 quantidade_test.py && python3 carencia_test.py unit && python3 mip_unit_test.py && python3 rend_multiconjuntos_unit.py
# bateria completa: cópia de docs/parceria/evidencias/v44-tabelas-05/un-20261005/00-bateria.sh com G=$G e E=/tmp/ctl-N
```

**Critério de verde:**
- testes novos da PR com 100%;
- vermelho comprovado na base;
- bateria completa sem falha nova contra a base.

**Linha de base (executado):** 11 vermelhos na bateria de `0cf6f90`:
- componentes_ajustes e componentes_interacao;
- etapas_complemento e etapas_desktop;
- cal01_test, cd05vtest, intest, os_cenario_test, patest, psfix38test e saf38test.

**Antes de editar:**
- commit só de reserva no RETOMADA (padrão `1fbb354`);
- a bateria no hash base guardada como "antes".

**Depois:** pacote de evidência em `docs/parceria/evidencias/v44-controle-0N/` com MANIFESTO, SHA256SUMS e `bateria/`, como o da 2d.

### CTL-1 · F (liberação com CMD-42 e CMD-06; elos para telas ocultas)

**Arquivos a reservar:**
- `gen37/areas/processo_os.py`: l.47, 153, 177, 230, 248, 298-311, 329-336, 559, 614, 802;
- `gen37/areas/inicio.py`: l.21, 122, 816;
- `gen37/areas/maquinas.py`: l.166, 265, 322-323, 362, 624, 627, 703-704;
- `gen37/areas/irrigacao.py`: l.577, 586, 593-594;
- `gen37/areas/mobile.py`: l.332-335, 375, 660, 669, 688, 695;
- `tools/prototipo/v37/RETOMADA-NUVEM.md`.

**Regras:**
- `OS_AGRO` e `osVn` como fonte única;
- `osc_aprovLib` grava `{cmd,v,por,at,t}` só quando a liberação dá certo;
- a reserva só aparece com `o.reservado`;
- a dose aparece com 4 casas.

**Testes novos:**
- `gen37/os_aprov_lib_unit.js`, que vem de `ctl/fFc/unit_liberar_c.js`: 21 verificações; a base falha 14;
- o executor (hoje `ctl/fFc/run.py`; no padrão de `carencia_test.py:20-32`);
- `gen37/links_ocultos_test.py`, que vem de `estrutura_test_c.py`: 7 verificações; a base passa 4.

**Testes a adaptar:**
- `map_decisoes_test.py:70-71`: `['Acompanhar OM-0233','MA-04.dc.html#OM-0233']`;
- `matest.py:66`;
- `etapas_celular_test.py:217`;
- `ostela.py:111`.

**Navegador:**
- estender `os_v39_liberar_test.py` (casos 1, 2 e 4);
- `os_cenario_test.py`, verificações 2 e 14;
- `map_decisoes_test.py`, `mbtest.py` e `irtest.py`.

**Comando:** comum + `python3 links_ocultos_test.py` + executor de `os_aprov_lib_unit.js` + os 5 de navegador acima.

**Aceite:**
- OS-0430 grava 2 registros, v1, Ana (agrônoma), REQ-041 com 320, 160 e 80 L;
- N1–N8 sem registro na recusa;
- L1–L3 verdes;
- cliques de "Liberar" iguais.

**Opcional:** se o Codex concordar, corrigir `os_cenario_test.py:20-22`, que compara `c.v` com 2 enquanto a semente é v=3 (`cenario.py:79-80`, PRE-REV P4). Isso tira um vermelho da base.

### CTL-2 · E1 (trava legal única)

**Arquivos:**
- `gen37/cenario.js`: `cenUsoLegal` depois de `cenNum`, l.41;
- `gen37/mip.js`: `mipChecks`, l.239-250;
- `gen37/dados_mip.py`: `uso`, `_agf`;
- `gen37/dados_carencia.py`: `_usos` (l.91), `_produtos` (l.125), `card` (l.209), `carSaf` e `carNap`;
- `gen37/areas/processo_os.py`: núcleo antes da l.340, `osc_liberar` antes da l.308, `osc_ajustar` depois da l.333, `osMerge` l.245-248, `osProx` l.415, l.557, 607-608, 614, 196, 802;
- `gen37/areas/inicio.py`: l.817.

**Regras:**
- só conta O.S. Liberadas em diante, mais o caderno, e a mensagem nomeia o que contou;
- alertas na confirmação.

**Ajuste de integração sobre o CTL-1:**
- os textos novos usam `OS_AGRO`;
- a confirmação fica = frase da F + "Atenção (não bloqueia): …";
- `os_aprov_lib_unit.js` ganha o N9: recusa legal não grava CMD-42.

**Testes:**
- novo `gen37/legal_unit_test.py`: 26 + 5 casos; a base passa 12 e 1;
- `e1_mip_eq` (AG-01 nos 1.136 casos, 0 travas diferentes) e `e1_planos` (2 travadas, ambas devidas) entram como verificação;
- navegador: `os_cenario_test.py` 14b, 14c e 14d; `map_decisoes_test.py` 14c no Mapa.

**Comando:** comum + `python3 legal_unit_test.py && python3 os_cenario_test.py && python3 map_decisoes_test.py && python3 ostest.py && python3 os_v39_liberar_test.py`.

**Aceite:**
- R1–R4 recusados com o texto do E §4;
- `ostest` c1·a7 e `os_v39_liberar` c1·a2, c1·a8 e c9·k4 liberam;
- confirmações da semente iguais.

### CTL-3 · E3 (outorga)

**Arquivos:**
- `gen37/dados_lagoa_fonte.py`, **que está na reserva da CAMADA-SINTETICA** (RETOMADA l.70): estender a reserva, porque o autor é o mesmo;
- `gen37/dados_irrigacao.py`: `CAPT`, `seed` v=3 (l.183), docstring l.11-13 e remoção de l.43 (G2);
- `gen37/irrigacao_estado.js`: l.209, mais 1 linha em `irrChecar`;
- `gen37/areas/irrigacao.py`: l.228, 252, 572-574.

**Testes:**
- novo `gen37/outorga_unit_test.py`: 11 casos (a base passa 5) + equivalência 16/16 com o CD-01;
- `irtest.py:59`: "outorga sint-002/0000 vence em 20/11/2026", mais IR-04 novo.

**Comando:** comum + `python3 outorga_unit_test.py && python3 irr_estado_test.py && python3 irr_fluxo_test.py && python3 irtest.py`.

**Aceite:**
- "186 L/s × 19,6 h/dia · 13.120 m³/dia";
- 3 das 6 tarefas mudam de início;
- tudo vencido trava com o gestor;
- volume do dia ≤ 13.120.

### CTL-4 · B (início com entrega parcial)

**Arquivos:**
- `gen37/cenario.js`: `cenIniFalta` antes da l.128; trava em `cenIniciarTurno` depois da l.131;
- `gen37/areas/processo_os.py`: `osMerge` l.237-238 (`fz`, `o.esg`), `osIniErro` l.344-351, `osProx` depois da l.418;
- `gen37/areas/mobile.py`: l.200 e 422-424.

**Ajuste:** o `o.dono` do caso (b) usa `OS_AGRO` (CTL-1).

**Testes novos** (de `ctl/b_cet/novos/` e `ctl/b/novos/`):
- `gen37/inicio_entrega_test.py` + `inicio_entrega_unit.js`: 25; a base passa 11;
- `gen37/app_entrega_parcial_test.py`, de navegador.

**Testes a adaptar:**
- `consumo_divergente_test.py` l.101, 114 e 138: turno aberto antes, como `app_saldo_zero_test.py:42`;
- `est_fix2_test.py:55` e `est_repro.py:43`: `cenConfirmarRecebimento`;
- `os_cenario_test.py` §6: +1 verificação.

**Comando:** comum + `python3 inicio_entrega_test.py && python3 app_entrega_parcial_test.py && python3 consumo_divergente_test.py && python3 est_fix2_test.py && python3 est_repro.py && python3 os_cenario_test.py`.

**Aceite:**
- o app recusa com o mesmo texto da web, mais o dono, e nada é gravado;
- P5 e P6: sem "Insumo esgotado" no caminho feliz.

### CTL-5 · D (aprova quem decide)

**Arquivos:**
- `gen37/g2lib.js`: `G2_PERFIS`, `g2perfil`, `g2papel`, `g2ator`, `g2quem`, `g2mesma`, e o `g2vals`/`g2navvals` na l.244;
- `gen37/ui37.py`: l.217-222;
- `gen37/cenario.js`: depois de l.44, `cenLiberarQuarentena` l.101, `cenContar`/`cenAprovarAjuste` l.105-117, `cenConcPrevia`/`cenConciliar` l.195-228;
- `gen37/areas/processo_estoque.py`: 16 trechos do diff;
- `gen37/areas/processo_os.py`: l.381-388, 426, 629-651, 908-921;
- `gen37/dados_manutencao.py`: l.401-409;
- `gen37/areas/maquinas.py`: l.452-465 e 505-516.

**Ajustes de integração (propostos; o Codex revisa):**
- **(a)** Constante `CEN_CONC_TXT` em `cenario.js` com "Rui (almoxarife) confere ou recusa o relato; Ana (gestora) aceita o excedente". Vale para `cenFecharTurno` (l.191), `cenPodeEncerrar` (l.246) e `v.k3`. Hoje o app diria só "Rui (almoxarife) concilia".
- **(b)** O texto do caso (b) da B passa a citar "Ana (gestora e agrônoma)" para a dispensa. É um literal: `cenario.js` não chama `g2lib` em código que o app e o unitário rodam sem ele (D, risco 4).

**Testes:**
- novo `gen37/aprova_quem_decide_unit.js`, que é o `teste_d2.js`: 71/71; a base passa 23 e falha 47;
- executor (hoje `ctl/d_cet/monta.py`);
- opcionais: `tela.py`, com EST 18/18, OS 7/7 e MA-04 4/4; `sintaxe.py`, com 144 telas e 0 erro.

**Testes a adaptar:**
- `esttest.py` l.47-49 e 125, mais a parte 4 nova;
- `est_cenario_test.py:58-60`, `est_repro.py:22` e `verif_est2.py:15`;
- `osacoes.py` l.80, 88-89 e 96, mais o caso Caio;
- `verif_os.py` l.82 e 93;
- `consumo_divergente_test.py:68`, mais o caso Rui;
- `ma_correcoes_om_test.py:45`, `ma_correcoes_pm_test.py:41` e `ma_planos_test.py:58`.

**Comando:** comum + executor do unit + `python3 esttest.py && python3 est_cenario_test.py && python3 est_fix1_test.py && python3 osacoes.py && python3 verif_os.py && python3 consumo_divergente_test.py && python3 ma_correcoes_om_test.py && python3 ma_correcoes_pm_test.py && python3 ma_planos_test.py && python3 widthcheck.py && python3 verif_largura.py && python3 verif_overflow.py`.

**Aceite:**
- tabela do D §5.1;
- seletor sem corte a 170 px; se cortar, rótulo "Ana · Gestora e RT";
- cliques do D §5.5 medidos.

### CTL-6 · A (apontamento único)

**Arquivos:**
- `gen37/cenario.js`: depois de l.142, `cenIniciarTurno`, `cenFecharTurno` l.158-193, `cenSinal` l.233-241, `cenPodeEncerrar` l.243;
- `gen37/areas/processo_os.py`: `osMerge` l.237-244, `osEncBloq` l.287, `osc_apontar` l.358-367, `STCOR` l.425, l.550, depois de l.621, l.628, l.754-755, 881-882, 958-962;
- `gen37/areas/inicio.py`: l.702, 828, 839;
- `gen37/areas/mobile.py`: l.20-22 e 489-491;
- `gen37/dados_carencia.py`: l.255, 299, 397.

**Ajustes de integração:**
- o `carNap` do CTL-2 passa a ignorar `CEN_AP_DESC`, com o mesmo predicado das três funções de carência (AP-09);
- os textos de consumo acima da custódia usam `CEN_CONC_TXT` (CTL-5).

**Testes:**
- novos `gen37/ap_unico_unit.js` (31 + 13) e `gen37/ap_unico_test.py` (unit e nav, até 18 verificações);
- a adaptar: `quantidade_test.py:31`, com `(24+out.n)+'/09'`, e `ostela.py:95`, com a data 2026-09-27.

**Comando:** comum + `python3 ap_unico_test.py unit && python3 ap_unico_test.py nav && python3 consumo_divergente_test.py && python3 app_mb03_turno_test.py && python3 os_cenario_test.py && python3 tabelas_est_test.py && python3 ostela.py`.

**Aceite:**
- casos do A §5.1-5.2: P1 240 ha · 120 L/40 L; W1 122/38; C11 "vale este";
- 0 item fantasma no EST;
- cliques: web 2 → 2; decisão +1.

**Se a revisão pedir divisão:** A1 = AP-01..04 e A2 = AP-05..09.

### CTL-7 · ATOR (especificar curto, o Codex revisa antes do código)

**Por quê:**
- Com o seletor do CTL-5, Caio pode clicar "Liberar", e o CTL-1 grava "aprovada por Ana (agrônoma)". É um registro de aprovação que não aconteceu, a mesma classe do S1 da F.
- O próprio D, risco 2, pede `cenExige(ator,'agronomo')` no CMD-42.
- O A, risco 5, grava "Paula" seja quem for que clique.

**Conteúdo:**
- `osc_liberar(…, ator)`: CMD-42 = `cenExige(ator,'agronomo',…)`; CMD-06 = `cenExige(ator,<papel liberador>,…)`.
  - Base: PRD 41.3 l.6864 ("o usuário possuir ambas as permissões") e CMD-06 l.2777 ("liberador autorizado por domínio").
  - O papel liberador da demonstração é decisão do Codex. Proposta: gestor.
- `osc_apDecidir(…, ator)`: `cenExige(ator,'conferente',…)` (CMD-09 l.2780).
- Paula passa a ter os papéis almoxarife e conferência. Fontes: `configuracoes.py:8`, `dados_cad.py:84` ("Conferir") e `processo_os.py:150`.
- O Mapa repassa `g2perfil()`.

**Arquivos:** `processo_os.py`, `inicio.py`, `g2lib.js` e `cenario.js`.

**Testes:** casos novos em `os_aprov_lib_unit.js`, `ap_unico_unit.js` e `aprova_quem_decide_unit.js`.

**Aceite:** Caio e Rui são recusados e nada é gravado; Ana grava os dois registros; Paula decide a duplicidade.

**Risco aberto (revisão do CTL-3, achado 5, S3 latente; vai junto do PEND-OS-01):**
- Com agrônomo e liberador em pessoas diferentes, nenhuma O.S. agrícola é liberada: a ação composta exige os dois papéis na mesma pessoa. Executado com Beto (só agrônomo) e Otávio (só gestor) injetados: os dois são recusados (`os_aprov_lib_unit.js` A8).
- No cadastro da demonstração não acontece: só Ana tem os dois papéis. No software real, travaria um fluxo essencial.
- Caminho previsto, sem código nesta entrega (PRD 8.4.1 l.2862 e 41.3 l.6864: "Aprovar sozinho não libera"; selo "Aprovada pelo agrônomo"): o agrônomo grava o CMD-42 e a ordem fica em A liberar, aguardando o liberador; o liberador grava o CMD-06. Entra quando o cadastro tiver os papéis separados (CF-01 ou software real).
- Observação: a alçada AL-01 do CF-02 (`configuracoes.py`) diz "Liberador do domínio · Caio (PCP)", e o padrão dos agentes é o gestor. Alinhar o texto do CF-02 quando o proprietário decidir o PEND-OS-01.

### CTL-8 · C1 (demanda única por fazenda)

**Arquivos:**
- `gen37/cal01.js`: l.5-7, 47 e funções novas;
- `gen37/safra.js`: `demanda()`, l.338-353;
- `gen37/dados2.py`: `os_dem`, `dem_restante`, `dem_os_evs`, `EST_FAZ`, `fisico_apto`, `RECEB_DT.faz`, `RESERVAS` l.798, `js_data` l.677-680;
- `gen37/dados.py`: l.85-86 e 93 (`chave='c4|a3'`);
- `gen37/areas/processo_compras.py`: l.235, 237, 319;
- `gen37/areas/processo_safra.py`: l.195;
- `gen37/areas/mobile.py`: l.38, 65, 667.

**Testes:**
- `cal01_test.py`: seção 4 com `negativos3` (20) e paridade JS × Python nas 3 safras;
- expectativas em l.88, 93, 100-101 e 104-107;
- `saf_cmp_continuidade_test.py`: l.61, 72, 75, 84, 92, 94-95, 135-141, 166-169, 171-172;
- `cmptest.py`: l.56, 58, 77, 102, 104, 124, 148, 151, 169-181, mais o caso Ureia;
- `tabelas_saf_test.py`: l.128-130, 137-138, 142-143.

**Comando** (o do C §5.2): `python3 build.py && python3 montar_render.py && python3 cal01_test.py && python3 saf_cmp_continuidade_test.py && python3 cmptest.py && python3 tabelas_saf_test.py && python3 partest.py`.

**Aceite:**
- S2627 com 14 insumos e R$ 430.255,00; S27SF R$ 1.094.946,91; LG2627 com 13 insumos e R$ 1.614.202,52;
- `cal01_test` sai dos vermelhos da base;
- `partest:68` continua passando.

### CTL-9 · C2 (Mapa)

**Arquivos:**
- `gen37/areas/inicio.py`: saem l.335-373 e 465-466; mudam as linhas JS 734, 784 e 895;
- `gen37/dados2.py`: `situacao_insumos`.

**Teste:** estender `map_decisoes_test.py`.

**Aceite:**
- Santa Rita, safra toda: 19 · 14 · 3 · 2;
- T1 Fungicida A com 236,6 L; T4 MAP com 17.500 kg;
- PV13 com "Falta 293 L";
- nenhum "Falta 194 L";
- a soma dos talhões fecha com a fazenda.

### CTL-10 · E2 (AG-07)

**Arquivo:** `gen37/areas/agronomia.py`: l.1116 e as remoções do E §3.

**Teste:** `agrofit_test.py`, itens 9, 12, 14 e 15.

**Aceite:** nenhuma tela diz "Receituário emitido" sem registro do AG-01.

---

## 3. Conflitos entre frentes e como resolver

| Onde | Frentes | Resolução |
|---|---|---|
| `processo_os.py` `osc_liberar` l.300-311 | F (fim comum + `osc_aprovLib`) × E1 (`osUsoErro` antes de l.308) | F → E1. A trava roda antes de qualquer gravação. N9 no unitário da F |
| `processo_os.py` `osMerge` A liberar l.245-248 e `osProx` l.415 | E1 (selo "Fora do registro", dono) × F (l.248 → `OS_AGRO`) | E1 sobre F, com `OS_AGRO` nos textos novos |
| `processo_os.py:614` e `inicio.py:816-817` (mesma linha) | F (frase "aprova esta versão e libera", `osVn`) × E1 (`osUsoAtencao`) | Texto final = F + sufixo E1. Um teste confere os dois na O.S. e no Mapa |
| `processo_os.py:802` e docstring 43-49 | F × E1 | Junção trivial |
| `cenario.js` `cenIniciarTurno` l.128-135 | B (trava) × A (`d` e `chave` no turno) | B → A. O A mantém a trava antes de criar o turno |
| `processo_os.py` `osMerge` Em execução l.237-238 (mesma linha) | B (Insumo esgotado, dono Ana, `o.esg`) × A (retido, dono Paula) | Proposta: com retido, o dono é Paula, porque a decisão muda saldo e custódia, e o selo da B continua. Caso combinado no `ap_unico_unit` |
| `cenario.js` `cenFecharTurno` e `cenPodeEncerrar`; textos | A × D (padrão 2) | Constante `CEN_CONC_TXT` no CTL-5; o A a usa |
| `dados_carencia.py` | E1 (`carNap` conta `st!=='Previsto'`) × A (`CEN_AP_DESC`) | O A estende o predicado ao `carNap` |
| `processo_os.py` l.621-651 | A (formulário, `pan_asave`) × D (`osWork` dispensa) | Linhas vizinhas; D → A, com rebase |
| `cenario.js` depois de l.41 e de l.44 | E1 (`cenUsoLegal`) × D (`cenExige`, `cenRevisao`) | Pontos distintos (conferido no diff) |
| `inicio.py` | F 21/122/816 · E1 817 · A 702/828/839 · C 335-373/465-466/JS | Rebase na ordem da pilha |
| `mobile.py` | F 332-335/375/659-695 · B 200/424 · A 20-22/489-491 · C 38/65/667 | A l.667 da C fica dentro do bloco que a F poda: F antes, e a C mexe só no texto da pendência |
| `irrigacao.py` | E3 228/252/572-574 × F 577/586/593-594 | F → E3 |
| `maquinas.py` | F × D | Sem linha comum (conferido): D 452-465/505-516; F 166-704 fora disso |
| Persona Paula | D ("Paula · Almoxarife") × A ("Paula (conferência)") | CTL-7: os dois papéis |
| Liberação com perfil | F (persona fixa) × D (seletor) | CTL-7, obrigatório antes da homologação |
| Texto da dispensa | B ("Ana (agrônoma) decide… Dispensar saldo") × D (exige gestor e agrônomo) | Ajuste (b) do CTL-5 |

---

## 4. Trabalho em andamento: conflitos e ordem

**Conflitos:**

| Frente em andamento | Estado | Conflito com o CONTROLE | Resolução |
|---|---|---|---|
| Cadeia #36–#44 e #45 (specs) | rascunho, em revisão | Base da pilha. `dados_lagoa_fonte.py` é do #36 | Só achados de revisão. Se mudar, a pilha refaz a base |
| **SAF-única 3-4-5** (`scratchpad/saf345/v2`) | especificada; impedimentos: DEC-0510 (Codex) e P1/P2 (proprietário, só para o PR 4) | `safra.js` (`outrasSafras` reusa o predicado de `demanda()` l.344); `processo_safra.py` 193/250 × C l.195; `processo_compras.py` 322 × C l.319; `dados2.py` 692 × C 677-680; o Resumo diz "já realizados" e usa a demanda bruta | **Muda o padrão de saf345 §10 l.712** (lá: CONTROLE depois do PR 5). O C entra antes do PR 1, que ainda não existe. "Não no meio dos PRs 2 a 5" continua valendo. O PR 5 usa o texto da DEM-06. A capacidade sem o realizado continua como limitação |
| **saf2, etapa 2** (`scratchpad/saf2`) | especificada | PR-A: `ocupacao.*` + `dados2.py:78-80`. PR-B: `safra.js` 291-307/495-577/885-927, `processo_safra.py` 29-49/201-222, `g2lib.js` 146/172/186/221 | PR-A pode correr em paralelo (spec §8). PR-B depois da SAF-única. Refazer a paridade da C depois do PR-B |
| **SUP simplificado v2** (`scratchpad/sup/v2`) | especificada | **Duas soluções para o mesmo problema** (l.48, 50, 375; DECISOES 10-11): "Ver como" × perfil da D; `cenLaudo` por parcela × `cenLiberarQuarentena(…,laudo,ator)`; "quem contou não aprova" (recusa pelo contador declarado: a burla que a D corrigiu) × padrão 2 (revisão posterior pelo registrante); SUP-1 em `processo_os.py` 242-244/287-291 × A; `osIniErro` l.347 × B | A D entrega os itens 1, 2 e o padrão 2. A SUP é revista para **reaproveitar** `G2_PERFIS`/`g2perfil` como "Ver como", estender o laudo da D a parcelas, seguir o padrão 2 e manter o ramo de duplicidade do A e o mapa de links da B |
| **PCM × suprimentos** (`sp-specs 9c53fc2`) | especificado | 1a: `dados_manutencao.py` 249-282, prefixos em `maquinas.py` 168/277/326/557/706/1171, `cenario.py` v=4. 1b: `cenEntregar`/`cenPodeEncerrar` com `cenOrdem`, `cenMudar(self,fn,cmd)` (G04), `osc_cancelar` 378-382, `maquinas.py` 379-401/469-478. 1c: `cenLiberarQuarentena` | Depois do CONTROLE e da SUP-2b. O 1b mantém a checagem do retido (A) e reaproveita a chave do A como `cmd.chave` (mesma semântica de conflito). O M15 chama `cenConciliar` com ator (padrão 2). O 1c parte da assinatura da D. A medição de cliques "antes" do PCM já inclui a D4 (sem "Marcar pendentes") |
| **Beneficiamento** (`sp-specs 9c53fc2`) | especificado; depende do PCM 1a-1c (P3) | BEN-1a move a regra "sem material" para `cenLiberar` e liga a OB por fora de `osc_liberar`: **quebra o E1b da F** ("só `osc_liberar` chama `cenLiberar`"). BEN-1b tira textos da OB-0104 (`processo_os.py` 66-142) × F l.177. Marta (Qualidade) × D (gestora libera quarentena) | Lista de exceções no E1b para `fam:'BEN'` (CMD-42 não se aplica, l.2874-2876). F antes. O padrão da quarentena é revisto quando a Marta entrar |

**Ordem proposta.** A ordem da fila é do Codex (RETOMADA D7; BEN P3; SUP §0.1).

0. Cadeia #36–#45 em revisão.
1. **CONTROLE-01**, do CTL-1 ao CTL-10, mais os portões G1 a G4. Em paralelo, só o que não muda tela nem toca arquivo do CONTROLE: saf2 PR-A e SUP-0.
2. **SAF-única**, do PR 1 ao PR 5. Mandar já ao proprietário as perguntas P1 e P2, para não travar o PR 4.
3. **saf2 PR-B**, depois **PR-C**.
4. **SUP-1, SUP-2a, SUP-2b.** A SUP-1 vem depois da SAF-única pela própria spec (K-R08).
5. **PCM 1a, 1b (1b-i/1b-ii), 1c-dados.**
6. **SUP-3** (= PCM 1c-tela): depois da SAF-única, do PCM 1c-dados e do CTL-8.
7. **BEN-1** (1a, 1b, 1c).

Condição: se o Codex classificar como S2 o item 12 da auditoria (estoque próprio da manutenção, `dados_manutencao.py:399-447`), o PCM 1a/1b sobe para logo depois do CONTROLE. Nenhuma versão sai com S2 conhecido.

---

## 5. Fica para depois

| Item | Por quê | Quando |
|---|---|---|
| Entrada de Controle transversal (previsto × realizado: custo, insumo, área, prazo); o ato de "revisar" a revisão posterior (D §9) | Padrão adotado (3). Sobre fontes ainda divergentes, mostraria números errados | CONTROLE-02, depois do CTL-10 |
| Conferência diária na O.S. (item 14; DEMO-13 l.4734; hoje `processo_os.py:375`) | Sem desenho. Precisa do comando único e da decisão CMD-09 do A. Modelo a reaproveitar: R-A01/R-A12/R-F02 da BEN | CONTROLE-02, 1º item |
| Versão de referência do plano (RN-031, item 15) | A SAF-única a remete ao CONTROLE (FORA-DE-ESCOPO l.8). Exige base, revisão e realizado juntos | CONTROLE-02 |
| Capacidade descontando o realizado (saf345 §7 l.517); realizado no custo | A Frente C cobre só a demanda de insumo | CONTROLE-02 / ORC-CUSTOS (fila D7) |
| Condição técnica única (item 11) | PCM Bloco 2 (PCMS-A01/A02). O PCM 1a reescreve o estado da manutenção | PCM Bloco 2 |
| Horímetro único e "Gerar ordem" repetido no PM (`maquinas.py:89, 961, 1129`) | O PCM não trata. O PCM 1a muda o estado e refaria o trabalho | Pedido ao Codex: incluir no PCM 1a (auditoria §6) |
| Leitura viva da semente na demanda (C, risco 1) | Não regride em relação ao HEAD | Fatia seguinte à C (P2) |
| Direção na Compra (item 5) | Risco do software real; no protótipo, "Ver como Direção" | SUP-3 / software real |
| Resíduos das frentes | Cada um como tarefa própria | Lista abaixo |

Resíduos das frentes:
- **A §9:** talhão e operador editáveis; formulário de consumo no Mapa; PER-12; corrigir com histórico.
- **B:** R6 (fora da requisição: semente); R7 (`confirmado` não zera a cada entrega); R9 (OS-0424-app).
- **C §6.5:** `cenLote` entre fazendas; `processo_os.py:794` (RN-008); NEC-028 2ª onda; incoerências da semente.
- **D §9:** laudo reprovado; respostas do PRD 54.2; CMD-46; lote vencido trava só na tela; SU-09; índice.
- **E §7:** P2 (contagem AG-01 × O.S., S3); duas regras de carência; cadastro do Inseticida B; AG-07 → AG-01 sem contexto.
- **F §9:** CA-01det/CA-01x fixos; ações simuladas no MB-02 e no MB-05; REQ-038 órfã (S3); rótulo "Aprovar e liberar" (S4); data no registro.

---

## 6. Registro

### 6.1 RETOMADA (commit só de reserva antes do CTL-1, padrão `1fbb354`)

```text
## Reserva ativa · CONTROLE-01 (auditoria P×C×E; pedido do proprietário 05/10/2026: "execute a melhor recomendação") · pilha claude/v44-controle-01..10 sobre claude/v44-tabelas-05 (884620c)
ID / resultado útil / persona: CONTROLE-01 · um comando por fato em todos os canais e aprova quem decide · Ana (gestora e agrônoma RT), Paula (conferência), Rui (almoxarife), Marcos (operador), Caio (PCP), Zé (mecânico)
Requisitos do PRD e fora do escopo: 41.1-41.3 (l.6842-6864), CMD-06/09/42/47/50, RN-015/016/018, 8.5 (OSDIA-03/04/06), DEMO-11, CAL-01, RN-006/011/013, AGUA-08, PRD 2.1 l.195, ENG-011/021 · fora: entrada de Controle, conferência diária, versão de referência, condição/horímetro (PCM Bloco 2)
Autor / revisor / integrador: Claude / Codex / Codex
Base / arquivos: 884620c · por PR (plano §2); cada PR registra a sua reserva antes de editar. dados_lagoa_fonte.py: extensão da reserva CAMADA-SINTETICA (mesmo autor)
Aceite e comando: por PR; bateria completa sem falha nova contra os 11 vermelhos de 0cf6f90 (v44-tabelas-05/un-20261005)
Estado / impedimento / próximo passo: especificado e executado em cópia (scratchpad/ctl) · G1 (OS-0424), G2 (ENG-017), G3 (B-R8), G4 (CTL-7) bloqueiam só a homologação · CTL-1
Padrões adotados em 05/10/2026 (o proprietário pode mudar):
(1) O.S. sem etapa de revisão (pedido de 01/10) fica; "Liberar para execução" = "Aprovar e liberar" do PRD 41.3 (l.6864): uma confirmação grava CMD-42 (aprovado por) e CMD-06 (liberado por) em separado. Pendente × DEC-2609-05.
(2) Ajuste de estoque e consumo acima da custódia: aprova o gestor; se quem decide registrou a contagem, a decisão vale e fica "revisão posterior pendente" (PRD 2.1 l.195).
(3) Entrada de Controle transversal fica para depois do CONTROLE-01.
Padrões técnicos dos agentes (o Codex revisa; o proprietário pode mudar): PA-C1..C4 (Frente C); quarentena liberada pela gestora com laudo (R-D2); checklist sem trava de papel (R-D4); duplicata provável retida, decidida por Paula com três saídas (AP-05..07); captação comum do Rio A (RL-E4, pergunta ao proprietário para a fazenda real); C antes do PR 1 da SAF-única (muda saf345 §10 l.712).
Sobreposições declaradas: SAF-única e saf2 (safra.js, processo_safra.py, dados2.py, processo_compras.py, g2lib.js por função); SUP v2 (reaproveita a D, sem regra paralela); PCM (cenario.js, dados_manutencao.py, maquinas.py, processo_estoque.py, processo_os.py); BEN (lista de exceções do E1b).
```

### 6.2 Pedido ao Codex (issue 1 e arquivo de rodada em `docs/parceria/rodadas/`, no main)

Pedidos:
1. Parecer sobre a ordem dos §1 e §4.
2. Registro do pedido de 05/10 na rodada.
3. Linhas em `docs/DECISIONS.md` › "Decisões pendentes do proprietário", dizendo "padrão adotado", porque o cabeçalho da seção manda valer o comportamento conservador do PRD:

```text
| PEND-OS-01 | O.S. sem etapa de revisão (pedido de 01/10) × DEC-2609-05. Padrão adotado pelos agentes em 05/10 (vale até a decisão; o proprietário pode mudar): "Liberar para execução" é o "Aprovar e liberar" do PRD 41.3, com CMD-42 e CMD-06 registrados em separado | PRD 41.3; 72.2 |
| PEND-CTL-02 | Quem aprova ajuste de estoque e consumo acima da custódia. Padrão adotado: o gestor; se a mesma pessoa registrou a contagem, fica revisão posterior | PRD 2.1; DEC-2609-13; RN-018 |
| PEND-CTL-03 | Entrada de Controle transversal (previsto × realizado). Padrão adotado: depois do CONTROLE-01 | PRD 71.6 |
```

Decisões pedidas ao Codex, que não são do proprietário:
- **(a)** correção da semente da OS-0424 (G1);
- **(b)** classificar a B-R8, o CTL-7 e o item 12 da auditoria;
- **(c)** qual papel de `G2_PERFIS` é o "liberador" do CMD-06;
- **(d)** incluir horímetro único e "Gerar ordem" do PM no PCM 1a;
- **(e)** conferir com o proprietário o possível dado real em `dados_irrigacao.py:43` antes de qualquer publicação (G2).

**Pergunta ao proprietário (realidade da fazenda):** os pivôs da Lagoa Grande captam numa rede comum às outorgas do Rio A? (E, risco 6.)
## 7. CTL-4 (demanda única) · revisão do `853a6a8`: correções

Revisão adversarial "lente estado" do `853a6a8` (ACHADOS-v1): 2 S2 e 5 S3, todos corrigidos, um commit por achado, cada um com regressão que falha no `853a6a8` e passa na candidata. Detalhe, regras e evidência em `desenho/FRENTE-C.md` §10.

- `7ffe412` · S2 · custódia sem uso nas O.S. (cancelada, em conferência, encerrada ou excedente) é suprimento: cancelar ou devolver não muda a compra (I1–I4, nav K1, K2). Semente: MAP 79.500 kg, R$ 428.305,00.
- `b64d556` · S3 (base) · cancelar com material entregue mostra a custódia e o próximo passo "Receber devolução" (I5, nav K3).
- `e907539` · S2 · quarentena com laudo pendente é falta condicionada à qualidade, fora da compra e da primária; laudo reprovado vira falta firme com o motivo (I6, I7, nav Q1–Q3).
- `6fce782` · S3 · turno do app sem sinal não muda a compra até o envio (I8, nav A7).
- `1fe0902` · S3 · reserva que a O.S. já não usa deixa de ser demanda (I9, nav R1).
- `84494d7` · S3 · reserva entre fazendas conta uma vez em cada (I10, nav F1).
- `4130972` · S3 · SU-03det e MB-05 leem a mesma demanda viva (nav D3).
- `6202376`, `78711bb` · vermelhos novos da bateria (cache do Mapa; saf_cmp_continuidade e esttest).

Bateria 853a6a8 × candidata (executado; logs em `scratchpad/ctl4fix/logs/{base,cand}/`): nenhum vermelho novo; os quatro vermelhos que já estavam no `853a6a8` (consumo_divergente 1, os_cenario 1, ostest 1, testes_pedido T01/T02/T05) continuam iguais; build 0 FALHA, varredura 140/140, ações duplicadas 0.

**Revisão do `16fb55e` (Codex, PR #47, comentário 6136083713; tarefa CTL4-FIX-REV-20261013-01).** São 4 S3 e os quatro procedem por execução. Cada um tem um commit e uma regressão que falha no `16fb55e` e passa depois. Detalhe e evidência em `desenho/FRENTE-C.md` §10.1.
- `81aef42` · ajuste 1 · o Mapa perdia a qualidade pendente quando havia falta firme ao mesmo tempo.
  - Contraexemplo: demanda 100 kg, estoque 0 e quarentena 40 davam só "Falta 60 kg".
  - Correção: o Mapa, o SU-03det e o MB-05 mostram também "Qualidade pendente · 40 kg", com quem decide. A compra continua em 60 kg e não há segunda ação.
  - Testes: J1 e J1b; nav M1 (no `est_laudo_lote_nav_test` desde o `718a914`).
- `7551f1a` · ajuste 2 · a memória atribuía todo o reprovado ao último laudo.
  - Contraexemplo: devolver 10 L, reprovar LAB-A, devolver mais 10 L e reprovar LAB-B dava "20 L · laudo LAB-B".
  - Correção: os laudos vêm do histórico do lote ("= 10 L no laudo LAB-A: motivo A + 10 L no laudo LAB-B: motivo B"). O selo do lote no Estoque segue a mesma regra.
  - Testes: J2 e nav L2.
- `0ee25bd` · ajuste 4 · reprovar com a mesma autora da entrada bloqueada não marcava revisão posterior.
  - Correção: vale a mesma regra de acúmulo da liberação (`cenRevEntrada`), sem veto nem segundo aprovador.
  - Testes: J4 (positivo e negativo), nav L2b e L3.
- `6236d70` · ajuste 3 · o motivo migrava entre lotes.
  - Contraexemplo: o motivo digitado no K26-11 aparecia ao abrir o F26-02.
  - Correção: abrir, manter, decidir, trocar o perfil ou restaurar limpam o laudo e o motivo. O foco, o Tab e a tela de 390×844 continuam iguais.
  - Testes: nav L1 e L1b.
- Bateria da candidata, uma execução por teste (logs em `scratchpad/ctl4rev01/logs/{cand,base}/`):
  - build 0 FALHA; varredura 140/140.
  - Motor: demanda_unica 70/0, cal01 45/0, aprova_quem_decide 102/102.
  - Telas: est_laudo_lote_nav 7/0, demanda_estado_nav 11/0, demanda_unica_nav 29/0, saf_cmp_continuidade 31/0, esttest, est_fix1/2, est_cenario, talmapa, sutest, mbtest e cmptest verdes.
  - No `16fb55e` falham só os casos novos: J1, J1b, J2 e J4; L1, L2, L2b e M1.
  - Vermelho novo: nenhum. O `demanda_estado_nav_test` com o M1 passou de 900 s sob carga (rc=124), por isso o M1 mudou de arquivo.
