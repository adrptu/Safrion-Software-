# CONTROLE-01-F · Frente F (corrigida): liberar a O.S. registrando quem aprovou (CMD-42) e quem liberou (CMD-06), e tirar das telas visíveis, inclusive do app em teste, os elos para telas ocultas e fixas

Severidade: S1 no item 1. Pela regra do AGENTS §3, a aprovação é exigida pelo domínio e a liberação a presume sem registrá-la. S3 no item 2. Os elos levam a telas fixas que fingem gravar (ROM-0791 no MB-10det, DV-0912 no MB-05det), mas o estado vivo (Estoque e O.S.) continua certo e segura o encerramento.

Dano: Item 1: uma O.S. com defensivo ou fertilizante vai a campo sem registro de quem aprovou, de qual versão, para que área e com que doses. A liberação passa a valer como aprovação, o que o PRD 41.1 proíbe ("não pode ser presumida"). Sem esse registro, falta rastro para a responsabilidade técnica e para a auditoria. Item 2: de uma tela viva, a pessoa cai numa tela de números fixos que não lê nem grava o estado. Ali ela decide com dado falso ou "registra" algo que some. Exemplos: o MB-10det emite o ROM-0791 sem gravar nada; no MB-05, o almoxarife abre o MB-05det, "confirma" a devolução DV-0912 e lê "custódia de Paula zerada", enquanto o Estoque e a O.S. seguem com 10 sc em custódia na OS-0417. Isso acontece no app MB-01..05, que a DEC-2609-13 põe em teste com clientes.

PRD: PRD 41.1: l.6842 ("aprovação não pode ser presumida"), l.6844 (manutenção com responsável próprio), l.6848 (água fora da revisão). PRD 41.2, l.6860: a aprovação grava identidade, papel, data/hora, versão, escopo e doses. PRD 41.3, l.6864: "Aprovar e liberar" registra CMD-42 e CMD-06 separadamente na mesma confirmação. CMD-42 (l.2825). CMD-06 (l.2777: "aprovado/pronto sem evento permanece A liberar"). l.2968 e OSFASE-02 (l.2997). l.10294 ("nenhum fluxo abrevia aprovação obrigatória [...] ou rastreabilidade"). DEC-2609-05 (l.12220), DEC-2609-10 (l.12224) e DEC-2609-13 (l.12227: app MB-01..05 e devolução conferida para os primeiros testes com clientes; "o que acontece numa tela aparece nas outras"). Recorte do protótipo: l.255 e 71.6. AGENTS §3 (S1–S4; regra repetida vira fonte única) e §4 (servidor autoridade, trava com dano nomeado, estado visível, uma ação primária).

Arquivos: /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/processo_os.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/inicio.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/maquinas.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/irrigacao.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/areas/mobile.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/map_decisoes_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/matest.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/etapas_celular_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/ostela.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/os_v39_liberar_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/os_cenario_test.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/mbtest.py, /home/user/sp-tab5/tools/prototipo/v37/gen37/irtest.py, /home/user/sp-tab5/tools/prototipo/v37/RETOMADA-NUVEM.md, /home/user/Safrion-Software-/docs/DECISIONS.md, scratchpad/ctl/fFc/patch2.py, scratchpad/ctl/fFc/patch3.py, scratchpad/ctl/fFc/patch4.py, scratchpad/ctl/fFc/unit_liberar_c.js, scratchpad/ctl/fFc/estrutura_test_c.py, scratchpad/ctl/fFc/run.py, scratchpad/ctl/fFc/chk.py, scratchpad/ctl/fFc/ataque1.js, scratchpad/ctl/fFc/ataque4.js, scratchpad/ctl/fFc/ataques_no_desenho.txt, scratchpad/ctl/fFc/unit_saidas.txt, scratchpad/ctl/fFc/estrutura_saidas.txt, scratchpad/ctl/fFc/processo_os.py.diff, scratchpad/ctl/fFc/inicio.py.diff, scratchpad/ctl/fFc/maquinas.py.diff, scratchpad/ctl/fFc/irrigacao.py.diff, scratchpad/ctl/fFc/mobile.py.diff, scratchpad/ctl/fF/repro.js, scratchpad/ctl/fF/links.py

# Frente F (corrigida): liberação da O.S. com aprovação registrada e elos para telas fixas

**Base:** protótipo `884620c` (`claude/v44-tabelas-05`), PRD v3.9.

