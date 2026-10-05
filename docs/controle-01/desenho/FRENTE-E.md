# FRENTE-E · Trava legal única e fontes únicas: uso de agrotóxico na O.S., receituário do AG-07 e outorga da irrigação (desenho corrigido pela revisão cética)

Severidade: S1

Dano: E1 (S1): "Liberar" e "Ajustar antes de liberar" da O.S. autorizam aplicação proibida. Executado na base: Glifosato a 7,5 L/ha (2,5 vezes o máximo da bula) foi liberado e reservou o lote G26-14 inteiro (1.200 L). Também foram liberados Abamectina na soja, Fungicida A no mamão e uma 2ª dessecação acima do limite de aplicações. São aplicações fora do registro, com resíduo acima do limite e risco ao aplicador e ao ambiente. E3 (S2): a trava de vazão da irrigação usa 573 L/s, de uma outorga vencida em 2023. Para a mesma SINT-002, o cadastro tem 41,67 L/s, vigente até 20/11/2026. Assim a trava deixa programar captação acima do outorgado, e as três captações da Lagoa Grande divergem do cadastro. E2 (S3): o AG-07 mostra "Receituário emitido · assinado por Ana Souza (RT)" sem gravar DIA, REC/RA nem O.S., ou seja, declara um documento legal que não existe. A alternativa segura (AG-01) já existe. A revisão achou 3 defeitos que o desenho original criava: (a) duas O.S. A liberar com o mesmo produto se bloqueiam uma à outra, com mensagem que não nomeia a outra; (b) o erro junto ao campo recusa por engano a cultura da ordem nova; (c) os alertas da regra eram descartados na O.S.

PRD: RN-016 (PRD l.218); RF-EXT-002 (l.2720: validar produto, dose, cultura e restrições na nova liberação); 41.1 (l.6846: o plano propõe, o agrônomo decide na O.S.); 41.2 (l.6856: Ajustar e aprovar; l.6860: o clique interno não substitui documento legal); 41.3 (l.6864: Aprovar e liberar = CMD-42 + CMD-06 na mesma confirmação; l.6866: mudança de dose ou produto exige nova decisão); ENG-011 (l.5233); ENG-013; ENG-017 (l.5239); AG-07 (l.540: Preparar receituário → FO-04; l.542: receituário é documento específico, com assinatura; l.548: destino de consulta abre o formulário de origem autorizado); FO-04 (l.2314, família de AG-04/PL-02; no protótipo, quem grava REC/RA é o Decidir controle do AG-01, via mipEmitir); captação (l.9064: limites autorizados cadastrados); AGUA-08 (l.6981); DEC-2609-10; AGENTS §4 (trava em dose e versão, com o dano nomeado).

Arquivos: tools/prototipo/v37/gen37/cenario.js, tools/prototipo/v37/gen37/mip.js, tools/prototipo/v37/gen37/dados_mip.py, tools/prototipo/v37/gen37/dados_carencia.py, tools/prototipo/v37/gen37/areas/processo_os.py, tools/prototipo/v37/gen37/areas/inicio.py, tools/prototipo/v37/gen37/areas/agronomia.py, tools/prototipo/v37/gen37/dados_lagoa_fonte.py, tools/prototipo/v37/gen37/dados_irrigacao.py, tools/prototipo/v37/gen37/irrigacao_estado.js, tools/prototipo/v37/gen37/areas/irrigacao.py, tools/prototipo/v37/gen37/legal_unit_test.py (novo), tools/prototipo/v37/gen37/outorga_unit_test.py (novo), tools/prototipo/v37/gen37/os_cenario_test.py, tools/prototipo/v37/gen37/map_decisoes_test.py, tools/prototipo/v37/gen37/agrofit_test.py, tools/prototipo/v37/gen37/irtest.py, scratchpad/ctl/e2/proposta_e2.py, scratchpad/ctl/e2/monta2.py, scratchpad/ctl/e2/monta_e3_2.py, scratchpad/ctl/e2/roda2.py, scratchpad/ctl/e2/e1_unit.js, scratchpad/ctl/e2/e1_extra.js, scratchpad/ctl/e2/e3_unit2.js, scratchpad/ctl/e2/deadlock.js, scratchpad/ctl/e2/ui_merged.js, scratchpad/ctl/e2/div_t2.js, scratchpad/ctl/e2/e1_mip_eq.js, scratchpad/ctl/e2/e1_planos.js, scratchpad/ctl/e2/unid.py, scratchpad/ctl/e2/e3_sit.py

# Frente E — Trava legal única e fontes únicas (desenho corrigido)

**Base:** protótipo `884620c` (sp-tab5, branch `claude/v44-tabelas-05`), PRD v3.9, `DECISIONS.md` e auditoria `pce/verificada.md` (itens 8 e 9).

**Como foi feito:**
- O desenho original está em `ctl/e/`. A revisão cética, em `ctl/e2/`.
- Todas as mudanças foram aplicadas **em memória** (`ctl/e2/proposta_e2.py`, por cima de `ctl/e/proposta_e.py`). Cada troca confere que o trecho original aparece uma vez só.
- O repositório ficou intocado: `git status` não mostra arquivo rastreado modificado, e nenhum arquivo do gen37 ficou mais novo que os scripts.

**Rótulos:** **executado** = saiu de comando rodado. **Especificado** = navegador, não rodado.

