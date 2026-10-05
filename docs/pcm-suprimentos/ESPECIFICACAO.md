# PCM × Suprimentos de manutenção · v2

**Resultado útil:** a ordem de manutenção (OM) pede, compra, recebe, usa e custeia peças no mesmo estado, no mesmo estoque e na mesma compra da O.S.

- **Rótulo:** especificado. Nada foi implementado. Só o que traz "(executado)" saiu de comando rodado em 05/10/2026 (DECISOES.md §8).
- **Versão 2**, de 05/10/2026. Aplica os 42 achados confirmados da revisão adversarial (DECISOES.md §9); conferência e correções em DECISOES.md §11.
- **Papéis:** autor Claude · revisor Codex (produto, aceite, QA) · integrador quem não for o autor (AGENTS §3).
- **Contrato:** PRD v3.9. "l.N" é a linha de `docs/PRD.md`. A reserva segue a **DEC-2609-13** (l.12227: "reserva na liberação da O.S."; `docs/DECISIONS.md:23`).
- **Pedido do proprietário (05/10/2026):** "Conecte PCM e suprimentos de manutenção (materiais e serviços) de forma brilhante, sistêmica, integrada e conectada." É pedido, não aprovação deste desenho.
- **Base lida (executado, só leitura):** `/home/user/sp-tab5`, branch `claude/v44-tabelas-05`, HEAD `0cf6f90` (TABELAS-FOCO 2d). A 2c é `e1091d5`. O `origin` para em `claude/v44-tabelas-03` = `cd9cdc3`. `git status` sem arquivo rastreado modificado. `gen37/` = `/home/user/sp-tab5/tools/prototipo/v37/gen37/`.
- **Arquivos irmãos:** `FORA-DE-ESCOPO.md` e `DECISOES.md`.
- **Fonte única (achado PCMS-R15):** valores esperados só no §10; regras no §4; testes no §11; aceite no §12, como matriz. Os Blocos 2 a 7 estão no Anexo, como insumo do Codex.

---

## 0. Como executar

### 0.1 Mapa do existente (linhas em `0cf6f90`)

**Fica: reutilizar sem mudar o comportamento**

| O quê | Onde | Uso aqui |
|---|---|---|
| Estado único, transação atômica, aviso entre quadros, restauração | `cenario.js:11-25` (`cenGet`, `cenReset`, `cenMudar`, `cenOuvir`) | OM, REQ, SC, PC e lote mudam numa só gravação |
| Lote, livre, movimento | `cenario.js:42-44` (`cenLote`, `cenDisp`, `cenMov`) | Peça passa a ser lote |
| Reserva na liberação | `cenario.js:48-63` (`cenLiberar`) | Mesmo formato de REQ para a OM |
| Entrega em custódia e devolução conferida | `cenario.js:68-89` | OM como destino |
| Recebimento com NF e quarentena; inspeção | `cenario.js:92-103` | Recebimento contra o PC |
| Contagem cega com trava abaixo do reservado | `cenario.js:105-111` (trava l.109) | Protege a reserva da OM |
| Consumo acima da custódia vai a conferência (RN-018, CMD-50) | `cenario.js:139-228` | Excedente do mecânico |
| Encerrar com custódia zero | `cenario.js:243-247` (`cenPodeEncerrar`) | Encerramento da OM |
| PCM interno: planos, vencimento, geração sem duplicar, checklist, leitura | `dados_manutencao.py:296-385, 402-415, 452-477` | Fica |
| Cinco fases | `dados_manutencao.py:268` (`MAN_FASES`) | Sem coluna nova |
| Mover a janela dentro da tolerância | `areas/maquinas.py:321-367` (`ma_mover`) | Saída do conflito (M09b) |
| CMP: convite só a homologado do grupo, escolha padrão "menor custo que chega a tempo", alçada | `areas/processo_compras.py:220-251`; `dados2.py:696-705` | Compra de peça |
| Natureza e centro | `dados_cad.py:119-120`, `150-151`, `155` | Custo (Bloco 7) |
| Teste de JS sem navegador | `carencia_test.py:9-32` | `pcm_sup_unit.js` |

**Muda**

| O quê | Onde | PR |
|---|---|---|
| Manutenção sai da chave própria e entra no cenário | `dados_manutencao.py:249-282` (chave na l.267); `cenario.py:80` (v=3 → 4), `84-85` (`js_prefixo`) | 1a |
| Prefixo das 6 telas da manutenção | `areas/maquinas.py:168, 277, 326, 557, 706, 1171` | 1a |
| Grupo Lubrificantes, unidade `kit`, local Almox. oficina, 14 itens | `dados2.py:682`; `dados_cad.py:119-123, 135-137`; `areas/cad_produtos_estrutura.py:30, 36-44, 57-61, 80` | 1a |
| `ITENS` vira catálogo sem saldo; peça vira lote | `dados_manutencao.py:66-78` | 1b |
| `manFalta`, `manLiberar`, `manConcluir`, `manCusto`, `manEncerrar` e os 7 leitores de saldo | `dados_manutencao.py:332, 386-393, 397, 416-444, 448-451`; `areas/maquinas.py:382, 469, 893` | 1b |
| Próximo passo e painel da OM | `areas/maquinas.py:379-401, 469-478, 552` | 1b |
| Motivo fixo "(agrônomo)" na entrega | `areas/processo_estoque.py:188` | 1b |
| Numeração de REQ | `areas/processo_os.py:341-342` (`osc_reqId`); `cenario.js:51` | 1b |
| Cancelar sem execução (hoje baixa a reserva sem movimento e ignora a custódia) | `areas/processo_os.py:378-382` (`osc_cancelar`) | 1b |
| Recebimento com "kg" fixo e só pedidos estáticos | `areas/processo_estoque.py:78-81, 209-211, 305-309, 335-337, 383` | 1c |
| Origem da CMP: hoje só a safra; CMP sem cenário | `areas/processo_compras.py:110, 164-176, 185-198, 241, 404, 436-441, 469-474` | 1c |
| Nome "Compra de insumos" | `ui37.py:41`; `areas/processo_compras.py:2, 146, 150`; `nav37_md.py:30`; `areas/indice.py:17` | 1c |

**Não existe: criar**

| O quê | Prova de que não existe |
|---|---|
| Local "Almox. oficina" | `dados_cad.py:135-137`: 10 locais. Os 27 lotes do cenário estão em 5 locais de insumo (executado) |
| Itens de manutenção no CD-06; unidade `kit`; grupo Lubrificantes | `cad_produtos_estrutura.py:30, 80`; `dados2.py:682` |
| Fornecedor homologado em Peças | F01-F07 sem Peças (`dados2.py:683-691`) |
| Responsável de manutenção | `dados_cad.py:77-88`; `cad_ativos_pessoas.py:28, 38` |
| REQ de OM; SC e PC no cenário | `cenEntregar` exige `c.ordens[r.os]` (`cenario.js:69`) |
| Chave de idempotência e versão por objeto | `cenario.js` não tem chave de comando (grep "idem" vazio, achado A04) |
| Lote de Diesel S10 no Tanque Sede (Bloco 6) | `cenario.seed()` não tem lote de diesel (executado); Tanque Sede só no cadastro (`dados_cad.py:136`) |
| Condição do ativo gravada por comando (Bloco 2) | Nenhuma função altera `ativos[aid].cond`; o MA-01 força Bloqueado (`maquinas.py:205-210`) |

**Sai**

| O quê | Onde | PR |
|---|---|---|
| "Solicitar compra" e a SC gravada dentro da OM | `manSolicitar` (`dados_manutencao.py:394-398`); `maquinas.py:384` | 1b (a aprovação abre a SC) |
| "Resolver sobras" pela própria OM | `manSobras` (l.445-447); `maquinas.py:389` | 1b (a devolução passa pelo EST) |
| "Registrar recebimento" pelo PCM | `manReceber` (l.399-401); `maquinas.py:385` | 1c (no 1b vira ponte rotulada, §11) |
| Chave `'talhao-os-manutencao-v1'` | `dados_manutencao.py:267` | 1a |

As telas SU-01 a SU-09 continuam ocultas e não são fonte de dados (FORA-DE-ESCOPO.md).

### 0.2 Portões antes de editar (AGENTS §3.1, §3.4)
1. A TABELAS-FOCO 2b, 2c e 2d tem PR aberto com a bateria verde, executada e com hash. Hoje: 2b no PR #42; 2c `e1091d5` e 2d `0cf6f90` implementadas, com a bateria remetida ao PR (`tools/prototipo/v37/RETOMADA-NUVEM.md:207, 215`). O PCM entra na fila depois dela.
2. Base de cada PR do Bloco 1: o hash do PR da 2d. O 1a só é integrado depois do merge da 2d.
3. O Codex escreve a tarefa e o roteiro; o Claude revisa (AGENTS §3.1, passo 1). §11 e §12 são o insumo técnico.
4. O Codex registra o pedido de 05/10 na rodada ou em `docs/DECISIONS.md`, como pedido.
5. O dono só é consultado se for para passar o PCM à frente da TABELAS-FOCO (AGENTS §3.2).

O 1a não edita arquivo da 2c ou da 2d, mas muda a saída de todas as páginas que embutem `cenario.js_prefixo()`: EST (`processo_estoque.py:126`), O.S. (`processo_os.py:1110`), App (`mobile.py:292`; `os_campo.py:107`), AG (`agronomia.py:211, 297, 837, 925, 1731`), IR (`irrigacao.py:93`), CO (`colheita.py:658`) e IN (`inicio.py:1301, 1422`). A v=4 reinicia o estado salvo da demonstração nessas telas (`cenario.js:11`).

### 0.3 Bateria (especificada, não executada)
```sh
cd /home/user/sp-tab5/tools/prototipo/v37/gen37
python3 dados_manutencao.py && python3 build.py && python3 montar_render.py && python3 varredura.py
python3 ma_planos_test.py && python3 ma_correcoes_om_test.py && python3 ma_correcoes_pm_test.py && python3 matest.py
python3 esttest.py && python3 est_cenario_test.py && python3 est_fix1_test.py && python3 est_fix2_test.py && python3 tabelas_est_test.py && python3 verif_ce_est.py && python3 consumo_divergente_test.py
python3 os_cenario_test.py && python3 tabelas_os_test.py && python3 os_v39_liberar_test.py && python3 app_cenario_test.py && python3 app_mb03_turno_test.py && python3 app_restaurar_test.py
python3 quantidade_test.py && python3 irr_estado_test.py && python3 carencia_test.py unit && python3 agtest.py && python3 mbtest.py b && python3 mbtest.py d && python3 cotest.py
python3 cadc_cd06_test.py && python3 cadc_fix_cd06.py && python3 cadc_cd07_test.py && python3 cadc_fix_cd07.py && python3 g2test.py CD-06.dc.html CD-07.dc.html && python3 cada_cd04_test.py && python3 cada_fix04_test.py && python3 cadp_fix_test.py && python3 cada_cd03_test.py
python3 cmptest.py && python3 saf_cmp_continuidade_test.py && python3 acao_unica_test.py && python3 testes_pedido.py && python3 saftest.py && python3 etapas_celular_test.py
python3 pcm_sup_test.py unit        # do 1b em diante
python3 pcm_sup_test.py fluxo       # 1b (C1, C3, ponte do C2) e 1c (C2 e C11 completos)
```
- Todo PR roda a bateria inteira, porque o 1a já muda o prefixo de todas as telas do cenário.
- **Critério:** nenhuma falha nova contra a base. O "antes" é a mesma bateria rodada no hash base, com a saída guardada. Hoje `os_cenario` 14/15 e `partest` 43/44 são iguais à base (`tools/prototipo/v37/RETOMADA-NUVEM.md:207`).
- `cadc_test.py` sozinho não roda nada; os arquivos são chamados um a um (achado PCM-COD-09).

---

## 1. Missão e princípios, em ordem de prioridade

**Missão:** a OM não para por falta de peça que poderia ter sido prevista. Peça, dinheiro e máquina ficam explicados por um fato registrado uma vez, por quem tem a competência.

1. **Fato físico verdadeiro.** Um estado, um estoque e um local de peças (RN-042 l.244). O saldo muda só por movimento (RF-SUP-003 l.2585; 8.3 l.2833).
2. **Autorização certa.** O responsável de manutenção aprova a OM; o agrônomo nunca aprova (CMD-42 l.2825; 47.4 l.7728). Dinheiro e consumo da OM só passam com alçada: a OM é autorizada pelo valor estimado antes de liberar (PCMS-G07) e a compra pela alçada do pedido (PCMS-G02).
3. **Máquina segura.** Ativo bloqueado não opera; liberar o ativo exige teste (RF-AST-005 l.2570; 47.5 l.7738). Bloco 2.
4. **Custo uma vez.** Só entra o consumido ou aceito (CAL-04 l.4249; PCM-09 l.7803).
5. **Ninguém redigita.** Item, quantidade, OM, ativo, unidade, local e recebedor são herdados; cada papel age na própria tela (AGENTS §3.3).
6. **Nenhuma tela e nenhuma coluna nova.** As condições viram selos com o vocabulário da 8.4.3 (l.2962) e os "selos correspondentes" da 47.5 (l.7740). Os selos novos estão na proposta à v3.10 (DECISOES.md §6).
7. **Trava só com dano nomeado.** Falta de peça trava, porque protege o estoque. O conflito com O.S. de produção não é aceito pela manutenção: a gerência decide dentro da alçada, com alternativa explícita (47.8 l.7820, 7823). O resto vira aviso.

---

## 2. Arquitetura do ciclo