**O que rodei nesta contestação:**
- O desenho original continua aplicado em `ctl/fF/v37`.
- As correções desta revisão foram aplicadas por cima numa segunda cópia, `ctl/fFc/v37`, com `patch2.py`, `patch3.py` e `patch4.py`. Cada trecho antigo apareceu exatamente uma vez.
- O build completo da cópia corrigida gerou 144 quadros.
- Os testes em node e python rodaram em três árvores:
  - o código atual, em `ctl/fFc/base` (fontes iguais às do repositório, conferido com `diff -rq`);
  - o desenho original;
  - o desenho corrigido.

**Não feito:** navegador; nenhuma edição no repositório.

**Padrão adotado (o proprietário pode mudar):** a O.S. continua sem etapa de revisão, como no pedido de 01/10. "Liberar para execução" passa a ser a ação composta "Aprovar e liberar" do PRD 41.3 (l.6864): uma só confirmação grava dois registros separados, a aprovação da versão (CMD-42) e a liberação (CMD-06).

## 1. Problema reproduzido (executado; continua válido)

Comando: `python3 ctl/fF/run.py ctl/fF/repro.js` (CEN0, `cenario.js` e `JS_NUCLEO` com carência).
- A OS-0430 vai a Liberadas e a REQ-041 reserva 320, 160 e 80 L. A única autoria gravada é "Sistema", nos movimentos de reserva, e não há CMD-42 nem CMD-06.
- A OS-0511 (sem insumos) é liberada sem nenhum registro.
- A OS-0501 ajustada e liberada grava só "v2 ajustada por Ana (agrônoma)" (`processo_os.py:336`).
- Repetir a confirmação da OS-0430 é recusado: "OS-0430 não está em A liberar.".
- O docstring confirma a lacuna: "não há aprovar… nem recibo APV-" (`processo_os.py:44-47`).

**Elos de telas visíveis para telas ocultas, nos pares do escopo** (`ctl/fF/links.py` sobre o `project/` do repositório):
- IN-04 → PL-05, CA-02 e CO-06det (estes dois pelo `OSD`);
- OS → CA-02 e CO-06det;
- IR-04 → GE-07;
- MA-01 → PL-04;
- MA-02 → PL-05det;
- MA-03 → PL-05;
- MA-04det → PL-05 e PL-05det;
- MA-05 → MB-09;
- MB-01 → MB-07, MB-08, MB-09 e MB-10;
- **MB-02 → MB-08;**
- **MB-05 → MB-05det e SU-03det.**

As duas últimas linhas entram nesta correção: são a mesma classe de elo, no app em teste com clientes (DEC-2609-13).

O elo de `inicio.py:1372` está no IN-01, que é oculto: vai de oculta para oculta e fica sem ação.

## 2. Regras

| ID | Regra (testável) | Dano que evita | Fonte |
|---|---|---|---|
| F-R1 | Confirmar a liberação de uma O.S. agrícola grava, na trilha da ordem, dois registros `{cmd, v, por, at, t}`. Vale com ou sem insumo e também para fertirrigação. CMD-42: "vN aprovada por <agrônomo> às hh:mm · <área> ha · <produto dose un/ha, …> (CMD-42)", com a dose na precisão do ajuste (até 4 casas). CMD-06: "vN liberada por <quem> às hh:mm[ · REQ-xxx reservada no Estoque] (CMD-06)". O trecho da requisição só aparece quando a reserva existe (`o.reservado`). | Aplicação a campo sem aprovação técnica rastreável; trilha que afirma dose ou reserva diferente da real | 41.1 l.6842; 41.2 l.6860; 41.3 l.6864; CMD-42 l.2825; CMD-06 l.2777; l.10294 |
| F-R2 | Nada é gravado quando a liberação falha (sem lote, saldo, carência, total 0), na prévia `osLibErro` ou no ajuste sem liberar. Repetir a confirmação não cria um terceiro registro. | Aprovação registrada para ordem não liberada; registro em duplicidade | AGENTS §4; OSFASE-02 l.2997 |
| F-R3 | Água só com água não grava CMD-42: libera pela prontidão, e a Irrigação grava o próprio `LIB-` (`irrigacao_estado.js:245`). O ramo água de `osc_liberar` (`processo_os.py:302-303`) não é alcançado hoje, porque o cenário da O.S. não tem ordem só de água (executado: chaves de `cenGet().ordens`). Manutenção (`manLiberar`, `dados_manutencao.py:386`) e beneficiamento não passam por esse comando. | Agrônomo registrado como aprovador fora da sua competência | DEC-2609-10 (l.12224; l.6848); l.6844; CMD-42 l.2825 |
| F-R4 | A confirmação diz que confirmar é **aprovar esta versão e liberar** e nomeia a mesma versão que o registro grava (`osVn`). O aviso não traz um segundo "Próximo passo": o próximo passo fica só no painel (`osCondGen`). | Aprovação dada sem a pessoa saber que aprovou; dois próximos passos diferentes | 41.1 l.6842; 41.3 l.6864; AGENTS §4 |
| F-R5 | Tela visível não leva a tela oculta e fixa: cada elo é removido ou aponta para a tela viva. No Mapa, o elo removido não é trocado por um detalhe fixo como primário. | Decisão com número falso; registro que some | l.255 e 71.6; DEC-2609-13 l.12227; AGENTS §4 e §3.2 |

