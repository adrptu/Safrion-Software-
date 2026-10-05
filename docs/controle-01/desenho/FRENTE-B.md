# FRENTE-B · Início com entrega parcial: uma regra para a web e para o app (cenIniFalta), corrigida pelo cético

Severidade: S2

Dano: Defeito executado no HEAD 884620c: o app abre o turno de uma O.S. com a mistura incompleta. A OS-0430 tinha só o Glifosato entregue e foi para Em execução; um turno de 10 ha fechou com Glifosato 20 L, 2,4-D 0 e Óleo 0, sem nenhuma conferência. A web recusa o mesmo início, então os dois canais divergem sobre o mesmo fato. O resultado técnico da lavoura fica comprometido: uma dessecação sem os parceiros da calda leva a reaplicação e custo. Esta correção fecha o início, na web e no app. Não fecha o registro: com o material na mão do operador, um turno informado só com Glifosato continua gravado sem alerta (executado, ctl/b_cet/c3.js, nas três árvores). Isso fica para a tarefa separada R8 (fechamento do turno, RN-018 e AC-21).

PRD: - **Base da regra:** PRD 42.2 l.7067 (a entrega parcial só libera o trecho que executa a instrução por inteiro; mistura incompleta não pode ser aplicada; o que falta fica pendente com responsável e próxima ação), ESTOS-03 l.7103, 41.3 l.6864 (preparo e início validam carga e recebimento) e 41.3 l.6866 (mudar a mistura invalida a aprovação).
- **Entrega e excesso:** SU-07 l.1251 (entrega parcial) e l.1253 (excesso exige revisão).
- **Início e fato ocorrido:** CMD-07 l.2778 (o início exige condições; o fato ocorrido continua registrável), RN-018 l.220 e AC-21 l.4781 (registrar dose ou área efetiva não conforme exige revisão; vão para a R8).
- **Exceções e turnos:** DEC-2609-10 (água sem produto). DEMO-13 l.4734 diz que os turnos seguintes mantêm a ordem iniciada; por isso a regra vale para cada turno pela 42.2, e não pelo CMD-07.
- **Severidade:** PRD 22.1 **l.5189** (a l.5190 citada antes está vazia) e AGENTS §3.

Arquivos: tools/prototipo/v37/gen37/cenario.js, tools/prototipo/v37/gen37/areas/processo_os.py, tools/prototipo/v37/gen37/areas/mobile.py, tools/prototipo/v37/gen37/inicio_entrega_test.py (novo), tools/prototipo/v37/gen37/inicio_entrega_unit.js (novo), tools/prototipo/v37/gen37/app_entrega_parcial_test.py (novo, especificado), tools/prototipo/v37/gen37/consumo_divergente_test.py, tools/prototipo/v37/gen37/est_fix2_test.py, tools/prototipo/v37/gen37/est_repro.py, tools/prototipo/v37/gen37/os_cenario_test.py (+1 verificação, especificada), scratchpad/ctl/b/patch.py, scratchpad/ctl/b_cet/patch2.py, scratchpad/ctl/b_cet/mk2.py, scratchpad/ctl/b_cet/novos/inicio_entrega_test.py, scratchpad/ctl/b_cet/novos/inicio_entrega_unit.js, scratchpad/ctl/b/novos/app_entrega_parcial_test.py, scratchpad/ctl/b_cet/c1.js, scratchpad/ctl/b_cet/c2.js, scratchpad/ctl/b_cet/c3.js, scratchpad/ctl/b_cet/c4.js, scratchpad/ctl/b_cet/r/repro.js, scratchpad/ctl/b_cet/r/replay_cd.js, scratchpad/ctl/b_cet/r/replay_est.js, scratchpad/ctl/b_cet/r/replay_rest.js, scratchpad/ctl/b_cet/r/diff_seed.js, scratchpad/ctl/b_cet/v37q/gen37

# FRENTE B: início com entrega parcial (desenho corrigido)

**Estado:** a correção foi especificada e depois executada numa cópia, em `scratchpad/ctl/b_cet/v37q`: primeiro `ctl/b/patch.py`, depois `ctl/b_cet/patch2.py`. Rodei com node e python, sem navegador. O repositório continua intacto no HEAD 884620c (`claude/v44-tabelas-05`); conferi com `git status` e `find -newer`.

**Severidade: S2.** Considerei S1 e recusei: a O.S. foi aprovada e liberada, e o defeito é executar só parte da mistura, sem nova versão. Isso é resultado técnico material incorreto, ou seja, o "caso contrário" da regra de aprovação no AGENTS §3.