```text
ID / resultado útil / persona: FRENTE-E · a O.S. só libera o uso de agrotóxico que a bula permite, o receituário só existe quando gravado e a irrigação respeita a outorga do cadastro · Ana (agrônoma RT), PCP, irrigante e gestor
Requisitos do PRD e fora do escopo: RN-016, RF-EXT-002, 41.1–41.3, ENG-011, AG-07 (l.540–548), l.9064, AGUA-08 · fora: carência no AG-01, contagem única no AG-01 (pendência P2), checagem no Iniciar e dado da OS-0424 (frente do item 7), outorga da Santa Rita (sem cadastro de água), gravação de CMD-42/CMD-06 (frente do padrão 1)
Autor / revisor / integrador: Claude / Codex / Codex
Base / arquivos: 884620c · cenario.js, mip.js, dados_mip.py, dados_carencia.py, areas/processo_os.py, areas/inicio.py, areas/agronomia.py, dados_lagoa_fonte.py, dados_irrigacao.py, irrigacao_estado.js, areas/irrigacao.py
Aceite e comando: §5 (ctl/e2: e1_unit 26/26, e1_extra 5/5, e3_unit2 11/11, AG-01 com as mesmas travas nos 1.136 casos, mip 34/34, quantidade 14/14, carência 48/48)
Estado / impedimento / próximo passo: desenho corrigido executado em memória · sem impedimento para a branch · para homologação, ver o portão da OS-0424 (§7.1) · próximo: aplicar em branch própria e passar ao Codex
```

## 0. Resumo

| Item | Severidade | Correção mínima | Executado |
|---|---|---|---|
| E1 · liberar e ajustar O.S. sem a trava legal | **S1** (libera aplicação proibida) | Uma função `cenUsoLegal` (cenario.js), chamada pelo `mipChecks` (AG-01) e pela O.S. em `osc_liberar`/`osc_ajustar`. A contagem de aplicações só considera O.S. já liberadas e nomeia o que contou | base 12/26 → 26/26; casos da revisão 1/5 (base) · 2/5 (desenho original) · **5/5** |
| E2 · AG-07 diz "Receituário emitido · assinado" e não grava | S3 | O AG-07 vira consulta; "Preparar receituário" abre o AG-01, que grava DIA, REC/RA e O.S. | estático |
| E3 · SINT-002 com dois valores | S2 | Vazão, horas, vencimento e situação lidos do cadastro (aba Água); vencida sem janela trava com o gestor | base 5/11 → **11/11** |

**Tamanho:** cerca de +135/−120 linhas de produto e +130 de teste (§8).

## 1. Problema reproduzido (executado)

### 1.1 E1 · O.S. (`processo_os.py:300-333`) × AG-01 (`mip.js:238-253`)

Comando: `python3 ctl/e/monta_os.py repro_e1.js` (base).

```text
R1 OS-0430 · Glifosato 480 de 2 para 7,5 L/ha · Salvar e liberar → ACEITO … REQ-041 reservou: Glifosato 480 1.200 L (lote G26-14: físico 1.200, reservado 0)
R2 OS-0430 · incluir Abamectina 18 EC 0,5 L/ha em soja → ACEITO … Abamectina 18 EC 80 L
R3 OS-0501 · incluir Fungicida A 0,5 L/ha no Pivô 13 (mamão) → ACEITO … Fungicida A 24,66 L
R4 2ª dessecação com Glifosato 480 no T1-A (bula: 1) → OS-0430 liberada … | OS-0440 liberada. REQ-042 … 320 L
```

- O AG-01 já trava esses casos. A O.S. só confere o estoque (`osc_ajFalta`, l.316) e o total 0 (l.333).
- **A semente pela regra:** só uma ordem falha, e ela já está Liberadas: `OS-0424 · Fungicida A 0,8 L/ha em P2 (milho): sem registro para milho`.

### 1.2 E2 · AG-07 (`agronomia.py:1712-1716`)

- `rx_emit` grava só `agf_rx` no estado da tela e mostra o aviso "Receituário emitido · … · assinado por Ana Souza (RT)".
- Não chama `mipMudar` nem `cenMudar`.
- Base do AG-07: dados abertos do AGROFIT, sem dose, carência nem nº de aplicações (`v.af_bula`, l.1690). Por isso não dá para aplicar a trava ali.

### 1.3 E3 · outorga (`dados_irrigacao.py:42` × `dados_lagoa_sintetico/kml.py:61`)

```text
irrigação: SINT-002/0000 573 L/s × 21 h/dia · vence 2023-11-22 · Em renovação
cadastro : SINT-002/0000 150 m³/h = 41,67 L/s · 20 h/dia · vence 2026-11-20
```

- Os 23 pivôs da Lagoa Grande estão na LG-PAR. Somam 1.607 L/s; o maior tem 101 L/s.
- 21 pivôs passam de 41,67 L/s sozinhos, e 17 passam de 55,56 L/s, que é a maior outorga do Rio A no cadastro.
- Se a irrigação lesse só a SINT-002 (executado, `irr_cad.js`):
  - as 6 tarefas voltam a A liberar com "Janela a definir";
  - irr_estado_test 3, irr_fluxo_test 19 e irtest 59 falham;
  - o PV01 vai para 25/09 00:00.

### 1.4 Defeitos do desenho original (executado em `ctl/e2/`)

1. **Bloqueio mútuo** (`deadlock.js`): com a OS-0440 (mesmo Glifosato no T1-A) em A liberar, **as duas** são recusadas com "1 de 1".
   - A `carNap` contava ordem ainda A liberar.
   - A OS-0430 original ganhava o selo "Fora do registro".
   - A mensagem não dizia qual era a outra ordem.