### 2.1 Diagrama
```
 Vencimento (MA-03 · Gerar, já existe) ─┐   Falha (Bloco 2: MA-02 → Criar ordem)
                                        ▼
            OM [A liberar] · selo "Aguardando aprovação · Otávio"
                                        │ APROVAR ORDEM (CMD-42) + autorização econômica (G07)
              ┌─────────────────────────┴──────────────────────────────┐
              ▼                                                        ▼
   REQ da OM (uma só), cobertura planejada                falta → SC "A cotar" (M07, M08)
   por linha, SEM reserva (M05)                                        │ CMP: convites a homologados → alçada
              │                                                        ▼
              │                                     PC-201 "Aprovado" · prev. versionada (M11)
              │                                                        ▼
              │                                     EST etapa 1: NF contra o PC → lote no Almox. oficina,
              │                                     livre · SC "Atendida" (M12, M13)
              ▼                                                        │
   cobertura 100% ◀─────────────────────────────────────────────────────┘
              │ LIBERAR SERVIÇO (CMD-06): reserva 100% por lote (CMD-44, DEC-2609-13) — M09
              ▼
   OM [Liberadas] → EST etapa 2: entregar a REQ ao mecânico (CMD-16) → custódia (M14)
              │ Iniciar → [Em execução] → Concluir: aplicado ≤ custódia vira consumo; excedente → conferência (M15)
              ▼
   OM [Em conferência] → EST etapa 3: devolução conferida (CMD-45) → custódia 0 (M17)
              ▼
   ENCERRAR ORDEM → custo = consumido × preço do lote + horas × custo-hora (C01) → [Encerradas]
```

### 2.2 Passos, quem move, modo e trava

Modo: **T** mesma transação (`cenMudar`) · **D** derivado na leitura · **R** registro de processo da CMP (`talhao-os-compras-v1`). As integrações dos Blocos 2 a 7 estão no Anexo B.

| # | Passo | Quem | Tela | Efeito | Modo | Regra |
|---|---|---|---|---|---|---|
| 1 | Vencimento vira preventiva | PCM | MA-03 | OM em A liberar, sem duplicar o ciclo (RF-AST-003 l.2568) | T (existe) | — |
| 2 | Aprovar ordem | Otávio | MA-04 | `o.aprov`, `o.autEcon`, REQ sem reserva, SC da falta | T | M05, M07, G07 |
| 3 | Cotar e aprovar a compra | Ana (CMP) | CMP 1-5 | Andamento em `proc['SC-041']`; PC no cenário | R + T | M10, M11 |
| 4 | Receber | Rui | EST 1 | Lote com o preço do PC; SC Atendida | T | M12, M13, M25 |
| 5 | Liberar serviço | Otávio | MA-04 | Reserva 100% por lote; Liberadas | T | M09, M09b |
| 6 | Entregar | Rui → Zé | EST 2 | Lote → custódia | T | M14 |
| 7 | Iniciar e concluir | Zé (na MA-04 até o Bloco 6) | MA-04 | Consumo ≤ custódia; excedente em conferência | T | M15, M16 |
| 8 | Receber devolução | Rui | EST 3 | Apta → livre; imprópria → quarentena | T | M17 |
| 9 | Encerrar | Otávio | MA-04 | Custo gravado; Encerradas | T | M18, C01 |
| — | Selos, KPIs, linha de SC na CMP | — | MA-04, CMP 1 | Leitura | D | §5.2, §7 |

### 2.3 Máquinas de estado

| Objeto | Estados | Invariante |
|---|---|---|
| OM | A liberar → Liberadas → Em execução → Em conferência → Encerradas; ou Cancelada (fora do quadro; "Cancelamento pendente" em A liberar enquanto houver custódia) | A fase muda só por comando |
| REQ de OM | Solicitada → Reservada (na liberação) → Entregue → Conciliada; ou Cancelada (nada entregue) | Conciliação por linha (C06) |
| SC | A cotar → Em cotação (congela em "Enviar convites") → Pedido → Atendida; ou Cancelada (com motivo) | Uma SC "A cotar" por tipo e origem Manutenção (M08) |
| PC de material | Aprovado → Recebido parcial → Recebido; ou Cancelado | Recebido acima da tolerância exige reaprovação (G02) |

---

## 3. Modelo de domínio

### 3.1 Cenário: o estado único (seed do Bloco 1)
```js
CEN0 = { v:6, rev:0,                       // 1a: v=4 (man); 1b: v=5 (lotes, REQs, scs, recibos); 1c: v=6 (pedidos)
  ordens, reqs, lotes, movs, ocorr, app,   // como hoje (cenario.py:17-81); confs e ajustes nascem no uso (cenario.js:107, 182)
  man:{ ativos, ordem, planos, ordemPlanos, vinc, oms, abast, ach, prop, seq:235, seqpm:11, hoje, horiz, antiga, custoh:320, maxdia, esp,
        itens:{ 'KIT-MF7719':{ nome:'Kit filtros MF 7719', un:'kit', preco:690, grupo:'Peças' } } },   // catálogo, sem saldo (1b)
  scs:{}, pedidos:{}, recibos:{} }
```
- **Ids:** `cenProxId(c, col, prefixo, piso)` = maior número da coleção + 1, com piso. REQ: maior 040 → REQ-041. SC: piso 41 → SC-041. PC: piso 201, contando `c.pedidos` e os PCs fixos (PC-088..095). As safras numeram a partir de PC-101, 10 por safra (`processo_compras.py:24, 175`; 4 safras no seed, PC-101..140); o PC-200 do C8 fica fora das duas séries. O id gerado nunca sobrescreve um existente. Não há `seq` de SC nem de PC (achados PCM-COD-04, PCM-COD-05).
- **Versão por objeto:** OM, linha de REQ e PC têm `ver`, incrementada pelo comando que os altera (PCMS-G04).
- **Campos de bloco futuro** (`serv`, `ret`, condição do ativo) entram no PR que os usar e sobem `v` (achado PCMS-R15).

Formatos (exemplo depois de aprovar a OM-0235 e comprar):
```js
'REQ-041':{ id, os:'OM-0235', dom:'man', estado:'Solicitada', ver, aut:{quem:'Otávio (resp. manutenção)', em},
  itens:[{ cod:'FIL-MF4292', prod:'Filtro de óleo MF 4292', un:'un', lote:'', solicitado:1, entregue:0, consumido:0,
           devolvido:0, custodia:0, quem:'', confirmado:'balcao', ver }] }          // lote definido ao liberar
'SC-041':{ id, tipo:'material', origem:'Manutenção', estado:'A cotar', criada:'2026-09-23', tok:'<não determinístico>', ver,
  itens:[{ cod, prod, un, grupo:'Peças', qtd:1,
           origens:[{ os:'OM-0235', req:'REQ-041', aid:'a03', ativo:'Trator 03', qtd:1, precisa:'2026-09-24' }] }], pcs:['PC-201'] }
'PC-201':{ id, sc:'SC-041', tipo:'material', forn:'F08', valor:160, estado:'Aprovado', ver,
  aprov:{ nivel:'Gestor de suprimentos', quem:'Ana (gestora)', em:'2026-09-23' },
  prevs:[{ data:'2026-09-24', em:'2026-09-23', quem:'Ana (gestora)', motivo:'promessa da proposta' }],   // só acréscimo
  itens:[{ cod, prod, un:'un', qtd:1, preco:160, recebido:0 }] }
'Filtro de óleo MF 4292|OF26-15':{ prod, cod, lote:'OF26-15', local:'Almox. oficina', un:'un', fisico:1, quarentena:0, reservado:0,
  validade:'', preco:160, origem:{ sc:'SC-041', pc:'PC-201' } }
OM: o.aprov:{quem,em}, o.autEcon:{quem,nivel,valor,em}, o.req, o.janIso, o.espera:{ini,fim}, o.conflito.dec, o.ver
```
- `prevAtual(pc)` = `prevs.at(-1).data`. Não há segundo campo `prev` (achados A05, PCMS-R10).
- No software real, dinheiro e quantidade em decimal (ENG-013).

### 3.2 Movimentos e sinais (achado PCM-COD-10)
`qtd` não tem sinal; o efeito no lote vem do tipo:

| Tipo | físico | reservado | quarentena | REQ (linha) |
|---|---|---|---|---|
| `recebimento-nf` | + qtd | — | + qtd se `apto=false` | — |
| `inspecao` | — | — | − qtd | — |
| `reserva` | — | + qtd | — | — |
| `estorno-reserva` (novo) | — | − qtd | — | — |
| `entrega` | − qtd | − `res` (parte que saiu da reserva; novo campo) | — | entregue, custódia + qtd |
| `consumo` | — | — | — | custódia − q, consumido + q |
| `devolucao` | + qtd | — | + qtd se `apto=false` | custódia − qtd, devolvido + qtd |
| `ajuste` | + dif | — | — | — |
| `contagem`, `recebimento` (confirmação no app, `cenario.js:123`), `sc` (novo), `autorizacao` (novo) | — | — | — | — |

Todo movimento grava `tipo, quem, em, origem (web|app), req, os, ped, sc, chave` (PCMS-G03).

### 3.3 Cadastros reutilizados (sem cadastro paralelo, 47.1 l.7694)
- **CD-04 Pessoas.**
  - Novo `p11` "Otávio", responsável de manutenção (sintético), com as habilidades `'Aprovar O.S. de manutenção'` e `'Liberar ativo'` (entram em `HABILIDADES`, `cad_ativos_pessoas.py:28`, e em `_ORDEM`, l.38).
  - Zé é o mecânico (`dados_cad.py:86`).
  - Rui é o almoxarife no CD-04 (override em `cad_ativos_pessoas.py:34-37`) e em todo o cenário (`cenario.js:77, 87, 98, 142`). O dado bruto `dados_cad.py:84-85` diz Paula almoxarife e Rui conferente, mas a tela já corrige. Nada a renomear.
  - Ana é gestora; na CMP acumula comprador e aprovador no nível Gerente da fazenda da G02 (`processo_compras.py:19`). O PRD admite acumular papéis (2.1 l.195).
- **CD-05 Parceiros.** F08 (Peças e Lubrificantes) e F09 (Peças), fictícios, homologados, com e-mail autorizado e CNPJ sintético de `D2.cnpj_valido`. Parceiros 20 → 22.
- **CD-06 Produtos.**
  - Grupo Lubrificantes entra **só** em `dados2.py:682`; `dados_cad.GRUPOS` (l.117) herda. Logo após a l.117: `assert len(GRUPOS)==len(set(GRUPOS))`. O CD-05 herda o grupo na homologação e na cobertura (`cad_parceiros.py:115, 176, 234`).
  - `GRUPO_NAT['Lubrificantes']='3.1.04'`; `CONTROLE_GRUPO['Lubrificantes']='Só lote'` (`dados_cad.py:119-123`).
  - `UNIDS` + `'kit'` (`cad_produtos_estrutura.py:30`).
  - Local `l11` "Almox. oficina", Santa Rita, Almoxarifado (`dados_cad.py:135`); `LOCAIS` do EST (`processo_estoque.py:19`).
  - `SEM_VALIDADE` + Peças e Lubrificantes (`processo_estoque.py:27`).
  - Peças "Sem lote" usam lote interno `OFaa-nn`; `cenLoteInterno(c)` = maior `nn` do ano + 1.
- **CD-07:** 3.1.05 (peças), 3.1.04 (lubrificantes), CC-OFI. Uso no Bloco 7.

### 3.4 Catálogo de manutenção (14 itens, `dados_cad.ITENS_MAN`)
- **11 de `ITENS`** (`dados_manutencao.py:67-77`): Lubrificantes OL-1540, OL-HID68 e GR-EP2; Peças, os outros 8.
- **3 códigos novos** para as corretivas hoje com `item=''`: `BOM-HID-6M` R$ 3.600 (l.197), `MANG-AP-6M` R$ 250 (l.198), `ROL-ELEV-7250` R$ 640 (l.180).
- `dados_manutencao.ITENS` deriva de `ITENS_MAN`.

### 3.5 Materiais × serviços
O Bloco 1 trata só de materiais. O serviço de terceiro está no Anexo B (Bloco 3): SC e PC do tipo serviço, com fornecedor homologado no grupo "Serviços de manutenção" (l.1752), medição e aceite antes do título.

---

## 4. Regras numeradas e testáveis

Cada regra traz enunciado, mensagens exatas, dano evitado, fonte e PR. Os números estão no §10; os testes, no §11 (U-nn e F-nn); o aceite, no §12. As regras dos Blocos 2 a 7 estão no Anexo A.

### 4A. Materiais

- **PCMS-M01 · Um estado.** Manutenção, O.S., Estoque, App, SC e PC vivem em `talhao-os-cenario-v1`. `cenOuvir` atualiza os outros quadros. Dano: saldo divergente (RN-042 l.244). PR 1a.
- **PCMS-M02 · Um catálogo.** Toda peça de OM tem código do CD-06; as OMs semeadas não têm `item=''`. Dano: corretiva fora da reserva e do custo (47.4 l.7726). PR 1a (catálogo) e 1b (códigos nas OMs semeadas).
- **PCMS-M03 · Saldo só por movimento.** Toda escrita em `fisico`, `reservado` ou `quarentena` acontece em função de `cenario.js` que chama `cenMov` na mesma função. As funções `man*` só chamam esses ajudantes. A prova é a conciliação C06; o teste estrutural é o grep do §11 (U44). Dano: estoque fabricado (RF-SUP-003 l.2585). PR 1b.
- **PCMS-M04 · Um local.** "Almox. oficina" é o único local de peças no MA, no EST e no CD-06. Sai "Almoxarifado Sede" das telas de manutenção (`dados_manutencao.py:447`; `maquinas.py:578`). PR 1b.
- **PCMS-M05 · Aprovar cria a REQ e a cobertura, sem reservar.** Só Otávio aprova (CMD-42 l.2825; 47.4 l.7728).
  - Cria uma REQ idempotente (`dom:'man'`) e não grava movimento `reserva` (DEC-2609-13 l.12227; DEC-2609-05 l.12220; 72.3 l.12234).
  - **Cobertura planejada** por linha, derivada e sem efeito no lote: mín(solicitado, máx(0, livre do item − solicitado das OMs aprovadas antes e ainda não liberadas)). Falta = solicitado − cobertura. Quantidade em SC ou PC aberto não é cobertura: só muda o selo (§5.2, itens 4-5) e não volta à SC (M08).
  - Aprovar de novo devolve a mesma REQ, sem movimento.
  - Dano: peça sai sem autorização própria (PCM-07 l.7801). PR 1b.
