# BEN · rodada 3 concluída e Beneficiamento publicado em Agrícola (13–14/10/2026)

- **Autor:** Claude (frente BEN). **Revisor:** Codex (regime leve do protótipo, AGENTS §3.5; não bloqueia).
- **Onde:** cópia isolada `fr_ben/v37/gen37` (sem commit e sem push). Base da cópia: `int/v59` (`c961d2f`) mais a Produção dentro de Agrícola.
- **Rótulos:** **executado** = comando rodado nesta cópia, com o log em `fr_ben/logs/`; **texto do revisor** = citado do parecer
  `scratchpad/ben3rev/PARECER.md` (revisão adversarial de 13/10 sobre `15e2976`, feita por Claude como revisor independente; o Codex ainda não verificou); **especificado** = só leitura de código.
  Nada aqui é reconstrução: o texto dos 3 S2 foi achado no parecer do revisor e no pacote `docs/integracao/BEN3/` da branch `claude/v44-ben3`.
- **Dados:** sintéticos (`SAFRION_DADOS=sintetico`). Nenhum segredo.

## 0. Em uma linha

Os 3 S2 que seguravam o Beneficiamento (A1, A2 e A8 da revisão da rodada 3) estão corrigidos, com teste que reprova no código antigo e
passa no novo; o BEN volta à navegação como cartão próprio de Agrícola, logo depois de Recebimento, e a ordem mostra o tipo da unidade
("Packing · Packing house").

## 1. Os 3 S2 que seguravam a publicação (revisão adversarial da rodada 3)

Fonte do texto: parecer do revisor (`ben3rev/PARECER.md`, §Veredito e §A1/A2/A8). No PR #47, o Codex registrou em 13/10 (6147268439):
"A1/A2/A8 e S3 A3/A5 BEN continuam relato em correção, não verificação minha"; e a condição de publicação foi "BEN3, quando os 3 S2 dele
estiverem corrigidos com as sondas do revisor verdes". As correções estavam na branch `claude/v44-ben3` (commits abaixo), fora da `int/v59`;
nesta frente elas foram trazidas para a cópia (seção 2) e provadas de novo aqui.

### A1 · S2 · a falta na execução não baixava com a reposição

- **Texto do revisor:** "depois de 'Pedir mais caixas', a falta não baixa. O 'Faltam N' vermelho e a sugestão pré-preenchida continuam ou
  reaparecem, e quem segue a sugestão reserva caixas a mais (61 a mais no roteiro do limite adicional)". Avaria: "pedir 50: a falta continua 50
  … depois de usar as 669 caixas … 'Faltam 50 caixas'".
- **Dano:** reserva de caixas acima da necessidade, tirada do livre de outras ordens (cálculo material errado, AGENTS §3).
- **Causa:** `benComplementar` somava o pedido a `solicitado` e ao "a entregar"; `benFaltaCx = máx(0, mín(teto, Σsol − Σcons) − Σcust − Σpend)`
  subia Σsol e Σpend na mesma medida, e a falta só caía quando o `mín` cortava no teto.
- **Correção** (`0e7e3cd`; aqui em `ben.js` l.169-172 e l.499): a parte do pedido que cobre a falta de quando foi pedida vai para
  `o.ben.cxRepos` e não entra no planejado: `benFaltaCx = máx(0, mín(teto, Σsol − cxRepos − Σcons) − Σcust − Σpend)`.
- **Regressão:** `ben_unit.js` U52a2 e U52c; propriedade I-f5 e caso fixo U53h (`ben_prop.js`); mutante M103 (`ben_mutantes.py`).
- **Antes × depois (executado):**
  - `ben_unit_test.py` no código antes da correção (rodada 3 até `15e2976`, cópia `v37_antesA`) com os testes novos: **FALHOU 200/206**
    (U52a2, U52c, U58a, U58b, U59, U60); depois: **OK 206/206**.
  - Sonda do revisor `pB.js` (motor de cada lado): antes `139 → pedir 9 → 139 → pedir 130 → 61`, avaria `50 → pedir 50 → 50 → … → 50`;
    depois `139 → 130 → 0 → 0`, avaria `50 → 0 → 0 → 0` (`fr_ben/sondas/pB_antesA.out`, `pB_depois.out`).

### A2 · S2 · caixa em uso devolvida bloqueada virava fonte de outra ordem

- **Texto do revisor:** "a nova fonte 'quarentena' leva a outra ordem as caixas em uso que uma ordem em execução devolveu bloqueadas para
  inspeção. A ordem de origem fica com 'Faltam 300' e o pedido é recusado."
- **Dano:** a ordem em execução fica com fruta perecível em processo e sem caixa; perda fictícia ou destinação forçada.
- **Causa:** `benSobraDev(apto=false)` mandava a devolução bloqueada inteira para `dispensado`; `cenLiberarQuarentena` soltava tudo no livre;
  `benQuarCx` e as fontes ofereciam a quarentena sem olhar a falta da ordem que a devolveu.
- **Correção** (`a415923`; aqui em `ben.js` l.86-101 e `cenario.js` l.319-334): na devolução bloqueada de ordem aberta, a parte acima da sobra
  fica ligada à linha (`it.quarUso`); `benQuarCx` não a oferece; o laudo que aprova (`benAposLaudo`, gancho do `cenLiberarQuarentena`) a
  devolve reservada à linha até a falta da ordem; o laudo que reprova (`benAposReprovar`) desfaz o vínculo; sem o `ben.js` na página, liberar
  essa quarentena é recusado sem gravar.
- **Regressão:** U58a, U58b; propriedade I-a3 (devolução bloqueada), I-a5, I-f6 e caso fixo U53i; mutantes M104 e M105.
- **Antes × depois (executado):**
  - unidade: no código antes, U58a e U58b reprovam (na conta dos 200/206 acima); depois passam.
  - propriedade no código antes: **FALHOU** com I-f6, I-a3, I-f1 e os casos fixos U53h, U53i, U53j; depois: **OK**, 360 sequências × 35 passos,
    10 casos fixos, nenhum invariante violado.
  - sonda do revisor `pI.js`: antes, a OB-0114 recebe "300 un em quarentena no CX26-02: se a inspeção aprovar, Ana (gestora) libera" como
    fonte, libera com 260 caixas do CX26-02 e o pedido de 300 da OB-0113 é recusado ("71 un livres"); depois, a recomendação não cita a
    quarentena, o laudo devolve as 300 reservadas à OB-0113 (falta 0) e a OB-0114 continua impedida.

### A8 · S2 · aba velha pela lista de Receba devoluções gravava a sobra de novo

- **Texto do revisor:** "pela lista de Receba devoluções (o caminho da primária), uma aba velha grava de novo a sobra já recebida. A gravação
  repetida passa porque o pré-preenchido agora é parcial. Pelo `#dev` a revalidação funciona; pela lista ela não existe." Movimentos
  `[139, 139]`, custódia 869 → 730 → 591.
- **Dano:** movimento duplicado; físico e custódia divergem (139 caixas a mais no lote, 139 a menos com o Igor).
- **Causa:** a revalidação (`self._estDev`: sobra e fase) só existia quando o formulário abria pelo `#dev`.
- **Correção** (`001f50c`; aqui em `areas/processo_estoque.py` l.402-411 e l.680-682): ao abrir o formulário de devolução de uma linha do BEN
  por qualquer caminho, o Estoque guarda a sobra, a fase e o "entregue − devolvido" da linha (`self._estDevVi`); no Salvar, se mudou,
  recusa sem gravar, diz o que mudou e atualiza a quantidade. A saída de Produto continua aceita (não muda entregue − devolvido).