2. **Erro junto ao campo com o objeto errado** (`ui_merged.js`): o `ck` proposto chamava `osUsoItem` com o objeto da tela (`osMerge`), que não tem `osc`.
   - Atrazina na safrinha de milho do T1-A: o comando aceita, a tela recusaria "sem registro para soja".
   - Na 2ª dessecação acontece o contrário: o comando recusa e a tela não mostra nada.
3. **Alertas descartados:** `osUsoItem` devolve só `tr[0]`. O alerta de unidade (Inseticida B em L/ha contra bula em kg/ha), o de uso não conferido e o de reavaliação nunca apareciam na O.S., embora o desenho os chamasse de "alerta".
4. **Contagem com duas fontes** (`div_t2.js`):
   - a Nova ordem do plano no T2 (Glifosato) é liberada;
   - depois o AG-01 emite RA-0142 e REC-019 "Receituário emitido" para uma 2ª dessecação no T2;
   - a O.S. dela é recusada com "1 de 1".
   - Ou seja, a regra é única, mas a contagem não. A correção 1 manteve esse resíduo, agora nomeando a outra O.S. (§7.2).
5. **Números:**
   - "4 das 6 tarefas passam a começar entre 24 e 27/09" está errado: são 3 (§7.5).
   - A IR-04 mostra "186 L/s" (`irrN` sem casas), não "186,11".
   - O limite do dia saía 13.119 m³, porque `ls` e `h` eram arredondados no dado; o certo é 13.120.

## 2. Regras novas (testáveis)

**RL-E1 · Uso legal na liberação e no ajuste da O.S.**
- **Quando:** `osc_liberar`, `osc_ajustar` (inclusive "Salvar ajuste" sem liberar), Mapa e Nova ordem → Liberar.
- **O que trava:** para cada agrotóxico × cultura de cada talhão ou parcela, a ordem só passa se:
  1. há uso registrado na cultura (a do cultivo da ordem nova; senão, a do talhão);
  2. o registro não está cancelado;
  3. a dose por ha cabe em algum uso, na mesma unidade;
  4. as aplicações já autorizadas ou feitas ficam abaixo do máximo da bula.
- **O que conta como aplicação** (item 4):
  - O.S. Liberadas, Em execução, Em conferência ou Encerradas, mais cancelada com apontamento;
  - o caderno de campo (`dados_mip.APL` sem O.S.), na mesma safra e no mesmo talhão ou parcela, sem a própria ordem.
  - **Ordem ainda A liberar não conta:** a primeira a liberar ocupa a vaga. `cenMudar` é atômico.
- **Mensagem:** nomeia o que contou, por exemplo "2 de 2 (OS-0504, caderno 28/08)".
- **O que é só alerta:** uso não conferido, produto em reavaliação, unidade da ordem diferente da bula. **Aparece** na confirmação da liberação (O.S. e Mapa), como "Atenção (não bloqueia): …".
- **Fora da regra:** fertilizante, corretivo, semente, muda, inoculante e adjuvante; uso só por semente (TS).
- **Dano que a trava evita:** aplicação proibida, resíduo acima do limite, risco ao aplicador e ao ambiente, fitotoxidez, lote recusado. A trava em "Salvar ajuste" protege a versão (AGENTS §4).
- **Padrão adotado (1):** a conferência roda antes de qualquer gravação. Na recusa nada é gravado, porque `cenMudar` não grava em caso de erro. A gravação separada de CMD-42 e CMD-06 é da frente do padrão 1.

**RL-E2 · Uma regra (ENG-011).**
- `cenUsoLegal` é a única implementação de registro, situação, conferência, dose e máximo de aplicações.
- A derivação da dose também é uma só: `dados_mip.uso`, que alimenta o AGF do AG-01 e o CARD da O.S.
- **Limite declarado:** a *contagem* tem duas fontes. O AG-01 usa o histórico do MIP; a O.S. usa o cenário mais o caderno. Na semente as duas dão o mesmo número (`nap_div.js`: 0 divergências). A O.S. é a autoridade. Pendência P2 (§7.2).
- **Aceite:** o AG-01 dá as mesmas travas nos 1.136 casos; só o texto de um alerta muda (C5).

**RL-E3 · Receituário só existe gravado.**
- O AG-07 é consulta. "Preparar receituário" abre o AG-01, onde `mipEmitir` grava DIA, REC/RA e a O.S. em A liberar.
- Nenhuma tela diz "Receituário emitido" sem esse registro.

**RL-E4 · Outorga com fonte única.**
- Vazão, horas por dia, vencimento e situação vêm só do cadastro (`LG_AGUA`). A irrigação não guarda valor de outorga.
- **Premissa declarada** (o cadastro não liga pivô a ponto de captação): a captação dos pivôs soma as outorgas vigentes de captação superficial para irrigação do curso de maior vazão vigente somada. Supõe rede comum aos 4 pontos do Rio A; sem ela, 17 dos 23 pivôs passariam da maior outorga sozinhos.
- Outorga vencida sai da soma e fica na observação.
- Nenhuma vigente → situação "Vencida". Cada tarefa ganha o bloqueio "Outorga vencida", com dono gestor, também quando não tem janela.
- A situação usa a regra do CD-01 (`cad_fazendas.py:314-318`), com teste de equivalência.
- **Dano:** captar acima do outorgado ou com outorga vencida (multa, embargo).

## 3. Mudança de código exata (especificado; aplicado em memória e testado)

### `gen37/cenario.js` (depois de `cenNum`, l.41): +18 linhas