- **PCMS-M06 · Reserva protegida.** A reserva só sai por entrega à própria REQ ou por `estorno-reserva` com motivo (cancelar a OM, reduzir ou retirar a linha). O remanejamento entre OMs é o M26 (Bloco 2). A checagem do livre e da reserva própria fica **dentro** de `cenEntregar`. A contagem abaixo do reservado continua recusada (`cenario.js:109`). Dano: peça reservada desviada. PR 1b.
- **PCMS-M07 · A falta vira SC sozinha.** Sem botão de compra na MA-04.
  - Na aprovação, com autorização econômica vigente (G07), a falta entra na SC "A cotar" com item, quantidade, OM, ativo e `precisa` = janela da OM em ISO (`o.janIso`, de `manAdd(c.hoje,1)` ou da projeção; `dados_manutencao.py:363`).
  - Quando um comando tira livre que cobria OM aprovada (liberar outra OM, ajuste de inventário aprovado), ele avisa antes: "Usar aqui deixa a OM-0235 sem Filtro de óleo MF 4292 (chegou pela SC-041). Confirmar?". Confirmado, a falta da OM afetada entra na SC "A cotar" na mesma transação. Se a OM que liberou tinha linha na SC, a origem passa para a OM afetada, sem mudar a quantidade.
  - Movimento `sc` com a OM de origem.
  - Dano: falta sem dono (54.5 l.8400). PR 1b.
- **PCMS-M08 · Sem compra em dobro.** A SC "A cotar" é única por tipo (material) e origem Manutenção, com destino ao Almox. oficina.
  - Linha identificada por `cod`; origem identificada por (OM, `cod`).
  - Aprovar de novo não duplica linha nem origem.
  - Itens de grupos diferentes ficam na mesma SC; a CMP separa convites por grupo (`processo_compras.py:222`) e PCs por fornecedor (l.240).
  - A SC congela no "Enviar convites" da CMP etapa 3 (o mesmo `env` que leva a "Em cotação", l.258). Depois disso, a falta nova abre a SC seguinte.
  - Isso muda o "uma SC por ordem" de hoje (`dados_manutencao.py:394`).
  - Dano: compra dupla (RF-SUP-004 l.2586; PCM-06 l.7800). PR 1b.
- **PCMS-M09 · Liberar reserva e exige tudo.** Liberar exige, numa só transação:
  - aprovação técnica vigente (CMD-42);
  - autorização econômica vigente (G07);
  - nenhum conflito aberto com produção (M09b);
  - reserva de 100% das linhas por lote (CMD-44, política autorizada pela DEC-2609-13). Lote: o de maior livre (`cenLote`, `cenario.js:42`), uma linha por lote, como o `cenLiberar` (l.55-56).
  - Grava o evento de liberação com a autorização econômica usada (CMD-06 l.2777).
  - Recusas, por item e sem gravar nada: "Aprove a ordem"; a da G07; "Falta peça: Filtro de óleo MF 4292 (livre 0 de 1 un) · SC-041 · Comprador · Ana".
  - Dano: execução sem material ou sem decisão sobre o valor. PR 1b.
- **PCMS-M09b · Conflito com produção é da gerência.** Com conflito aberto, a MA-04 não oferece "Liberar serviço"; o comando recusa com "Conflito com a OS-0420 · decide a gerência (Ana, gestora/PCP) · ou mova a janela dentro da tolerância".
  - Mover a janela dentro da tolerância elimina o conflito sem gerência (`ma_mover`, `maquinas.py:328-367`; `matest.py:64`).
  - A decisão grava `o.conflito.dec = {quem, papel, em, motivo, alternativa, ver}`, com alternativa ∈ {mover janela, substituto, remanejar O.S., aceitar atraso com déficit}. Sem alternativa é recusada (47.8 l.7823). Quem decide é o P9.
  - A mensagem "enviado ao PCP" (`dados_manutencao.py:392`) só aparece com esse registro.
  - Dano: plantio do T4 sem trator na janela, decidido por papel sem alçada (47.8 l.7820). PR 1b.
- **PCMS-M10 · Só Compras compra.** A SC aparece na CMP etapa 1 com origem "Manutenção". Convites só a homologados no grupo do item e com canal autorizado (l.1752; `processo_compras.py:222-226`). Alçada única (G02). Dano: compra com não homologado (RF-SUP-005 l.2587). PR 1c.
- **PCMS-M11 · Pedido aprovado vira fato.** O PC é gravado no cenário na aprovação (`cenGravarPedidos`).
  - Idempotente por (SC, fornecedor): gravar de novo devolve o mesmo PC, sem consumir número.
  - `prevs[0]` = hoje + prazo da proposta, como em `emitir` (`processo_compras.py:436`).
  - Reprogramar na etapa 6 é `cenReprogramarPC(c, pc, data, motivo, quem)`: acrescenta em `prevs`, nunca reescreve. Data anterior a hoje é recusada (l.469-471). Repetir a data vigente não cria entrada. O motivo é o campo atual (l.107). Para PC-2xx, o `pcx` deixa de guardar `prev`.
  - Selo da OM: o item 5 do §5.2, com `prevAtual` e, se houve reprogramação, "(prometido `prevs[0]`)".
  - Dano: atraso apagado pela reprogramação (RF-SUP-012 l.2594). PR 1c.
- **PCMS-M12 · Só o almoxarife recebe**, contra o pedido, com NF e na unidade do pedido.
  - Item "Sem lote" ganha lote interno. A quarentena fica fora do livre (`cenario.js:92-100`).
  - A MA-04 não tem comando de recebimento (a ponte do 1b sai no 1c).
  - Recusas: "Informe a nota fiscal"; "NF <n> já recebida no PC-201" (mesma NF + PC + item, com qualquer chave; FO-18 l.2328); "Unidade diferente do pedido PC-201 (un)".
  - Hoje o formulário tem "kg" fixo nos 4 campos (`processo_estoque.py:78-81`) e nas 3 mensagens (l.307-309); a grade já mostra a unidade da linha (l.388). A 2d trata da unidade fixa por coluna nas grades e não resolve este formulário (achado PCMS-R08).
  - Dano: estoque sem fato físico; quantidade em unidade errada (RF-SUP-007 l.2589). PR 1c.
- **PCMS-M13 · O que chega volta à cobertura de quem pediu.** O recebimento marca a linha da SC como Atendida e grava `lote.origem = {sc, pc}`. Não reserva: a parte apta vira livre e cobre a OM de origem pela cobertura planejada (M05). A parte em quarentena só cobre depois da inspeção. A prioridade "criticidade, depois data" só vale como aviso, até a decisão D5. Fonte: RF-SUP-007 l.2589; 47.4 l.7726; DEC-2609-13. PR 1c.
- **PCMS-M14 · Entrega só para OM liberada e autorizada** (Liberadas ou Em execução, com `autEcon` vigente; CMD-16 l.2787).
  - O recebedor é herdado (mecânico da OM) e corrigível.
  - **"Entregar REQ-0xx inteira"**: uma ação por REQ na etapa 2, sem formulário, com a quantidade "A entregar" de cada linha. O formulário por linha continua para parcial ou troca de recebedor.
  - Linha de OM grava `confirmado:'balcao'`. O chip "Aguardando confirmação no app" e a contagem `nag` (`processo_estoque.py:400-401, 525`) ignoram essas linhas. Mensagem: "Entregue no balcão a Zé (mecânico) · OM-0234".
  - Recusas: "OM-0235 aguarda a liberação na Manutenção (responsável de manutenção)"; a da G07.
  - Dano: peça sem responsável (CMD-16). PR 1b.
- **PCMS-M15 · O consumo nasce só do Concluir, uma vez.** Aplicado ≤ custódia vira `consumo`. O excedente vira "Consumo em conferência" (`confs`, `cenConciliar`), sem baixa e sem custódia negativa. Hoje o sistema baixa `max(planejado, aplicado)` direto do saldo (`dados_manutencao.py:429`). Dano: consumo fictício ou duplo (RN-013 l.215). PR 1b.
- **PCMS-M16 · Aplicado explícito.** Cada linha mostra o chip "Usei tudo (16 L)": um toque explícito, ou a quantidade digitada. Recusa: "Informe o aplicado: Óleo de motor 15W-40". Fonte: AGENTS §3.3 (nada de último valor para quantidade). PR 1b.
- **PCMS-M17 · A devolução passa só pelo EST, conferida.** Apta volta ao livre; imprópria vai à quarentena. Recusa acima da custódia (`cenario.js:83`). Dano: sobra que volta sem conferência (CMD-45 l.2828). PR 1b.
- **PCMS-M18 · Encerrar exige custódia zero e nenhuma conferência aberta.** A recusa é a **mensagem** comum de `cenPodeEncerrar` (`cenario.js:246`): "Sobra em custódia: <item> <qtd> <un>. Receba a devolução no Estoque." O **selo** é outro (§5.2). Dano: custo e saldo errados (RF-SUP-008). PR 1b.
- **PCMS-M19 · Cancelar sem execução** (CMD-46 l.2829; estado Cancelada l.2858; ESTOS-10 l.7110). Uma função do cenário, compartilhada com o `osc_cancelar` da O.S. (`processo_os.py:378-382`).
  - Quem: Otávio, com motivo obrigatório. Só sem trabalho iniciado (A liberar ou Liberadas).
  - Em execução ou depois: recusa "OM-0234 já foi iniciada: dispense o saldo e encerre; trabalho iniciado não se cancela" (o caminho é CMD-47 l.2830 e M18).
  - Efeito: revoga a liberação, bloqueia o Iniciar, estorna só a reserva não entregue (`estorno-reserva`), tira as linhas da OM da SC "A cotar" (a SC vazia vira Cancelada, com motivo). Com PC emitido, a peça chega livre.
  - Com custódia: uma única tarefa "Devolver sobras" na etapa 3 do EST (l.7079); a OM fica em A liberar com "Cancelamento pendente · Rui".
  - Só confirma Cancelada com custódia zero, nenhuma conferência aberta e REQ Conciliada (entregue = devolvido) ou Cancelada (nada entregue). A OM Cancelada sai do quadro e fica no chip "Canceladas", como na O.S. (`processo_os.py:444-448`).
  - O `osc_cancelar` atual baixa a reserva sem movimento (l.381) e marca Canceladas com material entregue. O 1b corrige os dois pela função comum.
  - `manOmCiclo` ignora Cancelada: o MA-03 pode gerar o ciclo de novo.
  - Repetir não duplica estorno, tarefa nem movimento.
  - Dano: custódia órfã e REQ sem conciliação. PR 1b.
- **PCMS-M25 · Peça comprada sem pedido (balcão) é fato registrado e exceção visível.** Caminho emergencial da 47.5 (l.7736).
  - Quem registra: Rui, no EST etapa 1, com o campo "Pedido" = "Sem pedido · regularizar".
  - Campos: NF, item do CD-06, quantidade conferida, preço unitário da NF, OM de destino, com quem está a peça (padrão: mecânico da OM) e **quem autorizou a compra**, quando e o motivo. O padrão de "autorizou" é o aprovador da OM. "Ninguém autorizou" é aceito e a exceção mostra "sem autorização registrada".
  - Efeito, num `cenMudar`: lote interno com `preco` da NF (exceção à C02); `recebimento-nf` com `semPedido:{autorizou, em, motivo}`.
    - OM em A liberar: a peça fica livre e cobre a OM (M05, M13).
    - OM em Liberadas ou Em execução: vai direto à custódia, com `entrega` marcada "regularização NF …" e linha nova na REQ, se preciso (precedente `cenario.js:218-220`).
  - A linha da OM na SC "A cotar" cai pela quantidade recebida; a SC vazia vira Cancelada. Com PC já emitido, a peça do PC chega livre.
  - Exceção visível: selo "Compra sem pedido · regularizar · Comprador · Ana" (informativo) e linha "Regularizar · NF … · OM-…" na CMP etapa 1.
  - PC de regularização: aprovado na alçada normal (P2), nasce "Recebido", vinculado à entrada, nunca aparece para receber no EST. Título e conciliação NF × PC (RF-SUP-011 l.2593): Bloco 7. A regularização pendente não trava o encerramento da OM.
  - Recusas: sem NF; sem OM ("Indique a OM que usou a peça. Compra para estoque passa por Compras."); mesma NF de novo; receber o PC de regularização ("já recebido pela NF …"); "autorizou" vazio ("Indique quem autorizou ou marque 'ninguém autorizou'").
  - Dano: peça instalada que some do estoque e do custo; estoque fantasma por ajuste de inventário. Fonte: 47.5 l.7736; 65.5 l.9202; RF-SUP-007/011. PR 1c.

### 4B. Custo e conciliação

- **PCMS-C01 · Custo da OM** = Σ (consumido × preço do lote) + horas próprias × custo-hora (P1) + Σ valor aceito dos serviços (Bloco 3). Não entram devolvido, reservado, entregue nem planejado. A mesma função calcula a **estimativa** (planejado × preço do lote, do PC ou do catálogo + horas previstas × custo-hora + serviços previstos), usada pela G07 (ENG-011). Fonte: KPI-PCM-10 l.8520. PR 1b.
- **PCMS-C02 · Preço do lote** = preço unitário do PC de entrada (no seed, o `preco` de `ITENS`; na M25, o da NF). PR 1b/1c.
- **PCMS-C05 · Espera por peça registrada** em `o.espera`, da aprovação com falta até a cobertura completa, fora das horas de reparo (CAL-06 l.4293; RF-AST-004 l.2569). PR 1b/1c.
- **PCMS-C06 · Conciliação contínua.** Depois de cada comando, no teste unitário:
  - por linha de REQ: entregue = consumido + devolvido + custódia;
  - por lote (oficina e insumos): físico, reservado e quarentena iguais ao inicial mais os movimentos, pela tabela do §3.2;
  - nenhum valor negativo.
  - PR 1b.

### 4C. Governança