## 3. Mudança de código exata (aplicada e construída em `ctl/fFc/v37`; diffs em `ctl/fFc/*.diff`)

### `areas/processo_os.py` (+30 −15)

**1. Antes de `osc_liberar` (l.299):**
```js
const OS_AGRO='Ana (agrônoma)';   // agrônoma das duas fazendas no protótipo (DONO aqui e em dados_lagoa_safra)
function osVn(s){ return (String(s||'').match(/\bv\d+\b/g)||['v1']).pop(); }   // o último vN: fonte única (tela, Mapa e registro)
function osc_aprovLib(o){ const hr=cenAgora(), vn=osVn(o.versao);
  const esc=cenNum(o.area)+' ha · '+((o.ins||[]).length?o.ins.map(x=>x.p+' '+cenNum(x.dose,4)+' '+x.un+'/ha').join(', '):'sem insumos');
  o.osc.ev=(o.osc.ev||[]).concat([{cmd:'CMD-42',v:vn,por:OS_AGRO,at:hr,t:vn+' aprovada por '+OS_AGRO+' às '+hr+' · '+esc+' (CMD-42)'},
    {cmd:'CMD-06',v:vn,por:OS_AGRO,at:hr,t:vn+' liberada por '+OS_AGRO+' às '+hr+(o.reservado&&o.req?' · '+o.req+' reservada no Estoque':'')+' (CMD-06)'}]);
  return ' '+vn+' aprovada e liberada por '+OS_AGRO+'.'; }
```

**2. `osc_liberar` (l.305-311):** os ramos "sem insumo" e `cenLiberar` passam a terminar num fim comum, `let r; … r.msg+=osc_aprovLib(o); return r;`. O ramo água (l.302-303) não muda.

**3. `osMerge`, depois da l.230:**
```js
if(x.ev&&x.ev.length) o.orig=(o.orig||[]).concat(x.ev.map(e=>e.t));
```

**4. Nome da agrônoma numa fonte só:**
- l.336: `'ajustada por Ana (agrônoma) às '` vira `'ajustada por '+OS_AGRO+' às '`;
- l.248 e l.802: `'Ana (agrônoma)'` vira `OS_AGRO`.

**5. Dose na trilha do ajuste (l.329-330):** `cenNum(x.dose)`, `cenNum(d)` e `cenNum(a.dose)` passam a usar `,4`. Assim 0,125 L/ha não vira 0,13 L/ha.

**6. Versão (l.559):** `const vs=…; const vcur=vs.length?…:'v1';` vira `const vcur=osVn(o.versao);`.

**7. Confirmação `pan_ct.liberar` (l.614):**
- depois de `'(versão '+o.versao+'): '`, entra `'ao confirmar, '+OS_AGRO+' aprova esta versão e libera; '`;
- "sem insumos a reservar; nenhuma…" vira "sem insumos a reservar, nenhuma…".

**8. Elos (l.153 e l.177):**
- l.153: `LINK={'OS-0417':'CA-02.dc.html'}` vira `SEM_LINK={'OS-0417','OB-0104'}`;
- l.177: `link=('' if o['id'] in SEM_LINK else (o['detalhe'] or ''))`.

**9. Docstring (l.47):** registra o padrão de 05/10 (CMD-42 e CMD-06 separados na Origem; o proprietário pode mudar).

### `areas/inicio.py` (+4 −4)
- **l.122:** `('OS-0420',['T4'],'','atrasada',('Acompanhar OM-0233','MA-04.dc.html#OM-0233','op',None))`. O destino é a OM-0233 viva: está no seed da manutenção (`dados_manutencao.py:192`) e o MA-04 abre o painel pela âncora (`maquinas.py:422`). O desenho original punha `None` aqui.
- **l.816 `mapCt`:** `const vn=osVn(o.versao);`, versão sempre exibida, e a mesma frase de confirmação da O.S. (`': ao confirmar, '+OS_AGRO+' aprova esta versão e libera; '`).
- **l.21, docstring:** "no Mapa o próximo passo é Acompanhar OM-0233 (MA-04…)".