## 1. Problema reproduzido (executado)
O comando foi `SIMDIR=r/base node r/repro.js`, depois o mesmo com `r/pat` (que é a v37q). No HEAD:
- **web iniciar:** "Iniciar bloqueado: REQ-041 sem entrega · 2,4-D 806 160 L, Óleo mineral 80 L a entregar."
- **app:** o passo é `iniciar` e o turno abre; a ordem vai para Em execução.
- **apontamento:** 10 ha gravados com `{"Glifosato 480":20,"2,4-D 806":0,"Óleo mineral":0}` e 0 conferências.

Com a correção, o app recusa com o mesmo texto da web, mais o dono. A ordem continua em Liberadas e nada é gravado.

**Causa:**
- `cenario.js:128-135` (`cenIniciarTurno`) não confere o material;
- `mobile.py:200` (`mbPasso`) só pede retirada quando nenhum item tem custódia;
- a web confere em `processo_os.py:344-351`.

**Furos extras (executados):**
- **N4:** no turno seguinte de uma entrega fracionada, com custódia 0/0/0, o app abre o turno.
- **N5:** com o componente esgotado (175 solicitados, 175 consumidos, custódia 0, 60 ha de saldo), o cartão manda retirar, mas Rui recebe "Acima do saldo a entregar: 0 L." (`cenario.js:74`).

**O que esta frente não fecha (executado, `c3.js`):** com tudo entregue e confirmado, fechar 10 ha informando 2,4-D 0 e Óleo 0 grava do mesmo jeito, sem conferência, no HEAD, no desenho original e no corrigido. Isso é defeito do fechamento → R8.

## 2. Regra nova (numerada e testável)
- **R1. Início exige todos os componentes com o executor.**
  - **Vale para:** o início da O.S. (CMD-07, web) e cada turno no app (PRD 42.2).
  - **Componentes:** os itens da requisição cujo produto está em `o.ins`.
  - **Condição:** custódia > 0 em cada componente e recebimento confirmado.
  - **Dano evitado pela custódia:** mistura incompleta aplicada.
  - **Dano evitado pela confirmação:** material em custódia sem que o operador ateste lote e embalagem (41.3 l.6864).
  - **Limite:** a confirmação conferida é a da 1ª entrega de cada item. Ver R7.
- **R2. Entrega fracionada vale.** Basta algo de cada componente (l.1251).
  - **Limite (executado, `c2.js §2`):** com 1 L de Óleo para 160 ha, o turno inicia e, se o operador informar 1 L, grava sem alerta.
  - Conferir a cobertura (custódia ÷ dose) seria uma fórmula nova no serviço único (ENG-011); vai para a R8.
  - Não é por "falta de dado de carga": a tela OS-0424-app tem cargas estáticas (`os_campo.py:23-29`); o cenário é que não tem.
- **R3. Quem resolve, em ordem de prioridade:**
  - (a) sem custódia e com saldo a entregar → "Rui (almoxarife) entrega no Estoque; <resp> confirma o recebimento no app.";
  - (b) sem custódia e com tudo já consumido → "Ana (agrônoma) decide a área restante: Dispensar saldo na O.S. e, se ainda precisar aplicar, emitir nova ordem." "Rever a quantidade" saiu do texto porque não existe em execução: `osc_ajustar` só aceita A liberar (`processo_os.py:320`);
  - (c) entregue e não confirmado → "<quem> confirma o recebimento no app.".
- **R4. Uma função, `cenIniFalta(o, r)` em `cenario.js`, para:**
  - web: `osIniErro`, que atende `osc_iniciar`, o painel e o Mapa;
  - selo da web e impedimento no painel para o caso (b);
  - comando do app: `cenIniciarTurno`, chamado por `mbIniciar`;
  - cartão do app: `mbPasso`.

  A recusa é atômica. Há uma exceção conhecida: a tela OS-0424-app mantém a própria cópia (R9).
- **R4b. O selo e o impedimento do caso (b) na web só aparecem com área a fazer.** A condição é `saldo − hectares no aparelho > 0`, calculada sobre a requisição vista pelo servidor (`osReqVis`, já calculada em `osMerge`). Sem isso, toda ordem concluída com consumo exato ganhava "Insumo esgotado" e dona Ana (SINT-C03 zera a custódia).
- **R5. Exceções:**
  - ordem sem insumo e água sem produto (DEC-2609-10) não têm requisição, então a regra não se aplica;
  - fertirrigação tem requisição e passa pela regra;
  - item opcional não existe no PRD (grep sem ocorrência);
  - o fato ocorrido continua registrável por ocorrência: `cenOcorrencia` (`cenario.js:229`) e MB-04.