- **PCMS-G01 · Segregação.** Otávio cria a necessidade, aprova e autoriza até o limite; não recebe material nem aprova pedido. Rui recebe e entrega; não cria necessidade. Ana cota e aprova o pedido na alçada (acúmulo admitido, l.195). No protótipo os perfis são fixos e cada movimento grava `quem`; no software real, vira permissão (RF-GOV-002 l.2673).
- **PCMS-G02 · Alçada única de compra** (`dados2.py:705`): até R$ 50.000 Gestor de suprimentos; até R$ 300.000 Gerente da fazenda; acima, Direção. Recebido acima de pedido × (1 + P3) exige reaprovação.
- **PCMS-G03 · Auditoria.** Todo comando grava movimento com os campos do §3.2. Nenhum saldo é editável na tela.
- **PCMS-G04 · Idempotência e versão esperada** (ENG-021/022/024/028 l.5285-5292; 8.2.1 l.2805; DEMO-18 l.4744; ACE-05 l.5784; AGENTS §4).
  - Todo comando (aprovar, autorizar, liberar, decidir conflito, entregar, devolver, receber, gravar PC, reprogramar, concluir, encerrar, cancelar) leva `chave` e `ver`.
  - A chave nasce quando quem age abre a ação (formulário `g2open` ou botão do passo), fica no estado da tela, é reenviada em qualquer repetição e sai só com a confirmação. Dois toques no mesmo formulário usam a mesma chave; duas entregas parciais são dois formulários.
  - `cenMudar(self, fn, cmd)` com `cmd = {chave, nome, obj, ver, payload}`: recibo existente com o mesmo nome e payload é devolvido sem aplicar `fn` e sem subir `rev` (`r.nada`); mesma chave com payload diferente é conflito; `ver` diferente é conflito ("Mudou desde que você abriu: <estado atual>. Revise e confirme."). O recibo grava na mesma mudança do efeito. Rejeição não grava recibo. `cenReset` limpa `c.recibos`.
  - Não usar o `c.rev` global (`cenario.js:19`) como versão: daria conflito falso.
  - Continuam, independentes da chave: a checagem documental NF + PC + item (M12) e a repetição por estado (M05).
  - Dano: movimento ou custódia duplicados (S2); entrega parcial legítima barrada como repetição. PR 1b (OM e EST) e 1c (CMP e recebimento).
- **PCMS-G05 · Nenhuma automação aprova, libera ou paga. Compra automática só com a política P8, que vem desligada.** A inteligência (§6) abre o comando de quem tem competência. Fontes: aprovar e liberar, RF-AI-002 l.2703, l.6064, l.3063 (a liberação automática de água sem insumos, 41.8 l.2968, não se aplica à OM); pagar, l.2404; comprar, 65.5 l.9202 e AGENTS §2.
- **PCMS-G06 · Dados sintéticos, nomes fictícios e sem segredo** (ENG-017).
- **PCMS-G07 · Autorização econômica da OM** (CMD-06 "equivalente CF-02 de manutenção" l.2777; 47.5 l.7740; RF-GOV-002 l.2673).
  - Valor: a estimativa da C01.
  - Limites: as faixas da G02 aplicadas à estimativa (P7, default). Até R$ 50.000, a aprovação de Otávio registra também a autorização econômica, num toque. Acima, autoriza o Gerente da fazenda ou a Direção, na faixa da G02.
  - `o.autEcon = {quem, nivel, valor, em}`, gravado com movimento `autorizacao`.
  - Acima do limite: a OM fica em A liberar com "Aguarda autorização econômica · Gerente da fazenda"; a REQ nasce, mas a SC só abre depois de `autEcon`. O painel da OM mostra a ação "Autorizar valor · Gerente da fazenda (Ana)" só nesse caso.
  - Recusas: "Autorização econômica pendente · <nível>" (liberar e entregar); "Acima da alçada do responsável de manutenção: autorize com o Gerente da fazenda"; quem autoriza não altera o próprio limite.
  - A peça comprada para OM já autorizada não pede nova autorização da OM; a compra segue a G02, sem dupla aprovação do mesmo valor.
  - Dano: gasto de estoque e mão de obra sem decisão de quem responde pelo valor. PR 1b.

---

## 5. Telas (nenhuma tela nova)

### 5.1 Mudanças do Bloco 1

| Tela | Pergunta da tela | Mudança | PR |
|---|---|---|---|
| MA-01..05, PM | (mantidas) | Prefixo do cenário: `MAN0 = CEN0.man`, DM.JS só nessas telas. "Restaurar demonstração" avisa que restaura O.S., Estoque, App e Manutenção juntos | 1a |
| MA-04 Ordens (`maquinas.py:376-560`) | "O que esta ordem precisa para andar, e quem age agora?" | Passo principal: **Aprovar ordem** → (selo, dono e link "Ver SC-041 em Compras") → **Liberar serviço** → "Aguarda entrega · Rui" (link EST etapa 2) → Iniciar → Concluir (chip "Usei tudo" por linha) → (sobra: link EST etapa 3) → **Encerrar ordem**. Com conflito: o passo é o conflito, com "Mover a janela ›" (l.497). Painel de peças: Planejado · Coberto · Reservado · Entregue · Em custódia · Aplicado · Origem. Faixa de KPIs (§7) no lugar da l.552. Ação secundária "Cancelar sem execução" (M19; mesmo rótulo da O.S., `processo_os.py:20`, e do PRD l.6856). Saem "Solicitar compra" e "Resolver sobras" (1b) e "Registrar recebimento" (1c) | 1b/1c |
| MA-03 | "O que vence, e tenho peça para isso?" | Ação "Decisão da gerência" no painel do conflito, ao lado de "Mover" (M09b) | 1b |
| PM | (mantida) | Selo de saldo lê o livre dos lotes (`maquinas.py:893-894`) | 1b |
| EST (`processo_estoque.py`) | "O que tenho de receber, entregar ou conferir hoje?" | Etapa 1: pedidos do cenário (PC-2xx) com a unidade do pedido no formulário e nas mensagens; lote interno; "Sem pedido · regularizar" (M25); bloco só de leitura "Peças pedidas pela manutenção" (SCs abertas). Etapa 2: linhas OM · ativo · mecânico; motivo por destino (l.188); "Entregar REQ inteira". Etapa 3: custódia da oficina. Etapa 4: Almox. oficina. Etapa 6: OM, PC e SC; consumo rotulado pela origem ("Consumo registrado na OM" para `origem:'web'`, l.219, 231) | 1b/1c |
| CMP (`processo_compras.py`) | "O que preciso comprar, de quem e até quando?" | Etapa 1: linhas "Manutenção · SC-041 · item · OM · precisa em" na coluna "Solicitação de compra" (l.73), com "Manutenção" na coluna Safra, acima das safras quando vencem antes; linha "Regularizar · NF …" (M25). Escolha como `{tipo:'safra'|'sc', id}`. Etapa 2: sem CAL-01 para SC; `falta` = menor `precisa` das origens. Etapa 5: grava o PC no cenário. Etapa 6: `prevAtual` e `cenReprogramarPC`. Andamento em `proc['SC-041']` | 1c |
| Nome da tela | — | "Compras" no menu (`ui37.py:41`, que também monta a trilha, l.264-267), no `title` de `shell37` (`processo_compras.py:146`, que alimenta `<title>` e `<h1>`, `ui37.py:294, 326`), no docstring e no comentário (l.2, 150), em `nav37_md.py:30`, `gen37/GUIA-PROCESSOS.md:6` e `areas/indice.py:17`. Subtítulo: "Da solicitação (safra ou manutenção) ao pedido entregue: cote, compare, aprove e acompanhe na mesma tela." Ficam, de propósito, os atalhos de insumo com o nome antigo (FORA-DE-ESCOPO.md §4) | 1c |
| CD-06, CD-05, CD-04 | — | §3.3 | 1a/1b/1c |

### 5.2 Selos da OM (derivados; mostrar o principal com dono e prazo)
Em ordem de pendência principal. Os selos atuais que não são de suprimento (Vencida, Pendência, Leitura a confirmar) continuam.
1. Aguardando aprovação · Otávio
2. Aguarda autorização econômica · Gerente da fazenda (G07)
3. Conflito · OS-0420 · Ana (gerência) (M09b)
4. Falta peça · SC-041 · Comprador · Ana
5. Aguarda PC-201 · prev. dd/mm (prometido dd/mm) · F08 (M11)
6. Compra sem pedido · regularizar · Comprador · Ana (M25; informativo)
7. Pronta para liberar · Otávio
8. Aguarda entrega · Rui
9. Consumo em conferência · Rui (já existe, `cenario.js:144`)
10. Sobras a receber · Rui — o mesmo selo da O.S. (`processo_os.py:242`)
11. Cancelamento pendente · Rui (M19)

---

## 6. Inteligência (gatilho → um toque → por quê)

O toque abre o comando de quem tem a competência, já preenchido. Nada aprova, libera ou paga sozinho; compra automática só com a P8 ligada (PCMS-G05). Linhas dos Blocos 2 a 4: Anexo B.

| Gatilho | Mensagem | Um toque | Por quê | PR |
|---|---|---|---|---|
| OM Liberada com REQ não entregue | "OM-0234 liberada · kit e 16 L aguardam entrega" | EST etapa 2 → Entregar REQ inteira | A oficina não espera no balcão | 1b |
| OM em conferência com custódia > 0 | "4 L com Zé desde 23/09" | EST etapa 3 → Receber devolução | Sem devolução, a OM não fecha (M18) | 1b |
| Peça recebida cobre OM aprovada | "Filtro MF 4292 chegou para a OM-0235 · libere para reservar" | MA-04 → Liberar serviço | Sem reserva na aprovação, quem libera primeiro leva (M13) | 1c |
| Data necessária < hoje + prazo da proposta mais rápida | "SC-041: a proposta mais rápida chega em dd/mm; a OM-0235 precisa em 24/09" | CMP → Abrir SC-041 | A compra vai atrasar a máquina | 1c |
| Proposta mais barata chega depois da data necessária | "F09 é R$ 4,80 mais barata, mas chega em 29/09; a OM-0235 precisa em 24/09" | CMP etapa 4 (mantém F08) | Preço não vence sozinho (RF-SUP-005) | 1c |
| PC de origem OM com previsão vencida e não recebido | "PC-201 atrasado · OM-0235 parada" | CMP etapa 6 → Reprogramar previsão | O retorno fica condicional (47.8 l.7821) | 1c |
| Duas OMs pedem o mesmo item | Sem mensagem: a SC é única (M08) | — | — | 1b |

---

## 7. Indicadores do Bloco 1

Até quatro cartões na faixa da MA-04 (l.8505). Cada indicador tem um dono, escrito "papel · pessoa". Metas são parâmetro do dono (P6), revistas depois de 60 dias de dados reais; não são referência de mercado. Indicadores dos Blocos 4 e 7 (KPI-SUP-05, KPI-PCM-10, KPI-PCM-02.MTTR e .RESTAURACAO, PCMS-I7): Anexo B.

| ID | Fórmula | População | Meta (default) | Dono | Onde | PR |
|---|---|---|---|---|---|---|
| **PCMS-I1 Espera por peça** (local; relaciona-se ao KPI-SUP-04 l.8547 e à "espera por peças", l.7746, 8494) | (a) Espera concluída = data da cobertura completa − data da aprovação com falta; distribuição (mediana e maior), não só média. (b) Envelhecimento das que ainda esperam: hoje − aprovação com falta, por OM, com selo e dono | (a) OMs cuja espera terminou no período, encerradas ou não; (b) OMs com falta abertas | Linha de base nos 60 primeiros dias | Comprador · Ana | MA-04, CMP etapa 6 | 1c |
| **KPI-PCM-08 Backlog por especialidade** (l.8518) | HH pendentes = Σ `o.tempo` das OMs em A liberar, Liberadas e Em execução, por `o.esp` (`dados_manutencao.py:178-201`), em três componentes: pronto para executar ("Pronta para liberar", Liberadas, Em execução), falta de peça (selos 4-5 do §5.2) e pendência técnica (selos 1-3; no Bloco 2, teste e ativo bloqueado). Semanas equivalentes = HH ÷ capacidade semanal (P10); sem P10, "não calculável" (nunca 0) | OMs não concluídas | Sem meta inicial | Otávio | MA-04 | 1b |
| **KPI-SUP-06 Custódias pendentes** (l.8551) | Quantidade e valor em custódia por OM e por responsável, com a idade desde a entrega ou a conclusão | Linhas de REQ de OM com custódia > 0 | 0 linhas com mais de 7 dias | Almoxarife · Rui | MA-04, EST etapa 3 | 1b |
| 4º cartão | "A liberar" (contagem que já existe) | — | — | Otávio | MA-04 | 1b |

- "R$ 0 em OM encerrada" não é meta: é invariante da M18, testado.
- O I2 do v1 (prontidão) saiu: o componente "falta de peça" do KPI-PCM-08 e a PCMS-I1 com envelhecimento respondem à mesma pergunta (l.8478: sem duplicar por sinônimo).
- "Retorno do Trator T1" fixo (`maquinas.py:552`) sai da faixa; volta derivado no Bloco 2.

---

## 8. Integrações

Integradas ao §2.2 (coluna Modo). As dos Blocos 2 a 7 estão no Anexo B. O ERP está em FORA-DE-ESCOPO.md. Duas regras de integração do Bloco 1:
- `proc['SC-x']` só vale com `key` igual à da SC no cenário atual: `solDe('SC-…')` usa `JSON.stringify([sc.id, sc.itens, sc.tok])`, e o `procLer` (`processo_compras.py:185-186`) recusa andamento antigo. Ao receber o evento de `CEN_KEY`, se `solDe(st.saf)` vier nulo ou com outra `key`, a CMP descarta `porSaf[id]` e o estado em memória (`trocaSafra`, l.193-197).
- `cenReset` (`cenario.js:12`) passa a limpar `proc['SC-*']` em `talhao-os-compras-v1` e grava o cenário inicial (`cenSave(cenGet())`, padrão de `mobile.py:345`). Os cinco botões de restaurar (MA; `processo_os.py:812`; `processo_estoque.py:573`; `mobile.py:345`; `agronomia.py:804`) ficam iguais; as mensagens citam também a Manutenção.

---