### `areas/maquinas.py` (+7 −9, igual ao desenho)
- l.166: sai "Ver agenda" (PL-04).
- l.265 e l.624: "Ver impedimento" (PL-05det) vira "Abrir O.S." → `OS.dc.html#OS-0431`.
- l.323 e l.362: saem "Abrir impedimentos" (PL-05) e `mi_link`.
- l.627: `ab:[{k:'mut',t:'—'}]`.
- l.704: sai "Abrir no app" (MB-09).

### `areas/irrigacao.py` (+1 −4, igual ao desenho)
- Saem `prob/p_has/p_t` (l.577), a ação "Abrir ação" (GE-07, l.586) e o primário com GE-07 (l.593-594).

### `areas/mobile.py` (+6 −12)
- **l.332-335:** saem os cartões MB-07 a MB-10. Ficam 5 cartões e 1 `<span>`.
- **l.375 (MB-02):** sai `btns(lnk('Abrir água simplificada','MB-08.dc.html',…))`. A nota "Água simplificada: abre em Irrigação…" fica.
- **l.660 (MB-05, aba Almoxarife):** sai `btns(lnk('Abrir tarefa','MB-05det.dc.html',…))`.
- **l.669:** sai `lnk('Ver conflito','SU-03det.dc.html',…)`. O `say('Registrar divergência',…)` fica e entra no resíduo.
- **l.688 e l.695:** saem `v.p_qr=!r0;` e o primário `('p_qr','a','Ler QR da O.S.','MB-05det.dc.html')`.

### Documentação
- **`docs/DECISIONS.md`:** vai num pull request separado, na linha de documentação. A linha do protótipo (`sp-tab5`) não tem `docs/DECISIONS.md`; ela só tem `docs/claude` e `docs/parceria`. Na seção "Decisões pendentes do proprietário", entra:

  `PEND-OS-01 | O.S. sem etapa de revisão (pedido de 01/10) × DEC-2609-05. Padrão adotado pelos agentes em 05/10, que vale até a decisão e que o proprietário pode mudar: "Liberar para execução" é o "Aprovar e liberar" do PRD 41.3, com CMD-42 e CMD-06 registrados em separado | PRD 41.3; 72.2`

  O texto precisa dizer "padrão adotado" porque o cabeçalho da seção manda valer o comportamento conservador do PRD, que seria a DEC-2609-05.
- **`tools/prototipo/v37/RETOMADA-NUVEM.md`:** estado da frente.

O cenário salvo no navegador não precisa de nova versão (`v`), porque `osc.ev` é opcional.

## 4. Textos de tela

**Confirmação na O.S.:** "Liberar OS-0430 (versão v1): ao confirmar, Ana (agrônoma) aprova esta versão e libera; a requisição reserva no Estoque, por lote: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L."

**Confirmação no Mapa:**
- com insumos: a mesma frase;
- sem insumos: "…e libera; sem insumos a reservar."

Os botões continuam "Liberar para execução" e "Confirmar liberação".

**Aviso depois de liberar:**
- com insumos: "OS-0430 liberada. REQ-041 reservou no Estoque: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L. v1 aprovada e liberada por Ana (agrônoma)."
- sem insumos: "OS-0511 liberada. Sem insumos a reservar: nenhuma requisição no Estoque. v1 aprovada e liberada por Ana (agrônoma)."

**Próximo passo:** só no painel, por exemplo "Liberada · REQ-041 reservou os insumos no Estoque. Próximo passo: iniciar na janela 25/09 (DAP −20)." (executado).

**Origem:**
- "v1 aprovada por Ana (agrônoma) às 17:05 · 160 ha · Glifosato 480 2 L/ha, 2,4-D 806 1 L/ha, Óleo mineral 0,5 L/ha (CMD-42)"
- "v1 liberada por Ana (agrônoma) às 17:05 · REQ-041 reservada no Estoque (CMD-06)"