- **Regressão:** `ben_fluxo_test.py sobra` e `sobra390`, passo 6 (1440 e 390, toque e clique reais).
- **Antes × depois (executado):**
  - `ben_fluxo_test.py sobra sobra390` no código antes: **FALHOU 14/16**, "S1440 6" e "S390 6" com `[591, [139, 139]]`; depois (com `conferencia` e `conferencia390`): **OK 30/30**, o passo 6 com `[730, [139]]` (recusado sem gravar).
  - Sonda de tela do revisor `rev_u3.py` (cópia em `fr_ben/tela/`): antes **FALHOU 3/5** (U3b a 1440 e a 390: movimentos `[139, 139]`,
    custódia 591); depois **OK 5/5** (U3b com `[139]` e custódia 730).

### Os demais achados da mesma revisão (vieram juntos; não bloqueavam)

| Achado | Sev. | Correção | Teste |
|---|---|---|---|
| A3 · quarentena reprovada citada como fonte que cobre | S3 | `74c2607`: `benQuarCx` desconta `quarRep` | U59; I-f6 e U53j; M106; sonda `pC.js` |
| A5 · lote do BEN devolvido pelo cliente perdia a genealogia | S3 | `9117ec7` (`comDevolverEf`) | `comercial_unit` C06l |
| A6 · ciclo na genealogia passava sem avaliação | S4 | `8dc39a3` (`comOrigens` marca o caminho) | `comercial_unit` C06m |
| A7 · "com tudo registrado"/"caixas em uso" numa ordem conferida | S4 | `20a73c0` (texto pela fase) | U60; `conferencia` passo 5; M107 |
| A4 · ajuste de contagem velha deixava o físico negativo | S2 do Estoque | fora do BEN; na `int/v59` já está a correção da frente do Estoque (`cenario.js`, contagem com marcador e `CEN_AJ_ABAIXO_RESERVA`), mantida aqui | U55 (BEN) e `est_a4_test` 53/53 |

### Os 3 S2 da rodada 2 (o motivo da saída da navegação na v55)