```js
function cenUsoLegal(us, rot, dose, un, nap, refs) {   // RN-016 · RF-EXT-002 · ENG-011: a mesma no AG-01 e na O.S.
  const tr = [], al = []; us = us || [];
  if (!us.length) { tr.push('Sem registro para ' + rot + '.'); return { tr, al }; }
  if (us[0].sit === 'Cancelado') tr.push('Registro cancelado: uso proibido.');
  else if (us[0].sit === 'Em reavaliação') al.push('Produto em reavaliação na Anvisa.');
  const cmp = us.filter(u => !un || u.un === un), ok = cmp.filter(u => dose >= u.dmin - 1e-9 && dose <= u.dmax + 1e-9);
  const base = ok.length ? ok : (cmp.length ? cmp : us);
  const ft = L => L.map(u => cenNum(u.dmin, 3) + (u.dmax !== u.dmin ? '–' + cenNum(u.dmax, 3) : '') + ' ' + u.un + '/ha')
    .filter((x, i, a) => a.indexOf(x) === i).join(' ou ') + (L.some(u => u.calda) ? ' (calda de 1.000 L/ha)' : '');
  if (base.every(u => !u.conf)) al.push('Uso não conferido na bula: confira antes de aplicar.');
  if (!(dose > 0 && isFinite(dose))) tr.push('Informe a dose.');
  else if (!cmp.length) al.push('Dose em ' + un + '/ha e bula em ' + ft(us) + ': confira a unidade na bula.');
  else if (!ok.length) tr.push('Dose fora da bula: ' + ft(cmp) + '.');
  const mx = Math.max.apply(null, base.map(u => u.mx || Infinity));
  if (isFinite(mx) && nap >= mx) tr.push('Nº máximo de aplicações no ciclo atingido: ' + nap + ' de ' + mx + (refs && refs.length ? ' (' + refs.join(', ') + ')' : '') + '.');
  return { tr, al };
}
```

### `gen37/mip.js` · `mipChecks`: l.239-245 trocadas por 5 linhas; l.249-250 saem

- A troca é igual à do desenho original: o AG-01 chama `cenUsoLegal(u ? [u] : [], …, nap)` sem `refs`, então o texto da trava não muda.
- `hist` sobe e continua servindo à rotação (l.251-253).

### `gen37/dados_mip.py`: +7/−4

- `uso(q, u)` passa a ser a derivação única (`_dose`, `_dias`, `_max`) e devolve `None` para dose por semente. `_agf()` chama `uso()`.
- Executado: o AGF refeito é idêntico ao atual (assert).

### `gen37/dados_carencia.py`: Python +10, JS +7

- `_usos(p)` (l.91): `fx=[{dmin,dmax,un,mx,conf,calda}]` por cultura, via `dados_mip.uso`.
- `_produtos()` (l.125): `sit`.
- `card()` (l.209): `saf` de `D.ORDENS + D.ORDENS_LG` e `apl0` (APL sem O.S., `saf='2026/27'`, ciclo do MIP).
- JS:

```js
function carSaf(o){ const s=String((o&&o.osc&&o.osc.novo&&o.osc.novo.saf)||(CARD.saf||{})[o&&o.id]||''); const m=/\d{4}\/\d{2}/.exec(s); return m?m[0]:s; }
function carNap(c,tid,parc,p,o){ const sf=carSaf(o), FEZ=['Liberadas','Em execução','Em conferência','Encerradas'];
  const os=Object.keys((c&&c.ordens)||{}).map(k=>c.ordens[k]).filter(h=>h.id!==o.id&&carSaf(h)===sf&&(FEZ.indexOf(h.etapa)>=0||(h.ap||[]).some(a=>a.st!=='Previsto'))
    &&(h.ins||[]).some(x=>x.p===p)&&carTals(h.talhao).some(y=>y.tid===tid&&(!y.parc||!parc||y.parc===parc))).map(h=>h.id);
  return os.concat((CARD.apl0||[]).filter(a=>a.tal===tid&&a.p===p&&a.saf===sf).map(a=>'caderno '+a.d.slice(8,10)+'/'+a.d.slice(5,7))); }
```

### `gen37/areas/processo_os.py`

**Núcleo (`JS_NUCLEO`, antes de `// próxima requisição`, l.340): +14 linhas**

```js
function osUsoItem(c,o,x,al){ const P=CARD.prod[x.p]; if(P?(!P.defn||P.adj):(x.g&&!/^(Herbicida|Fungicida|Inseticida|Acaricida|Nematicida)/.test(x.g))) return '';
  const ts=carTals(o.talhao); if(!ts.length) return x.p+': o talhão '+(o.talhao||'da ordem')+' não está no cadastro; o registro é por cultura.';
  const cv=String((o.osc&&o.osc.novo&&o.osc.novo.cultura)||'').split(' ')[0];
  for(const t of ts){ const T=CARD.tal[t.tid]; const cu=cv||T.cult; const u=P?(P.usos||{})[cu]:null; if(u&&!(u.fx||[]).length) continue;
    const us=((u&&u.fx)||[]).map(f=>Object.assign({sit:P.sit},f));
    const ap=carNap(c,t.tid,t.parc,x.p,o); const R=cenUsoLegal(us,String(cu||'a cultura').toLowerCase(),x.dose,x.un,ap.length,ap);
    if(al) R.al.forEach(a=>{ const s=x.p+': '+a.charAt(0).toLowerCase()+a.slice(1); if(al.indexOf(s)<0) al.push(s); });
    if(R.tr.length) return x.p+' '+nd(x.dose)+' '+x.un+'/ha em '+carNome(t.tid)+(t.parc?' ('+t.parc+')':'')+': '+R.tr[0].charAt(0).toLowerCase()+R.tr[0].slice(1); }
  return ''; }
function osUsoErro(c,o,al){ for(const x of (o.ins||[])){ const e=osUsoItem(c,o,x,al); if(e) return e; } return ''; }
function osUsoAtencao(c,id){ const co=c.ordens[id], al=[]; if(co) osUsoErro(c,co,al); return al.length?' Atenção (não bloqueia): '+al.join(' '):''; }
```

