# Apêndice técnico do parecer: todos os achados

**Base:** branch `claude/prototipo-v44`. O parecer olhou o `cdc185f` (v53). O HEAD atual é o `9fb09a5`, igual ao `cdc185f` exceto em `ocupacao.*`, por causa do SAF-C01.

**Caminhos:** relativos a `tools/prototipo/v37/gen37/`. O prefixo `sp-pcm:` indica arquivos da worktree `/home/user/sp-pcm` (branch `claude/v44-pcm`), e o mesmo vale para as outras frentes.

**Contrato:** PRD v3.11 (main, merge `266a682`). Os identificadores marcados como "v3.10/3.11" não existiam na v3.9; conferi com `git show 266a682^1:docs/PRD.md`.

**Severidade:** valor final, depois da verificação. "(era S2)" indica que a segunda passada ajustou.

**Verificação:**

| Código | Significado |
|---|---|
| C | lido no código |
| E | executado no motor real com dados sintéticos (node) |
| T | visto na tela (Chrome headless) |
| I | inferido |
| R | reverificado de forma independente na segunda passada |

**Sondas:** `scratchpad/parecer/` (`verif_*`, `os/`, `ir/`, `sup/`, `pcm/`, `ge/`, `gap/`, `*_probe*.py`).

## Totais

| Módulo | S1 | S2 | S3 | S4 | Total |
|---|---|---|---|---|---|
| Cadastros e Mapa (CAD) | 0 | 0 | 14 | 8 | 22 |
| Agronomia (AGRO) | 0 | 4 | 12 | 1 | 17 |
| Planejar safra (SAF) | 0 | 6 | 16 | 2 | 24 |
| O.S. e app (OS) | 0 | 7 | 13 | 2 | 22 |
| Irrigação (IR) | 0 | 3 | 10 | 6 | 19 |
| Suprimentos (EST, CMP, SUPR) | 0 | 6 | 20 | 2 | 28 |
| Manutenção (MAN) | 0 | 7 | 16 | 2 | 25 |
| Produção (PRO) | 0 | 2 | 13 | 1 | 16 |
| Gestão e Configurações (GES) | 0 | 2 | 13 | 2 | 17 |
| Entre módulos (GAP) | 0 | 1 | 4 | 0 | 5 |
| **Total** | **0** | **38** | **131** | **26** | **195** |

**Estado dos 38 S2:**

- **9 em correção** numa frente com código: SAF-5, SAF-6, OS-7, OS-8, CMP-3, MAN-6, MAN-7, PRO-1 e PRO-2. O SAF-6 já está integrado em `9fb09a5`.
- **3 só especificados**, sem código: CMP-1, CMP-2 e MAN-4.
- **26 sem frente, ou com cobertura parcial.**

**Duplicados entre módulos:**

- OS-2 = EST-1 + EST-3
- AGRO-4 = OS-6
- CMP-2 ≈ GES-2 (parte da Compra)
- SAF-2 ≈ AGRO-6
- MAN-1 ≈ IR-1 (mesma causa raiz)

---

## Cadastros e Mapa

| ID | Sev. | Achado | Evidência (arquivo:linha) | Cobertura | Verif. |
|---|---|---|---|---|---|
| CAD-1 | S3 (era S2) | CREA vencido não é conferido na aprovação nem na liberação | g2lib.js:258-260; areas/processo_os.py:334; cenario.js:68; areas/cad_ativos_pessoas.py:29-31; dados_cad.py:91-99 | Parcial: sp-conf R4 / CONF-D09 / CONF-D26 (só na concessão do papel; configuracoes.js:66, 91) | C R |
| CAD-2 | S3 | Importar e desenhar no Mapa gravam sem as conferências do talhão (motivo automático, área cultivável igual ao polígono, CRS) | talmapa.js:38-50, 109-121 (117); talgeo.js:65; assinatura.js:70-75 | Não coberto | C |
| CAD-3 | S3 | Item de defensivo sem registro nem composição; ficha ligada pelo nome | areas/cad_produtos_estrutura.py:93-112; agrofit_dados.py:1-40; cenario.js:45-47 | Parcial: sp-ctl5, sp-solo | C |
| CAD-4 | S3 | Sem bloco de conversões nem proprietário; densidade em texto livre | areas/cad_produtos_estrutura.py:30, 98-104 | Parcial: sp-solo (PRNT, K₂O) | C |
| CAD-5 | S3 | Tipo de local sem Packing, Terreiro ou Secador | areas/cad_produtos_estrutura.py:122; dados_cad.py:158; dados_producao.py:16 | Não coberto | C |
| CAD-6 | S3 | Rendimento com R$/h digitado (não lê o CD-03 nem o CD-04); vigência ignorada; sem versão | areas/cadastros.py:422-424; areas/cad_culturas.py:107-116, 143; areas/cad_ativos_pessoas.py:112 | Parcial: sp-pcm (só o nome) | C |
| CAD-7 | S3 | Unidade de produtividade da cultura editável sem trava | areas/cad_culturas.py:84-85, 229; dados_cad.py:32, 46 | Não coberto | C |
| CAD-8 | S3 | Operação sem "família"; a exceção da água é decidida pelo nome. Vira S1 se for para o software real assim | areas/cad_culturas.py:119-122; areas/processo_os.py:338 (osSoAgua) | Não coberto | C |
| CAD-9 | S3 | Calibração sobrescrita e não lida pela O.S. | areas/cad_ativos_pessoas.py:115-117 | Parcial: sp-pcm D-16 | C |
| CAD-10 | S3 | Habilitação para aplicação igual à de operação de máquinas; alocação não lê "não alocável" | areas/cad_ativos_pessoas.py:29-31; alocacao.py:14-36 | Não coberto | C |
| CAD-11 | S3 | Parceiro sem documentos, avaliação, validade da homologação ou dados bancários | areas/cad_parceiros.py:107-137 | Não coberto | C |
| CAD-12 | S3 | Máquina sem fazenda, propriedade, série ou fonte da capacidade; pivôs fora do CD-03 | areas/cad_ativos_pessoas.py:90, 100-118; areas/cadastros.py:492; areas/cad_fazendas.py:135 | Parcial: sp-ctl5, sp-pcm | C |
| CAD-13 | S3 | Estrutura gerencial aceita ciclo pai-filho | areas/cad_produtos_estrutura.py:345-346 | Não coberto | C |
| CAD-14 | S3 | Camadas do Mapa diferentes da DEC-2609-12, sem decisão registrada | areas/inicio.py:99-101, 476 | Não coberto (decisão do proprietário) | C |
| CAD-15 | S4 | Sem CCIR, NIRF, IE nem textura; o dossiê afirma CCIR | engine.py:95; agrofit_dados.py:149-155; areas/cad_fazendas.py:29 | Não coberto | C |
| CAD-16 | S4 | Empresa e arrendador fora do cadastro mestre | dados_cad.py (EMPRESAS) | Não coberto | C |
| CAD-17 | S4 | Cultivar sem nº RNC, grupo de maturação, tecnologia ou ZARC | areas/cad_culturas.py:64-77 | Não coberto | C |
| CAD-18 | S4 | Jornada sem intervalo; pessoa sem fazenda | areas/cad_ativos_pessoas.py:316 | Não coberto | C |
| CAD-19 | S4 | Defensivo aceito em qualquer local; sem marcação de embalagem devolvível | areas/cad_produtos_estrutura.py:109 | Não coberto | C |
| CAD-20 | S4 | Vigência do CD-07 sem aviso; sem "Simular relatório" | areas/cad_produtos_estrutura.py (cd07) | Não coberto | C |
| CAD-21 | S4 | "Dentro do perímetro" e "Sem sobreposição" sempre ✓ no CD-01det | areas/cad_fazendas.py:618 | Não coberto | C |
| CAD-22 | S4 | Colunas compostas nas grades | areas/cad_*.py | sp-tabr (TABELAS-FOCO) | C |