## 9. Leveza: orçamento de atrito

**Regra de contagem.** Conta como toque cada acionamento de botão de comando, chip, abertura de painel e confirmação de aviso. Navegação entre telas conta à parte. Campo digitado conta como campo. O teste `fluxo` conta os cliques instrumentados no C2 em duas medições: no commit base do PR 1a (o "antes", com hash) e no candidato. Contagem feita à mão não vale como "antes".

**Estimativa lida no código (a medição a substitui):**

| Papel · tela | Hoje no C2 | Depois no C2 | Por quê |
|---|---|---|---|
| Responsável · MA-04 | 4: Solicitar compra, Registrar recebimento, Liberar, Encerrar (`maquinas.py:384-390`), dois deles fatos de outro papel | 3: Aprovar, Liberar, Encerrar | Corte real |
| Mecânico · MA-04 (até o Bloco 6) | 3 toques (Iniciar, "Marcar pendentes como feitas", Concluir) + 1 campo (leitura) | 5 toques (+ 2 chips "Usei tudo") + 1 campo | Aplicado explícito (M16) evita consumo fictício (RN-013) |
| Almoxarife · EST | 0 | Receber: abrir + salvar; NF, quantidade na nota, conferida e apta digitadas (Pedido herdado da linha do PC-201; lote gerado; local e validade herdados). Entregar: 1 toque ("Entregar REQ inteira") | NF e entrega com custódia passam a existir |
| Comprador e aprovador · CMP | 0 | N, medido na compra SC-041 → PC-201 | Cotação com alçada passa a existir |

**Manchete:** "Responsável: 4 → 3, sem fato de outro papel. O cenário sobe de X para Y porque passam a existir nota fiscal, cotação com alçada, entrega com custódia e aplicado explícito." X e Y saem da medição. Reduzir toques nunca remove a NF, a conferência física nem o aplicado explícito (AGENTS §3.3).

**Teto da compra de 1 item:** na primeira medição, registrar N. Se N passar de 6 (uma ação por etapa, `processo_compras.py:16`), abrir caso de produtividade antes do aceite humano.

---

## 10. Seed e casos plantados (fonte única dos números)

Tudo sintético. Hoje da demonstração: 23/09/2026 (`dados_manutencao.py:19`; `dados2.py:5`). Custo-hora R$ 320 (P1). Preços de `dados_manutencao.py:67-77`.

**Lotes do Almox. oficina** (PR 1b; `OF26-nn` na ordem de `ITENS`; o 02 não é usado porque o FIL-MF4292 começa sem saldo):
KIT-MF7719 OF26-01 2 kit · KIT-JD OF26-03 3 · KIT-U3030 OF26-04 3 · KIT-C7250 OF26-05 1 · KIT-CB01 OF26-06 1 · OL-1540 OF26-07 120 L · OL-HID68 OF26-08 200 L · GR-EP2 OF26-09 18 kg · VED-MB OF26-10 1 · DSC-15 OF26-11 24 · BOM-HID-6M OF26-12 0 · MANG-AP-6M OF26-13 0 · ROL-ELEV-7250 OF26-14 0.
Total: 13 lotes, 10 com saldo (executado). O primeiro lote interno gerado é o OF26-15.

**Requisições semeadas** (PR 1b; 032-034 estão livres; as existentes são REQ-021..025, 031, 035, 036, 038..040, executado; 11 + 3 = 14):
- REQ-032 · OM-0221: ROL-ELEV-7250, 2 entregues, 2 consumidos. Conciliada.
- REQ-033 · OM-0230: KIT-U3030 3 entregues, 1 consumido, 2 em custódia; OL-HID68 40/40; GR-EP2 1/1.
- REQ-034 · OM-0233: BOM-HID-6M 1 e MANG-AP-6M 2, entregues e em custódia de Zé (consumo no Bloco 2).

**Fornecedores e propostas** (PR 1c; `dados2.py`): `PROPOSTAS['Peças']` = [F08 fator 1,00, prazo **1 dia**, CIF; F09 fator 0,97, prazo 6 dias, CIF]. `PROPOSTAS['Lubrificantes']` = [F08 fator 1,00, prazo 2 dias, CIF].

**Janela e chegada (executado em node e python):** gerar no MA-03 cria OM-0235 (a03, PM-02, crit Alta, janela 24/09), OM-0236 e OM-0237. A OM-0235 precisa em 2026-09-24. F08 chega 24/09 e não atrasa (a regra é `chega > falta`, estrita, `processo_compras.py:232`). F09 chega 29/09 e atrasa. A escolha padrão (l.235) é F08; F09 exige justificativa (l.236, 441).

| Caso | Base | Roteiro | Resultado esperado | PR |
|---|---|---|---|---|
| **C1 Da prateleira** · OM-0234, Trator 02 (a02), Revisão 250 h, conflito com a OS-0420 | `dados_manutencao.py:199-204` | Aprovar → MA-03 "Mover OM-0234 para 29/09" → Liberar → EST entrega a REQ (1 kit, 16 L) → Iniciar → Concluir (kit 1, 12 L) → Encerrar (recusado) → EST devolução de 4 L apta → Encerrar | Aprovar: REQ-041, nenhuma reserva. Estimativa (G07) **R$ 2.738,00** (690 + 16 × 28 + 5 × 320), dentro do limite do Otávio. Liberar: reserva OF26-01 1, OF26-07 16. Entrega: físicos 1 e 104. Custódia final 4 L. Devolução: OF26-07 **108**. Custo **R$ 2.626,00** (690 + 12 × 28 + 5 × 320), o mesmo de `ma_correcoes_om_test.py`; R$ 2.738,00 seria custo com os 16 L entregues (executado) | 1b |
| **C1b Conflito decidido** | C1 | Aprovar → Liberar recusado (decide a gerência) → Ana registra "substituto para a OS-0420" com motivo → Liberar | Libera; MA-03 mostra quem, quando, motivo e alternativa | 1b |
| **C2 Falta e compra** · OM-0235, Trator 03 (a03, MF 4292) | `dados_manutencao.py:31, 68`; MA-03 Gerar | MA-03 Gerar → MA-04 Aprovar → Liberar (recusado) → CMP: SC-041 → convites F08 e F09 → enviar → manter a proposta sugerida (F08) → aprovar → PC-201 → EST: NF, 1 un apta → MA-04 Liberar → EST entrega → Iniciar → Concluir (Usei tudo × 2) → Encerrar | Aprovar: REQ-041 (cobertura óleo 12/12, filtro 0/1), SC-041 "A cotar" 1 un, precisa 24/09. PC-201 F08 **R$ 160,00**, prevs[0] 24/09. Lote OF26-15 1 un livre. Custo **R$ 1.776,00** (160 + 12 × 28 + 4 × 320); com F09 justificada, **R$ 1.771,20** (155,20 + 336 + 1.280) (executado). Espera (PCMS-I1): 1 dia no teste unitário com recebimento datado 24/09; 0 dia no navegador, porque a data da demonstração é fixa | 1b (ponte) / 1c |
| **C3 Sobra existente** · OM-0230, Pulverizador PJ-3030 (a05), Em conferência | l.185-191 | Encerrar (recusado) → EST recebe 2 kits aptos → Encerrar | OF26-04 3 → **5**. Custo **R$ 4.392,00** (520 + 40 × 24 + 32 + 9 × 320) (executado) | 1b |
| **C11 Balcão** · OM-0235 | C2 até aprovar | Zé traz 1 Filtro MF 4292 com a NF sintética "NF B-0001" a R$ 175,00 → Rui registra "Sem pedido · regularizar" para a OM-0235, autorizado por Otávio → Liberar → entregar → iniciar → concluir (1 un, 12 L) → Encerrar | OF26-15 1 un livre, cobrindo a OM-0235. SC-041 Cancelada, sem a linha. CMP mostra a regularização. PC de regularização aprovado na primeira faixa da G02 (Gestor de suprimentos), já "Recebido", ausente do EST etapa 1. Custo **R$ 1.791,00** (175 + 336 + 1.280) (executado) | 1c |
| **OM sintética acima do limite** (só no teste unitário) | — | 15 BOM-HID-6M + 4 h | Estimativa **R$ 55.280,00** (executado) > R$ 50.000 | 1b |

---

## 11. Ordem de execução

### 11.1 Acordo curto (AGENTS §3.4)
```text
ID / resultado útil / persona: PCMSUP-B1 · a OM obtém peça do estoque único ou da compra, com cobertura, reserva na liberação, entrega, consumo, devolução e custo verdadeiros · Otávio (resp. manutenção), Ana (comprador e aprovador na CMP; gerência no conflito), Rui (almoxarife), Zé (mecânico)
Requisitos do PRD e fora do escopo: DEC-2609-13 l.12227; 47.4 l.7726-7728; 47.5 l.7736-7740; CMD-06/16/42/44/45/46 (l.2777, 2787, 2825, 2827-2829); RF-SUP-003..008, 011, 012 (l.2585-2594); PCM-06/07 (l.7800-7801); RN-013/042; ENG-021/022. Fora: Blocos 2 a 7 (Anexo) e FORA-DE-ESCOPO.md
Autor / revisor / integrador: Claude / Codex (tarefa, roteiro, reprodução, contraexemplos) / Codex
Base (commit ou hashes) / arquivos sob responsabilidade: hash do PR da TABELAS-FOCO 2d (hoje 0cf6f90) ou o pós-merge; arquivos de §11.2
Aceite e comando de verificação: §12; bateria de §0.3
Estado / impedimento / próximo passo: especificado · aguarda os portões de §0.2 · começar pelo 1a
```

### 11.2 PRs: a menor sequência que mantém o C2 funcionando a cada PR

**PR 1a · Um estado** (sem mudar regra; o C2 de hoje continua igual)
- `cenario.py`: `seed()` v=4 com `man`; `js_prefixo()` emite CEN0 (com `man`) e `cenario.js`. DM.JS **não** entra aí.
- `dados_manutencao.py`: `MAN0 = CEN0.man`; `manGet = () => cenGet().man`; `manMudar(self, fn) = cenMudar(self, c => fn(c.man, c))`; `manOuvir` escuta `CEN_KEY`; `manReset = cenReset`. `c.man.itens.saldo` e as funções `man*` continuam iguais: só muda o acesso. `manReceber` fica.
- `cenario.js`: `cenMudar` aceita `r.nada` (não grava) e `r.st` (hoje só em `manMudar`, `dados_manutencao.py:275-279`); `cenReset` limpa `proc['SC-*']` e grava o inicial (§8).
- `areas/maquinas.py`: as 6 telas usam `cenario.js_prefixo()` + `DM.js_prefixo()` com `MAN0 = CEN0.man`; mensagem do Restaurar.
- `dados_cad.py`: `ITENS_MAN` (14 itens; `dados_manutencao.ITENS` deriva dele e mantém `saldo` até o 1b; os códigos nas OMs semeadas entram no 1b), local `l11`, `GRUPO_NAT` e `CONTROLE_GRUPO` de Lubrificantes, `assert` de grupos únicos. `dados2.py:682`: + Lubrificantes. `cad_produtos_estrutura.py`: `UNIDS` + kit; preço com data (`PRECO_DATA`), embalagem e local lidos de `ITENS_MAN` (l.36-44, 57-61); sai o comentário da l.80.
- **Tamanho (executado sobre o build atual):** CEN0 = 19.134 caracteres; `man` = 19.195; DM.JS = 25.856; `cenario.js` = 25.143. As 6 telas da manutenção ganham cerca de +44 mil (CEN0 sem `man` + `cenario.js`). As 23 páginas que já usam o cenário ganham cerca de +19 mil (só o `man`). O `man` fica no CEN0 de todas, porque `cenGet`, `cenMudar` e `cenReset` gravam o estado inteiro. A tabela antes/depois por página entra no PR, com o teto aceito.
- Testes a ajustar: `matest.py` (chave do localStorage); `cadc_cd06_test.py:10, 20` e `cadc_fix_cd06.py:12, 23` (contagens "sem preço" e "sem embalagem" iguais, ou os novos números declarados); `cadc_fix_cd06.py:44` (folga ≥ 20 px com o `l11`; senão, ajustar `HEIGHTS37`); `cadc_cd07_test.py` (nova verificação da linha 3.1.04). `ma_correcoes_om_test.py:71-75` e `ma_planos_test.py:46, 51` continuam iguais (prova de não regressão).
- Guarda nova sobre `project/*.html`: toda página com `const CEN0 =` tem o mesmo CEN0 (mesmo hash) e a chave `man`; toda página que chama `man[A-Z]\w*(` contém DM.JS; tamanho da maior e da menor página registrado.