**Demais trocas no núcleo** (iguais ao desenho original):
- `osc_liberar`, antes de l.308: `if(!o.ins.some(x=>x.dose>0&&!(x.tot>0))){ const e=osUsoErro(c,o); if(e) throw new Error(e); }`.
- `osc_ajustar`, depois de l.333: `{ const e=osUsoErro(c,o); if(e) throw new Error(e); }`.
- `osMerge`, l.245-248:
  - `lg` com selo vermelho "Fora do registro · <produto>", dono Ana e prazo "ajustar produto ou dose";
  - precedência: total 0, regra legal, estoque.
- `osProx`, l.415: ramo `o.legal`.

**Tela:**
- l.557: `ajLib=…||!!b.legal`.
- l.607-608 (correção C3): o erro junto ao campo usa a ordem do cenário, a mesma que o comando lê:

```js
if(!isNaN(ar)&&ar>0){ const co=cenC.ordens[o.id]; const ck=(p,un,d,k,g)=>{ if(errs[k]) return; const m=(co?osUsoItem(cenC,co,{p,un,dose:d,g}):'')||(ajLib?osc_ajFalta(cenC,p,un,d,ar):''); if(m) errs[k]=m; };
  (o.ins||[]).forEach(x=>{ if(ds[x.p]!==undefined) ck(x.p,x.un,ds[x.p],x.p,x.g); }); add.forEach(a=>ck(a.p,a.un,a.dose,'+'+a.p,a.g)); }
```

- l.614 `pan_ct.liberar`: `… +osUsoAtencao(cenC,o.id)`.
- Nova ordem: `_nova_ordem_dados` (l.196) leva `cultura=c['cultura']`, e o `no` (l.802) leva `cultura:c.cultura`.
- Docstring (l.43-49): +2 linhas.

### `gen37/areas/inicio.py` (Mapa)

- l.817 `mapCt` liberar: `… +osUsoAtencao(cenGet(),o.id)`. A confirmação fica igual à da O.S.

### `gen37/areas/agronomia.py` (E2): cerca de +5/−80

O conteúdo é o mesmo do desenho original:
- l.1116: `<a href="AG-01.dc.html">Preparar receituário em Pragas e doenças ›</a>`, com texto fixo.
- Saem:
  - `_agf_receituario` (l.1193-1219) e `EXTRA.append` (l.1730);
  - `agRxFechar` (l.1436) e os ramos `rx` de `agTeclas` (l.1438-1440);
  - l.1453-1471 (`agTal`, `agUn`, `agFaixa`, `agConv`, `agFaixaT`, `agValDose`, usados só pelo receituário);
  - `agRefFaixa` e `agRxAbrir` (l.1480-1486);
  - `agRxVals` (l.1583, l.1692-1717);
  - `af_rx*` (l.1612), `af_hasDone`/`af_done` (l.1617) e `AG_RT`/`AG_RT_NOME` (l.1228).
- `af_dica` fica só para "Todas as culturas". `agCref` fica.

### E3

- **`gen37/dados_lagoa_fonte.py`: +28 linhas.**
  - `agua_ls`, `agua_h`, `agua_sit` e `captacao(agua, curso=None, hoje)`.
  - **Sem arredondar `ls` e `h` no dado** (C6): o limite do dia fecha em 13.120 m³. Arredonda-se só na tela.
- **`gen37/dados_irrigacao.py`: +3/−8.**
  - `CAPT['LG-PAR']=dict(faz='LG', **F.captacao(F.LG_AGUA, None, str(HOJE)))`.
  - Saem LG-STC e LG-BAR, que não têm setor ligado.
  - `seed()` passa a `v=3` (l.183).
  - Docstring l.11-13 sem 573 L/s, sem 19 L/s e sem as datas antigas.
- **`gen37/irrigacao_estado.js`:**
  - l.209: `if (cp && cp.aviso) av.push({ k: 'renov', t: cp.aviso });`.
  - **+1 linha (C4)**, em `irrChecar` antes de `const prop = []`:

```js
{ const cp0 = s.capt[x.capt]; if (cp0 && cp0.st === 'Vencida' && pend.some(p => p.ini === null || p.ini === undefined)) bloq.unshift({ k: 'outorga', c: 'red', t: 'Outorga vencida · ' + cp0.nome, dono: F.gestor }); }
```

- **`gen37/areas/irrigacao.py`:**
  - l.228 e l.574: `'Vence em 90 dias':'yellow'`;
  - l.252: `(cp.st==='Vencida'?'venceu em ':'até ')`;
  - l.572-573: `irrN(cp.h,1)+' h/dia'`.

## 4. Textos de tela (com dono e próximo passo)

**E1 · painel e Mapa** (A liberar impedida; executado):
- "Liberar bloqueado: Glifosato 480 7,5 L/ha em T1 (T1-A): dose fora da bula: 1,5–3 L/ha."
- "Quem resolve: Ana (agrônoma), ajustando produto ou dose antes de liberar."
- Primária: "Ajustar antes de liberar" → "Salvar e liberar".
- Selo: "Fora do registro · Glifosato 480" (vermelho).