## Agronomia

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| AGRO-1 | S2 | O MIP emite receituário e decide controle com qualquer perfil e grava "Ana" | mip.js:307, 316, 322, 334, 339, 341; areas/agronomia.py:697, 701 | Não coberto | C E T R |
| AGRO-2 | S2 | Unidade da bula (kg) contra a do lote (L): reserva sem conferir a unidade | mip.js:257-261, 292; cenario.js:75-88 (124 só no recebimento); cenario.py:27-35; dados2.py:32, 43; agrofit_dados.py:212-220 | Não coberto | C E T R |
| AGRO-3 | S2 | Plano publicado sem conferir bula, alvo e unidade; a demanda usa a dose do plano | areas/processo_planos.py:41-45, 166-171, 188-195, 323-328; dados2.py:32, 43; agrofit_dados.py:215-216; safra.js:547-549; areas/processo_os.py:395-402 | Parcial: sp-ctl5 6bf966a (alvo só no item do "Usar na O.S.") | C E T R |
| AGRO-4 | S2 | Reentrada fora da ficha, da decisão, do receituário e da O.S. | agrofit_dados.py:213 (dado em 44 produtos); areas/agronomia.py:987-992, 1081; nenhuma regra em mip.js, cenario.js, processo_os.py, mobile.py, os_campo.py | Não coberto (sp-ds só traz a dica) | C R |
| AGRO-5 | S3 | Publicar plano sem papel, autor nem fonte | areas/processo_planos.py:303-317, 323-328 | Não coberto | C |
| AGRO-6 | S3 | Versão aplicada guardada como constante local; a mensagem promete adoção no SAF | areas/processo_planos.py:20-22, 328, 336, 346; safra.js:421, 721 | Não coberto (sp-nav deixa fora) | C |
| AGRO-7 | S3 | O.S. do plano sem receituário; o REC do MIP sem RT, registro, calda, EPI nem embalagens | mip.js:318-320 | Não coberto | C |
| AGRO-8 | S3 | Nº de aplicações e rotação contados em base diferente da O.S.; intervalo da bula não conferido | mip.js:52, 240; dados_mip.py:227; dados_carencia.py:455-458 | Não coberto | C |
| AGRO-9 | S3 | Protocolo MIP sem fonte, RT ou validade; AG-05 oculta | dados_mip.py:36-71; mip.js:86; areas/agronomia.py:4; ui37.py:39 | Não coberto | C |
| AGRO-10 | S3 | Sem inimigos naturais, espécie e estádio da daninha, nem critério de risco para doença | dados_mip.py:36, 43; mip.js:68-75 | Não coberto | C |
| AGRO-11 | S3 | Catálogo do plano limitado aos produtos que já estão em algum plano | areas/processo_planos.py:44-48, 203 | Não coberto | C |
| AGRO-12 | S3 | Gatilho de perene só por data (sem florada, poda ou recorrência) | areas/processo_planos.py:80; dados2.py (CAFE-AR, MAMAO-PROD) | Não coberto | C |
| AGRO-13 | S3 | Controle localizado sem pontos nem polígono na O.S. | areas/agronomia.py:666-667; mip.js:286-299 | Não coberto | C |
| AGRO-14 | S3 | Dose pré-preenchida com o mínimo da bula | areas/agronomia.py:667, 682 | Não coberto | C |
| AGRO-15 | S3 | AG-07 "emite" receituário sem registro, assinado por Ana fixa | areas/agronomia.py:1116, 1218, 1228, 1716 | sp-ctl5 eeff236 (CTL-5 E2) | C |
| AGRO-16 | S3 | Calagem em texto; "Validar dados" sem papel | areas/agronomia.py:4, 158, 283, 294 | sp-solo (SOLO-01, até P6) | C |
| AGRO-17 | S4 | Memória do KCl não fecha (117 kg/ha; +2,9 %) | areas/agronomia.py:334, 369-370 | Não coberto | C |