**Mapa, OS-0420:** o impedimento "Apontamento pausado: Trator T1 bloqueado (OM-0233)" mostra:
- primário "Acompanhar OM-0233" (MA-04#OM-0233);
- o elo "Abrir a ordem completa ›";
- "Abrir ordem ›" (O.S.).

Nenhum destino se repete.

**Recusas:** não mudam.

## 5. Decisão por elo (sem criar tela)

| Origem visível (arquivo:linha) | Destino | Decisão | O que fica |
|---|---|---|---|
| O.S., OS-0417 (`processo_os.py:153`) | CA-02, fixa (`campo.py:425-438`) | remover | "Encerrar bloqueado: sobra em custódia…" com "Receber devolução no Estoque" (EST, vivo) |
| O.S., OB-0104 (`processo_os.py:177`) | CO-06det, fixa | remover | A situação já cita o lote L27-013 e a INSP-88 |
| Mapa, OS-0420 (`inicio.py:122`) | PL-05 | apontar para a tela viva: "Acompanhar OM-0233" → `MA-04.dc.html#OM-0233` | Mantém o mesmo arranjo do painel. Não promove o CA-01x-os0420, que é fixo e leva de novo a PL-05 por "Reprogramar saldo" (`campo.py:355`) |
| MA-03 (`maquinas.py:323, 362`) | PL-05 | remover | "Mover a preventiva" e "Propor substituição" |
| MA-02 e MA-04det, OS-0431 (`maquinas.py:265, 624`) | PL-05det | apontar para `OS.dc.html#OS-0431` | "Liberar bloqueado: Trator T1… · Quem resolve: PCP" |
| MA-04det, "Agenda do Trator T1" (`maquinas.py:627`) | PL-05 | remover (fica "—") | Não existe agenda viva |
| MA-01 (`maquinas.py:166`) | PL-04 | remover | Seletor de tarefa e quadro de ativos |
| MA-05 (`maquinas.py:704`) | MB-09 | remover | "Registrar abastecimento" já grava na própria tela |
| IR-04 (`irrigacao.py:577, 586, 593-594`) | GE-07 | remover | Chip de suspeitas e sem dado (`irrigacao_estado.js:583`); "Validar leitura" e "Marcar leitura suspeita" na linha |
| MB-01 (`mobile.py:332-335`) | MB-07 a MB-10 (só simulam, `mobile.py:23`) | remover | MB-02 a MB-06 |
| **MB-02, OS-0419 (`mobile.py:375`)** | MB-08 (só simula) | remover | A nota da água; a ordem viva está na Irrigação |
| **MB-05, aba Almoxarife (`mobile.py:660, 695`)** | MB-05det (DV-0912 só no estado da tela, `mobile.py:716-717`) | remover os dois elos | A devolução viva é no EST ("Receber devolução da REQ-031") |
| **MB-05, aba Almoxarife (`mobile.py:669`)** | SU-03det, fixa | remover | O cartão do conflito F26-02, que fica no resíduo |
| IN-01 → CA-02 (`inicio.py:1372`) | — | sem ação | IN-01 é oculto |

"Rotular simulação" não foi usado.

## 6. Testes

### 6.1 Unitário em node (executado)
Arquivos: `ctl/fFc/unit_liberar_c.js`, que entra no repositório como `gen37/os_aprov_lib_unit.js`, e o executor `ctl/fFc/run.py`. Saídas em `ctl/fFc/unit_saidas.txt`.

| Árvore | Verificações | Falhas |
|---|---|---|
| Código atual | 21 | 14 (passam só P1e e N2–N7) |
| Desenho original | 21 | 5 (P1d, P2, P5, N8, D) |
| Desenho corrigido | 21 | 0 |

**Casos positivos e de versão:**
- **P1 (OS-0430):** grava 2 registros, v1, por Ana (agrônoma).
  - CMD-42: "160 ha · Glifosato 480 2 L/ha, 2,4-D 806 1 L/ha, Óleo mineral 0,5 L/ha".
  - CMD-06: "REQ-041 reservada no Estoque".
  - O aviso termina em "v1 aprovada e liberada por Ana (agrônoma).". O painel diz "Próximo passo: iniciar na janela 25/09 (DAP −20).".
  - As reservas não mudam: 320, 160 e 80 L.
  - A Origem fica com 4 linhas.
- **P2 (OS-0511, 36,17 ha):** 2 registros. O CMD-06 sai sem requisição e não surge nenhum movimento novo.
- **P3 (OS-0501 ajustada):** aprova a v2 com 2,5 L/ha; a REQ-042 reserva 123,28 L.
- **P4 (OS-0418, fertirrigação v2):** "95 ha · Ureia 45% 12 kg/ha"; reserva de 1.140 kg.
- **P5 (ordem nova sem executor):** aviso sem "—"; CMD-42 com "Fungicida TS 0,1 L/ha, Inoculante líquido 0,2 L/ha".
- **V e V2 (`osVn`):** "REC-014 v2 · v1" dá v1; "" dá v1; a regra é a mesma de `osc_ajustar`.

**Casos negativos e de precisão:**
- **N1:** repetir a confirmação não cria um 3º registro nem muda `rev`.
- **N2 a N7:** sem registro nas recusas (sem lote, saldo, carência), no ajuste sem liberar, na prévia `osLibErro` e na água.
- **N8 (novo):** ajustar a OS-0418 tirando a Ureia e liberar. O CMD-42 da v3 diz "95 ha · sem insumos"; o CMD-06 diz "v3 liberada por Ana (agrônoma) às hh:mm (CMD-06)", sem "reservada", e `reservado` fica `false`.
- **D (novo):** a dose de 2,4-D ajustada para 0,125 L/ha aparece igual na linha do ajuste e no CMD-42, e a reserva é de 20 L.

### 6.2 Estrutural em python (executado)
Arquivo: `ctl/fFc/estrutura_test_c.py`, que entra como `gen37/links_ocultos_test.py`. Saídas em `ctl/fFc/estrutura_saidas.txt`.

| Árvore | Resultado |
|---|---|
| Código atual | 4/7 |
| Desenho original | 4/7 (L1, L2 e L3 falham) |
| Desenho corrigido | 7/7 |

Verificações:
- **E1:** em todo o código de produto, não só em 4 arquivos, apenas `processo_os.py` e `inicio.py` chamam `osc_liberar`.
- **E1b:** só `osc_liberar` chama `cenLiberar(c`. Logo, nenhum atalho libera sem gravar CMD-42 e CMD-06.
- **E2 e E3:** iguais às do desenho.
- **L1:** nenhum par do escopo, incluindo MB-02 → MB-08 e MB-05 → MB-05det/SU-03det.
- **L2:** o resíduo é listado **por par** (origem → destino) com motivo. Assim, um elo novo quebra o teste mesmo numa tela já listada.
- **L3:** a ação da OS-0420 no Mapa é `MA-04.dc.html#OM-0233`, a OM-0233 existe no seed e o MA-04 está na página visível.

### 6.3 Regressão (executado na cópia corrigida, igual à base)
- `quantidade_test.py`: 14/14.
- `carencia_test.py unit`: 50/50.
- `mip_unit_test.py`: 34/34.
- `rend_multiconjuntos_unit.py`: 106/106.
- Build: 144 quadros. Mudam IN-04, IR-04, MA-01, MA-02, MA-03, MA-04det, MA-05, MB-01, MB-02, MB-05 e OS; no `canvas.json`, só o carimbo `createdOnFiles.at`.
- `node --check` nos scripts dessas 11 páginas: ok.
- O IN-04 e a OS definem `osVn` e `OS_AGRO`; não sobram `p_qr`, `p_has` nem `mi_link`.
- A varredura de elos depois da mudança mostra só os pares do resíduo.

### 6.4 Navegador (a estender; não executado)
- **`os_v39_liberar_test.py`:**
  - caso 2 (OS-0441): a Origem casa, por regex, com o CMD-42 e com "REQ-041 reservada no Estoque (CMD-06)"; o aviso termina em "v1 aprovada e liberada por Ana (agrônoma).";
  - caso 1 (OS-0440): "sem insumos (CMD-42)" e um CMD-06 sem "reservada" (o teste já exige `'reservou' not in p`);
  - caso 4: `osc.ev` vazio.
- **`os_cenario_test.py`:**
  - verificação 2: a confirmação contém "aprova esta versão e libera";
  - verificação 14 (executado no núcleo): "v2 aprovada por Ana (agrônoma) às hh:mm · 150 ha · Glifosato 480 1,8 L/ha, 2,4-D 806 1 L/ha, Óleo mineral 0,5 L/ha (CMD-42)".
- **`map_decisoes_test.py`:** liberar a OS-0430 pelo Mapa grava 2 registros; "Acompanhar OM-0233" abre o painel da OM-0233 no MA-04.
- **`mbtest.py`:** sem `href` para MB-07..MB-10 no MB-01, para MB-08 no MB-02 nem para MB-05det e SU-03det no MB-05.
- **`irtest.py`:** o IR-04 não tem elo para o GE-07.

## 7. Testes existentes que mudam de expectativa
- **`map_decisoes_test.py:70-71` (verificação 6):** `pr==['Reprogramar saldo','PL-05.dc.html']` passa a `pr==['Acompanhar OM-0233','MA-04.dc.html#OM-0233']`. Continuam valendo "ordem completa → CA-01x-os0420" e `unico(lk)`.
- **`matest.py:66`:** "Abrir impedimentos" não aparece.
- **`etapas_celular_test.py:217`:** o alvo do MA-01 passa a `['Tarefa']`.
- **`ostela.py:111`:** nenhum `href` para CA-02; o atalho para o EST continua.
- **Nenhum teste referencia os elos novos do MB-02 e do MB-05** (grep). O `mbtest.py` abre MB-05det e MB-08 direto (l.12 e l.92) e não muda.
- **Continuam valendo:** `os_v39_liberar_test.py` e `os_cenario_test.py`, porque conferem por "contém"; e `map_aprov_test.py:30-31`, que confere a OS-0418 antes de liberar.
- **Observação pré-existente:** `os_cenario_test.py:20-22` compara `c.v` com 2, mas o seed é `v=3` (`cenario.py:80`).

## 8. Riscos e limites
- **Persona fixa "Ana (agrônoma)":** no software real, o servidor tira `por` da sessão, recusa CMD-42 sem papel habilitado, usa a chave de idempotência de quem inicia e grava efeito, recibo e outbox juntos. No protótipo, a repetição é barrada pelo estado (N1).
- **Hora sem data:** o PRD 41.2 pede data/hora. A trilha do protótipo inteira usa só hh:mm do navegador (`cenario.js:13`), inclusive o ajuste e os movimentos. No software, o carimbo é do servidor.
- **Versão pelo último vN:** a OS-0420 daria v2, mas não passa pela liberação.
- **Ordens já liberadas no seed:** continuam sem registro; não invento histórico.
- **Beneficiamento:** não chega ao `osc_liberar` (E2, E3).
- **MB-01:** a altura fixa `H_=1740` deixa espaço em branco. O `mbtest` só mede excesso (`over()<=0`), então não falha; medir com o `qa37`.
- **Telas que ficam sem primário:**
  - a aba Almoxarife do MB-05 fica sem primário no rodapé;
  - o cartão da OS-0419 no MB-02 fica sem ação;
  - o IR-04 fica sem primário.

  É aceitável: não há decisão viva nessas telas.
- **Rótulos:** "Liberar para execução" e "Confirmar liberação" ficam como estão; a frase da confirmação diz que confirmar é aprovar.

## 9. Resíduo da varredura, fora desta frente (cada item precisa de frente própria)

**Pares registrados no L2, com motivo:**
- Main → índice;
- MB-02det, MB-03x-recibo e MB-06: vivos, mas na página de ocultos (`build.py VIS_ROWS`);
- cadeia MIP: AG-01/AG-01det/AG-07/IN-04 → AG-03, AG-04det, AG-06, PL-02.

**Detalhes fixos na página visível (CA-01det e CA-01x-os0420):**
- São abertos pela O.S. e pelo Mapa ("Abrir ordem", `dados.py:92-93`).
- Eles mesmos levam a PL-05 (`campo.py:205, 355`) e CA-02.
- A OS-0421 é a ordem mais dinâmica da demonstração, e o CA-01det mostra 190/350 ha fixo.
- Testes que dependem: `ostest.py:60, 75` e `intest.py:59`.

**Ações simuladas e cartões fixos dentro do app (segunda metade da recomendação 4):**
- MB-02: cartão da OS-0418 "v2 a liberar por Ana · Revogada no servidor" (`mobile.py:365-370`) e "Reconhecer" com o CI-0931 só no estado da tela (l.380-381).
- MB-05, aba Almoxarife: REQ-031, REQ-038 "aguarda a liberação por Ana" e F26-02 fixos, e "Registrar divergência" simulado (l.656-670).
- Depois desta frente, liberar a OS-0418 grava o CMD-42 e o MB-05 continua dizendo "aguarda a liberação".

**Defeito anterior achado (executado, `ataques_no_desenho.txt` A2), S3:**
- Ajustar a OS-0418 tirando a Ureia e liberar deixa a REQ-038 aberta com 1.140 kg.
- O aviso diz "nenhuma requisição no Estoque", e o painel diz "REQ-038 reservou os insumos": o `osCondGen` (`processo_os.py:256`) usa `o.req`.
- Não há dano de estoque: o `cenEntregar` recusa, porque o lote é "—".
- Correção própria: cancelar a requisição sem entrega no ramo sem insumo.

## 10. Tamanho

| Arquivo | Linhas |
|---|---|
| `processo_os.py` | +30 −15 (3 de docstring) |
| `inicio.py` | +4 −4 (1 de docstring) |
| `maquinas.py` | +7 −9 |
| `irrigacao.py` | +1 −4 |
| `mobile.py` | +6 −12 |
| **Total** | **+48 −44** |

- Testes novos: cerca de 75 linhas no unitário JS (21 verificações), 15 no executor e 55 no estrutural.
- Edições em testes de navegador: cerca de 20 linhas.
- Documentação: 1 linha no `DECISIONS.md` (outro pull request) e cerca de 3 no `RETOMADA-NUVEM.md`.

---

## Contestações: aceitas · recusadas

**Conferido no desenho e mantido (executado):**
- 18 verificações e 11 falhas no código atual, 18/18 com a mudança;
- estrutural 3/5 → 5/5;
- os números P1–P4 e N1–N7;
- regressões 14, 50, 34 e 106;
- 144 quadros e as 9 páginas alteradas;
- as linhas citadas, no `884620c`.

**Aceitas (mudaram o desenho):**
1. **O aviso trazia um segundo "Próximo passo", que contradizia o painel** (executado):
   - aviso: "Próximo passo: Rui (almoxarife) entrega os insumos a Marcos.";
   - painel: "Próximo passo: iniciar na janela 25/09 (DAP −20).".

   Além disso, "Rui" ficava fixo no código para as duas fazendas, e `dados_lagoa_safra.py:147` cita Edson. Agora o aviso termina na aprovação, e o tratamento do "—" deixou de ser necessário.
2. **O CMD-06 afirmava uma reserva que não houve** (executado): "v3 liberada… · REQ-038 reservada no Estoque (CMD-06)" com `reservado=false`. Corrigido com `o.reservado&&o.req` e protegido pelo N8.
3. **A dose saía arredondada na trilha** (executado): 0,125 L/ha virava "0,13 L/ha", com 20 L reservados (0,13 × 160 daria 20,8). Corrigido com `cenNum(…,4)` no registro e na linha do ajuste; protegido pelo teste D.
4. **O desenho promovia o CA-01x-os0420 a primário do Mapa.** É uma tela fixa e leva de volta a PL-05 por "Reprogramar saldo" (`campo.py:355`). Agora o primário é "Acompanhar OM-0233" → MA-04#OM-0233, com estado vivo; protegido pelo L3.
5. **O escopo do item 2 era incoerente:**
   - tirava MB-01 → MB-08, mas mantinha MB-02 → MB-08;
   - mantinha MB-05 → MB-05det, que finge zerar a custódia (DV-0912) e contradiz o Estoque e a O.S., no app em teste com clientes (DEC-2609-13).

   Agora MB-02 → MB-08, MB-05 → MB-05det (dois elos) e MB-05 → SU-03det entram na frente; protegido pelo L1.
6. **O desenho criava duas fontes novas:**
   - `osVn` era a terceira cópia da conta de versão (`processo_os.py:559`, `inicio.py:816`);
   - `OS_AGRO` não era fonte única (l.248 e l.802 continuavam com o nome fixo).

   Agora as duas regras são referências únicas.
7. **Os testes estruturais eram fracos:** o E1 varria só 4 arquivos, e o L2, por arquivo, aceitava elo novo numa tela já listada. Agora o E1 varre todo o código de produto, há o E1b e o resíduo é conferido por par.
8. **O `DECISIONS.md` não existe na linha do protótipo** e o cabeçalho da seção de pendentes manda valer o comportamento conservador do PRD. A linha vai em pull request separado e nomeia o padrão adotado.
9. **As docstrings especificadas no desenho** (`inicio.py:21` e `processo_os.py:44-47`) não estavam na cópia. Agora estão aplicadas.

**Recusadas (com motivo):**
1. **Baixar o item 1 para S2** ("quem clica é a agrônoma"): sem registro, a liberação presume a aprovação (PRD 41.1, l.6842). A regra do AGENTS §3 dá S1.
2. **Trocar os rótulos para "Aprovar e liberar":** mexeria em 9 arquivos de teste de navegador ("Confirmar liberação") e 8 ("Liberar para execução"). A frase da confirmação já cobre o F-R4. Fica como melhoria S4.
3. **Data no registro:** o protótipo inteiro usa só a hora, e a data da demonstração não tem fonte única. Vai para o §8 e para o software real.
4. **Corrigir agora a REQ-038 órfã:** é defeito anterior, sem dano de estoque; está no §9.
5. **Tirar já os elos para CA-01det e CA-01x-os0420:** são detalhes visíveis com testes que dependem deles. Esta correção só evita promovê-los.
6. **Tirar as ações simuladas dentro das telas do app:** não são elos; estão listadas com linha no §9.
7. **Remover o ramo água de `osc_liberar`:** não é alcançado e o N4 o protege.
8. **Mudar a altura do MB-01 sem medida:** o `mbtest` só mede excesso; medir com o `qa37`.