**E1 · erro junto ao campo** (executado):
- "Abamectina 18 EC 0,5 L/ha em T1 (T1-A): sem registro para soja."
- "Fungicida A 0,5 L/ha em Pivô 13: sem registro para mamão."
- "Glifosato 480 2 L/ha em T1 (T1-A): nº máximo de aplicações no ciclo atingido: 1 de 1 (OS-0430)."
- "Abamectina 18 EC 0,5 L/ha em Pivô 6: nº máximo de aplicações no ciclo atingido: 2 de 2 (OS-0504, caderno 28/08)."
- "Paraquate 200 SL 1,5 L/ha em T1: registro cancelado: uso proibido."

**E1 · confirmação** (Nova ordem c1·a7; executado):
- "… Atenção (não bloqueia): Inseticida B: dose em L/ha e bula em 0,8–1 kg/ha: confira a unidade na bula."
- Nas ordens A liberar da semente (OS-0430, OS-0501, OS-0431), o texto fica vazio, e a confirmação continua igual.

**E2 · AG-07:**
- Link: "Preparar receituário em Pragas e doenças ›".
- Texto: "Ana (agrônoma RT) emite o receituário na vistoria do talhão, em Pragas e doenças. A decisão confere registro, dose, nº de aplicações e carência e gera a O.S. em A liberar."

**E3:**
- Aviso: "Outorga SINT-002/0000 vence em 20/11/2026" (não trava).
- IR-04: "Rio A (demonstração) · SINT-001/0000 + SINT-002/0000 + SINT-007/0000 + SINT-014/0000 · **186 L/s × 19,6 h/dia**", com o selo "Vence em 90 dias" (amarelo).
- Travas:
  - "Sem vazão outorgada · 439 de 186 L/s" (gestor);
  - tudo vencido: "Outorga vencida · Rio A (demonstração)", com o próximo passo "Ajustar à outorga · Gestor da Lagoa Grande".

## 5. Testes

### 5.1 Sem navegador (executados)

Os comandos rodam em `ctl/e2/`, salvo indicação.

| Comando | Base 884620c | Desenho original | Corrigido |
|---|---|---|---|
| `python3 monta2.py e1_unit.js <modo>` | 12/26 | 26/26 | **26/26** |
| `python3 monta2.py e1_extra.js <modo>` (D1–D3, A1, U1) | 1/5 | 2/5 | **5/5** |
| `monta2.py e1_mip_eq.js` (AG-01, 1.136 casos) | — | 0 travas diferentes; 4 com o 1º erro em outra ordem | 0 travas diferentes; os alertas mudam só no texto "confira antes de aplicar"; os mesmos 4 casos com o 1º erro em outra ordem |
| `monta2.py e1_planos.js` (236 atividades dos planos) | — | 3 travadas | **2 travadas**, ambas devidas (abaixo) |
| `monta2.py nap_div.js` (contagem AG-01 × O.S. na semente) | — | 0 divergências | 0 divergências |
| `monta2.py div_t2.js` (resíduo P2) | — | recusa "1 de 1" | recusa "1 de 1 (OS-0440)" |
| `python3 roda2.py mip_unit_test.py proposta` | 34/34 | 34/34 | **34/34** |
| `roda2.py quantidade_test.py proposta` (E1 + E3 + irrigacao_estado.js corrigido) | 14/14 | 14/14 | **14/14** |
| `roda2.py carencia proposta` | 48/48 | 48/48 | **48/48** |
| `python3 monta_e3_2.py e3_unit2.js <modo>` | 5/11 | — | **11/11** |
| `python3 e3_sit.py` (situação × `aguaSit` do CD-01) | — | 16/16 | **16/16** |

**As 2 atividades travadas em `e1_planos.js`:**
- c9·k3: Fungicida C 0,8 L/ha, acima da bula de 0,5–0,75.
- lg06·q2: 2 de 2 (OS-0504, caderno 28/08).
- A c1·a1 deixa de travar, porque a OS-0430 ainda está A liberar. A Nova ordem já recusa duplicata (`osacoes.py:104`).

**Casos novos (`e1_extra.js`):**
- **D1:** duas A liberar. Cada uma libera sozinha; liberada a OS-0440, a OS-0430 é recusada com "1 de 1 (OS-0440)".
- **D2:** Pivô 6 dá "2 de 2 (OS-0504, caderno 28/08)".
- **D3:** com a OS-0504 cancelada, sobra 1 de 2 e a nova libera.
- **A1:** os alertas são recolhidos sem repetir: unidade do Inseticida B e Cletodim não conferido.
- **U1:** com a ordem do cenário, a tela aceita a Atrazina na safrinha de milho, igual ao comando. Com o objeto da tela, recusaria. É a prova do motivo da correção C3.

**Novos em `e3_unit2.js`:**
- **11:** tudo vencido → 6 de 6 com "outorga+jan" e próximo passo do gestor.
- **Exibição:** "186 L/s × 19,6 h/dia · 13.120 m³/dia".

**Arquivos de teste em gen37:**
- `legal_unit_test.py`: 26 + 5 casos.
- `outorga_unit_test.py`: 11 casos + equivalência de situação nas 16 linhas.
- Formato de `mip_unit_test.py`.

### 5.2 Navegador (especificado, não rodado)

- **`os_cenario_test.py` 14b:**
  - Ajustar a OS-0430 com Glifosato 7,5 → erro junto ao campo "dose fora da bula: 1,5–3 L/ha"; a ordem continua A liberar, sem v2 e sem REQ;
  - Abamectina 0,5 → "sem registro para soja";
  - voltando a 2,0, "Salvar e liberar" passa.
- **`os_cenario_test.py` 14c:**
  - com `cenMudar` gravando 7,5, lista e Kanban mostram "Fora do registro · Glifosato 480";
  - o painel mostra "Liberar bloqueado… Quem resolve: Ana", sem "Liberar para execução".