Codex BEN-REV-20261010-06 (`docs/integracao/BEN3/codex-BEN-REV-20261010-06.md` na branch `claude/v44-ben3`): (1) em conferência a custódia
inteira era sobra (60 em vez de 0); (2) 500 + 420 livres em dois lotes e o BEN via só 500; (3) depois da devolução, o "a entregar"
reabria sem reserva por trás e a entrega baixava a reserva de outra requisição (`Math.max` na reserva agregada). Corrigidos pela rodada 3
(BEN-D33 e BEN-D34). **Contraprova (executado):** os testes finais no código da rodada 2 (o que estava na cópia antes desta frente,
`v37_antesR2u`): `ben_unit_test` **FALHOU 165/206**, inclusive U47c (reprodução 1: sobra 60), U49d (reprodução 2: "500 un disponíveis
para 900") e U48d (reprodução 3: entrega aceita, reserva da QA-B de 80 para 20); `ben_prop_test` **FALHOU** com I-d2, I-a3, I-d4, I-b1, I-b3,
I-a1, I-e4 e I-a4. No código final: OK 206/206 e propriedade OK.

## 2. O que foi trazido da branch `claude/v44-ben3` e como

O retrato `64ea68d` é uma árvore velha; não foi aplicado inteiro. Para cada arquivo que a rodada 3 tocou, fiz a junção de três vias
(`git merge-file`): base = `3f9e4f6` (a v56 sobre a qual a rodada 3 foi feita), deles = `1495d08` (ponta da `claude/v44-ben3`, com A1 a A8),
nossa = a cópia. Arquivos: `ben.js`, `areas/processo_beneficiamento.py`, `areas/processo_estoque.py`, `areas/producao.py`, `cenario.js`,
`comercial.js`, `dados_ben.py`, `ben_unit.js`, `ben_prop.js` (novo), `ben_prop_test.py` (novo), `ben_mutantes.py`, `comercial_unit.js`,
`ben_fluxo_test.py`, `links_ocultos_test.py`. Só `ben.js`, `processo_beneficiamento.py` e `DECISOES.md` estavam no diff pedido; os outros
são parte das mesmas correções (o `cenEntregar`, o `cenDevolver` e o `cenLiberarQuarentena` do `cenario.js`, a devolução guiada do
Estoque e a genealogia do Comercial): sem eles os ganchos do `ben.js` não seriam chamados.

Conflitos (6, todos de convivência com a v57-v59, nenhum de regra):
- `cenario.js` (3): a v57 envolveu o `cenEntregar` no recibo (`cenIdem`, `cenEntregar0`) e passou a revisão de quem registrou para
  `cenRevEntrada`. Ficaram as duas coisas: o recibo e o `cenRevEntrada` da v57, mais o `cenSaldoEntregar` com `dispensado`, o `usoBen`
  e o gancho `benAposReprovar` da rodada 3.
- `areas/processo_estoque.py` (3): ficou o recibo da v57 (`estEntregar` com chave, `eChave(fm,'ENT')`, `lib_mot` no `g2perfilFecha`) e
  entrou a regra única de reserva própria no `cenEntregar` (o `estEntregar0` deixou de recalcular a reserva: mesma conta, `eresTot` =
  `cenResTot`), a revalidação A8 no `ESAVE.g_dev` e o `#dev=` com o "Voltar à OB-…".

## 3. Publicação e navegação (BEN-D39)

- `ui37.BEN_PUBLICADO=True`.
- Agrícola: `… Colheita · Recebimento · Beneficiamento · Estoque de produto`. O item de Cargas passa de "Recebimento e beneficiamento" a
  "Recebimento" (o beneficiamento tem cartão próprio). Cartão: "Beneficiamento", ícone de fábrica (Lucide factory, ISC, novo em
  `engine.ICONS['fabrica']`; o ícone antigo "Beneficiamento" é o mesmo desenho da caixa do Estoque).
- A tela volta por "‹ Agrícola"; o caminho no topo é "Agrícola › Beneficiamento".
- A faixa de telas "Cargas e recebimento | Beneficiamento" (BEN-D14) saiu das duas telas: com o cartão próprio ela seria um 2º caminho.
  Cargas aponta o Beneficiamento só onde faz sentido: a carga recebida em processo diz "Abrir ordem de beneficiamento · Igor" ou "na
  OB-0113 (A liberar)" (`PR_BEN_H` ligado); o Estoque mostra "Voltar à OB-…" depois da devolução guiada (`EST_BEN_H`); a Auditoria liga à
  ordem (`CONF_BEN_H`).
- Mensagens com o caminho antigo: "pesa em Produção › Recebimento e beneficiamento (Cargas)" (`producao.js`) e "em Produção › Recebimento
  e beneficiamento (Cargas) antes de cancelar" (`areas/processo_os.py`) passaram a "Agrícola › Recebimento"; "a Qualidade libera em
  Produção › Estoque de produto" (`ben.js`) passou a "Agrícola › Estoque de produto".

## 4. Packing house, indústria e outros (BEN-D40)

- A unidade é o local de processo onde a linha roda (o `l8 Packing` hoje). O tipo vem do tipo do local (colheita R-10):
  `Packing → Packing house`, `Secador/Terreiro → Grãos e café`, `Agroindústria → Agroindústria` (`dados_ben.TIPO_UNID`, em `BENC.tipoUnid`).
- Na tela: uma linha curta no painel da ordem, "Unidade · Packing · Packing house" (`benUnidTxt`). O texto do bloco ficou neutro: "Da
  matéria-prima recebida ao produto beneficiado: entradas, saídas pesadas, embalagens e balanço na mesma ordem." O rodapé diz
  "embalagem não é produto" (antes "não é fruta"). O fluxo do mamão não mudou.
- **Segunda unidade: não incluída (próximo passo).** O modelo pede três coisas que ainda não existem sem gambiarra: (1) um local do tipo
  Secador/Terreiro ou Agroindústria no CD-06 (lista compartilhada `dados_cad.LOCAIS`, contada por outros testes; "Agroindústria" ainda não
  é tipo de local nem está no R-10), (2) uma linha (ativo do CD-03 e da Manutenção) e (3) uma rota oferecida: SEC-GRA e CAF-BEN estão
  aprovadas como dado, mas são do BEN-3 e do BEN-4 (balanço com umidade e impureza; rendimento do café) e o BEN-1 só oferece a PACK-FRU v3.
  Uma unidade sem rota apareceria vazia. Entra com o BEN-3 (grãos/café) ou com a rota de agroindústria.

## 5. Linhas para `docs/beneficiamento/DECISOES.md` (§12)

Para levar ao repositório: as linhas BEN-D13, BEN-D31 e BEN-D32 com o prefácio em itálico, e as BEN-D33 a BEN-D38, estão literalmente como
no `64ea68d` (`git show 64ea68d:docs/beneficiamento/DECISOES.md`, escritas na rodada 3 e não revisadas pelo Codex); estão copiadas no fim
deste arquivo (Anexo A). Ajustes desta frente às linhas antigas:
- **BEN-D14:** prefixar "*Superada pela BEN-D39 (13/10): o Beneficiamento é cartão próprio de Agrícola e a faixa de telas saiu.*"
- **BEN-D37 (e):** prefixar "*Com a BEN-D39 (BEN_PUBLICADO=True), os modos `roteiro`, `fluxo` e `faixa390` entram pelo cartão de Agrícola.*"

Linhas novas:

| ID | Decisão | Por quê | Como reverter |
|---|---|---|---|
| BEN-D39 | (13/10/2026, proprietário: "coloque beneficiamento dentro de menu produção. Packing house, industria, etc" e "coloque tudo de produção, dentro de Agrícola"; supera a BEN-D14) **O Beneficiamento é cartão próprio de Agrícola, logo depois de Recebimento**, com "‹ Agrícola" de volta e o ícone de fábrica; `BEN_PUBLICADO=True` depois dos 3 S2 (A1, A2, A8) corrigidos e provados. O item de Cargas passa a "Recebimento". A faixa de telas Cargas \| Beneficiamento sai das duas telas (e a pendência dela, `benPendRec`): Cargas aponta a ordem pelo lote em processo ("Abrir ordem de beneficiamento", "na OB-…"), o Estoque volta à ordem depois da devolução guiada e a Auditoria liga à ordem. As mensagens com "Produção › …" passam a "Agrícola › …" | Pedido do proprietário; com o cartão próprio a faixa seria um 2º caminho para a mesma tela (minimalismo, 13/10). A contagem da faixa continua na barra de estado do BEN ("1 a liberar · 3 lotes a beneficiar"). Evidência: `links_ocultos_test` L4a-L4c (o BEN visível por um caminho só; 3 mutantes de página derrubam cada um), `ben_fluxo_test` (1), R1 e faixa390, `producao_fluxo_test` AC-01, `nav_modulos_test`, `paginas_scan_test` com o BEN na varredura | `BEN_PUBLICADO=False` em `ui37.py` (o cartão some, os elos de Cargas, Estoque e Auditoria ficam vazios e o L4 volta a exigir o BEN oculto); voltar a faixa = `faixa_rec`/`prFaixaRec`/`benPendRec` do `int/v59` |
| BEN-D40 | (13/10/2026, mesmo pedido) **A unidade de beneficiamento tem tipo**, lido do tipo do local de processo: Packing → Packing house; Secador e Terreiro → Grãos e café; Agroindústria → Agroindústria (`dados_ben.TIPO_UNID`). Aparece curto no painel da ordem ("Unidade · Packing · Packing house"); o texto da tela fica neutro ("Da matéria-prima recebida ao produto beneficiado"). Nenhuma regra muda: rota, balanço e caixas são os do BEN-1. **Segunda unidade fica para o BEN-3**: ela pede local, linha e rota oferecida que ainda não existem | Servir a packing house, indústria e café sem inflar a tela nem prometer o que o BEN-1 não faz (só a PACK-FRU v3 é oferecida) | Tirar `tipoUnid` de `dados_ben.py`, `benUnidTxt` de `ben.js` e a linha "Unidade" do painel |

## 6. Testes desta frente (executado)

Montagem: `SAFRION_DADOS=sintetico python3 build.py && SAFRION_DADOS=sintetico python3 montar_render.py` (build 0 FALHA, 144 quadros:
61 no menu e 83 ocultos; `_render` com 152 páginas). Navegador: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
python3 -B <teste>.py`, um por vez por lote (`flock`), com a carga da máquina entre 10 e 30 (outros agentes).

Logs: montagem antiga (a cópia como chegou, BEN oculto) em `fr_ben/logs/base/`; montagem nova em `fr_ben/logs/depois*/`.

| Teste | Montagem antiga (BEN oculto) | Montagem nova (BEN publicado) |
|---|---|---|
| `build.py` + `montar_render.py` | 0 FALHA · 144 quadros (60 menu, 84 ocultos) · 152 páginas | 0 FALHA · 144 quadros (61 menu, 83 ocultos) · 152 páginas |
| `ben_unit_test.py` | OK 168/168 (suíte antiga) | **OK 206/206** |
| `ben_prop_test.py` (360 × 35, 10 casos fixos) | não existe | **OK**, nenhum invariante violado |
| `ben_mutantes.py` | — | **OK 104/104** |
| `comercial_unit_test.py` | OK 114/114 | OK 118/118 |
| `producao_unit_test.py` | OK 160/160 | OK 160/160 |
| `links_ocultos_test.py` | 16 · 0 falhas (L4 com o BEN oculto) | 16 · 0 falhas (L4 com o BEN visível) |
| `nav_modulos_test.py` | 15 ok · 0 falhas | 15 ok · 0 falhas |
| `producao_fluxo_test.py` | OK 91/91 | OK 92/92 (+1: o cartão Beneficiamento abre a tela com "‹ Agrícola") |
| `busca_unica_test.py` | 6 ok · 0 falhas | 6 ok · 0 falhas |
| `paginas_scan_test.py` | 4 ok · 0 falhas (143 páginas) | 4 ok · 0 falhas (144 páginas: o BEN entrou na varredura) |
| `varredura.py` | — | 152/152 páginas sem erro |
| `tabelas_ben_test.py` | OK 12/12 | OK 12/12 |
| `ben_fluxo_test.py` (23 modos) | **FALHOU 1/13** e parou com exceção no passo (2): o (1) esperava o menu antigo (vermelho já existente, o mesmo citado no pedido) | **OK 223/223**: fluxo+erros+celular+revisao 66/66, roteiro+roteiro390 34/34, faixa390+teclado+cancelar 33/33, sobra+sobra390+conferencia+conferencia390 30/30, complemento+lotes+duplo+criada 26/26, cadeia+cadeia390 16/16, multilote+multilote390+rodape+manutencao 18/18 |
| `tabelas_est_test.py` | 34/34 | 34/34 |
| `cafe_apurar_test.py` | OK 10/10 | OK 10/10 |
| `comercial_fluxo_test.py` / `comercial_revisao_test.py` | OK 74/74 / OK 33/33 | OK 74/74 / OK 33/33 |
| `est_cenario_test.py`, `cen_grava_test.py`, `est_a4_test.py`, `solo_unit_test.py`, `cada_cd04_test.py` | 15/15, 10/10, 53/53, 128/128, 15/15 | 15/15, 10/10, 53/53, 128/128, 15/15 |
| `os_irrig_filtro_test.py` / `tabelas_os_test.py` | 15 ok / 40/40 | 15 ok / 40/40 |
| `os_cenario_test.py` | **FALHOU 21/22** ("A liberar sem revisão … cenário v2 sem aprov") | FALHOU 21/22, a mesma verificação e o mesmo texto: **vermelho já existente, da O.S.**, fora do BEN |
| `config_test.py` | **FALHOU 87/88** (A14: "%" na célula da AL-05) | FALHOU 87/88, o mesmo A14: **vermelho já existente, da CONF**, fora do BEN |

Medida da tarefa do proprietário (`ben_fluxo_test fluxo`): **20 toques e 0 campos digitados**, desde o cartão Beneficiamento (a mesma
medida da BEN-D14, que partia da faixa de Cargas).

Sondas do revisor (cópias em `fr_ben/sondas/` e `fr_ben/tela/`):

| Sonda | Achado | Código antes da correção (`v37_antesA`) | Código final |
|---|---|---|---|
| `pB.js` (motor) | A1 | 139 → 139 → 61; avaria 50 → 50 | 139 → 130 → 0; avaria 50 → 0 |
| `pI.js` (motor) | A2 | a quarentena da OB-0113 vira fonte da OB-0114, que leva 260 caixas; o pedido da OB-0113 é recusado | sem fonte quarentena; o laudo devolve as 300 à OB-0113; a OB-0114 continua impedida |
| `pC.js` (motor) | A3 | quarentena reprovada citada como fonte que cobre | só a sobra real da OB-0110 (60) como fonte |
| `rev_u3.py` (tela, 1440 e 390) | A8 | FALHOU 3/5 (U3b: `[139, 139]`, custódia 591) | **OK 5/5** |
| `rev_tela.py` U1, U2, U4, U5, U6 (tela, 1440 e 390) | A1, A3, A7 | — (o revisor já a tinha rodado no `15e2976`) | 18/20: U1, U2, U4, U5 e U6 OK; reprovam só os 2 "U4b" (a gestora vê o CX26-02 "como reprovado"), a verificação que o próprio parecer descartou como fraca ("lia só o resumo do cabeçalho do Estoque") |

Contraprova das regras novas do `links_ocultos_test` L4 (executado, página da montagem nova alterada e restaurada, `cmp` igual):
sem o cartão do BEN em Agrícola → L0 e L4a reprovam; `PR_BEN_H` vazio em Cargas → L4b reprova; a faixa de volta em Cargas → L4c
reprova (`fr_ben/contraprova_L4/`).

Capturas da montagem nova: `fr_ben/capturas/agricola_1440.png`, `agricola_390.png` (cartões, com o ícone de fábrica),
`ben_ob0112_1440.png`, `ben_ob0112_390.png` ("‹ Agrícola", "Agrícola › Beneficiamento", "Unidade · Packing · Packing house"),
`carga_1440.png`, `carga_390.png` (sem a faixa; o L39-131 com "Abrir ordem de beneficiamento · Igor").

## 7. Pendências

- **Revisão do Codex** das correções A1, A2, A3 e A8 trazidas para cá e desta publicação (regime leve: não bloqueia; o parecer dele
  pedia as sondas verdes, e estão verdes aqui).
- **Levar ao repositório** (sem commit nesta frente): os arquivos da seção 8, as linhas da seção 5 e o Anexo A em `DECISOES.md`; no
  `docs/beneficiamento/README.md`, trocar "No menu: Produção › Recebimento e beneficiamento › Beneficiamento (BEN-D14)" por "No menu:
  Agrícola › Beneficiamento (BEN-D39)"; o pacote `docs/integracao/BEN3/` da `claude/v44-ben3` (DESENHO, README, brutos) também pode ir.
- **Segunda unidade** (secador/terreiro de grãos e café, agroindústria): com o BEN-3/BEN-4 (seção 4).
- **Texto fora do BEN com "Produção ›"**: `areas/mobile.py` ("publica em Produção › Previsão e colheita") ficou antigo com a mudança da
  Produção para Agrícola (não é desta frente; não alterei).
- **Vermelhos já existentes**, iguais nas duas montagens: `os_cenario_test` 21/22 (O.S.) e `config_test` 87/88 (A14, CONF).
- **Limites conhecidos da rodada 3** (do pacote BEN3, seguem valendo): a demanda viva da CTL-4 lê as caixas como bruto (sem efeito em
  compra hoje; muda com o BEN-2); o gerador da propriedade não cobre contagem, ajuste, `benRetirar`, `benConfirmarCorrecao` nem comandos
  de O.S.; perguntas P1 a P5 ao Codex (README do BEN3).

## 8. Arquivos alterados na cópia (`fr_ben/v37/gen37`)

Trazidos da rodada 3 (junção de três vias, seção 2), com A1 a A8:
`ben.js`, `cenario.js`, `comercial.js`, `dados_ben.py`, `areas/processo_beneficiamento.py`, `areas/processo_estoque.py`,
`areas/producao.py`, `ben_unit.js`, `ben_prop.js` (novo), `ben_prop_test.py` (novo), `ben_mutantes.py`, `comercial_unit.js`,
`ben_fluxo_test.py`, `links_ocultos_test.py`.

Desta frente (publicação, navegação e tipo da unidade):
- `ui37.py`: `BEN_PUBLICADO=True`; Agrícola com "Recebimento" e "Beneficiamento"; `CURTO37['BEN.dc.html']=('Beneficiamento','fabrica')`; sem o `MENU_OF` do BEN.
- `engine.py`: ícone `fabrica` (Lucide factory, ISC).
- `build.py`: o BEN publicado não entra de novo como detalhe de Agrícola (evita quadro repetido) e perde o título antigo.
- `areas/producao.py`: sai a faixa de telas (`REC_TELAS`, `faixa_rec`, `prFaixaRec`).
- `areas/processo_beneficiamento.py`: sem a faixa; linha "Unidade" no painel; texto do bloco e do rodapé neutros; docstring "Agrícola ›".
- `ben.js`: sai `benPendRec` (só servia à faixa); entra `benUnidTxt`; "Agrícola › Estoque de produto" na mensagem do Fechar.
- `dados_ben.py`: `TIPO_UNID` e `BENC.tipoUnid`.
- `producao.js` e `areas/processo_os.py`: "Agrícola › Recebimento" nas duas mensagens com o caminho antigo.
- Testes: `ben_unit.js` (U29 e U40c sem a pendência da faixa, com a contagem da tela), `ben_fluxo_test.py` ((1), R1 e faixa390 pela
  navegação nova; passo (2) confere a unidade), `links_ocultos_test.py` (L4a/L4b/L4c exigem o BEN visível quando publicado; E4 com o
  caminho novo), `producao_fluxo_test.py` (AC-01 com o cartão Beneficiamento), `paginas_scan_test.py` (o BEN publicado entra na varredura).
  Cada ajuste tem o motivo em comentário.

## Anexo A · linhas BEN-D13 e BEN-D31 a BEN-D38, literais do `64ea68d`

Cabeçalho da tabela do §12: `| ID | Decisão | Por quê | Como reverter |`. Texto da rodada 3 (Claude, 10–13/10), não revisado pelo Codex.

| ID | Decisão | Por quê | Como reverter |
|---|---|---|---|
| BEN-D13 | *Em parte superada pela BEN-D23 (rodada 1, 09/10): o Igor está no "Entregar a" do Estoque; e pela BEN-D33 (rodada 3) para o endereço `EST.dc.html#dev=…`, que abre Receba devoluções com o formulário da linha.* Limitações do Estoque (arquivo em reescrita por outra frente; instrução (c)): a lista "Entregar a" do EST não tem o Igor e a linha da OB mostra o link da O.S.; a entrega no balcão é confirmada quando o Igor inicia a ordem (`confirmado:'balcao'`), não no app. O EST não abre seção pelo endereço: o atalho leva ao Estoque | Não editar `areas/processo_estoque.py` | `cenBalcao` e o recebedor herdado na frente Suprimentos simplificado |
| BEN-D31 | *Estendida pela BEN-D34 (rodada 3): a liberação também faz uma linha por lote, e liberação e complemento dividem entre lotes quando nenhum cobre sozinho (tudo ou nada).* (09/10/2026, BEN-REV-20261009-03, S2) **Uma linha de caixas por lote.** O complemento sai do lote de uma linha da ordem que tenha as caixas livres (a REQ da liberação primeiro) e soma a ela; sem caixa livre bastante nesses lotes, sai do lote com caixas livres numa **requisição própria da ordem** (REQ do complemento, `o.ben.reqc`, `os` = a ordem), com reserva e movimento no lote dela. O lote de uma linha nunca muda. A saída de Produto consome da custódia por linha, a mais antiga primeiro, e grava as partes (`s.cons`: REQ, lote, quantidade e movimento de consumo de cada uma); o estorno devolve cada parte à custódia da sua linha e do seu lote, com `ref` ao movimento original; a devolução e a entrega no Estoque são por linha (REQ e lote). O Fechar (`cenPodeEncerrar`) olha a custódia de todas as requisições da ordem e, com mais de uma, diz a REQ e o lote da sobra. O painel mostra uma linha por REQ e lote e a custódia por linha. Cai a recusa "use as caixas em custódia e peça de novo" do complemento: ela só protegia o item único; com a linha por lote, caixa nova e antiga convivem sem misturar o saldo | O complemento trocava o lote do item da REQ (`it.lote`): no roteiro do Codex (540 caixas do CX26-01 entregues e usadas na S-01; 1.000 recebidas no QA-CX-02; pedir 100; estornar a S-01; devolver 540) o consumo MV-1003 era do CX26-01, o estorno MV-1006 ref MV-1003 ia para o QA-CX-02 e a devolução também: o CX26-01 ficava em 0 e o QA-CX-02 subia de 1.000 a 1.540 (total conservado, origem e saldos por lote corrompidos sem transferência). Evidência (executado): o harness do Codex (`codex-ben-rev-03-harness.js` + `ben_unit_test.motor()`, node, sintético) antes: CX26-01 0 e QA-CX-02 1.540, estorno no QA-CX-02; agora CX26-01 540, QA-CX-02 1.000 com reserva 100, estorno no CX26-01, e os 3 controles (versão vencida, papel insuficiente, recibo igual e conflitante) sem escrita. `ben_unit.js` U45a-h (a reprodução, caixas misturadas consumidas e estornadas por lote, Fechar recusado pela sobra da REQ do complemento e encerrado com 12.300 kg e diferença 0, trilha de cada lote fechando com movimentos, linhas e reservas; recibo, versão e perfil) e U41e/U41g reescritos: antes FALHOU 153/163, agora OK 163/163; mutantes M66 (o item troca de lote), M69 (consumo sem as partes), M70 (estorno no lote da REQ da liberação), M71 (Fechar só com a REQ da liberação), M72 (REQ nova com caixa livre noutra linha) e M21b mortos; `ben_fluxo_test.py lotes` (pela tela: pedir 100 abre a REQ-042 no QA-CX-02 com as duas linhas no painel, estorno da S-01 no CX26-01, Rui recebe a devolução da REQ-041 no CX26-01 e entrega a REQ-042 do QA-CX-02): antes FALHOU no L1 (o item da REQ-041 passava ao QA-CX-02, sem REQ-042), agora OK 7/7 | Voltar `benComplementar` ao item único (não recomendado: volta o S2); tirar `o.ben.reqc`, `benLinhas`, `s.cons` e `benPartes` de `ben.js` e a varredura das requisições da ordem em `cenPodeEncerrar` (`cenario.js`) |
| BEN-D32 | *Precisada pela BEN-D33 (rodada 3): o teto vale em toda fase aberta pelo kg aberto (em conferência também, conferida ou não; a custódia inteira não é mais sobra), e a devolução se divide em sobra (livre) e caixa em uso (volta reservada à linha). A frase "a devolução no Estoque não muda" caiu.* (10/10/2026, integração BEN, rodada 2: S2 da reverificação BEN-c1-B) **Sobra de caixas é só o que a ordem não pode mais usar.** A falta de caixas de uma ordem (impedimento da liberação e recusa do "Pedir mais caixas") só aponta como saída a **sobra** de outra ordem (`benCxSobra`): a custódia acima do máximo que ela ainda pode embalar, ⌈kg a embalar ÷ 10 kg⌉ com toda a fruta em caixa (sem a fração vendável, para não subestimar o uso). Liberada: a entrada inteira; em execução: o que falta registrar; enviada para conferência: nada (a custódia inteira é sobra, como o selo "Sobra em custódia" e o Fechar, que exige custódia zero). Com mais de uma ordem com sobra, a que cobre a falta (ou a maior). O texto diz a sobra ("A OB-0110 tem sobra de 60 un em custódia"). Sem nota nem sobra, a ordem em A liberar continua com "Cancelar a ordem" (BEN-D22); a ordem liberada ou em execução, que não se cancela (BEN-6), recebe o caminho real: "Quando a nota das caixas chegar, Rui confere em Estoque › Confira recebimentos e você pede de novo (Pedir mais caixas)". A devolução no Estoque (`cenDevolver`) **não** muda: devolver caixas durante a execução é operação legítima (o roteiro do Codex do BEN-REV-20261009-03 devolve 540 caixas em execução depois do estorno) e o Estoque já mostra a linha como "Em uso na O.S."; o defeito era o sistema recomendar essa devolução como recuperação | O atalho "Receber a devolução da OB-0113" contava como sobra a custódia de qualquer outra ordem, em qualquer fase: com a OB-0113 liberada e as 1.169 caixas do L39-132 entregues, a OB-0112 (600 para 881) mandava recebê-las; seguido, a OB-0112 liberava com elas, a OB-0113 conseguia no máximo 919 das 1.169 caixas (faltavam 250 cx, ~2.500 kg sem caixa), não podia ser cancelada e o L39-132 ficava preso: perda fictícia ou destinação forçada. No L39-131 a mesma recomendação tirava as 1.169 caixas e nem resolvia a OB-0114 (1.200 para 2.292). E a recusa do "Pedir mais caixas" em execução mandava "Cancelar a ordem", que não existe para ordem liberada. Evidência (executado, dados sintéticos): `ben_unit.js` U46a-e (a cadeia da reverificação; em execução com 1.300 kg a registrar e 69 cx, sobra 0; com tudo registrado e em conferência, sobra 69; liberada com 1.300 cx para 12.300 kg, sobra 70; recusa do complemento em execução sem "Cancelar"): antes FALHOU 163/168, agora OK 168/168; U25a e o `ben_fluxo_test` fluxo com o texto "tem sobra de 60 un"; mutantes M73 (custódia inteira de qualquer ordem), M74 (ignora o que falta registrar), M75 (fração vendável), M76 (manda cancelar ordem liberada) mortos, OK 76/76; `ben_fluxo_test.py cadeia` (1440, clique real) antes FALHOU 4/8 (K1-K4), e `cadeia` + `cadeia390` (390, toque real) agora OK 16/16: a OB-0112 sem o atalho da OB-0113 liberada e em execução, a recusa do complemento sem "Cancelar", a sobra de 69 un recebida pelo atalho e a OB-0113 fechando 12.300 kg com diferença 0; as sondas `p10_cadeia.py` e `p9_sobra.py` da reverificação param no passo 2 ("NÃO ACHEI: Receber a devolução da OB-0113"); o harness do Codex do BEN-REV-20261009-03 continua 4/4 | Voltar `benCaixasRec` a contar `benCxTot(c, b).cust` de qualquer ordem e a frase única com "Cancelar a ordem" (não recomendado: volta o S2); tirar `benCxSobra` |
| BEN-D33 | *Precisada pela BEN-D38 (revisão adversarial: A1, a reposição não entra no planejado; A2, caixa em uso devolvida bloqueada continua da ordem até o laudo; A7, o texto segue a fase; A8, a revalidação vale em todo caminho de abertura).* (10/10/2026, integração BEN, rodada 3: S2-1 e S2-2 da rodada 2, limite adicional do Codex; desenho `docs/integracao/BEN3/DESENHO.md` com a crítica C-1 a C-18) **A sobra é a custódia acima do teto do kg aberto, em toda fase aberta; a devolução se divide em sobra e caixa em uso.** kg aberto = entrada − saídas válidas em Liberadas, Em execução e Em conferência, com ou sem conferência dada (`benKgAberto`; não é a `benEmProc`, que zera no Concluir); teto = ⌈kg aberto ÷ 10 kg⌉ (`benCxUsoMax`); sobra = custódia − teto (`benCxSobra`), repartida pelas linhas (`benSobraLinhas`). Ao receber a devolução de uma linha de ordem do BEN, o `cenDevolver` chama `benSobraDev` antes de baixar a custódia e `benAposDevolver` depois: a parte até a sobra volta livre e sai do "a entregar" (campo interno `dispensado`, gravado só pelo BEN; `cenSaldoEntregar` = solicitado − dispensado − consumido − custódia, e nas linhas de O.S., app e SUP o termo é 0); o resto volta **reservado à mesma linha** (movimento `reserva`), e a mensagem diz as duas partes. Avariada: tudo à quarentena e sai do "a entregar". Sem o ben.js na página, a devolução de linha BEN é recusada (falha fechada). O Estoque pré-preenche `benDevPadrao` (a parte da sobra da linha; em conferência com o kg aberto dentro da faixa ou já conferida, a custódia inteira, porque o que passa da sobra fica reservado e o Fechar baixa) e mostra a conta (custódia − o que ainda embala, kg ÷ 10 kg); a palavra "dispensado" não aparece em tela (a O.S. já a usa para área): a conta diz "devolvido como sobra", "avariado" ou "baixado no Fechar". A entrega (`cenEntregar`) baixa só a reserva própria e recusa acima de reserva própria + livre, **mantida a trava física** (físico − quarentena; crítica C-2). A falta na execução é `benFaltaCx` = mín(teto, caixas da ordem − usadas) − custódia − a entregar, sem reaplicar a fração vendável (crítica C-1): aparece no selo "Faltam N caixas" e no próximo passo com a recuperação da fase (Pedir mais caixas; em conferência, Reabrir a execução, porque ali não entra caixa) e é a sugestão do Pedir mais caixas (sem falta, o campo vem vazio e a estimativa pelo kg em processo fica só no texto). Liberada ou em execução com reserva maior que o físico (ajuste de inventário aprovado depois da reserva): aviso "Reserva sem físico: N caixas da REQ-… · o almoxarife confere o lote". `cenResTot`: base da semente não Reservada = o entregue da semente (era 0), menos as `reserva-baixa`. Revalidação do atalho guiado pela sobra e pela fase da ordem, não pela versão nem pela custódia da linha (uma saída de Produto sobe a versão e baixa a custódia sem mudar a sobra; o desenho pedia as duas coisas, e a custódia contradizia o controle "saída de Produto na outra aba → aceita") | Rodada 2 (lentes A e B em 0139898): em conferência a custódia inteira era sobra, e a OB-0112 levava as 1.000 caixas que a OB-0113 precisava para relançar a S-01 estornada (ou as 169 de "faltou a classe B"); a sobra parcial dizia 139 e o formulário trazia 869 (ou 1.169); depois da devolução o "a entregar" reabria sem reserva por trás (fantasma) e a entrega dele baixava a reserva de outra REQ (`Math.max` na reserva agregada; reprodução 3 do Codex: QA-B de 80 para 20). Evidência (executado, dados sintéticos; brutos em `docs/integracao/BEN3/`): `ben_unit.js` U47a-e, U48a-e, U52a-b, U54, U55, U56 e o `TRILHA` reescrito (reserva do lote = "a entregar" das linhas abertas), antes (código do 0139898 com os testes novos) FALHOU 165/193, agora OK 193/193; propriedade `ben_prop_test.py` (3 sementes, 360 sequências × 35 passos, oráculo independente) antes FALHOU com I-a1, I-a3, I-a4, I-d2, I-e4, I-b1 e I-b3 e as trilhas mínimas, agora OK, também no tamanho noturno (1.200 × 50); as trilhas mínimas do antes viraram os casos fixos U53a-g; mutantes M74-M81, M84-M86, M89-M91, M93-M95 mortos (`ben_mutantes.py` OK 92/92); `ben_fluxo_test.py conferencia`, `conferencia390`, `sobra` e `sobra390` (estorno na conferência sem o atalho; atalho que abre Receba devoluções com a REQ-041 e 139; a sobra mudada em outra aba recusada sem gravar e a saída de Produto aceita; "Voltar à OB-0112"); harness do Codex do BEN-REV-20261009-03 OK 4/4 com o CX26-01 em `[540, 540]` (antes `[540, 0]`: as 540 caixas devolvidas em execução, com 12.300 kg a embalar, voltam reservadas à ordem; pergunta P1). Expectativas mudadas de propósito: U45c/U45g (pelo `TRILHA`), X2 do modo complemento (sugestão vazia), L3 do modo lotes (formulário vazio; 540 voltam reservadas) | Voltar `benCxSobra` à BEN-D32 e tirar `benSobraDev`/`benAposDevolver` do `cenDevolver` (não recomendado: volta o S2-1/S2-2); tirar o termo `dispensado` do `cenSaldoEntregar` (volta o fantasma); voltar o `cenEntregar` ao `Math.max` (volta a reprodução 3 do Codex) |
| BEN-D34 | *Precisada pela BEN-D38 (A3: a quarentena reprovada não é fonte; A2: nem as caixas em uso de ordem aberta).* (10/10/2026, rodada 3: S2-3 e o S3 do "lote errado") **Livre total dos lotes elegíveis; uma linha por lote na liberação; tudo ou nada; fontes de recuperação combinadas.** O mesmo conjunto conta e reserva: `benLotesCx` (lotes do item caixa com livre, a quarentena fora), `benLivreCx` (soma) e `benAlocarCx` (um lote que cubra sozinho, as linhas da ordem primeiro e depois o de maior livre; senão divide pela mesma ordem; sem bastante, nada é gravado). A liberação (`benAutorizarLiberar`) deixa de chamar o `cenLiberar`: aloca e grava com `benReservaCx` (uma REQ por lote: a 1ª é `o.req`, as outras `o.ben.reqc`, BEN-D31); com um lote que cobre, uma linha só, como antes. O complemento usa a mesma alocação. O impedimento, o aviso da ordem nova, a recusa do complemento e a falta usam o mesmo livre total. `benCaixasRec` devolve `{t, h, why, falta, fontes, cobre}`: fontes na ordem sobra de outra ordem (nunca a própria; as linhas e a quantidade exata), nota a conferir ("traz até N un") e quarentena ("se a inspeção aprovar, a gestora libera com o laudo"); vale a que cobre sozinha, senão todas, com "Ainda faltam K un" e a ação real da fase. O atalho da sobra é `EST.dc.html#dev=<REQ>&para=<ordem pedinte>&ver=<versão>&sob=<sobra>`: o Estoque abre Receba devoluções com o formulário da linha, a primária é essa linha, e depois de salvar aparece "Voltar à OB-…" (só com a tela do BEN publicada: com `BEN_PUBLICADO=False`, v55, o endereço vem vazio da constante `EST_BEN_H` e o Estoque não aponta a tela oculta). No Entregue por O.S., "O.S. pede" compara com as linhas da ordem e a ordem do BEN não mostra "Aguardando confirmação no app" (recebe no balcão) | Com 920 a 1.700 caixas livres em dois lotes (e parte em quarentena) a liberação e o complemento olhavam só o lote de maior saldo e diziam "Sem caixa, Cancelar a ordem"; a sobra recebida voltava ao lote de origem e o texto a comparava com a falta de outro lote. Evidência: U49a-f (NF com 1.100 aptas e 100 em quarentena; a sobra de 289 que libera a OB-0112; L39-131 "Faltam 492"; reprodução 2 do Codex 500 + 420, com 921 recusado sem reserva; complemento de 600 em dois lotes; quarentena citada com quem libera), U50a-c (A1 e A6 da lente mortos; fontes estruturadas), M82, M83 e M63/M65/M66/M72 com âncoras novas; `ben_fluxo_test.py multilote` e `multilote390` (libera em duas linhas, o Rui entrega as duas sem "O.S. pede" nem chip do app, fecha 12.300 kg com reserva 0). Expectativas mudadas de propósito: U39c ("traz até"), U39f, U46a/c/e e os passos 1, 3, 4 e 5 do modo `cadeia` (631 livres: os 31 do CX26-02 contam; "Ainda faltam 181"; o atalho abre o formulário guiado); `links_ocultos_test` E1b, E1d e E1e: a OB não chama mais o `cenLiberar`, e a trava do CTL-1 passa a ser "nenhum `cenLiberar` em ben.js e a única passagem para Liberadas dentro do `benAutorizarLiberar`, com perfil, `benO`, CMD-42 e CMD-06" (5 mutantes de atalho derrubados) | Voltar o impedimento ao `cenLote` e a liberação ao `cenLiberar` (não recomendado: volta o S2-3); tirar `benAlocarCx`/`benReservaCx` e o tratamento de `#dev=` do Estoque |
| BEN-D35 | (10/10/2026, rodada 3; S3 da rodada 1) **O Fechar baixa a reserva não entregue.** Em cada linha da ordem, a reserva própria ainda não entregue sai do lote com o movimento `reserva-baixa` (o Estoque mostra "Reserva baixada no Fechar") e o que restava a entregar sai do "a entregar" | A reserva presa depois do Fechar diminuía o livre para sempre e alimentava o impedimento falso de outra ordem (rodada 1: "fís 31 res 5"). Evidência: U51, U47e (o reservado à linha pela regra de divisão baixa no Fechar numa visita só), U53e (trilha mínima do I-e4), M84 e M95 mortos | Tirar o bloco de baixa do `benFechar` (não recomendado) |
| BEN-D36 | (10/10/2026, rodada 3: S3 e S4 da tela) **Um gesto, uma ação; rascunho protegido; aviso e rodapé sem ambiguidade.** No BEN, keydown de Enter ou Espaço com `e.repeat` num botão não aciona nada (num campo de texto é digitação); depois de um comando que muda a fase ou fecha um formulário o foco vai ao título do painel (`tabindex=-1`), nunca à primária nova; o toque duplo continua absorvido (BEN-D25). Esc, X, fundo escurecido e Voltar com campo digitado (número ou texto) não descartam: aparece "Rascunho não salvo" com Continuar editando e Descartar, e um 2º Esc descarta; escolher por toque não pede confirmação, e reabrir o rascunho preenchido fica vetado (seria último valor de quantidade, AGENTS §3.3). Com o painel aberto o aviso sobe ao topo e não recebe toque. Rodapé: o formulário com Voltar não repete o fechar (`closeHide`, opcional no painel comum, falso nas outras telas); sem formulário ou depois de uma recusa o fechar diz "Voltar à lista" (não "Fechar" ao lado de "Fechar processo"). Medida no modo teclado: um Tab a mais para chegar à primária depois de cada comando | Rodada 2: Enter segurado em "Autorizar rota e liberar" iniciava o processo, e no "Registrar" da última saída enviava para conferência; Esc descartava caixas e bruto digitados; o aviso cobria a primária 2 a 4 s a 390 px; "Voltar \| Cancelar \| Confirmar" e "Fechar" ao lado de "Fechar processo". Evidência: `ben_fluxo_test.py teclado` T13-T16, antes FALHOU nos quatro (Em execução, Em execução, Em conferência, painel fechado e valores perdidos), agora OK; `rodape` R1-R4 (R4 a 390 antes coberto pelo aviso, agora livre); os modos fluxo e celular com o rótulo novo; o roteiro do proprietário continua 34/34 com 29 toques a 1440 e 31 a 390 (mouse e toque não mudam) | Tirar `bnRepete`, `bnFocoTitulo`, `bnSujo`/`bnVolta`, o `<style>` do aviso e o `closeHide`/"Voltar à lista" de `areas/processo_beneficiamento.py` e o `pp_closeOn` de `areas/producao.py` |
| BEN-D37 | *Estendida pela BEN-D38 (A5: a devolução do cliente mantém a genealogia; A6: ciclo na genealogia impede).* (13/10/2026, rodada 3 integrada na v56 `3f9e4f6`, branch `claude/v44-ben3`; pacote `docs/integracao/BEN3/`) **A rodada 3 entra na v56 sem mudar regra do BEN; o que nenhum teste prendia ganha teste; o Comercial lê a origem do lote embalado pela genealogia.** (a) Merge: conflito só na `MTIPO` do Estoque (ficam `reserva-baixa` e `inspecao-reprovada`); no `cenario.js` as duas frentes mexem em funções diferentes (CTL-4: `cenOsSup`, `cenOsDem`, `cenEstDem`, `cenReprovarQuarentena` e o `quarRep` do `cenLiberarQuarentena`; BEN: `cenSaldoEntregar`, `cenEntregar`, `cenDevolver`, `cenResTot`). (b) Sete regras do desenho sem teste de unidade ganham U57a-g e os mutantes M96-M102 (a `reserva-baixa` e a base da semente no `cenResTot`; avaria fora do "a entregar"; Reabrir a execução em conferência; selo da sobra; kg aberto com a conferência dada; todas as notas como fonte). A propriedade ganha o I-d4 (a reserva própria do motor é a do oráculo) e o selo no I-a1. (c) O `comImpede` do Comercial passa a ler a origem pela genealogia (`comOrigens`): origem de campo segue a avaliação de carência; folha de saldo de abertura conta como origem anterior ao sistema; lote da cadeia sem origem, ou parte que aponta lote inexistente, continua impedindo. (d) A demanda viva da CTL-4 (`cenOsSup`, `cenEstDem`) lê as caixas da ordem como bruto e não conhece o `dispensado` nem a sobra: hoje não muda compra, porque a caixa não é insumo do plano (fora de `dados2.os_base` e `est_base`); quando a compra de caixas entrar (BEN-2), a demanda passa a ler `benFaltaCx` e `benCxSobra`. (e) Com `BEN_PUBLICADO=False`, os modos `roteiro`, `fluxo`, `revisao` (B3) e `faixa390` do `ben_fluxo_test` conferem que a navegação não oferece a tela oculta e entram pelo endereço; a navegação publicada é conferida numa cópia de rascunho com a tela publicada (sem commit). O passo (4) do `fluxo` segue a v56: sem o papel da Qualidade não há verde e o próximo passo diz o dono; o PV-031 é lido em Contratos e pedidos, e a situação de crédito é do Comercial | (b) Uma sonda de 24 mutantes extras nas regras da rodada achou 8 que sobreviviam aos testes de unidade; 7 viraram teste e o 8º é equivalente (ordem sem caixa não é alcançável: a PACK-FRU v3 exige ao menos 1 caixa). (c) Com o BEN publicado, o roteiro do proprietário terminava com o PV-031 Em risco: "Expedição impedida no L39-120: origem — colhida em — sem lote de campo". Dano: toda venda de fruta beneficiada ficava com a saída impedida (S2 latente, já presente na base v56). Evidência (executado, sintético; brutos em `docs/integracao/BEN3/brutos/`): `ben_unit_test` antes (3f9e4f6 + testes novos) FALHOU 165/200, depois OK 200/200; `ben_prop_test` antes FALHOU com I-d2, I-a3, I-d4, I-b1, I-a4, I-e4, I-b3 e I-a1, depois OK (360 × 35 e 1.200 × 50); `ben_mutantes` OK 99/99; `comercial_unit` antes FALHOU 114/116 (C06j, C06k), depois OK 116/116; harness do Codex OK 4/4 com o CX26-01 `[540, 540]`; navegador (carga ≤ 8, lock I) no pacote | Tirar U57/M96-M102/I-d4 (perde a proteção, não muda comportamento); voltar `comImpede` a ler `L.origem` (volta a travar toda venda de fruta beneficiada); voltar os modos do `ben_fluxo_test` (ficam vermelhos com a tela oculta) |
| BEN-D38 | (13/10/2026, revisão adversarial da rodada 3 sobre `15e2976`; parecer em `ben3rev/PARECER.md`, achados A1 a A8; pacote `docs/integracao/BEN3/`) **A falta baixa com a reposição; caixa em uso devolvida bloqueada continua da ordem até o laudo; quarentena reprovada não é fonte; a devolução do BEN revalida a linha em todo caminho; a genealogia sobrevive à devolução do cliente e o ciclo impede; os textos seguem a fase.** (A1, S2) A parte de cada "Pedir mais caixas" que cobre a falta de quando foi pedida (`o.ben.cxRepos`) não entra no planejado: `benFaltaCx = máx(0, mín(teto, Σsol − cxRepos − Σcons) − Σcust − Σpend)`; o que passa da falta é planejamento. (A2, S2) Na devolução bloqueada para inspeção de ordem aberta, a parte acima da sobra fica ligada à linha (`it.quarUso`): não é fonte de outra ordem; o laudo que aprova (`benAposLaudo`, gancho do `cenLiberarQuarentena`) a devolve reservada à linha até a falta da ordem e solta o resto; o laudo que reprova (`benAposReprovar`) desfaz o vínculo; sem a regra do BEN na página, liberar essa quarentena é recusado sem gravar. (A3, S3) `benQuarCx` desconta a parte reprovada (`quarRep`, CTL-4). (A8, S2) O Estoque guarda, ao abrir o formulário de devolução de uma linha do BEN por qualquer caminho, a sobra, a fase e o "entregue − devolvido" da linha; no Salvar, se mudou, recusa sem gravar, diz o que mudou e atualiza a quantidade (a saída de Produto continua aceita: P4, C-11). (A5, S3) `comDevolverEf` mantém a genealogia: a parte de lote vira `{lote vendido, kg devolvido, modo 'devolucao'}`. (A6, S4) `comOrigens` marca o caminho: lote que reaparece nele impede ("ciclo na genealogia"). (A7, S4) Ordem conferida: "N un ficam reservadas à OB até o Fechar" e "OB conferida: a custódia inteira volta ao lote e fica reservada à OB até o Fechar", sem "com tudo registrado" nem "caixas em uso". (A4) Fica fora do BEN, com o Estoque: aprovar um ajuste de contagem velha ainda pode deixar o físico de caixa negativo (−69); a trava física do `cenEntregar` vale para a entrega, não para o ajuste | Achados reproduzidos pelo revisor (sondas pB, pI, pC, pH, pH2, pA2; tela U1, U3b, U4, U6). Dano evitado: reserva de 61 caixas a mais para uma falta já reposta (A1); a outra ordem levando as caixas em uso de uma ordem em execução, que ficava sem caixa e com o pedido recusado (A2); recomendação de uma quarentena que o Estoque não libera (A3); devolução da sobra gravada duas vezes por uma aba velha, com físico e custódia divergentes (A8); lote devolvido pelo cliente invendável para sempre (A5); saída sem avaliação de origem num ciclo (A6); texto que contradiz a fase (A7). Evidência (executado, sintético; números e commits por achado em `docs/integracao/BEN3/README.md`): no `15e2976` com os testes novos, `ben_unit_test` FALHOU 200/206 (U52a2, U52c, U58a, U58b, U59 e U60), `comercial_unit_test` FALHOU 116/118 (C06l, C06m), `ben_prop_test` FALHOU (I-f6, I-a3, I-f1 e os casos fixos U53h-j), `ben_fluxo_test sobra` FALHOU 14/16 (passo 6, A8: `[591, [139, 139]]`) e `conferencia` FALHOU 12/14 (passo 5, A7); depois, `ben_unit_test` OK 206/206, `comercial_unit_test` OK 118/118, `ben_prop_test` OK (360 × 35, 10 casos fixos; novos I-f5, I-a5, I-f6 e o I-a3 da devolução bloqueada), `ben_mutantes` OK 104/104 (M103 a M107 novos); as sondas do revisor no código corrigido sem violação, salvo o `pE` (A4); a propriedade estendida do revisor (`propX`) sem X1, X3 nem I-f1 (restam X2, I-e4 e I-e3, todas com ajuste aprovado na trilha: A4) | Voltar cada correção ao `15e2976` (não recomendado: volta o defeito correspondente); tirar `cxRepos`, `quarUso`/`benAposLaudo`/`benAposReprovar`, o desconto de `quarRep`, a revalidação `_estDevVi`, a genealogia na devolução do cliente, a marcação de caminho do `comOrigens` e os textos pela fase |