**PR 1b · Um estoque** (depois do merge da 2d)
- `cenario.py`: v=5; lotes do Almox. oficina; REQ-032..034 com `dom:'man'`; `scs:{}`; `recibos:{}`.
- `cenario.js`: `cenOrdem(c, id) = c.ordens[id] || c.man.oms[id]`; `cenProxId`; `cenEntregar`, `cenDevolver`, `cenConfAbertas`, `cenSeloConf`, `cenPodeEncerrar` passam a usar `cenOrdem` (para OM, exigem `o.aprov` e ignoram `o.ap`); checagem do livre e da reserva própria dentro de `cenEntregar`; `entrega.res`; novas `cenEstornarReserva`, `cenCancelar` (comum à O.S. e à OM), `cenLoteInterno`; `cenMudar(self, fn, cmd)` com recibos e versão (G04).
- `dados_manutencao.py`: novas `manAprovar` (grava `c.scs[id].tok` uma vez, ao criar a SC), `manAutorizarValor`, `manDecidirConflito`, `manLivre(c, cod)` (Σ `cenDisp` dos lotes do item; sem lote, 0), `manCobertura`; reescritas **uma vez** `manFalta`, `manLiberar`, `manConcluir`, `manCusto(c, o, modo)` e `manEncerrar`; saem `manSolicitar`, `manSobras`, `ITENS.saldo` e `ITENS.reservado`; `o.janIso` nas OMs semeadas e geradas; `manOmCiclo` ignora Cancelada.
- `areas/maquinas.py`: `ma_passo` e `ma_exec` (l.379-401); leitores de saldo l.382, 469 e 893; painel de peças; chips "Usei tudo"; faixa de KPIs; "Cancelar sem execução"; "Autorizar valor"; MA-03 "Decisão da gerência". Saem "Solicitar compra" e "Resolver sobras".
- **Ponte temporária do C2:** o botão "Registrar recebimento (simulado até a compra)" na MA-04 chama `cenReceber` com `cenLoteInterno` (OF26-15), Almox. oficina, preço do catálogo e documento "SC-041 · recebimento simulado", sem número de NF inventado; movimento com `simulado:true`; SC Atendida. A cobertura da OM-0235 fecha e o Liberar reserva. O teste do C2 percorre aprovar → receber (simulado) → liberar → entregar no EST → concluir → encerrar.
- `areas/processo_estoque.py`: `LOCAIS` (l.19); `eitem` (l.181-193) com `cenOrdem` e motivo por destino (l.188); etapas 2, 3 e 4 com linhas de OM; "Entregar REQ inteira"; `confirmado:'balcao'` (l.273, 400-401, 525); rótulo do consumo (l.219, 231).
- `areas/processo_os.py`: `osc_reqId` (l.341-342) chama `cenProxId`; `osc_cancelar` (l.378-382) chama `cenCancelar`.
- Cadastros: `p11` Otávio (`dados_cad.py:77-88`; `cad_ativos_pessoas.py:28, 38`).
- Testes a ajustar: `est_cenario_test.py:99` e `os_cenario_test.py:87-89`: 11 → **14** requisições; `cada_cd04_test.py:25, 28`: '10/10' → '11/11'; `matest.py` (sobras e encerramento pelo EST); `ma_correcoes_om_test.py` (sobra de 4 L e custo do C1 pelo EST); `ma_planos_test.py:51` ("Solicitar compra" sai) e `:53-56` ("Liberar mesmo assim" sai; o conflito vai para Mover ou gerência). `os_v39_liberar_test.py:43` (REQ-041) continua igual.
- Se o 1b ficar grande demais para revisão, dividir em 1b-i (lotes, REQ, aprovar, liberar, entregar, concluir, devolver, encerrar, ponte) e 1b-ii (cancelar, conflito, autorização acima do limite, chave de idempotência). Cada metade mantém o C2 pela ponte.

**PR 1c · Compra e recebimento reais**
- `cenario.py`: v=6; `pedidos:{}`.
- `cenario.js`: `cenGravarPedidos(c, sc, pcs)` (M11); `cenReceberPedido(c, pc, nf, qtdConf, apto, quar, data, un)` (M12, M13); `cenReceberSemPedido` (M25); `cenReprogramarPC`; `prevAtual`; `cenLiberarQuarentena` devolve a peça à cobertura.
- `areas/processo_compras.py`: `cenario.js_prefixo()` no EXTRAJS (l.110); `solDe('SC-…')` monta a solicitação de `c.scs`, sem `pcIni` (a l.175 continua só para safras); `M()` (l.241) mostra na prévia `cenProxId` sem consumir número (textos l.530, 537-539, 554); `emitir` (l.436-439) chama `cenGravarPedidos` dentro de `cenMudar` e guarda em `proc['SC-041'].aprov.pcs` os ids devolvidos; `pick` (l.404), `abrirHash` (l.484-485), `trocaSafra` (l.193) e `hashSync` (l.198) aceitam SC; estado `{tipo, id}`; `NOMES` (l.16, 596), `WHYMSG` (l.476) e `whys` (l.494) cobrem SC; etapa 6 com `prevAtual` e `cenReprogramarPC`.
- `areas/processo_estoque.py`, formulário "Registrar recebimento": `u` de `qtd_nf`, `conf`, `apto` e `quar` = unidade do pedido selecionado, atualizada no render a partir de `fmR.draft.ped` (padrão das l.423 e 445); `epedBase`, `epeds` e `efert` (l.209-211) leem também `c.pedidos` (hoje `ESAVE.g_rec` quebra em `p.item`, l.337, com PC-2xx); sai o `u='kg'` (l.78-81); as 3 mensagens (l.307-309) usam `p.un`; sai o fallback `x.un||'kg'` (l.383); opção "Sem pedido · regularizar" com o campo OM e "autorizou".
- `dados2.py`: F08, F09 e `PROPOSTAS` (§10). Nome "Compras" (§5.1).
- Sai a ponte e o botão "Registrar recebimento".
- Testes a ajustar: `cadp_fix_test.py:75, 80`: 20 → **22** parceiros; `cmptest.py`: linha de SC e a proteção do nome (`header h1` e `document.title` = "Compras", trilha "Suprimentos › Compras", item ativo do menu); `etapas_celular_test.py:132` continua passando; `ma_correcoes_om_test.py:71-75`: o C2 completo pela CMP e pelo EST.

### 11.3 Testes novos
`gen37/pcm_sup_unit.js` e `gen37/pcm_sup_test.py`, no padrão de `carencia_test.py:9-32`. Cada caso parte do seed, salvo indicação, e confere a C06 depois de cada comando. Formato: `U-nn · regra · caso · o que confere`. Números e mensagens: §10 e §4.

**Parte `unit` (node ou jsc, sem navegador)**
- U01 · M02, M03 · seed · KIT-MF7719 só em lote; `man.itens[...].saldo` é `undefined`; nenhuma peça de OM semeada com `item=''`. 1b
- U02 · M05 · C1 · aprovar cria a REQ-041 com 2 linhas e cobertura total, sem `reserva`; aprovar de novo devolve a mesma REQ, sem movimento. 1b
- U03 · M09 (−) · — · liberar sem aprovar. 1b
- U04 · M09 · C1 · depois de mover, liberar grava 2 `reserva` (os='OM-0234') e o evento com a autorização econômica. 1b
- U05 · M14 (−) · C1 · entregar 2 kits numa linha de 1. 1b
- U06 · M06 (−) · C1 · entregar a outra REQ além do livre não toca a reserva da OM-0234. 1b
- U07 · M06 (−) · C1 · contagem 0 no OF26-01 com 1 reservado. 1b
- U08 · M15 · C1 · concluir com 12 L: consumo 12, custódia 4. 1b
- U09 · M15 (−) · C1 · 18 L com 16 em custódia abre conferência; lote igual; encerrar recusado até conciliar. 1b
- U10 · M18 (−) · C1 · encerrar com custódia: a mensagem. 1b
- U11 · M17, C01 · C1 · devolução apta: OF26-07 e custo do §10. 1b
- U12 · M17 (−) · C1 · devolução imprópria: +4 L em quarentena, livre igual. 1b
- U13 · M05, M07, M08 · C2 · SC-041 com 1 un e `precisa` 2026-09-24; segunda OM sintética com o mesmo filtro soma (2 origens, 2 un); com livre 2 de KIT-MF7719, duas OMs aprovadas de 1 kit não abrem SC e a terceira abre com 1. 1b
- U14 · M08 · — · OM sintética com filtro e óleo em falta: 1 SC, 2 linhas (2 grupos de convite na CMP); outra OM com outro item, com a SC "A cotar", entra nela; aprovar de novo não duplica; depois de "Enviar convites", a falta nova abre a SC-042; cancelar uma OM tira só as linhas dela. 1b
- U15 · M14 (−) · C2 · entregar para OM em A liberar. 1b
- U16 · M19 · C2 · cancelar a OM-0235 aprovada: REQ-041 Cancelada, SC-041 vazia Cancelada, nenhum `estorno-reserva`. 1b
- U17 · M19 (−) · C1 · cancelar a OM-0234 Em execução. 1b
- U18 · M19 · C1 · cancelar a OM-0234 Liberada com 16 L entregues: A liberar, "Cancelamento pendente · Rui", 1 `estorno-reserva` (kit), Iniciar recusado, uma tarefa; Cancelada só depois da devolução de 16 L. 1b
- U19 · M19, G04 (−) · C1 · cancelar duas vezes: um estorno, uma tarefa. 1b
- U20 · M07 · C2 · OM sintética aprovada depois da OM-0235 libera usando o OF26-15: aviso; confirmado, a falta da OM-0235 entra na SC "A cotar". 1c
- U21 · M11, G04 · C2 · SC-041 aprovada gera PC-201 (não PC-101 nem PC-NaN; o PC-101 da S2627 continua da safra); gravar de novo a mesma (SC, F08) devolve o mesmo PC. 1c
- U22 · M11 · C2 · reprogramar 24/09 → 28/09: `prevs` com 2 entradas, a primeira 24/09; repetir 28/09 não cria a 3ª; data anterior a hoje recusada. 1c
- U23 · M12, G04 (−) · C2 · mesma NF no PC-201 com chave nova: uma entrada e a mensagem. 1c
- U24 · M12 (−) · C2 · `cenReceberPedido` com unidade diferente: nada gravado; (+) com PC em un, kit e L, os 4 campos e as 3 mensagens mostram a unidade do PC. 1c
- U25 · M13 · C2 · 1 un apta: OF26-15 livre 1 com `origem`; SC-041 Atendida; cobertura da OM-0235 completa; liberar reserva. 1c
- U26 · M13 · C2 · 1 un em quarentena: cobertura incompleta até a inspeção. 1c
- U27 · C05, PCMS-I1 · C2 · espera de 1 dia (SC 23/09, recebimento datado 24/09); uma OM sintética com falta ainda aberta aparece no envelhecimento e fica fora da distribuição concluída. 1c
- U28 · C01, M10 · C2 · proposta padrão F08 sem clicar; custo do §10; F09 sem justificativa bloqueia a aprovação (toast da l.441). 1c
- U29 · C01 · C3 · custo do §10. 1b
- U30 · ids · — · liberar a OS-0430 gera REQ = maior + 1; nenhum id gerado sobrescreve SC, PC ou REQ existente. 1b
- U31 · G04 · C1 · entregar 8 L com K1 e reenviar K1: 1 `entrega`, custódia 8, mesmo recibo, `rev` igual. 1b
- U32 · G04 · C1 · 8 L com K1 e 8 L com K2: 2 entregas, custódia 16. 1b
- U33 · G04 (−) · C1 · K1 reenviada com 9 L: conflito, nada gravado. 1b
- U34 · G04 (−) · C1 · formulário com `ver` N; outra entrega grava; salvar o primeiro: conflito. 1b
- U35 · G04 · C1 · devolver 2 L com K3 e reenviar: 1 devolução; 2 L com K4: custódia 0. 1b
- U36 · G04 · C1 · liberar e reenviar a mesma chave: mesmo recibo, sem segunda reserva; aprovar duas vezes com a mesma chave e payload diferente: conflito. 1b
- U37 · G07 (−) · OM sintética · aprovar registra só a aprovação técnica, sem SC; liberar e entregar recusados com "Autorização econômica pendente · Gerente da fazenda". 1b
- U38 · G07 · OM sintética · o Gerente autoriza: SC abre; liberar reserva; repetir a autorização devolve o registro; Otávio autorizando acima do limite é recusado. 1b
- U39 · M14 · C1 · "Entregar REQ-041 inteira": 2 `entrega`, custódia certa, `confirmado:'balcao'`. 1b
- U40 · M09b · C1/C1b · liberar com conflito aberto: recusado; depois de mover: libera; decisão com alternativa: libera; decisão sem alternativa: recusada. 1b
- U41 · M25 · C11 · caso completo. 1c
- U42 · M25 · — · OM Em execução recebe peça sem pedido direto na custódia; concluir consome; lote não fica negativo. 1c
- U43 · M25 (−) · C11 · sem NF; sem OM; mesma NF de novo; receber o PC de regularização no EST; a SC-041 mantendo a linha atendida; "autorizou" vazio. 1c
- U44 · M03, C06 (−) · — · comando sintético que muda `l.reservado` sem movimento quebra a conciliação; e o grep estrutural, restrito aos arquivos da manutenção, não retorna nada: `grep -nE "\b(saldo|reservado|fisico|quarentena)\b['\"]?\]?\s*(\+\+|--|[-+*/]?=[^=])|(\+\+|--)\s*[A-Za-z_$.]*\b(reservado|fisico|quarentena)\b|Object\.assign\([^)]*\b(fisico|reservado|quarentena)\b" gen37/dados_manutencao.py gen37/areas/maquinas.py` (hoje pega as l.389, 400, 429 e 446). 1b

**Parte `fluxo` (CDP, navegador)**
- F1 · C1 de ponta a ponta, com o selo "Sobras a receber · Rui" depois do concluir. 1b
- F2 · C2: no 1b pela ponte; no 1c pela CMP e pelo EST, aprovando a cotação sem clicar em proposta (PC-201 com F08 e o custo do §10). 1b/1c
- F3 · C3. 1b
- F4 · C11. 1c
- F5 · F5 e dois quadros: liberar a OM-0234 aparece no EST do outro quadro sem recarregar; "Entregar 8 L" aberto nos dois e salvo nos dois grava uma entrega e dá conflito de versão no segundo; duas entregas parciais sucessivas gravam duas. 1b
- F6 · textos: "(agrônomo)" ausente nas linhas de OM; linhas de OM sem "Aguardando confirmação no app"; HTML da MA-04 sem "Solicitar compra" e "Resolver sobras" (1b) e sem "Registrar recebimento" (1c); PM-01 mostra "saldo 2 kit" no KIT-MF7719 e PM-02 "falta · saldo 0 un" no FIL-MF4292; o FIL-MF4292 não aparece "disponível" no painel da OM-0235; `grep -nE "itens\[[^]]+\]\.(saldo|reservado)|\bit\.(saldo|reservado)" dados_manutencao.py areas/maquinas.py` vazio. 1b/1c
- F7 · restaurar, para cada um dos cinco botões e para a troca de versão (`c.v` ≠ `CEN0.v`): 14 requisições, 0 movimentos, OM-0234 em A liberar, OF26-07 com 120 L, nenhum `proc['SC-*']`; refazer o C2 até a SC-041; a CMP etapa 1 mostra "A cotar" sem convites, escolha ou aprovação; aprovar grava o PC-201. Caso no navegador: `proc['SC-041']` antigo com outro `tok` faz `procLer('SC-041')` devolver `null`. 1b/1c
- F8 · toques, campos e navegações do C2 por papel, antes (hash base) e depois (§9). 1c
- F9 · CMP: abrir a SC-041 pela etapa 1, recarregar e continuar na etapa 2 com "SC-041 · Manutenção". 1c