- **`os_cenario_test.py` 14d (C3):**
  - Nova ordem da Safrinha 2027 no T1-A com Atrazina → "Ajustar antes de liberar", sem erro junto ao campo;
  - Nova ordem c1·a7 → a confirmação contém "Atenção (não bloqueia): Inseticida B".
- **`map_decisoes_test.py`:** o item 4 continua; acrescentar 14c no painel do Mapa.
- **`agrofit_test.py`:**
  - 9: link com `href=AG-01.dc.html`;
  - 12: não existe `aside[aria-label="Preparar receituário agronômico"]` nem "Receituário emitido" no AG-07;
  - 14: lotes e referência mantidos, sem a parte da gaveta;
  - 15: as opções de Cultura e a orientação de "Todas as culturas" ficam, sem `disTD` nem "Receituário emitido · Soja".
- **`irtest.py` IR-04 novo:** a Lagoa Grande tem 1 captação, "SINT-001/0000 + … · 186 L/s", com o selo "Vence em 90 dias". O CD-01 continua com 16 pontos.

## 6. Testes existentes que mudam de expectativa

- **`irtest.py:59`:** `'outorga em renovação'` → `'outorga sint-002/0000 vence em 20/11/2026'`.
- **`agrofit_test.py`, itens 9, 12, 14 e 15:** usam a gaveta que sai (l.192, 219-226, 249-250, 263-271). O desenho original listava só 9 e 12.
- **Nenhum teste do E1 muda:**
  - os_cenario 14 fica dentro da bula;
  - ostest c1·a7 e os_v39_liberar c1·a2, c1·a8 e c9·k4 liberam (executado);
  - as confirmações da semente ficam iguais, e os testes comparam com `in`.

## 7. Riscos de regressão e pendências

1. **OS-0424 (S1, dado) · portão de liberação:**
   - Está Liberadas com Fungicida A em milho, sem registro, e continua executável.
   - Pela regra do AGENTS (nenhuma versão sai com S1 conhecido), **a candidata de homologação só sai com a frente do item 7**: `osUsoErro` no Iniciar e o dado da OS-0424 corrigido com o Codex.
   - A base demonstrativa não tem fungicida foliar registrado para milho. Não invento uso.
2. **P2 · contagem AG-01 × O.S. (S3, ENG-011):**
   - Depois de uma O.S. do plano liberada no mesmo talhão, o AG-01 ainda emite o receituário (RA-0142) que a O.S. recusa com "1 de 1 (OS-0440)" (`div_t2.js`).
   - A execução fica travada e a mensagem diz o que cancelar.
   - Correção, numa frente própria: o AG-01 contar com `carNap`, carregando o motor de carência (≈88 KB) ou levando `carTals` e `carNap` ao `cenario.js`.
3. **Carência:** continuam duas regras (AG-01 contra a colheita prevista; motor `dados_carencia`). Pendência de unificação.
4. **Inseticida B:** cadastro em L e bula em kg/ha, só nos planos SOJA-AT·a7 e MILHO-SF·m4 (`unid.py`). Agora aparece como alerta na confirmação. Corrigir o cadastro (`agrofit_dados.py:215` já registra).
5. **E3, janelas** (corrigido):
   - Com o limite de 186 L/s, **3 das 6** tarefas passam a começar depois: OS-0602 em 24/09, OS-0603 em 25/09 e OS-0604 em 24/09.
   - Em OS-0605 e OS-0606 a 1ª passada continua hoje, e a 2ª vai para 27/09 e 26/09. A OS-0601 fica igual.
   - O PV01 programado vai para 26/09 21:00 (na base, hoje 21:00). O volume por dia de 23 a 28/09 fica em 5.153 · 8.557 · 9.098 · 7.761 · 6.188 · 3.091 m³, todos ≤ 13.120.
6. **Premissa da soma por curso (S3, pergunta ao proprietário para a fazenda real):**
   - Os pivôs da Lagoa Grande captam numa rede comum às outorgas do Rio A? Sem rede comum, o limite é por ponto, e 17 de 23 pivôs passam da maior outorga sozinhos.
   - O cadastro não liga pivô a ponto. Não invento a hidráulica.
7. **E3 no Mac (dado real):** a irrigação passa a ler as outorgas reais (formato pt-BR tratado). Não verificável aqui.
8. **Possível dado real (ENG-017, não confirmado):**
   - `git grep` mostra a observação da captação LG-PAR e 573 L/s **só** em `dados_irrigacao.py` (o proprietário confirmou em 05/10/2026 que não era dado real), desde a raiz limpa `e8d780d`.
   - Esses valores não saem do gerador sintético (os pivôs somam 1.285,23 ha), e a RETOMADA (l.17) diz que outorgas reais não saem do Mac.
   - A frente remove os valores do HEAD. Se forem reais, é S1: o Codex, dono da remediação, confere com o proprietário a limpeza do histórico antes de publicar.
9. **Estado salvo:** sem `v=3`, navegadores com estado antigo continuam com 573 L/s.
10. **AG-07 → AG-01 sem contexto (S4):** o AG-01 abre sem filtro de cultura e alvo, porque o hash do AG-01 não tem esse filtro.

## 8. Tamanho estimado

