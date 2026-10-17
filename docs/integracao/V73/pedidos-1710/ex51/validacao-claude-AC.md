# EX-51 · Validação independente do Claude · cadeias A e C

- **Autor:** Claude, validação independente (a do Codex é separada). Data: 17/10/2026.
- **Base:**
  - fontes em `tools/prototipo/v37/gen37/` da árvore `ex51` (b2912bf8);
  - páginas montadas da composição em `int90` (c709db66), só leitura. As fontes das duas árvores são iguais; só a pasta `_probe` muda.
- **Método (executado):** leitura estática das fontes e dos renders, com `grep` e `sed`.
- **Não executado:**
  - navegador;
  - robô v5;
  - recálculo dos valores em R$ da A-11.

  Os percentuais do robô vêm do anexo e não foram medidos de novo.
- **Linhas citadas:** de `gen37/`, salvo indicação. `PRD.md` é o do repositório principal.

## Quebras

| ID | Prior. | Veredito | Evidência atual | Melhoria | Fatia | Autor |
|---|---|---|---|---|---|---|
| A-1 | alta | Confirmada | `safra.js:1579-1583` (proxSaf) termina em "Continuar: dimensionar operações e recursos". SAF não tem nenhum link para `OS.dc.html`. `processo_os.py:1402` (`nv_open`) zera saf/cult/atv/jan. "Preparar O.S. do período" só existe no PL-04, como mensagem (`planejamento.py:438`). | Reaproveitar o `#nova:cult:atv:data` que a OS já aceita (`processo_os.py:1174`, usado pelo COLH): cada operação da etapa 3 do SAF ganha "Emitir O.S. ›" preenchido. "Emitir O.S. do período" no cabeçalho da OS = prévia do PL-04 + emissão CMD-41 em lote, todas em A liberar, com idempotência por cultivo+atividade+versão do plano; nunca aprova. "Criar ordem" herda o escopo pela R5. | F5 (emissão, migração do PL-04) + F2 (herdar filtro) | Codex (comando e prévia); Claude (ação no cabeçalho) |
| A-4 | alta | Confirmada; proposta corrigida | `inicio.py:1667` "O.S. não entra aqui"; `:1687` assert proíbe O.S. no IN-02, contra `PRD.md:2865` e `:179` (revisão da O.S. no IN-02, inclusive mecânica). APROV fixa com "Aprovar selecionados" (`:1686`); IN-01 com fila fixa (`:1712-1717`). Card A liberar do PAGR sem link (`paineis.py:18`; render sem `<a>`). Duas definições de "A liberar": o Mapa conta a lista fixa `_ORD_MAPA` com `'lib'` (`inicio.py:141,146,891`; `dados_lagoa_safra.py:191-194`, sem a OS-0431); o PAGR conta a etapa. | IN-02 lista toda O.S. agrícola que aguarda CMD-42, não só "com produto": inclui a mecânica (ex.: OS-0511); ficam fora água só com água, manutenção e beneficiamento. A linha abre `OS.dc.html#painel=<fila>` (recorte que já existe); a decisão fica no painel da O.S., onde estão a regra legal e a trava; "aprovou → próxima" no mesmo recorte. Aprovada e não liberada vira pendência "Liberar" para quem tem AL-01. Trocar o assert por "O.S. nunca entra no lote". Contagem de um seletor único (R8). | F3 | Codex (seletor, IN-02); Claude (atalho e contador no cabeçalho do Mapa) |
| A-5 | alta | Confirmada (solução única com C-1) | `processo_os.py:300` `o.dono='Suprimentos'`; `:694` só "Ver saldos no Estoque" (EST sem hash). Render OS com 0 links para CMP. `processo_compras.py:459` `cal01Memo(...).map(t=>({t}))`: a OS-0418 é texto na demanda. A CMP só aceita `#sol=&saf=` e `#tipo=&sc=` (`:620`, `:760`). | Mesma solução da C-1. Na demanda da CMP, a origem OS-… vira referência (R2). Da O.S. para a compra: `CMP.dc.html#sol=…&item=…` (acrescentar `item=` ao `abrirHash`). | F3 (+F1) | Codex |
| A-7 | alta | Confirmada | `alocacao.py:78-88` (`alTrocar`) grava `co.rec`/`recHist` sem tocar `bloq`; `processo_os.py:254` só troca o nome no conjunto. `:314-317` (`osManCond`) lê a condição do `bloq.aid` fixo (`:149`, OS-0431 → a01): trocado o T1, o impedimento fica. | Derivar o impedimento da alocação vigente (`alDaOrdem` × `AL0.ativo` × `c.man`), não do aid fixo; uma correção para A-7 e D-1. A troca por ativo apto, que `alCandidatos` já garante, tira o impedimento e grava na trilha. A O.S. volta para aprovação/liberação individual; não libera sozinha. Primária para PCP: "Trocar máquina"; "Acompanhar OM-0233" vira secundária. | F5 (junto com D-1) | Codex |
| A-8 | alta | Confirmada (solução única com C-6 e A-9) | `processo_os.py:374`, `:573`, `:694` levam a `EST.dc.html` sem registro. EST aceita `#dev=` só para a caixa do BEN (`processo_estoque.py:656-659`), e a volta só vai ao BEN (`:663`, `EST_BEN_H`). A OS lê `#OS-…` mas não grava o painel aberto no endereço (`processo_os.py:1164-1183`). | EST aceita `#ent=REQ` (Entregas, linha aberta), `#dev=REQ&prod=` (generalizar `estDevHash`) e `#lote=`. A volta fica no motor (R4). A OS grava `#OS-…` ao abrir o painel, como MA (`ma_hashSync`) e AG-01 (`agSetHash`) já fazem; isso já dá o Voltar do navegador. | F1 | Claude (registro de referências e volta); Codex (hashes do EST) |
| A-10 | alta | Confirmada | `g2lib.js:133`: dica "Encerradas: realizado, consumo e custo gravados". `processo_os.py:687`: "somente consulta". `cusOrdem` (`areas/custo_dominio.py:16`) entra só nos renders IN-04 e PAGR; na OS, 0 ocorrências. | Incluir `custo_dominio.js_prefixo` na OS. Seção "Custo realizado" (insumos + operação, provisório/conferido, R$/ha × previsto) pelo mesmo `cusOrdem` do Mapa e do Painel (R8). Até lá, corrigir a dica. "Ver lançamentos" só depois da A-11. | F4 (elo Custo) | Codex (seletor); Claude (seção no painel) |
| A-11 | alta | Confirmada (valores não recalculados) | GE-03 sem `cenGet`/`cusOrdem` (render: 0); a grade ainda tem REQ-037 · OS-0420. | GE-03 gerado dos movimentos de consumo e apontamentos do cenário, com `cusOrdem` por O.S.; tirar REQ-037/OS-0409 semeados. Uma solução para A-11, A-12 e C-18. | F5 | Codex |
| A-15 | alta | Parcial | **Resolvido:** fila real no CA-02 (`campo_conferencia_ui.js`, `caFila` sobre todas as O.S., AL-12). Encerrar exige conferência (`processo_os.py:612`; `conferencia_diaria.js:44-50`, `cdPendente`). **Falta:** CA-02 só por link (`ui37.py:92`); OS sem filtro "A conferir"; Meu dia ainda manda ao CA-02 (`inicio.py:1717`); nenhuma pendência chega à Paula. | Filtro "A conferir" na OS lendo o mesmo `caFila` (sem segunda fila); depois o CA-02 sai (EX-50). Pendência "Conferir dia N" para AL-12, derivada do apontamento Provisório (R7). | F3 | Codex |
| A-2 | média | Confirmada | `processo_safra.py:340` "Crie um em Planos agronômicos." sem link; `safra.js:2014` `sg_hasPA=false`, `sg_ph='#'`. O PA só volta ao SAF com `c.ver<p.versao` (`processo_planos.py:462`). | Usar o `#plano=` que o PA já aceita (`processo_planos.py:127`, `155`) pela R2. Ao publicar, estender a mesma linha do `paSitCult` aos cultivos sem plano da cultura. | F1 | Codex |
| A-3 | média | Confirmada | IN-02 "Orçamento revisado" leva a `GE-02det.dc.html` (`inicio.py:1671`). `plano_referencia.js:180` só diz "Orçamento a revisar"; `safra.js:939` não registra aprovação de orçamento. | Selo na safra com link à versão (R2) e IN-02 abrindo a versão a decidir. "Autorizar execução" como trava muda regra de dinheiro: até decisão registrada, só aviso (AGENTS §4, nomear o dano). | F5 | Codex |
| A-6 | média | Confirmada (solução única com C-5) | `cenario.js:374-383` (`cenReceber0`) responde sem citar a O.S.; IN-01 e IN-02 fixos. | Mesma solução da C-5. | F3 | Codex |
| A-9 | média | Confirmada | `processo_estoque.py:524`, `549`, `565`, `578`, `620`, `636`: `{k:'link',t:x.os,h:'OS.dc.html'}` sem o ID. | Sai com a R2: o componente monta `OS.dc.html#OS-…`. Não corrigir grade a grade. | F1 | Claude (componente); Codex (adoção nas grades) |
| A-12 | média | Confirmada | Render GE-03: links para SU-07 (6), CA-02 (4), SU-06 (2), CA-01 (2) e LO-04 (2), telas que saem no EX-50. | Com a A-11, a origem passa pela R2: `EST#ent=`, `OS#OS-`, `EST#nf=`, `EXPED#RM-`. | F5 | Codex |
| A-13 | média | Confirmada | `gestao.py:40` `OS_ORC='OS-0409'` fixo; GE-02det não lê o endereço. Camada Custos do Mapa abre o SAF (`inicio.py:1127`). | Só depois de A-11 e A-14: GE-02det por recorte (`#os=`, `#cult=`) com o mesmo custo. | F5 | Codex |
| A-14 | média | Confirmada | `custo_dominio.py:67-77` (`dados()`): uma cultura por talhão e safra (assert); P1 = Soja. A OS-0417 tem origem "Feijão P1" (`processo_os.py:107`). | Custo por cultivo, não por talhão: a O.S. guarda o cultivo na emissão (o `#nova:` já o leva) e o `custo_dominio` agrupa por ele. Corrigir o registro da OS-0417. | F5 | Codex |
| A-16 | média | Confirmada | `processo_os.py:150`: bloqueio da OS-0420 com `h` para o CA-01x. `dados.py:108`: detalhe CA-01det; o render da OS mantém os dois links. Meu dia leva a PL-05 e CA-02 (`inicio.py:1712`, `1717`). | Tirar `h`/`hl` do bloqueio: `osManCond` gera "Acompanhar OM-0233" para `MA#om=`. Detalhe vazio: abre `OS#OS-0421`. Meu dia lê as pendências (R7). | F5 (links do EX-50) | Codex |
| A-17 | média | Confirmada (solução única com C-11) | `mobile.py:763-771`: cartões fixos REQ-031 e REQ-038 com `say()`. | Mesma solução da C-11. | F3 | Codex |
| A-19 | média | Confirmada | `processo_os.py:1393` `pan_orig=o.orig.map(t=>({t}))`: a Origem é só texto. | `o.orig` vira lista de referências pela R2: cultivo, plano, REQ, REC/RA e VIS. A mesma mudança atende a B-2. | F1 | Claude (componente); Codex (dados da origem) |
| A-18 | baixa | Confirmada | `processo_os.py:856` `pan_fichas=o.id==='OS-0424'`. | Pelo EX-50: o OS-0424-app vira a ficha de toda O.S. com calda, com impressão; volta pela R4. | F5 | Codex |
| C-1 | alta | Confirmada; proposta ajustada | `processo_os.py:300` e `:694`. `g2lib.js:723`: `G2_PAPEIS` sem papel de compras. `manSolicitar`/`cmmDaOm` existem (`dados_manutencao.py:672`, `dados_compras_mat.py:142`), mas a fila é de materiais e recusa safra ou cultura (`dados_compras_mat.py:152`). | **Não abrir SC paralela para insumo:** a demanda da O.S. já entra uma vez na SOL (DEM-04); outra SC duplicaria a compra. **Comando de domínio "Pedir compra do item":** cenário, `cenIdem` com chave O.S.+item+versão. Marca a origem e o "precisa até" na linha da SOL existente; sem SOL (Safra Mamão), cria o complemento pelo mesmo caminho do Planejar safra. **Quantidade:** falta líquida do cal01. **Dono:** pela alçada (`g2alcQuem`), nunca "Suprimentos". **Selo da O.S.:** mostra a SOL e o estado. | F3 | Codex |
| C-2 | alta | Confirmada | `dados_lagoa_safra.py:176`: texto semeado "pedido de 50.000 kg em 30/09". Na base da demanda (renders CMP e SAF), esse recebimento previsto tem `ref: null`. A O.S. não lê a cobertura. | Linha do insumo da O.S. lida da mesma demanda: tem · chega DD/MM (PC) · falta. Vermelho se a chegada passa da janela. A ação vai a quem decide: agrônomo ajusta ou troca; compras antecipa. Dar ID de pedido ao calcário e tirar o texto semeado. | F3 (+F4) | Codex |
| C-3 | alta | Confirmada | Pedidos da CMP ficam na chave própria de compras (`processo_compras.py:257`), lida só por CMP e SAF. O EST lê `E2.pedidos` fixo (`processo_estoque.py:244`); render EST: 0 ocorrências da chave de compras. | Mover SOL e PC para o cenário: uma persistência, `cenMudar` estrito, emissão com `cenIdem`. O EST lista os PC abertos no recebimento. Pré-requisito de C-4, C-5, C-14 e da jornada OS-0502: primeiro item da F3. | F3 | Codex |
| C-4 | alta | Confirmada | `processo_compras.py:431-432`: `rec:0,quar:0` nos pedidos novos; os antigos são fixos. O motor de demanda já calcula o recebido por PC a partir de `recebimento-nf` (`cenario.js:223`). | Extrair esse cálculo para um seletor único (recebido, apto, quarentena por PC) e usá-lo na etapa 6, sem segunda conta. | F3 | Codex |
| C-5 | alta | Confirmada; pré-reserva restrita | `cenario.js:374-383`: receber só soma físico. A D5 reserva para a OM porque a SC leva a OM de origem (`dados_manutencao.py:678-682`). | Reservar só o que chega de pedido com origem na O.S. (vínculo da C-1), espelhando a D5. Sem vínculo, não reserva; a pendência "OS-… pode ser liberada" vai a quem aprova. Estender a D5 a insumo exige registro: decisão técnica dos agentes, ou proprietário se mudar a prioridade entre O.S. | F3 | Codex |
| C-6 | alta | Confirmada | As mesmas linhas da A-8 e da A-9. | Solução única com A-8 e A-9: R2, R4 e hashes do EST. | F1 | Claude (motor); Codex (hashes do EST) |
| C-8 | alta | Confirmada | `paineis.py:29-34`: o PSUP conta só lotes e REQ; cartões sem link (render). | Reaproveitar o agrupamento "onde agir primeiro" do PAGR (`pnaOSGrupos`, `OS.dc.html#painel=`) para "O.S. aguardando insumo" por item, da mesma projeção (`agrCausa`). "Chega depois da falta" vem da demanda. Sem novo cartão de KPI (DS). | F3 | Codex |
| C-10 | alta | Confirmada; proposta reduzida | `mip.js:259`: "a liberação na O.S. aguarda a compra", sem ação. A requisição avulsa recusa safra ou cultura (`dados_compras_mat.py:152`). | Para defensivo, o AG-01 já emite receituário e O.S. numa ação; o pedido sai da O.S. pela C-1, e o aviso do MIP ganha o link. Sem fluxo avulso novo de insumo; a reposição fora do plano fica com a política de estoque (SU-02 → CD-06, EX-50). Esforço G → M. | F5 (depois da C-1) | Codex |
| C-11 | alta | Confirmada | `mobile.py:763-771`: aba Almoxarife fixa; "Conferir e entregar · bloqueado" por `say()`. A aba do operador já é viva (`mbFila`, `cenConfirmarRecebimento`). | Fila "A separar" pelo seletor da etapa Entregas do EST (`cenSaldoEntregar`). "Avisar compras" chama o comando da C-1. O bloco de devolução abre `MB-05det#REQ-…`. | F3 | Codex |
| C-12 | alta | Confirmada | `mobile.py:819-842`: MB-05det com estado local e recibo DV-0912 fixo. `estDevolver` (validade + `cenIdem`) só existe no EST (`processo_estoque.py:346`). | Levar `estDevolver` para o `cenario.js` e chamá-lo do MB-05det com a quantidade contada, sem pré-preencher, e a quarentena como condição padrão. | F3 | Codex |
| C-7 | média | Confirmada | Links para CMP sem registro: `inteligencia.py:244`, `251`; `processo_estoque.py:503` "Ver pedido"; `inicio.py:1020` "Comprar"; `paineis.py:34`. Da CMP para o EST sem NF: `processo_compras.py:435`. | CMP aceita `#pc=` e `#item=` no mesmo `abrirHash`; EST aceita `#nf=`. Os links passam pela R2. | F1 | Codex (hashes); Claude (registro de prefixos) |
| C-9 | média | Confirmada | O IC usa a primeira data de demanda bruta, gerada no build (`dados_inteligencia.py:115-118`). O SU-01 de insumo também é do build (`suprimentos.py:206-230`). | IC e "Pedir até" leem a falta líquida do cal01 com `supPedirAte` (`sup_necessidades.js:3`): uma data por item. | F5 | Codex |
| C-13 | média | Confirmada | `processo_estoque.py:84-97`: nota, conferida, apta e quarentena são digitadas; apta repete conferida − quarentena. | Apta calculada como conferida − quarentena. A conferida continua contada: não pré-preencher quantidade (AGENTS §3.3). NF-e só como demonstração até haver leitor validado (EX-50 #24). | F5 | Codex |
| C-14 | média | Confirmada | `processo_estoque.py:307`, `329`: o item diferente só é recusado. `processo_compras.py` não tem nenhuma ocorrência de "divergência". | A divergência do recebimento vira pendência derivada (R7) para compras no PC, com link `#nf=`. | F3 | Codex |
| C-15 | média | Parcial | **Melhorou:** os movimentos do lote mostram "reserva REQ → OS" (`processo_estoque.py:258`); Entregas diz "O.S. pede X, reservado Y" (`:538`). **Continua:** RS-7741 semeado na OS-0424 (`processo_os.py:97`); grade de lotes só com o número (`:484`); 64 L × 65 L sem explicação. | Tirar o RS-7741. Mostrar "64 L → 13 galões = 65 L" (`osPk` já calcula). O reservado do lote referencia as REQ pela R2. | F5 | Codex |
| C-16 | média | Confirmada | `cenario.js:158` (`cenLote`): maior disponível, sem fazenda nem validade. | `cenLote` filtra a fazenda e ordena por FEFO, numa regra só. Se só houver lote em outra fazenda, aviso; transferência quando o SU-08 migrar. Rodar a bateria de reserva. | F5 | Codex |
| C-17 | média | Confirmada | `inicio.py:1713`: "Liberar" na OS-0418 com Falta insumo. `:1715`: "Receber devolução" leva a `EST.dc.html`. | Sai com a R7: o Meu dia lê as pendências derivadas, e o verbo vem do impedimento. | F3 | Codex |
| C-18 | média | Confirmada | Render GE-03: 0 ocorrências de REQ-031; links para SU-06, SU-07 e CA-02. | Mesma solução de A-11 e A-12. | F5 | Codex |
| C-19 | média | Parcial | **Continua:** sem título em CMP e EST; GE-04 leva ao SU-05 (5 links). **Respondido pelo proprietário (17/10):** pagar no ERP; no Safrion só a situação do título e a aprovação em Aprovações. | Sem link GE-04 → CMP. Conferência pedido × nota × recebido no PC e no recebimento; situação do título lida do ERP (sandbox); aprovação no IN-02. | F5 | Codex |
| C-20 | baixa | Confirmada | `processo_compras.py`: sem "esclarec" e sem PT-0. Os esclarecimentos só existem no portal (`parceiros.py:168`, `180`). Portal mínimo decidido: o PT-02det fica. | Gravar o esclarecimento na SOL (cenário) e mostrá-lo nas etapas 3 e 4 da CMP; o PT-02det lê o mesmo registro. | F5 | Codex |

### Soluções únicas

- C-1 = A-5.
- C-5 = A-6.
- C-6 = A-8 = A-9.
- C-11 = A-17.
- A-11 = A-12 = C-18.
- A-7 = D-1.

### Ordem sugerida dentro da F3

1. C-3 (pedidos no cenário).
2. C-4.
3. C-1.
4. C-2.
5. C-5.
6. As pendências.

## Melhorias às oito regras (para A e C)

**R1 · Fio do processo**
- Derivar o fio das chaves que já existem, sem mapa escrito à mão: `o.req`, `req.itens[].lote`, `recebimento-nf` com PC, memória da demanda com a O.S., `osc.ev` (CMD-42/06), apontamentos/`conferenciaDia` e `cusOrdem`.
- A linha do tempo junta as trilhas existentes (`osc.ev`, `recHist`, `c.movs`, `conferenciaDia`, `c.recibos`), sem armazém novo de eventos.
- Elos A/C: Cultivo/Plano › O.S. › (SOL/PC se falta) › REQ › Execução › Conferência › Custo.
- Pontos de mudança:
  - `cenario.js`: novas funções `cenFio(c,id)` e `cenLinhaTempo(c,id)`;
  - `ui37.py`: faixa do fio no topo do detalhe;
  - `g2lib.js`: `aria-current`.

**R2 · Referência é link**
- Um ponto só: `g2part` (`g2lib.js:146`) ganha a parte `{k:'ref',id}` e o registro `G2_REF` (prefixo → arquivo + hash).
- Entradas que já existem: `OS#OS-`, `#painel=`, `MA#om=`, `AG-01#VIS-`, `CMP#sol=`, `EXPED#RM-` (`comHashRm`), `CARGA#CG-`, `BEN#OB-`, `VEN#PV-`, `PA#plano=`.
- Entradas novas: `EST#ent=`, `#dev=`, `#lote=`, `#nf=`; `CMP#pc=`, `#item=`.
- ID conhecido em parte de texto gera aviso no console.
- Vale também nas listas `o` do detalhe e na Origem da O.S.

**R3 · Painel empilhado**
- Reduzir o escopo. Cada tela é um HTML com handlers próprios; embutir a lógica de outra tela criaria duas implementações da mesma regra.
- O painel empilhado mostra um resumo só leitura do registro ligado, lido de `cenResumo(c,id)` no `cenario.js`, com "Abrir na tela de X" e volta (R4).
- Ações só pelas funções de domínio compartilhadas.
- Pontos de mudança: `g2lib.js` (abrir/fechar, Esc, foco), `ui37.py` (`aside`) e `cenario.js`.

**R4 · Endereço do registro e volta**
- (a) Gravar o registro aberto no endereço com `replaceState`. Generalizar `ma_hashSync` (`maquinas.py:96`), `agSetHash` (`agronomia.py:610`), `paHashSet` (`processo_planos.py:127`) e `hashSync` (`processo_compras.py:328`) num `g2hashReg` do motor. A OS é a maior falta: lê `#OS-…` mas não grava; corrigido isso, o Voltar do navegador reabre o detalhe.
- (b) O link R2 leva `de=<arquivo>#<id>`, e `shell37` (`ui37.py`) mostra "Voltar à OS-…". É a generalização do `est_volta` do EST (`processo_estoque.py:454`, `663`), que hoje só volta ao BEN.
- (c) `g2voltaGuarda` grava também o detalhe aberto e a seção, não só a linha.
- (d) `g2voltaValida` (`g2lib.js:1321`) recusa a volta por "outro escopo". Com a R5, deve ajustar o escopo com aviso; senão F1 e F2 se contradizem.

**R5 · Escopo global**
- Hoje há padrões diferentes:
  - motor: Santa Rita/Todas (`engine.py:2172-2174`);
  - Mapa: Lagoa Grande (`inicio.py:1106-1111`, `mapa-ctx`);
  - `g2keep`: por arquivo (`g2lib.js:38`).
- Mudar para uma chave de sessão única, lida no primeiro desenho e gravada por `mf_setfaz`/`mf_setsaf`; o Mapa migra para ela.
- O ajuste com aviso que a OS já faz (`processo_os.py:1176-1180`) passa para o motor, na chegada por link.
- Pela mesma regra, "Criar ordem" herda o filtro (A-1).

**R6 · Resolver onde o problema aparece**
- A ação nasce no registro, mas segue o caminho de domínio que já conta a demanda:
  - insumo: SOL/complemento (DEM-04);
  - peça: `manSolicitar`.
- Sempre com `cenMudar` estrito e `cenIdem`, com a chave gerada por quem inicia.
- Dono pela alçada (`G2_ALCADAS`/`g2alcQuem`), nunca por papel inexistente.

**R7 · Pendência e evento**
- A pendência é derivada do estado, não um evento gravado: `cenPendencias(c,perfil)` no `cenario.js`.
- Ela some quando o estado muda, não duplica, e o servidor continua sendo a autoridade.
- O evento serve só à linha do tempo, que já existe nas trilhas.
- Meu dia, Aprovações, o contador do cabeçalho e o PAGR leem a mesma função.
- Corrigir o catálogo: "O.S. com produto emitida" vira "O.S. agrícola que exige CMD-42", inclusive mecânica (AGENTS §4, `PRD.md:179`).
- Pontos de mudança:
  - `cenario.js`;
  - `inicio.py` (`build_in01`/`build_in02`): trocar FILA/APROV fixas e o assert da linha 1687;
  - `ui37.py`: contador.

**R8 · Um número, uma fonte**
- O seletor único fixa também a definição. Hoje "A liberar" tem duas: lista fixa no Mapa e etapa no PAGR.
- `cenContagens(c,escopo)` no `cenario.js`.
- `cusOrdem` também na OS e no GE-03; custo por cultivo (A-14).
- Teste automático de igualdade entre Mapa, PAGR, IN-02 e OS.

**Contagem (39 quebras: A 19, C 20):** 36 confirmadas · 3 parciais (A-15, C-15, C-19) · 0 já resolvidas · 0 refutadas.