### 11.4 Homologação (AGENTS §3.1 passo 3)
- **Depois do 1b:** C1 e C3 como fatia útil. Limitação dita ao dono: o C2 usa recebimento simulado até a compra.
- **Depois do 1c (tarefa curta):**
  1. "No MA-03, toque em 'Gerar 3 ordens preventivas'."
  2. "Na linha do Trator 03, abra 'OM-0235 · A liberar'. Na MA-04, toque em 'Aprovar ordem'. Confira a falta do Filtro de óleo MF 4292 e a SC-041. A OM-0236 e a OM-0237 não fazem parte deste teste."
  3. "Em Compras, abra a SC-041 e compre o filtro com a proposta já sugerida (F08, chega 24/09)."
  4. "No Estoque, receba a nota do PC-201."
  5. "Volte à OM-0235 e libere o serviço."
  6. "No Estoque, entregue a requisição ao Zé."
  7. "Na OM-0235, faça a parte do mecânico (iniciar, responder o checklist, 'Usei tudo' em cada peça, concluir) e encerre."
  8. "Confira o custo: R$ 1.776,00 (160 + 12 L × 28 + 4 h × 320)."
- Limitações ditas ao dono: serviço de terceiro (concessionária, oficina externa) entra no Bloco 3, depois do Bloco 2; até lá o custo de serviço das OMs semeadas aparece como hoje. A parte do mecânico é feita na MA-04 até o Bloco 6. A espera por peça mostra 0 dia porque a data da demonstração é fixa.
- Se o dono preferir uma só homologação, ela fica depois do 1c.

### 11.5 Blocos seguintes (um ativo por vez; detalhe no Anexo)

| Bloco | Resultado útil | Depende de | Prioridade |
|---|---|---|---|
| 2 · Corretiva, teste e ativo | Corretiva no cenário, "Incluir linha", condição única do ativo com histórico, impedimentos derivados, remanejar reserva, PCP lendo o conflito | Bloco 1 | P0. Operar ativo bloqueado é candidato a S1 |
| 3 · Serviço de terceiro | SC e PC de serviço, medição, aceite com teste, título só depois do aceite, exceção sem pedido | Bloco 2 só para linhas com teste obrigatório (P5) | P0 (RF-OPS-008, E2; atende ao pedido de 05/10, que não é aprovação) |
| 4 · Antecipação e política | "Pedir até", cobertura no MA-03, mínimo/máximo, KPI-SUP-05, PCMS-I7 | Bloco 1c | P1 |
| 5 · Peça retirada, reparável, garantia, kit | Destinos, remessa e retorno com teste | Bloco 3 (remessa por PC de serviço) | P1 |
| 6 · Campo e combustível | MB-04 → MA-02, MB-05/MB-09 no cenário, diesel como saída de lote, balcão pelo app | Bloco 2 | P2 |
| 7 · Gestão | GE-03/04/06 do cenário, KPI-PCM-10, KPI-PCM-02 | C04 (Bloco 3) | P1 |

---

## 12. Critérios de aceite do Bloco 1 (matriz de rastreio)

O texto do aceite fica só para o observável que não está na regra. Os critérios dos Blocos 2 a 7 são escritos pelo Codex (AGENTS §3; `docs/parceria/protocolo.md`), com o Anexo como insumo.

| AC | Regra(s) | Caso §10 | Teste | Observável | PR |
|---|---|---|---|---|---|
| AC-01 | M01 | — | F5; grep | `grep -rn "talhao-os-manutencao-v1" gen37 --include=*.py --include=*.js` vazio (fora `_render`) | 1a/1b |
| AC-02 | M02, M04, §3.3 | — | cadastros | CD-06: 11 itens em Peças, 3 em Lubrificantes, unidade `kit`; cada grupo uma vez; ids únicos na árvore `g_itm`; o select "Grupo" não repete; CD-07: 3.1.04 mostra "Combustível, Lubrificantes" | 1a |
| AC-02b | G01, §3.3 | — | `cada_cd04_test` | CD-04 lista 11 pessoas, com "Otávio · Responsável de manutenção · Aprovar O.S. de manutenção; Liberar ativo" | 1b |
| AC-03 | M04 | seed | F1 (etapa 4) | EST etapa 4: Almox. oficina com os lotes do §10; FIL-MF4292 sem lote | 1b |
| AC-04 | M09, M14, M15 | C1 | U04, U08, U39, F1 | Reservas e físicos do §10; selo "Sobras a receber · Rui" | 1b |
| AC-05 | M18 | C1 | U10 | Mensagem da M18 | 1b |
| AC-06 | M17, C01 | C1 | U11 | Valores do §10 | 1b |
| AC-07 | M05, G04 | C1 | U02, U36 | Uma REQ-041 e 0 `reserva` depois de aprovar duas vezes; 2 `reserva` depois de liberar | 1b |
| AC-07b | G04 | C1 | F5, U31-U35 | Dois quadros e entregas parciais | 1b |
| AC-08 | M09 | — | U03 | "Aprove a ordem" | 1b |
| AC-08b | G07 | C1, sintética | U04, U37, U38 | C1: o evento mostra "autorização econômica: Otávio · alçada OM até R$ 50.000"; sintética: selo e recusa | 1b |
| AC-09 | M17, M18, C01 | C3 | U29, F3 | Valores do §10 | 1b |
| AC-10 | M05, M07 | C2 | U13 | SC-041 "A cotar": "Filtro de óleo MF 4292 · 1 un · OM-0235 · Trator 03 · precisa 24/09"; nenhuma reserva | 1b |
| AC-11 | M09 | C2 | F2 | Mensagem de falta da M09 | 1b |
| AC-11b | M09b | C1, C1b | U40, F1 | Sem "Liberar serviço" com conflito; Mover libera; decisão registrada aparece no MA-03 de outro quadro | 1b |
| AC-12 | M08 | — | U13, U14 | Agregação e congelamento | 1b |
| AC-13 | M10, M11 | C2 | U21, F2 | CMP etapa 1 com a SC-041 "Manutenção"; convites só a F08 e F09 (F07 e F01-F06 nunca); PC-201 no cenário; selo "Aguarda PC-201 · prev. 24/09 · F08" | 1c |
| AC-14 | M11 | C2 | U22 | Selo "prev. 28/09 (prometido 24/09)" | 1c |
| AC-15 | M12 | C2 | U23, U24 | Recusas da M12 | 1c |
| AC-16 | M13, M07 | C2 | U20, U25 | OF26-15 livre e SC-041 Atendida; liberar reserva; outra OM que use o filtro antes recebe o aviso | 1c |
| AC-17 | M13 | C2 | U26 | Quarentena só cobre depois da inspeção | 1c |
| AC-17a | M25 | C11 | U41-U43, F4 | Regularização na CMP; PC de regularização fora do EST; custo do §10 | 1c |
| AC-18 | C01, M10 | C2 | U28, F2 | Custo do §10 com a proposta padrão F08; F09 só com justificativa | 1c (1b pela ponte) |
| AC-19 | M14 | — | U15, F6 | Recusa da M14; textos da F6 | 1b |
| AC-19b | M19 | C1, C2 | U16-U19 | O botão só aparece nas fases da M19; a tarefa "Devolver sobras" aparece no EST etapa 3 de outro quadro; a O.S. agrícola cancelada com material entregue passa pelo mesmo caminho | 1b |
| AC-20 | M15 | C1 | U09 | Conferência sem baixa | 1b |
| AC-21 | M06 | C1 | U07 | Contagem recusada | 1b |
| AC-22 | M01, §8 | — | F7 | Restaurar pelos cinco botões e pela troca de versão | 1a (chave) / 1b / 1c |
| AC-23 | §5.1 | — | F6 | Botões que saem | 1b/1c |
| AC-24 | §9 | C2 | F8 | Responsável ≤ antes − 1 (estimado 4 → 3); mecânico ≤ antes + 1 por linha de peça; almoxarife entrega a REQ com 1 toque; compra de 1 item ≤ N medido; nenhum total sobe sem a linha que nomeia o fato real que o justifica | 1c |

Aceite do corte (achado PCMS-R15): nenhum ID de regra perdido; cada valor de C1, C2 e C3 aparece uma vez neste arquivo, no §10 (`grep -c '2\.626' ESPECIFICACAO.md` = 1); a única exceção é o custo do C2 no roteiro do dono (§11.4), que ele lê sem o §10; cada AC tem regra e teste; o Codex confere a preservação de escopo e de significado.

---

## Anexo A · Regras dos Blocos 2 a 7 (uma linha cada, com dano e fonte)

**Bloco 2 · Corretiva, teste e ativo**
- **PCMS-M20 · Só o aumento volta à aprovação.** Item novo, troca de código ou aumento cria nova versão da linha; a diferença aguarda Otávio (CMD-42 l.2825). Se quem altera é o próprio Otávio, é "ajustar e aprovar" num ato. OM não iniciada volta a A liberar; OM Em execução fica com o selo "Revisão pendente" (adaptação de "Revisão de saldo pendente", l.2978) e só a entrega da diferença fica bloqueada (DEMO-17 l.4726). Redução ou retirada não pede reaprovação: a parte reservada e não entregue sai por `estorno-reserva` com motivo; abaixo do entregue, vira devolução esperada (M17); a linha na SC "A cotar" é reduzida. A troca de lote é da reserva e do EST (CMD-44), não da linha. Se a estimativa passar do `autEcon`, pede nova autorização (G07). Dano: peça ou quantidade sem autorização competente (PCM-07 l.7801; l.9961).
- **PCMS-M26 · Remanejar reserva** (antes "M25" no achado PCMS-R12). Só Otávio, só entre OMs `dom:'man'`, nunca de O.S. agrícola. Origem A Liberada, sem nada entregue do item (com custódia, o caminho é a devolução); destino B aprovado com falta do item; quantidade ≤ menor entre o reservado de A e a falta de B; motivo obrigatório. Num `cenMudar`: `estorno-reserva` em A ("remanejada para OM-B: <motivo>"), `reserva` em B no mesmo lote, falta de A na SC "A cotar", A volta a A liberar com o evento de revogação e o selo "Peça remanejada para OM-B · SC-04x". Físico e reservado do lote não mudam. Aviso, sem trava, quando B não é mais crítica nem tem janela anterior. Fonte: 47.8 l.7820; precedente 42.4 l.7085. Dano: corretiva urgente parada por reserva de preventiva com janela futura.
- **PCMS-M02 (tela):** aprovar OM com linha "Especificar item" é recusado com "Especifique o item: <nome>".
- **PCMS-A01 · Condição do ativo com uma fonte:** `c.man.ativos[aid].cond` com histórico; MA-01, CD-03, O.S., EST, App e PCP só leem (RN-021 l.223; DEC-2609-14 l.12228).
- **PCMS-A02 · Bloquear (CMD-18 l.2789) grava condição e motivo**, pelo MA-02 ou pelo MA-01 (hoje só local, `maquinas.py:205-210, 271-275`).
- **PCMS-A03 · Liberar o ativo (CMD-19 l.2790) é recusado** com OM bloqueante aberta sem teste aprovado.
- **PCMS-A04 · Teste reprovado mantém o bloqueio** e devolve a OM a Em execução, sem OM nova; teste aprovado permite a aptidão antes do encerramento do custo (l.7738).
- **PCMS-A05 · Impedimento derivado:** a O.S. com ativo bloqueado ganha "Falta máquina · Trator T1 (OM-0233)" (8.4.3 l.2962); `cenIniciarTurno` recusa (`cenario.js:128-135`); liberar o ativo não reassume a agenda (DEMO-17).
- **PCMS-A06 · Peça em falta torna o retorno condicional** (47.8 l.7821); preventiva vencida com falta gera aviso, sem trava, nas O.S. do ativo.
- **PCMS-A07 · Uma tabela recurso do PCP → ativo** em `alocacao.py`, sem segundo cadastro.
- **PCMS-C07 · Nota em conferência nunca segura o ativo** (47.5 l.7738, regra do PRD e não parâmetro). As outras pendências de custo ou material também não seguram a aptidão: o RF-AST-005 (l.2570) admite política em contrário, mas aqui não há dano concreto a proteger, porque a conciliação já trava o Encerrar.

**Bloco 3 · Serviço de terceiro**
- **PCMS-S01** · O serviço é linha da OM (escopo, especialidade, critério de aceite, teste obrigatório, valor previsto), com `grupo='Serviços de manutenção'`; aprovar abre a SC de serviço.
- **PCMS-S02** · Cotação só com fornecedor homologado no grupo "Serviços de manutenção" e canal autorizado (l.1752, regra vigente). Dentro do grupo, o convite filtra pela especialidade (refinamento proposto à v3.10). F08, F09 e parceiro só Prestador nunca são convidados. Equalização por valor, prazo e garantia (RF-SUP-005).
- **PCMS-S03** · Sem PC aprovado, não há medição.
- **PCMS-S04** · Medido acima do PC exige reaprovação na alçada (G02).
- **PCMS-S05** · O aceite físico é de Otávio. Com "teste obrigatório", só vale com teste aprovado; o default do campo vem do P5 e quem desmarca registra o motivo. Recusar volta a OM a Em execução, sem OM nova (l.7738).
- **PCMS-S06** · Aceite não é pagamento. O título no GE-04 só fica "A propor" depois do aceite; NF sem PC aceito não gera título; nada é pago automaticamente. Fonte: RF-OPS-008 l.2540; SU-06 l.1228; GE-04 l.1574; RF-SUP-011 l.2593; RF-LOG-004 l.2642 por analogia (frete). "A propor" e "NF sem PC aceito não gera título" são política proposta do protótipo.
- **PCMS-S07** · Serviço sem pedido é exceção visível, com `semPedido = {autorizou, em, motivo}` (47.5 l.7736); "ninguém autorizou" é aceito e aparece como "sem autorização registrada"; aceite e título só depois do PC de regularização na alçada.
- **PCMS-S08** · A OM não encerra com serviço sem aceite e sem cancelamento.
- **PCMS-C03** · Horas próprias só de especialidade própria; as do prestador estão no valor do serviço.