- **R6 (residual).** Um componente fora da requisição não é visto pela regra.
  - Casos: OS-0421 (Adjuvante; `processo_os.py:135` × `dados2.py:718`) e OS-0420 (MAP).
  - Corrigir exige mudar o seed, e o `consumo_divergente_test` §5 usa justamente o Adjuvante fora da REQ-035.
- **R7 (residual, executado `c2.js §1`).** `cenEntregar` (`cenario.js:76`) não zera `confirmado`. Por isso a 2ª entrega herda a confirmação da 1ª, e `cenConfirmarRecebimento` devolve "Nada entregue para confirmar.".
- **R8 (tarefa separada).** Fechamento com dose efetiva abaixo da aprovada (informado bem abaixo de dose × área): fato preservado, revisão exigida (RN-018, AC-21). Severidade a classificar.
- **R9 (residual).** A tela OS-0424-app (`os_campo.py:83`) repete a regra com a exceção `consumido>0`. A tela não grava início nem apontamento: só confirma o recebimento e guarda o estado da própria tela.

## 3. Mudança de código (executada na cópia; diff real contra o HEAD)
**`cenario.js` (+15):**
- `cenIniFalta` entra antes da l.128, como no desenho original, com o texto novo do caso (b) e o comentário do limite R7;
- `cenIniciarTurno` ganha, depois da l.131: `{ const f = cenIniFalta(o, o.req && c.reqs[o.req]); if (f) throw new Error('Iniciar bloqueado: ' + f.t + ' ' + f.q); }`.

**`areas/processo_os.py` (+8 −9):**
- `osIniErro` (l.344-351) passa a formatar `cenIniFalta`, com os mesmos textos e atalhos;
- `osMerge`, no bloco Em execução (l.237-238):
```js
+    const fz=((co.saldo||0)-osApPend(co)>0.001)&&cenIniFalta(co,r);   // r = osReqVis(...), já calculado no início de osMerge
+    if(fz&&fz.k==='rever'){ o.selos=o.selos.concat([{t:'Insumo esgotado · '+fz.its.map(i=>i.prod).join(', '),c:'red'}]); o.dono='Ana (agrônoma)'; o.prazo='decidir a área restante';
+      o.esg={acao:'apontar',t:'Apontar bloqueado: '+fz.t,q:fz.q}; } }
```
- `osProx`, depois da l.418: `if(!b&&P.fn==='apontar'&&o.esg) b=o.esg;`. Assim o primário "Registrar apontamento", que sempre falharia (`osc_apontar` recusa consumo acima de custódia 0), dá lugar ao impedimento, e "Dispensar saldo" continua no painel (`canDisp`, l.631).

**`areas/mobile.py` (+4 −2):**
- em `mbPasso`, l.200, o caso `rever` mostra o selo vermelho "Insumo esgotado · Ana (agrônoma)";
- o caso `entregar` mostra "Entrega parcial" ou "Reservado";
- em `d_falta`, l.422-424, entra `rever:'decisão de Ana (agrônoma) sobre a área restante'`.

**Alternativa recusada:** pôr a trava só em `mbIniciar`, como a carência em `mobile.py:982`. O comando ficaria sem a regra, contra o princípio de que o servidor é a autoridade.

## 4. Textos de tela
- **Entrega parcial:**
  - **app:** "Entrega parcial · REQ-041", com "Retirar no almoxarifado" (que leva a `MB-05.dc.html#OS-0430`) e os itens "com você 320 L · retirar 160 L · retirar 80 L"; em FALTA, "retirar os insumos com Rui";
  - **recusa:** "Iniciar bloqueado: REQ-041 sem entrega · 2,4-D 806 160 L, Óleo mineral 80 L a entregar. Rui (almoxarife) entrega no Estoque; Marcos confirma o recebimento no app.";
  - **web:** inalterada.
- **Caso (b):**
  - **app:** selo "Insumo esgotado · Ana (agrônoma)", com o texto "Fungicida A: todo o solicitado na REQ-035 já foi consumido e nada está com Marcos. Ana (agrônoma) decide a área restante: Dispensar saldo na O.S. e, se ainda precisar aplicar, emitir nova ordem.";
  - **web:** selo vermelho "Insumo esgotado · Fungicida A", com Quem resolve "Ana (agrônoma) · decidir a área restante";
  - **painel e Mapa:** "Apontar bloqueado: Fungicida A: …", com "Quem resolve: Ana (agrônoma) …" no lugar do primário.