## Planejar safra

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| SAF-1 | S2 | Variedade em texto livre: "58W" vira uma semente nova a comprar (15.496 kg) | areas/processo_safra.py:52; safra.js:20, 483, 514, 551, 559, 1489-1500; dados2.py:114, 117, 848; ocupacao.js:20, 50 | Não coberto | C T R |
| SAF-2 | S2 | O cultivo não guarda a versão do plano; a safra encerrada mostra v6/v6/v4 | dados2.py:63-64; safra.js:529-537, 721; areas/processo_planos.py:22, 24, 323-328, 336, 346 | Não coberto | C T R |
| SAF-3 | S2 | Safra sem estados do 8.1, sem CMD-02/03/04 e sem encerrar; CMD-06 não confere autorização | areas/processo_safra.py:31; dados2.py:15; areas/planejamento.py:135, 196; areas/processo_os.py:340-363; cenario.js:75-91; ui37.py:36-44 | Parcial: CONTROLE-02 (só versão de referência; não iniciado) | C R |
| SAF-4 | S2 | Uso com data passada vira "realizado" e sai da compra; plantio sugerido antes de hoje | cal01.js:5, 14; safra.js:546-549 | Parcial: sp-ctl4 DEM-06 (muda o nome; o descarte continua em cal01.js:14) | C T R |
| SAF-5 | S2 | Estoque e recebimentos sem filtro de fazenda | safra.js:556-559; dados2.py:931-943 | sp-ctl4 DEM-07 (cal01.js:110-114) | C R |
| SAF-6 | S2 | Soma de área com perene antiga não travava (horizonte de 900 dias) | ocupacao.js:75; ocupacao.py:208 (em cdc185f) | sp-safc01 ef0d7b2, integrado em 9fb09a5; d1b81f4 ainda fora | C R (bateria da frente) |
| SAF-7 | S3 | Plantio sugerido antes de hoje; sem janela de ZARC nem vazio sanitário | safra.js:484-485; ocupacao.js:138-142 | Não coberto | C T |
| SAF-8 | S3 | Exclui cultivo com O.S. em execução; plantio real ignorado | areas/processo_safra.py:84; engine.py:1236-1237 | Não coberto | T |
| SAF-9 | S3 | Fazenda da safra editável com cultivos | areas/processo_safra.py:29-31; safra.js:626 | Não coberto | T |
| SAF-10 | S3 | Capacidade mensal sem janela em dias nem dias aptos | dados2.py:8; areas/processo_safra.py:163-164; safra.js:1165 | Não coberto | C T |
| SAF-11 | S3 | Capacidade assimétrica entre safras abertas | safra.js:309-313 | sp-safc02 62b0904 | C |
| SAF-12 | S3 | Capacidade e custo não descontam o realizado das O.S. | safra.js:1166 | Não coberto (CONTROLE-02) | C |
| SAF-13 | S3 | Resumo sem natureza, talhão, R$/sc e base; preço sem fonte | safra.js:1137-1169; areas/processo_safra.py:277-280; dados2.py:28 | Não coberto (D7) | C T |
| SAF-14 | S3 | A prévia do recurso grava no cadastro único | safra.js:1119-1132 | Não coberto | C |
| SAF-15 | S3 | Ajuste por talhão sem conferir a bula | safra.js:1416, 1473-1478; cenario.js:43-56 | Não coberto | C |
| SAF-16 | S3 | Sem modo "produto fixo / alternativas" (40.5, v3.11) | grep em areas/*.py e *.js | Não coberto | C |
| SAF-17 | S3 | "Enviar para cotação" nunca reduz a solicitação | safra.js:1501-1507 | sp-ctl4 DEM-09 | C |
| SAF-18 | S3 | "Coberto pelo estoque" quando quem cobre é o pedido | safra.js:1216 (o mesmo em sp-ctl4 cal01.js:143-146) | Não coberto | C T |
| SAF-19 | S3 | Prazo de reposição fixo de 7 dias | dados2.py:842, 959-961 | Não coberto | C |
| SAF-20 | S3 | Etapa "concluída" com pendência; etapas futuras em vermelho | g2lib.js:369-373; safra.js:1245 | Não coberto (ETP-01 aprovado, sem diff) | C T |
| SAF-21 | S3 | Sem curva de colheita contra recepção e secagem | safra.js:565-569, 598-603; areas/planejamento.py:337-359 | Não coberto | C |
| SAF-22 | S3 | Links vivos para PL-* com números fixos | areas/campo.py:205, 297, 355; areas/comercial.py:137, 173; areas/agronomia.py:97, 319; areas/planejamento.py:1-14 | Não coberto (sp-nav não trata) | C |
| SAF-23 | S4 | Sem aviso de rotação (soja sobre soja) | safra.js:8-11, 1390 | Não coberto | C |
| SAF-24 | S4 | 16 e 18 colunas; "Salvar" genérico; eficiência sem faixa; "Nova safra" sem contexto; PRD 71.6 com 6 etapas | areas/processo_safra.py:31, 42-46, 153, 221-225; safra.js:9, 1473 | Parcial: PEND-SAF-01, sp-ds | C |

## Ordem de Serviço e app de campo

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| OS-1 | S2 | A reserva não entregue não volta ao dispensar, conferir ou encerrar | areas/processo_os.py:443-452, 464-473; cenario.js:75-90 (baixa só em 103, 399 e processo_os.py:458) | Não coberto | C E R |
| OS-2 | S2 | Lote único escolhido pelo maior saldo, sem validade e sem FEFO | cenario.js:61-62, 75-90, 96-105 | Não coberto (FEFO como lacuna em sp-sup FORA-DE-ESCOPO.md:11) | C E R |
| OS-3 | S3 (era S2) | Cancelar com material entregue mostra "Reserva liberada"; sem pendência de devolução | areas/processo_os.py:285, 454-462, 726, 733; processo_estoque.py:437, 556-557 | Não coberto | C E R |
| OS-4 | S2 | O início ignora componente da versão fora da requisição; "usado" estimado | cenario.js:168-177; areas/processo_os.py:139, 604-606 | Não coberto | C E T R |
| OS-5 | S2 | Tanque e volume de calda fixos e diferentes entre web, app e ficha; fora da versão aprovada | areas/processo_os.py:365-385, 610-613; areas/mobile.py:70, 390, 430; areas/os_campo.py:24 | Não coberto | C T R (−17 % I) |
| OS-6 | S2 | Reentrada ausente na liberação e no início (= AGRO-4) | grep 'reentr' em cenario.js, processo_os.py, mobile.py, os_campo.py, campo.py, g2lib.js, safra.js, producao.js | Não coberto | C R |
| OS-7 | S2 | Aprovar e liberar exigem a mesma pessoa; dispensar também | areas/processo_os.py:325, 334, 464; g2lib.js:260, 265 | sp-conf R13 (processo_os.py:340-358, 241); resíduo AL-05; decisão PEND-OS-01 | C T R |
| OS-8 | S2 | Divergência de dose encerrada como conforme | cenario.js:430-435 | sp-dom B-R8 (e2d1040, f0a0cd8, dbc1acc) | C R |
| OS-9 | S3 | Encerrar converte todo "Provisório" em "Conferido"; tabela diária com 5 colunas | areas/processo_os.py:447-451, 1010-1013 | CONTROLE-02 (não iniciado) | C T |
| OS-10 | S3 | Apontamento web sem horas nem talhão; aceita data futura | areas/processo_os.py:715-724; cenario.js:307 | Não coberto | C E |
| OS-11 | S3 | App: pausa sem motivo, horas digitadas, sem horímetro nem "Concluir" | areas/mobile.py:202, 506, 526; cenario.js:179-190 | Não coberto | C |
| OS-12 | S3 | Sem "Revisar saldo" nem "Reprogramar saldo" em execução | areas/processo_os.py:50, 370, 484-494 | Não coberto | C |
| OS-13 | S3 | Revisão do agrônomo sem cultura, estádio, histórico ou MIP | areas/processo_os.py:599-603 | Parcial: sp-ctl5 (alvo) | C T |
| OS-14 | S3 | Sem registro de vento, temperatura e umidade | areas/mobile.py:473 | Não coberto | C |
| OS-15 | S3 | Fichas sem EPI | grep 'EPI' em os_campo.py, mobile.py, processo_os.py | Não coberto | C |
| OS-16 | S3 | Ficha do caldeiro só na OS-0424; carga preparada não é gravada | areas/processo_os.py:615; areas/os_campo.py:98, 119 | Não coberto | C |
| OS-17 | S3 | Conflito de recurso não impede; nova ordem sem responsável | areas/processo_os.py:145, 345-360, 921; areas/mobile.py:171 | Não coberto | C T |
| OS-18 | S3 | "Abrir ordem completa" leva a detalhe fixo | areas/campo.py (sem cenGet); dados.py | Não coberto | C |
| OS-19 | S3 | O.S. sem custo realizado × planejado | areas/processo_os.py (sem R$); areas/gestao.py (sem cenGet) | Não coberto | C |
| OS-20 | S3 | O.S. sem nº de receita nem ART vinculados | cenario.js:45; areas/processo_os.py:395-405 | Não coberto | C |
| OS-21 | S4 | OB-0104 encerrada com selo vermelho "Lote bloqueado" | areas/processo_os.py:164-167; dados.py:105 | Não coberto | C T |
| OS-22 | S4 | "Hoje no campo" sem Agora/Depois/Impedidas (64.7, v3.10); lista com 18 colunas; carência no invólucro do app | areas/mobile.py:1050; cenario.js:179; areas/processo_os.py:467 | Parcial: sp-conf R9 | C T |

## Irrigação

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| IR-1 | S2 | "Iniciar" não reconfere bomba, PCM e outorga; a irrigação não lê o estado do PCM | irrigacao_estado.js:159-160, 288, 322, 326-335, 486; dados_irrigacao.py:177-178; dados_manutencao.py:40, 182; areas/processo_os.py:149-152, 345, 702 | Não coberto | C E R |
| IR-2 | S2 | Volume pré-preenchido (98,5 % do previsto) como "telemetria" vira medição e encerra sozinho | irrigacao_estado.js:358, 382-407; areas/irrigacao.py:364, 396, 473; dados_irrigacao.py:50-62 | Não coberto | C E R |
| IR-3 | S2 | Vazão da irrigação diferente da do cadastro (P1, P2 e T7); "Cadastrar setores" sem setor | dados_cad.py:74-76; dados_irrigacao.py:88-93; areas/irrigacao.py:155-156, 203; areas/cad_fazendas.py:93; ui37.py:37 | Não coberto | C E R |
| IR-4 | S3 | Sem lâmina a 100 % nem percentímetro; passada abaixo do mínimo do pivô | irrigacao_estado.js:116-120; dados.py:52; areas/mobile.py:861 | Não coberto | C E |
| IR-5 | S3 | Déficit sem teto de CAD; limiar fixo; Kc sem valor nem fonte | irrigacao_estado.js:107-108; dados_irrigacao.py:88-105, 122-125; areas/irrigacao.py:153-156, 177 | Parcial: sp-solo (CAD só referência) | C |
| IR-6 | S3 | "medido" quando é estimativa por ET; a umidade da sonda não entra | irrigacao_estado.js:73; areas/irrigacao.py:167; dados_irrigacao.py:53-56 | Não coberto | C |
| IR-7 | S3 | Sem validade por fonte (PROJ-13/14, v3.10); recibo LIB sem versões | dados_irrigacao.py:50-62; irrigacao_estado.js:246; areas/irrigacao.py:582-585; areas/gestao.py:542 | Não coberto | C |
| IR-8 | S3 | Sem kWh nem custo por ordem; ponta fixa; o recibo declara "energia conferida" | dados_irrigacao.py:183; irrigacao_estado.js:172-175, 246; areas/irrigacao.py:549-558 | Não coberto | C |
| IR-9 | S3 | Outorga sem meses, horas ou protocolo; sem ligação ponto → setor | irrigacao_estado.js:181-191 | Parcial: sp-ctl5 | C E |
| IR-10 | S3 | Parâmetros sem versão; a ordem liberada muda com a eficiência | irrigacao_estado.js:409-417; dados_irrigacao.py:93, 136; areas/configuracoes.py:190, 423 | Não coberto | C E |
| IR-11 | S3 | MB-08 estático, sem comandos | areas/mobile.py:340, 850-897 | Não coberto | C |
| IR-12 | S3 | "Adicionar produtos" sem papel; autor fixo; lista fixa em kg/ha | areas/irrigacao.py:375, 444, 512; irrigacao_estado.js:448 | Não coberto | C |
| IR-13 | S3 | Sem "Simular capacidade" nem "Programar período" | irrigacao_estado.js:177-193, 255-266; areas/irrigacao.py:216-283 | Não coberto | C |
| IR-14 | S4 | Sem cenário de chuva prevista; chuva efetiva com fator fixo; cor única no mapa | irrigacao_estado.js:221-226; dados_irrigacao.py:101; areas/inicio.py:657-664 | Não coberto | C |
| IR-15 | S4 | Desempenho com números fixos; "Eficiência" com dois sentidos | areas/irrigacao.py:549-558, 571 | Parcial: sp-tabr | C |
| IR-16 | S4 | Sensor sem setor; "Validar leitura" sem motivo | areas/irrigacao.py:543, 584; irrigacao_estado.js:421, 426-428 | Parcial: sp-tabr | C |
| IR-17 | S4 | Pendência comum pintada de vermelho (DS-17, v3.10) | ui37.py:122; areas/irrigacao.py:135-138, 576 | Não coberto | C |
| IR-18 | S4 | "Água só na Irrigação" sem registro em DECISIONS nem no PRD | areas/irrigacao.py:19; areas/processo_os.py:7 | Não coberto | C |
| IR-19 | S4 | Colunas compostas; sem energia nem "Atualizado em" | areas/irrigacao.py:151-157, 213-215, 295-297, 337-341, 538-548 | sp-tabr (exceto energia) | C |

## Suprimentos

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| EST-1 | S2 | Lote vencido entra no disponível, é reservado e é entregue | cenario.js:61-62, 75-91, 95-106; areas/processo_estoque.py:244, 324-330, 374-383; mip.js:258; irrigacao_estado.js:156 | Não coberto (cenVencido do sp-sup só no laudo) | C E R |
| EST-2 | S2 | "Item diferente do pedido" entra como o item comprado e fica apto | areas/processo_estoque.py:25, 274-279, 316-331, 348 | Não coberto | C E R |
| EST-3 | S2 | Sem FEFO e sem repartir entre lotes; reserva em lote de outra fazenda | cenario.js:61; cenario.py:25-41; areas/processo_estoque.py:83 | Não coberto | C E R |
| EST-4 | S3 (era S2) | A entrega no comando consome reserva de outra O.S. (a tela protege) | cenario.js:95-106; areas/processo_estoque.py:191-199, 281-284, 333-336 | sp-sup 455f3b3 (SUP-2a) | C E R |
| CMP-1 | S2 | O PC emitido na Compra não chega ao Estoque | areas/processo_estoque.py:53, 68; areas/processo_compras.py:161, 184-190, 294; cenario.js:6 | Especificado: sp-specs pcm-suprimentos ESPECIFICACAO.md:535; SUP-3 adiada. Sem código | C R |
| CMP-2 | S2 | Aprovação gravada como Ana, seja qual for o perfil; o comprador registra a decisão da Direção | areas/processo_compras.py:19, 248, 436-449, 554-555, 587; ui37.py:223-224 | Especificado: SUP-3 (sp-sup ESPECIFICACAO.md:81, 342, 376); rascunho ddfb47f. Sem código ativo | C R (efeito com outro perfil: I) |
| CMP-3 | S2 | A Compra pede o que a OS-0421 já executa (145,2 L) | cal01.js:14; areas/processo_compras.py:40 | sp-ctl4 702633b, 21487ed | C E R |
| EST-5 | S3 | Um laudo libera a quarentena do lote inteiro | cenario.js:137 | sp-sup d28b12f (SUP-2b) | C |
| EST-6 | S3 | Contagem abaixo do reservado não grava e revela o saldo | cenario.js:144 | sp-sup d28b12f | E |
| EST-7 | S3 | Recebimento com unidade fixa em kg; "Apta" digitada; pedido pré-selecionado | areas/processo_estoque.py:76-81, 317-319 | sp-sup 4e1023b | C |
| EST-8 | S3 | Devolução pré-preenchida; "Entregar a" fixo; MB-05 com dados fixos | areas/processo_estoque.py:21, 439; areas/mobile.py:38, 665, 713-724 | sp-sup 455f3b3, 4e1023b | C |
| EST-9 | S3 | Conferência do recebimento vendo a nota (não cega) | areas/processo_estoque.py (PREVALS g_rec) | Não coberto | C |
| EST-10 | S3 | Recebimento sem preço, emitente nem tolerância; sobra aceita | areas/processo_estoque.py:74-87, 320; areas/suprimentos.py:702 | Parcial: PCMS-C02/G02 especificados | C |
| EST-11 | S3 | Estoque sem valor; ajuste sem R$ nem alçada por valor | areas/processo_estoque.py | Parcial: PCMS-C02 especificado | C |
| EST-12 | S3 | Defensivo aceito em galpão de fertilizante | areas/processo_estoque.py:19, 84 | Não coberto | E |
| EST-13 | S3 | Sem registro de embalagens vazias | grep em gen37 | Não coberto | C |
| EST-14 | S3 | Sem transferência nem estorno | areas/processo_estoque.py:226-227 | Não coberto | C |
| EST-15 | S3 | Reserva sem validade (RN-046, CMD-49, RSV-16; v3.10) | cenario.js:83-86 | Não coberto | C |
| EST-16 | S3 | Validade diferente num lote já existente é ignorada | cenario.js:122-124; verif_ce_est.py:31-35 | Não coberto | E |
| CMP-4 | S3 | A mesma pessoa cota e aprova; proposta única sem alerta | areas/processo_compras.py:19, 248; dados2.py (SOL_INICIAL) | Não coberto | C |
| CMP-5 | S3 | Custo sem prazo de pagamento nem tributos; proposta vencida aprovável | areas/processo_compras.py:232, 442-449 | Não coberto | C |
| CMP-6 | S3 | Proposta sem identidade do produto (40.5, SUBST-12; v3.11) | dados2.py:835-843 | Não coberto | C |
| CMP-7 | S3 | Quantidade limitada à necessidade (sem múltiplo de embalagem) | areas/processo_compras.py:358; g2lib.js:126 | Não coberto | C |
| CMP-8 | S3 | "Cancele o pedido" sem comando de cancelar | areas/processo_compras.py:381, 423 | Parcial: PCMS (especificado) | C |
| CMP-9 | S3 | Reprogramar sobrescreve a data prometida; motivo opcional | areas/processo_compras.py:107, 468-474 | Especificado: SUP-3 / PCMS-M11 | C |
| CMP-10 | S3 | Compra só nasce de safra (sem reposição) | areas/processo_compras.py:2-7, 73; areas/suprimentos.py:1-5 | Parcial: PCM-1c / SUP-3 | C |
| EST-17 | S4 | Inventário sem plano cíclico; corte gravado no registro, não na abertura | areas/processo_estoque.py:281 | Parcial: sp-sup | C |
| SUPR-1 | S4 | Grades de 12 a 14 colunas; unidade fora da célula; condição do PC pelo 1º item | areas/processo_estoque.py:72-124; areas/processo_compras.py:75-80, 99, 241 | sp-sup 4e1023b; SUP-3 | C |

## Manutenção (PCM)

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| MAN-1 | S2 | Bloquear o ativo diz "O.S. impedidas", mas não impede (PJ-3030 em OS-0421, 0424, 0430) | areas/maquinas.py:140-147, 205-210, 271-274; areas/processo_os.py:147-151; sp-pcm: dados_manutencao.py:830-834, areas/processo_os.py:278; cenario.js:75-90, 179-187; alocacao.py:21, 28, 29 | Parcial: sp-pcm (só a01); PCMS-A05 (Bloco 2) | C E R |
| MAN-2 | S3 (era S2) | Sem verificação de segurança e isolamento antes do serviço | dados_manutencao.py:402-403, 431; sp-pcm: dados_manutencao.py:629-633 | Não coberto | C R |
| MAN-3 | S3 (era S2) | Liberar a OM sem CMD-42 separado nem alçada econômica | dados_manutencao.py:386-392; sp-pcm: dados_manutencao.py:460, 609-619 | PCM-1b especificado (ESPECIFICACAO:376) | C E R |
| MAN-4 | S2 | Peças com saldo próprio, fora do Estoque | dados_manutencao.py:64-78, 266-267, 389, 432-435; areas/suprimentos.py:564, 703 | PCM-1b especificado, não executado | C R |
| MAN-5 | S2 | Corretiva nasce sem peças e sem "Incluir peça" | sp-pcm: dados_manutencao.py:256, 735, 798-799, 816; areas/maquinas.py:1132 | Bloco 2 (PCMS-M20). Não coberto | C R |
| MAN-6 | S2 | Triagem e "Criar ordem" sem efeito (v53) | areas/maquinas.py:219-235, 283, 305, 542-556; dados_manutencao.py:353 | sp-pcm S1 (dados_manutencao.py:784-808; 103/103 OK) | C E R |
| MAN-7 | S2 | Condição técnica livre no formulário; aptidão sem teste | areas/maquinas.py:143-146, 205-210, 631, 639-641 | sp-pcm S1/S2 (dados_manutencao.py:722-748, 826-845) | C R |
| MAN-8 | S2 | O mesmo abastecimento por dois autores vira dois lançamentos (640 L) | areas/maquinas.py:716-720; sp-pcm: dados_manutencao.py:892-901 | Não coberto (CONC-09/11, AC-75; v3.10) | C E R |
| MAN-9 | S2 | O L/h ignora os abastecimentos parciais (8,2 em vez de 17,3) | sp-pcm: dados_manutencao.py:889-891; areas/maquinas.py:166; dados_manutencao.py:34 | Não coberto (defeito do sp-pcm) | C E R |
| MAN-10 | S3 | Criticidade calculada pelo atraso; CD-03 sem criticidade | dados_manutencao.py:364, 449; sp-pcm: 583, 718; dados_cad.py:62-77 | Não coberto | C E |
| MAN-11 | S3 | Custo da OM e disponibilidade divergentes entre GE-03/GE-06 e MA | areas/gestao.py:279, 347, 481; dados_manutencao.py:22, 454; areas/maquinas.py:626-627 | Não coberto | C |
| MAN-12 | S3 | Janela liberada não reserva capacidade no PCP | areas/maquinas.py:326-330; dados_manutencao.py:203, 367-368; sp-pcm: 534-540, 619, 629-631 | Parcial: sp-pcm | C |
| MAN-13 | S3 | Apontamento de turno sem horímetro | cenario.js:287-310; dados_manutencao.py:28-44 | Não coberto | C |
| MAN-14 | S3 | Sem checklist pré-uso por classe | areas/maquinas.py:242-250; sp-pcm: areas/mobile.py:670-682 | Não coberto | C |
| MAN-15 | S3 | "Pode operar? Não" não restringe a máquina | sp-pcm: areas/mobile.py:670-682; dados_manutencao.py:461, 768 | Não coberto | C |
| MAN-16 | S3 | Executante sem validade da habilitação nem ocupação | sp-pcm: dados_manutencao.py:181, 613; dados_cad.py:104, 107 | Parcial: sp-pcm D-37 | C |
| MAN-17 | S3 | Quem reparou declara apto sozinho | sp-pcm: dados_manutencao.py:461, 465-466 | Não coberto | C E |
| MAN-18 | S3 | Serviço sem fonte, garantia ou gatilho por condição | areas/maquinas.py:797-818 | Não coberto | C |
| MAN-19 | S3 | Conclusão sem causa nem modo de falha | dados_manutencao.py:422-450; sp-pcm: 686-721; areas/gestao.py:544 | Não coberto | C |
| MAN-20 | S3 | Horas e aplicado assumidos; data da conclusão sempre hoje | dados_manutencao.py:427-428, 441; sp-pcm: 670, 691-692, 704 | Parcial: sp-pcm D-18; 1b/1c | C |
| MAN-21 | S3 | Sem cancelar OM nem serviço de terceiro | sp-pcm: dados_manutencao.py:229, 512 | PCM-1b (cancelar); Bloco 3 | C |
| MAN-22 | S3 | Sem componente nem dependência funcional (bomba → setores) | dados_cad.py:62-77 | Não coberto | C |
| MAN-23 | S3 | Números fixos nas telas MA e MB-09 (v53) | areas/maquinas.py:122-126, 148-158, 252-266, 548-549, 660-667, 683-694; areas/mobile.py:899-941 | sp-pcm S1/S2/S4 (GE-06 continua) | C |
| MAN-24 | S4 | Seis itens de menu; "Restaurar demonstração" em três telas | ui37.py:41-42; areas/maquinas.py:32-36, 98-110, 305 | sp-pcm S1 | C |
| MAN-25 | S4 | Volume sem teto do tanque; Pendência com 1 h fixa | sp-pcm: dados_manutencao.py:717-719, 895; areas/maquinas.py:851 | Não coberto | C E |

## Produção

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| PRO-1 | S2 | Contrato em sc de 50 kg convertido por 60 kg; reserva e oferta erradas | dados_producao.py:51, 102-103; areas/comercial.py:451, 453; producao.js:221; docs/colheita/DECISOES.md:49 | sp-com A-17 (3044c79, 4533879, d7b91ff, c6b17da) | C E R |
| PRO-2 | S2 | Café da roça como "200 sc" e produtividade 0 / −100 % | producao.js:39-41, 113, 128-138, 180; dados_cad.py:45 | sp-dom f614da7 (D-38) | C E R |
| PRO-3 | S3 | "Físico" do grão = comercial a 14 % | producao.js:331, 347 | Não coberto (BEN-3 planejado) | C |
| PRO-4 | S3 | Balança aceita valor 10× maior sem aviso | producao.js:318-320; dados_cad.py:157 | Não coberto | E |
| PRO-5 | S3 | Previsão anual = meta × área | producao.js:155-157, 161; areas/producao.py:486 | Não coberto | C E |
| PRO-6 | S3 | Rascunho usa só a última contagem; aceita 1 planta | producao.js:146; areas/mobile.py:828, 839 | Não coberto | E |
| PRO-7 | S3 | Perecível vencido reservável sem aviso | producao.js:197, 380-397 | sp-com R-C05; BEN-6 planejado | E |
| PRO-8 | S3 | Liberar lote, pesar, estornar e publicar sem papel; nomes fixos | producao.js:371; areas/producao.py:203, 306, 384, 577 | Parcial: sp-ben, sp-com | C E |
| PRO-9 | S3 | O.S. de colheita encerra sem carga recebida | cenario.js:430-436; producao.js:227-230 | Não coberto | C |
| PRO-10 | S3 | Lotes "Em processo" sem caminho de saída | dados_producao.py:71-87; producao.js:178-182 | sp-ben BEN-1 | C |
| PRO-11 | S3 | Sem expedição nem contrato; pedidos em duas fontes | areas/producao.py:211; areas/comercial.py:310-311, 451-453; ui37.py:40 | sp-com | C |
| PRO-12 | S3 | Lote sem proprietário ou depositário; sem inventário nem transferência | producao.js:339-340; areas/producao.py:225-240 | Não coberto (BEN-8) | C |
| PRO-13 | S3 | Umidade e impureza fixas; classe "Padrão" | dados_cad.py:42-44; areas/producao.py:376-377; producao.js:203, 339 | Parcial: sp-ben | C |
| PRO-14 | S3 | Pesagem sem veículo, segunda pesagem ou romaneio | areas/producao.py:359-383; areas/mobile.py:1019 | Não coberto | C |
| PRO-15 | S3 | Programar colheita sem capacidade; 120 dias fixos | areas/producao.py:473, 478-489 | Não coberto (BEN-5) | C |
| PRO-16 | S4 | Rótulos e filtros; veículos fixos; silo em sc; R$/sc fixo | producao.js:196; areas/producao.py:226, 264, 300, 323 | Parcial | C |

## Gestão, custos e Configurações

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| GES-1 | S2 | Custo realizado do Mapa = R$/ha padrão × ha (ignora horas); insumo a preço do plano | areas/inicio.py:270, 282, 699-706, 741-742, 909; cenario.js:119-125, 307; areas/mobile.py:526; areas/processo_os.py:421 | Não coberto (CONTROLE-02 / ORC-CUSTOS, D7) | C E R |
| GES-2 | S2 | Compra e Assinatura gravam "Ana" seja qual for o perfil | areas/processo_compras.py:19, 248, 436-439, 554-555; areas/assinatura.py:19, 161, 178, 181, 204, 206, 289; assinatura.js:139 | CF-05: sp-conf a3e9172 (P7). Compra = CMP-2 (SUP-3 adiada) | C R |
| GES-3 | S3 | "Restaurar dados iniciais" não restaura | areas/indice.py:81, 95; cenario.js:2-12; areas/agronomia.py:582 | Não coberto | C T |
| GES-4 | S3 | Sem base aprovada; o previsto é o plano atual | areas/inicio.py:292-333; areas/gestao.py:160-215 | CONTROLE-02 (não iniciado) | C |
| GES-5 | S3 | Previsto do Mapa calculado em paralelo ao SAF | areas/inicio.py:282, 292-333, 490; safra.js:560, 1154 | Não coberto | C I |
| GES-6 | S3 | CF-01, CF-02 e CF-04 com regras e trilha digitadas, diferentes dos comandos | areas/configuracoes.py:95-103, 167, 418-424, 457 | sp-conf P1-P6 (revisão pendente) | C |
| GES-7 | S3 | Liberador padrão "gestor" (o PRD diz PCP) | areas/processo_os.py:325 | Parcial: sp-conf AL-01; decisão do proprietário | C |
| GES-8 | S3 | Gestão oculta com números fixos e dimensões em texto | areas/gestao.py:132-138, 185, 207, 271-282, 294, 318, 323 | Não coberto (D7) | C |
| GES-9 | S3 | Custo da O.S. soma diesel, manutenção e mão de obra que já estão na tarifa | areas/gestao.py:277-281; areas/cad_ativos_pessoas.py:113 | Não coberto | C |
| GES-10 | S3 | Indicadores sem ficha completa (ID, alerta, frequência) | areas/gestao.py:157, 470-520 | Não coberto | C |
| GES-11 | S3 | Índice sem viewport (1440 px fixos) | areas/indice.py | Não coberto | C T |
| GES-12 | S3 | "Entrar como" não troca o perfil; perfis do índice diferentes de G2_PERFIS | areas/indice.py:63-65; g2lib.js:257-260 | Não coberto | C E |
| GES-13 | S3 | Sem "Ajuda › Relatar problema" (75.2, FB-01..05; v3.10) | grep em gen37 | Não coberto | C |
| GES-14 | S3 | Custo-hora de pessoas visível a todos | areas/cad_ativos_pessoas.py:296, 301 | Não coberto | C |
| GES-15 | S3 | Integrações sem modo de gravação nem ficha da credencial (RF-INT-008; v3.11) | sp-conf: areas/configuracoes.py:297, 313 | Parcial: sp-conf P6 | C |
| GES-16 | S4 | KPI verde pela posição; recusa com role=status; busca falsa; vários menus abertos | engine.py:151, 509, 1461; areas/maquinas.py:267, 315, 693; ui37.py:302-306; g2lib.js:286 | Parcial | C |
| GES-17 | S4 | Índice com "PRD v3.7"; DEMO-14 60/40 em vez de 30/70; datas; código morto | areas/indice.py:22, 79; dados.py:5; cenario.js:13, 220; areas/inicio.py:29-30, 199-207 | Não coberto | C |

## Entre módulos (crítica de completude)

| ID | Sev. | Achado | Evidência | Cobertura | Verif. |
|---|---|---|---|---|---|
| GAP-1 | S2 | Ocorrência sem gravidade, dono nem destino; a O.S. encerra | cenario.js:411-413, 430-435; areas/mobile.py:232, 443, 614, 628; areas/processo_os.py:518; areas/campo.py:440-485; ui37.py:36-44 | Parcial: sp-pcm (Equipamento → achado; areas/mobile.py:1301) | C E (reconferido no código nesta consolidação) |
| GAP-2 | S3 | Sobra de calda só sai como devolução de produto puro | cenario.js:108-116, 287-320 | Não coberto | C E |
| GAP-3 | S3 | Cadastros salvos não chegam aos processos; frota em listas paralelas | areas/cad_fazendas.py:182, 305; talmapa.js:3; assinatura.js:9, 69-76; areas/processo_safra.py:37; ocupacao_cen.py:18-26; areas/processo_compras.py:58, 334-335; alocacao.py:10-12 | Parcial: sp-conf (pessoas), sp-ctl5 (outorga), sp-pcm (REC_DO_ATIVO) | C I |
| GAP-4 | S3 | Custo da terra, arrendamento e formação de perene fora do custo e da oferta | areas/cad_fazendas.py:108; dados_cad.py:16-17; dados_producao.py:56-58; dados_lagoa_safra.py:25-34 | Não coberto | C E |
| GAP-5 | S3 | Apontamento sem equipe, HH nem custo de mão de obra; jornada fixa | cenario.js:307; areas/mobile.py:465, 951; alocacao.py:6; dados_lagoa_safra.py:56; areas/cad_ativos_pessoas.py:301 | Não coberto | C |

---

## Conferências feitas nesta consolidação (09/10)

**PRD v3.11 está na main:**
- `git merge-base --is-ancestor 266a682 origin/main` deu verdadeiro;
- `docs/PRD.md:3` traz "Versão 3.11";
- o AGENTS.md cita a 3.11 como vigente.

**IDs novos da v3.10/3.11:** comparei a contagem de cada ID na versão anterior ao PR #48 (`git show 266a682^1:docs/PRD.md`, que é a v3.9) com a contagem na main.

| Situação | IDs |
|---|---|
| Zero na v3.9, presentes na main (novos) | SUBST-01, 40.5, RN-046, CMD-49, CMD-50, RSV-16, RSV-03, CONC-09, CONC-11, CONC-13, AC-75, PROJ-13, PROJ-14, DS-17, DS-37, FB-01, APROV-01, APROV-04, APROV-09, AC-142, RF-INT-008, 64.7, 73.9, CAMPO-14 |
| Já presentes na v3.9 | RN-015, RN-016, FEFO, CMD-46, CMD-47, CMD-04, CMD-16, AGR-028, AGR-031, RF-WAT-004, RF-AST-001, RF-AST-004, RF-AST-006, RF-SUP-006, RF-SUP-007, RF-SUP-011, RF-OPS-006, RF-DAT-001, CAL-01, CAL-07, CAL-09, CAL-12, ESTOS-03, ESTOS-10, AGUA-08, PCMP-04, SAFRA-05, 40.3, RN-031, 44.5, AJUSTE-07, PARC-02 |

**Protótipo e frentes:**
- HEAD da `claude/prototipo-v44` = `9fb09a5`, que é o `cdc185f` mais o SAF-C01 (`ef0d7b2`).
- As frentes sp-pcm, sp-sup, sp-tabr, sp-ben, sp-com, sp-ctl4, sp-ctl5, sp-solo, sp-conf, sp-ds, sp-dom, sp-safc02 e sp-nav têm commits que ainda não estão em `9fb09a5`.
- Do sp-safc01, só o `d1b81f4` está fora.

**GAP-1:**
- `cenPodeEncerrar` (cenario.js:430-436) não lê `c.ocorr`;
- em `areas/processo_os.py`, `ocorr` aparece só na exposição `window.__cen`.

**Frente sp-nav (NAV-1, `19aeb94`):**
- muda só `areas/processo_planos.py` e os testes;
- mantém `VER_APLICADA` local;
- declara fora a adoção de versão por cultivo.