**Blocos 4, 5 e 7**
- **PCMS-M21** · Demanda datada antecipa a compra: vencimento projetado com prazo do fornecedor maior que o tempo até a janela vira "pedir até" (47.4 l.7726; 8.6.4 l.3081; PCE-06 l.9223). Bloco 4.
- **PCMS-M22** · Mínimo/máximo e OM compartilham a SC "A cotar", com origem "Política" (PCM-06; 65.2 l.9159-9164). Bloco 4.
- **PCMS-M23** · Kit sem duplicar: o plano usa o kit ou os componentes (65.2 l.9160). Bloco 5.
- **PCMS-M24** · Peça retirada nunca entra como nova; recondicionada com condição própria (PCM-07; 47.4). Bloco 5.
- **PCMS-S09** · Remessa para reparo conserva a identidade; retorno com conferência e teste (47.4 l.7728). Bloco 5.
- **PCMS-C04** · Custo encerrado alimenta o ativo e o GE-03 por 3.1.05/3.1.04 e CC-OFI; nunca entra também na O.S. agrícola (CAL-04; 51.3 l.8137). Bloco 7.

## Anexo B · Insumo do Codex para os Blocos 2 a 7

**Casos (valores executados em python, DECISOES.md §8)**

| Caso | Base | Resultado esperado | Bloco |
|---|---|---|---|
| C4 Corretiva bloqueante · OM-0233, Trator T1 (a01), INSP-105, SM-0147, Em execução | `dados_manutencao.py:192-198`; `maquinas.py:220-223` | Aptidão recusada sem teste → teste reprovado (OM volta, sem OM nova) → aprovado → Concluir consome 1 bomba e 2 mangueiras → aptidão → OS-0420 e OS-0431 desimpedidas, REQ-036 entregável, agenda antiga não reassumida. Custo sem serviço **R$ 6.180,00** (3.600 + 2 × 250 + 6,5 × 320), igual ao MA-04det (≈ R$ 6,2 mil, `maquinas.py:629-630`). Vale no estado do Bloco 2; com serviço semeado no Bloco 3, ver C9 | 2 |
| C5 Bloqueio sem teste · OM-0228, Bomba do Pivô 2 (a11), Restrito, Alta, Liberadas | l.182-184 | MA-01 "Apto" recusado (A03) | 2 |
| C6 Máquina alocada sem peça · Trator 03 na OS-0421 e na OS-0430 | `alocacao.py:21, 29` | Aviso nas duas O.S.; nenhuma trava (A06) | 2 |
| C7 Corretiva do campo · NC-0912, disco de corte | `maquinas.py:233-234` | Criar ordem → Incluir linha DSC-15 → Aprovar → Liberar reserva do OF26-11. Se a OM-0236 já existir, o caminho é Vincular (`ma_correcoes_om_test.py:68-70`) | 2 |
| C7b Remanejar · VED-MB saldo 1; OM-0237 (PM-07, a11, Média, janela 01/10) Liberada com o kit; OM-0228 (Alta) ganha VED-MB por M20 | — | Otávio remaneja 1 VED-MB com motivo: OM-0228 coberta e reservada; OM-0237 volta a A liberar com "Falta peça · SC-04x"; lote igual; 1 `estorno-reserva` + 1 `reserva`. (−) mesma chave, sem motivo, feito por Rui, quantidade acima, origem com custódia ("Já entregue a Zé; receba a devolução no Estoque") | 2 |
| C8 Serviço histórico · OM-0221 (a08), "Terceiro (concessionária)" | l.177-181 | Seed: REQ-032 conciliada; **PC-200** de serviço da concessionária fictícia, Aceito, R$ 2.520,00 (abaixo do piso 201, para não colidir com o PC-201 do C2). Custo = 1.280 + 2.520 = **R$ 3.800,00**, igual ao gravado; as 14 h são do prestador (C03) | 3 |
| C9 Serviço sem pedido · OM-0233 | `gestao.py:279, 347`; `maquinas.py:629-630`; `dados_manutencao.py:193` | **O seed é incoerente** (DECISOES.md §4, pendência do Codex). Sem total fixo: depois da regularização, do teste e do aceite, o título fica "A propor" e não é pago; o custo encerrado é o do C4 + o valor aceito do serviço (C01), cada componente uma vez, sem as horas do prestador como próprias (C03). Seed: `aprov` e `semPedido = {autorizou:'Otávio (resp. manutenção)', em:<data da execução semeada>, motivo:'Trator T1 bloqueado; OS-0420 e OS-0431 impedidas'}` (`maquinas.py:339`) | 3 |
| C10 Peça retirada · bomba usada da OM-0233 | `maquinas.py:578-580` | Recuperável → remessa (PC de serviço) → retorno com teste → "recondicionada", fora do disponível até o teste | 5 |
| C12 Serviço vivo em preventiva (só se o Bloco 3 for dividido em 3a/3b) · linha "Terceiro (concessionária)" na PM-06 da a08, valor fictício | — | Aprovar → SC de serviço → PC → medir → aceitar → "A propor" | 3a |

**Verificações propostas** (ex-AC-25 a 34 e novas; o Codex as transforma em critério)
- B2: aptidão do T1 recusada sem teste; teste reprovado devolve a OM sem criar OM (ex-AC-25). Depois do teste aprovado e da aptidão: OS-0420 sai de "Impedida", OS-0431 sai de "Falta máquina", REQ-036 entregável, agenda não reassumida (ex-AC-26). Turno no app com ativo bloqueado recusado com motivo e dono (ex-AC-27). MA-01 "Apto" na Bomba do Pivô 2 com a OM-0228 aberta recusado (ex-AC-28). OM-0235 em falta avisa a OS-0421 e a OS-0430, sem trava (ex-AC-29). OM-0233 encerrada sem serviço custa o do C4 (ex-AC-30, só no estado do Bloco 2). Reduzir 16 → 14 L na OM-0234 Liberada estorna 2 L com motivo, sem reaprovação (aprovada e ainda não liberada: só a cobertura muda, sem movimento); aumentar para 18 L ou incluir item numa OM Liberada bloqueia só a entrega da diferença com "OM-0234 aguarda aprovação da revisão (responsável de manutenção)". C7b. PL-03/04/05 (`planejamento.py:115-116`) leem `o.conflito.dec` do cenário (o MA-03 já lê desde o 1b).
- B3: OM-0221 mostra a composição do C8 (ex-AC-31). Aceitar o serviço da OM-0233 sem PC de regularização e sem teste é recusado; GE-04 mostra "Aguarda aceite" (ex-AC-32). Depois da regularização, do teste e do aceite, "A propor" e não pago; custo pela invariante do C9 (ex-AC-33). Medido acima do PC exige reaprovação; OM com serviço "Medido" não encerra (ex-AC-34). Serviço sem pedido sem "autorizou" é recusado; com "ninguém autorizou", mostra "sem autorização registrada" e o aceite segue recusado. A cobertura do CD-05 mostra "Serviços de manutenção · 2 fornecedores concorrem"; a SC de serviço da OM-0233 convida só quem tem a especialidade "Hidráulica". Aceitar serviço na OM-0228 sem a medição de pressão de recalque é recusado (com linha sintética, se a OM-0228 não tiver serviço). Com o PC-200 no seed, rodar o C2 e depois o C9: o PC-200 continua Aceito e a OM-0221 mantém o custo do C8. Com a opção do seed da OM-0233 escolhida (DECISOES.md §4), GE-03, GE-04 e MA-04det mostram o mesmo custo da OM-0233.
- B4: o PC-201 prometido em 24/09, reprogramado para 28/09 e recebido completo em 27/09 conta fora do prazo no KPI-SUP-05, com 3 dias de atraso contra `prevs[0]` (executado); reprogramar para depois do período não tira o PC do denominador.
- B6: abastecimento de 180 L no Tanque Sede reduz o lote de Diesel S10 de 5.700 para 5.520 L com 1 movimento; repetir não cria segundo movimento (RF-AST-006 l.2571) (executado).

**Bloco 3 · cadastros e modelo**
- HidroMec (`gestao.py:347`) e uma concessionária fictícia com os papéis **Fornecedor e Prestador**, e-mail autorizado, homologadas no grupo "Serviços de manutenção" (natureza 3.1.05, não estocável, fora de `CONTROLE_GRUPO`, sem local nem lote), com a especialidade como atributo da homologação ("Hidráulica"; "Motor e transmissão (concessionária)"). O grupo entra em `dados2.GRUPOS` e propaga para o CD-06 e o CD-05; `GRUPO_NAT['Serviços de manutenção']='3.1.05'`. Entram em `D2.FORNECEDORES` com `homologado=True`, e o papel Prestador em `PAPEL_EXTRA`. A linha de serviço leva `grupo='Serviços de manutenção'`, para o filtro existente da CMP (`processo_compras.py:58-59, 222-226`) e `cotaveis()` (`cad_parceiros.py:222`) funcionarem sem caminho paralelo.
- PC de serviço: `serv:{escopo, esp, criterio, teste, medido, aceite:{quem,em,valor}, nf, semPedido:{autorizou,em,motivo}}`.
- Arquivos: `dados_manutencao.py`; `cenario.js`; `maquinas.py` (painel "Serviços"); `processo_compras.py`; `cad_parceiros.py:30, 115-116, 133`; `gestao.py:279, 347`; `maquinas.py:630`.
- Opcional, se Claude e Codex preferirem antecipar o serviço: **3a** depois do 1c (linha com `teste:false` por default, SC e PC de serviço reaproveitando `cenGravarPedidos`, medição, aceite, "A propor"; linha com `teste:true` tem o aceite recusado com "aguarda teste (Bloco 2)"; caso C12); **3b** depois do Bloco 2 (S05 com teste, S07, C9). "Incluir linha" (peça ou serviço) nasce no 3a e o Bloco 2 a reaproveita.

**Bloco 6 · diesel**
- Lote de Diesel S10 no Tanque Sede, em L: físico 5.700 (38% de 15.000, `maquinas.py:696`, `dados_cad.py:136`), reservado 0, quarentena 0, preço R$ 6,19 (`dados_cad.py:133`); não usar o 5,84 nem os 12.400 L da SU (`suprimentos.py:72`).
- Decisões do bloco: código do lote (D-118, como o MA-05, `maquinas.py:680`, com exceção à regra "Sem lote" do grupo Combustível, `dados_cad.py:124`; ou lote interno, trocando D-117/D-118 em `maquinas.py:663-702`); Comboio CB-01 (`maquinas.py:665, 680`) como local com transferência própria, ou fora do bloco; versão do cenário (o bloco sobe `v`). Sem decisão, o Bloco 6 depende da criação do lote e do local do comboio.
- MB-09 diverge hoje (`mobile.py:865, 871, 894`); arquivos `mobile.py:607-619, 631-695, 863-905`; `maquinas.py:660-729`.
- MB-05 offline: a chave de idempotência viaja na fila junto com o fato (ENG-028 l.5292); não derivar a chave do conteúdo, como `'AP|os|dia'` (`cenario.js:179, 235`).

**Inteligência dos Blocos 2 a 4**
| Gatilho | Mensagem | Um toque | Bloco |
|---|---|---|---|
| Ativo alocado com preventiva vencida e falta de peça | "Trator 03: Revisão 250 h vencida, filtro em falta, alocado à OS-0421 e à OS-0430" | MA-03 → Propor parada ao PCP | 2 |
| Ativo apto com O.S. reprogramáveis | "T1 apto · OS-0420 e OS-0431 aguardam reprogramação" | Recursos → Reprogramar | 2 |
| OM aprovada com falta e item reservado para OM menos crítica ou de janela posterior | "1 kit no Almox. oficina reservado para a OM-A (janela dd/mm, Média)" | MA-04 → Remanejar reserva | 2 |
| Serviço medido sem aceite | "Serviço HidroMec · OM-0233 medido · aguarda o seu aceite" | MA-04 → Aceitar serviço | 3 |
| Vencimento ≤ prazo do fornecedor e sem cobertura | "Pedir até 24/09 · Filtro MF 4292" | MA-03 → Gerar SC antecipada | 4 |
| Sobra ≥ 10% no mesmo serviço em 3 OMs | "Revisão 250 h devolve 4 L em média" | PM → Ajustar quantidade | 4 |

**Indicadores dos Blocos 4 e 7**
- **KPI-SUP-05 filtrado por origem OM** (l.8548; RF-SUP-012 l.2594; CAL-20 l.4467). Unidade: linha de item devida do PC. Numerador: linhas recebidas aptas ou aceitas na quantidade pedida até `prevs[0]`, com tolerância P3. Denominador: linhas cujo `prevs[0]` cai no período. Não recebida na data de corte conta como não cumprida. Mostrar também o número de reprogramações e o atraso contra `prevs[0]`. Meta ≥ 90% (P6). Dono: Comprador · Ana. Bloco 4.
- **PCMS-I7 Acerto do kit planejado** = 1 − Σ devolvido ÷ Σ entregue, por plano e serviço. Meta ≥ 90%. Dono: Otávio. PM. Bloco 4.
- **KPI-PCM-10 Custo de manutenção** (l.8520): Σ C01 das OMs encerradas por ativo; R$/h = Σ ÷ horas de uso. Sem meta. Dono: Gestora · Ana. MA-01, GE-03. Bloco 7.
- **KPI-PCM-02.MTTR** (l.8512): horas de reparo ativo ÷ corretivas com liberação técnica (CMD-19) no período, com ou sem teste obrigatório. **KPI-PCM-02.RESTAURACAO** (l.8513): início da indisponibilidade → liberação técnica, com distribuição, espera por peça e por teste separadas e envelhecimento das corretivas abertas (contagem e a mais antiga). Não subtrair médias de conjuntos diferentes. Dono: Otávio. GE-06. Bloco 7.