| Parte | Arquivos e linhas |
|---|---|
| E1 | `cenario.js` +18 · `mip.js` +5/−9 · `dados_mip.py` +7/−4 · `dados_carencia.py` +17 · `processo_os.py` ≈ +28/−3 · `inicio.py` ±1 |
| E2 | `agronomia.py` +5/−80 |
| E3 | `dados_lagoa_fonte.py` +28 · `dados_irrigacao.py` +3/−8 · `irrigacao_estado.js` ±1 +1 · `irrigacao.py` ±4 |
| Testes | `legal_unit_test.py` ≈55 · `outorga_unit_test.py` ≈40 · `os_cenario_test.py` +14 · `agrofit_test.py` ±20 · `irtest.py` +4 |
| **Total** | produto ≈ +135/−120; testes ≈ +130 |

## 9. Evidência

**Pastas:**
- Desenho original: `scratchpad/ctl/e/`
- Revisão: `scratchpad/ctl/e2/`

**Arquivos em `ctl/e2/`:**
- `proposta_e2.py`: correções C1–C6 sobre `proposta_e.py`.
- Montagem: `monta2.py` (base, proposta e corrigida), `monta_e3_2.py` e `roda2.py`.
- Testes: `e1_unit.js`, `e1_extra.js`, `e1_mip_eq.js` (com `eq_b.json` e `eq_c.json`), `e1_planos.js`, `e3_unit2.js` e `e3_sit.py`.
- Reproduções: `deadlock.js`, `ui_merged.js`, `div_t2.js`, `nap_div.js`, `atencao.js` e `unid.py`.

Nenhum arquivo do repositório foi gravado: `git status` sem modificação rastreada, e nenhum arquivo do gen37 (nem `__pycache__`) foi alterado durante a revisão.

---

## Contestações: aceitas · recusadas (com motivo)

**Aceitas e aplicadas neste desenho:**
1. **C1 · bloqueio mútuo** (executado, `deadlock.js`): duas ordens A liberar com o mesmo produto se recusavam. Agora a contagem só considera O.S. Liberadas em diante, mais o caderno, e a mensagem nomeia o que contou (D1–D3).
2. **C2 · alertas descartados** (`osUsoItem` só devolvia `tr[0]`): agora aparecem na confirmação da O.S. e do Mapa (A1). Nas ordens da semente o texto fica vazio.
3. **C3 · erro junto ao campo com o objeto da tela** (executado, `ui_merged.js`): recusava por engano a cultura da ordem nova e não mostrava a contagem. Agora usa `cenC.ordens[o.id]`.
4. **C4 · outorga vencida sem janela:** antes mostrava "Janela a definir" com o irrigante. Agora trava com o gestor (+1 linha; e3 11).
5. **C5 · texto "confira antes de emitir"**, errado na O.S.: passa a "confira antes de aplicar" nas duas telas. Nenhum teste compara esse texto (grep).
6. **C6 · `ls` e `h` arredondados no dado:** o limite do dia saía 13.119 m³ em vez de 13.120. Agora arredonda só na tela (ENG-013).
7. **C7 · `agrofit_test` 14 e 15** também dependem da gaveta (l.249-250, 263-271), não só 9 e 12.
8. **C8 · números do E3:** são 3 tarefas (não 4) que passam a começar em 24–25/09, e a IR-04 mostra "186 L/s", não "186,11".
9. **C9 · "uma regra só"** era verdade para a regra, não para a contagem (executado, `div_t2.js`). Declarado como P2 (S3), com a mensagem nomeando a O.S. a cancelar.
10. **C10 · premissa da soma por curso** (17 de 23 pivôs acima da maior outorga sozinhos): declarada, e vira pergunta ao proprietário para a fazenda real. O texto "a irrigação guarda só a ligação" saiu: não há ligação guardada.
11. **C11 · OS-0424:** S1 conhecido continua executável. Vira portão de homologação junto com a frente do item 7.
12. **C12 · possível dado real:** confirmado por `git grep` que está só em `dados_irrigacao.py`, desde `e8d780d`. Se for real, é S1 e o histórico fica com o Codex e o proprietário.
13. **C13 · citação do FO-04:** é família de AG-04/PL-02 (l.2314). No protótipo, quem grava o receituário é o Decidir controle do AG-01. O link fica no AG-01.

**Recusadas, com fundamento:**
1. **Travar a unidade diferente (Inseticida B):** a ideia segue "nunca liberar por falta de dado". Mas o produto tem registro para a cultura, o erro é de cadastro já conhecido e é o único caso (`unid.py`). Travar quebraria o ostest c1·a7 e os planos SOJA-AT·a7 e MILHO-SF·m4. Fica alerta visível (C2) e pendência de cadastro.
2. **Pôr a trava em `cenLiberar`:**
   - na interface, só `osc_liberar` chama `cenLiberar` (grep); os demais são testes;
   - as páginas do app não carregam o CARD;
   - a carência já segue esse padrão.
3. **Selo "Fora do registro" nas O.S. já liberadas (OS-0424):** 12 testes de navegador citam a OS-0424, e sem navegador o risco não é medido. Vai com a frente do item 7.
4. **Unificar a contagem no AG-01 agora:** exige ≈88 KB a mais no AG-01 ou mover `carTals` e `carNap` para o `cenario.js`, o que é maior que a frente. Fica como P2 (S3): a execução já está travada e a mensagem nomeia a O.S.
5. **Tirar a trava do "Salvar ajuste":** o AGENTS §4 inclui "versão" entre o que a trava protege. Mantida.
6. **Ligar pivô a ponto de outorga por proximidade:** inventaria hidráulica sem fonte. Fica a premissa declarada (contestação aceita 10).
7. **Levar cultura e alvo do AG-07 ao AG-01:** o AG-07 não carrega o estado do MIP, e o hash do AG-01 não tem esse filtro. Limitação S4 registrada.