- **O selo não conta como "impedida":** o cabeçalho só conta `/impedida|falta máquina|falta insumo/` (`processo_os.py:684`), e o Mapa só `/^(Impedida|Falta máquina)/` (`inicio.py:1033`).

## 5. Testes
**Unitário, executado:** `inicio_entrega_test.py` (17 linhas) e `inicio_entrega_unit.js` (92 linhas), em `ctl/b_cet/novos/`.

| Árvore | Resultado |
|---|---|
| HEAD | 11/25 |
| Desenho original | 21/25 (falham N5 app e N5 web pelo texto, e **P5 e P6 por regressão**) |
| Corrigido | **25/25** |

Casos:
- **N1–N5** como no desenho, com o texto novo do caso (b). O N5 da web confere também o impedimento do painel.
- **N4b** não chama mais `conf()`, que falhava em silêncio. O caso passa a documentar o limite R7.
- **P5 (novo):** entrega completa, 160 ha → sem "Insumo esgotado", sem Ana, primário "Enviar para conferência".
- **P6 (novo):** o último turno fica no aparelho → só "Aguardando sinal do app".
- **P1–P4** como no desenho.

**Também executados na árvore corrigida:**
- `carencia_test.py unit`: 50/50;
- `quantidade_test.py`: 14/14;
- `replay_rest.js`: 0 testes com diferença;
- `diff_seed.js`: 7 diferenças, as mesmas do desenho (OS-0420 cartão, comando e web, que só aparece em Liberadas; comandos de OS-0424, OS-0425 e OS-0503; OS-0508 em conferência, sem efeito na tela);
- `c4.js`: OS com o registro real (OSD).

**Navegador, especificado e não rodado:**
- `ctl/b/novos/app_entrega_parcial_test.py`, sem mudança (43 linhas);
- `os_cenario_test.py` §6 ganha `and 'Insumo esgotado' not in T.linha(OS)`. No desenho original essa linha mostraria "Insumo esgotado · 2,4-D 806, Óleo mineral" com Ana (`c4.js`).

## 6. Testes existentes que mudam de expectativa
- **`consumo_divergente_test.py`, l.101, l.114 e l.138.**
  - Passam a usar um turno aberto antes, como `app_saldo_zero_test.py:42`, e ganham a recusa "Iniciar bloqueado: REQ-035 sem entrega · Fungicida A 14 L a entregar. …".
  - O replay (`r/replay_cd.js`) deu as expectativas iguais ao HEAD: r0 `[524,45,20,"CC-304",…]`, r1 `[519,40,0,25,25,40]` e o recibo "…3 L relatados, nada em custódia".
  - Não dá para trocar a injeção por "Rui entrega 14 L": `cenEntregar` desconta a reserva de outra requisição (`cenario.js:76`).
- **`est_fix2_test.py` l.55 e `est_repro.py` l.43:** acrescentar `cenConfirmarRecebimento(c,'{RQ}');`. O replay deu consumo de 10/5/2,5 L e fila 1, iguais ao HEAD. Aparece um movimento a mais de recebimento, que só pesa na contagem da §3 (já feita antes).
- **`os_cenario_test.py` §6:** +1 verificação (§5).
- **Sem mudança, pelo replay:** `os_v39_bloq`, `tabelas_est`, `est_cenario`, `app_cenario`, `app_saldo_zero`, `app_mb02det`, `app_mb03x`, `app_mb03_turno`, `app_restaurar`, `mbtest`, `ostela`, `app_os0424_test` (a tela OS-0424-app não muda, ver R9) e `carencia_app_unit` A3 (OS-P sem insumo).

## 7. Riscos de regressão
1. Os estados de teste com `cenIniciarTurno` e custódia 0 são só os três do §6.
2. **Seed:** o cartão de OS-0420 (do Carlos) passa a "Entrega parcial"; os comandos de OS-0424, OS-0425 e OS-0503 agora recusam.
3. **Web:** o selo do caso (b) só aparece com área a fazer e com a custódia do servidor (P5 e P6). Nenhuma ordem do seed cai nesse caso (`r/t_merge.js`).
4. **Software real:** o pacote offline precisa trazer a entrega e a confirmação.
5. **Residuais:** R6 a R9, cada um como tarefa separada. A R8 é a que carrega o resto do dano declarado.

## 8. Tamanho
- **Produto:** +27 −11 (`cenario.js` +15, `processo_os.py` +8 −9, `mobile.py` +4 −2).
- **Testes novos:** 152 linhas (17 + 92 + 43).
- **Testes ajustados:** cerca de 8 linhas.

## Evidência (`scratchpad/ctl/b_cet/`)
- **Patch:** `patch2.py`, aplicado depois de `ctl/b/patch.py`.
- **Montagem:** `mk2.py` (bundle com o OSD real).
- **Contraexemplos:** `c1.js` (regressão no caminho feliz), `c2.js` (confirmação pegajosa, custódia mínima, sem sinal), `c3.js` (registro sem alerta com o material na mão), `c4.js` (`os_cenario` §6 e painel do N5).
- **Testes:** `novos/`.
- **Replays:** `r/` (`repro`, `diff_seed`, `replay_*`, `t_merge`).
- **Árvore:** `v37q`.

## Contestações: aceitas · recusadas (com motivo)
**Aceitas (incorporadas):**
1. **Regressão no caminho feliz (executado).**
   - **O que acontecia:** o selo "Insumo esgotado" e a dona Ana apareciam em toda ordem concluída com consumo exato. A OS-0430 depois de 160 ha mostrava "Quem resolve: Ana · decidir o saldo" junto do passo "Enviar para conferência".
   - **Correção:** R4b.
2. **Sem sinal (executado).** Um turno no aparelho que consumia tudo punha "Insumo esgotado" e Ana na web ao lado de "Aguardando sinal". **Correção:** usar `osReqVis` e descontar a área que está no aparelho.
3. **Texto que prometia ação inexistente.** "Rever a quantidade" não existe em execução (`processo_os.py:320`). **Correção:** "Dispensar saldo" e nova ordem.
4. **Primário condenado no painel.** "Registrar apontamento" sempre falharia no caso (b). **Correção:** impedimento no painel (`o.esg`), com "Dispensar saldo" visível.
5. **O dano declarado era maior que o corrigido.** Com material na mão, ou com custódia mínima, o turno informado grava sem alerta (`c2.js`, `c3.js`). Dano e escopo foram reescritos, e o resto virou a R8.
6. **R1 dizia "confirmado", mas a 2ª entrega herda a confirmação da 1ª.** O N4b passava por isso, com `conf()` falhando calado. Texto corrigido e residual R7.
7. **"Todos os canais" era falso.** A OS-0424-app (`os_campo.py:83`) tem cópia própria. Fica como R9.
8. **Citações corrigidas:** PRD 22.1 l.5189; `osc_ajustar` em `processo_os.py:320`; item fora da requisição em `cenario.js:71`; desconto da reserva em `cenario.js:76`; injeção em `app_saldo_zero_test.py:42`. "Sem dado de carga" era impreciso (`os_campo.py:23-29`).
9. **O risco 3 estava errado:** o selo não entra na contagem de "impedidas" (`processo_os.py:684`; `inicio.py:1033`).
10. **Os replays só comparavam o estado, não a visão da web.** Foi isso que deixou a contestação 1 passar. Ganharam P5, P6 e a linha no `os_cenario_test` §6.

**Recusadas:**
- **S1:** a ordem foi aprovada e liberada; o defeito é divergir da instrução (S2, AGENTS §3).
- **Quantidade mínima ou cobertura por turno nesta frente:** seria fórmula nova (ENG-011), e o dano restante está no fechamento (R8).
- **Zerar `confirmado` a cada entrega agora:** muda o Estoque e telas que não rodo sem navegador; o dano não é mistura incompleta (R7).
- **Cobrir componente fora da requisição:** exige mudar o seed, e o `consumo_divergente` §5 depende disso (R6).
- **Pôr OS-0424-app na regra agora:** testei e reverti. Depois de consumo ou com a ordem concluída, a tela volta a "Reservado · retire com Rui" e "Nada entregue ainda", textos errados. Precisa de textos próprios (R9).
- **"A trava fere RN-018":** o CMD-07 permite exigir condições no início, e o fato segue registrável por `cenOcorrencia`. O registro estruturado de dose ou área não conforme (AC-21) vai para a R8.
- **Entregar 14 L em vez de injetar o turno no `consumo_divergente`:** consumiria a reserva da REQ-039 (`cenario.js:76`) e mudaria a §7.
- **Unificar o passo "confirmar" do cartão (`mobile.py:192`) com a regra:** é a ação do próprio operador antes da retirada; a recusa do comando já usa o texto único.