# DS-MODULOS · Paridade dos módulos com o padrão do Agrícola

> Proprietário, 16/10/2026:
> - "colone os icones de drill down sempre na esquerda, fica mais intuitivo em todas telas"
> - "padronize a altura das colunas cabeçalho das tabelas, em diferentes telas temos diferentes alturas."
> - "os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola. Faça seu melhor e mantenha sempre o padrão para mim não ter que ficar cobrando toda vez."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: DS-MODULOS (TAB-09, TAB-10 e paridade) / toda tela de todos os módulos com a mesma tabela, a mesma seta e as mesmas regras do Agrícola / todos os usuários da equipe
Requisitos do PRD e fora do escopo: PRD cap. 74; padroes-1510.md (TAB-01 a TAB-08, VIS-05) e padroes-1610.md (TAB-08, VIS-06, AGR-02, FIL-01); fora: frente Cadastros (arquivos da lista proibida), conteúdo de cada tela
Autor / revisor / integrador: Claude / Codex / integrador da composição (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: 519ed7b / engine.py, g2lib.js, areas/processo_planos.py, areas/agronomia.py, areas/os_campo.py, areas/colheita.py, areas/processo_os.py, safra.js e os testes novos
Aceite e comando de verificação: tab_drill_cab_test.py (A, B e C nas 2 larguras), ds_modulos.py --catraca e os testes listados em "Provas"
Estado / impedimento / próximo passo: executado na branch claude/v44-v72-ds-tabelas; pendências abaixo, com a mudança exata
```

## Como se mede

**`ds_modulos.py`.** Abre as 148 telas do `_render` a 1440 × 900, no estado inicial, e mede o que a tela de referência do Agrícola cumpre:

| Regra | O que conta como desvio |
|---|---|
| CAB-1 | tela de módulo sem "‹ Módulo" no cabeçalho |
| CAB-2 | fazenda e safra como texto solto no cabeçalho, fora da faixa de filtros |
| BOT-01 | mais de um botão verde no mesmo contexto |
| FIL-01 | filtro de contexto fora da faixa comum, ou faixa sem o funil |
| TAB-07 | cartões de resumo (número grande) acima da lista de trabalho; o Painel do módulo não conta |
| TAB-05 | botão de ação com texto dentro da célula (link e atalho "… ›" ficam) |
| TAB-08 | tabela própria sem ⇅ e funil no cabeçalho |
| VIS-05 | lista do motor sem o modo Cartões |
| VIS-06 | lista de cartões própria, fora do motor |

- **TAB-09 e TAB-10** se medem em `tab_drill_cab_test.py`, nas duas larguras e em mais estados de cada tela.
- **Catraca** ("mantenha sempre o padrão"): `ds_modulos.py --catraca` reprova se a contagem de alguma regra subir em algum módulo; a base fica em `ds_modulos_base.json`.
- **Brutos:** `ds-modulos-base.json` (519ed7b) e `ds-modulos.json` (candidata), nesta pasta.

## Resultado (executado)

### TAB-09 e TAB-10 em todas as telas

| Medida | Base 519ed7b | Candidata |
|---|---|---|
| Telas ou estados com a seta fora da 1ª coluna (1440 / 390) | 6 / 6 | 0 / 0 |
| Alturas distintas de cabeçalho (1440 / 390) | 7 / 9 | 1 / 1 (40 px) |
| Telas com cabeçalho fora de 40 px (1440 / 390) | 69 / 65 | 0 / 0 |

Brutos em `tabelas/` (ver "Provas").

### Desvios por módulo (`ds_modulos.py`)

| Módulo | No menu | Telas | Base | Candidata | O que resta |
|---|---|---|---|---|---|
| Agrícola | sim | 25 | 16 | 11 | TAB-07 (5), TAB-05 (3), CAB-1 (2), TAB-08 (1) |
| Manutenção | sim | 3 | 0 | 0 | — |
| Suprimentos | sim | 5 | 2 | 2 | TAB-07 (IC), TAB-05 (CMP) |
| Comercial | sim | 5 | 1 | 1 | TAB-07 (IV) |
| Crédito | sim | 2 | 2 | 2 | TAB-07 e TAB-05 (GE-08, arquivo proibido) |
| Configurações | sim | 5 | 1 | 1 | TAB-07 (CF-05) |
| Cadastros | sim | 10 | 1 | 1 | FIL-01 (CD-01det, arquivo proibido) |
| Portal do parceiro | sim | 1 | 0 | 0 | — |
| App de campo | sim | 2 | 0 | 0 | — |
| Onboarding e backoffice | sim | 3 | 6 | 5 | CAB-1 (2), TAB-07 (2), TAB-05 (1) |
| Agrícola, telas fora do menu | não | 18 | 51 | 34 | CAB-1/CAB-2 (11/14), TAB-07 (5), TAB-05 (4) |
| Comercial, fora do menu | não | 22 | 78 | 56 | CAB-1/CAB-2 (17/22), TAB-07 (8), TAB-05 (9) |
| Suprimentos, fora do menu | não | 12 | 44 | 32 | CAB-1/CAB-2 (9/12), TAB-07 (7), TAB-05 (4) |
| Gestão, fora do menu | não | 6 | 22 | 16 | CAB-1/CAB-2 (5/6), TAB-07 (3), TAB-05 (2) |
| Portal do parceiro, fora do menu | não | 9 | 16 | 7 | TAB-05 (6), TAB-07 (1) |
| Mapa e Início, fora do menu | não | 3 | 9 | 6 | CAB-1/CAB-2 (3/3) |
| Onboarding e backoffice, fora do menu | não | 2 | 3 | 1 | CAB-1 (1) |
| App de campo, fora do menu | não | 14 | 0 | 0 | — |
| **Total** | | **148** | **253** | **176** | |

Leitura:
- As telas do menu de Manutenção, Suprimentos, Comercial, Configurações e Portal já seguem a tabela do motor. O que falta nelas também falta no próprio Agrícola: ação na célula (TAB-05) e cartões de resumo (TAB-07).
- A diferença grande está nas **86 telas fora do menu** (legado ainda gerado; 37 delas abrem por link das telas do menu). Nelas o cabeçalho é outro (CAB-1/CAB-2), há cartões de resumo e ação na célula, e antes deste lote nenhuma lista tinha Cartões.

## O que mudou neste lote (peça comum)

| ID | Mudança | Onde | Alcance |
|---|---|---|---|
| TAB-09 | Seta de abrir na 1ª coluna, antes da seleção; nos cartões, a coluna da seta antes da seleção; Atividades do plano com a seta antes do DAP; seta de seção antes do nome | `engine.grid`, `g2lib` (`carT`, `_selArw`, `_cdgtc`), `processo_planos.py`, `colheita.py`, `processo_os.py`, `safra.js` | 1.572 setas a 1440 e 1.378 a 390 conferidas |
| TAB-10 | Cabeçalho de 40 px (`.g2th`, `.g2thr`), rótulo em até 2 linhas (`.g2hl`), largura pela melhor quebra (`--g2hbw`) | `engine.TABELA_CSS`, `g2cabVals`, `agronomia.py` (Agrofit), `os_campo.py` (ficha), `processo_planos.py` | 214 cabeçalhos a 1440 e 197 a 390 |
| VIS-05 | Toda lista do motor com ordenar e filtrar ganha Tabela \| Cartões (antes só o quadro `MODO_LISTAS` e as listas com colunas essenciais ou Agrupar por). Matriz sem ordenar (capacidade por mês) fica só em Tabela | `engine.grid` | de 83 para 237 das 247 grades; VIS-05 de 77 telas para 0 |
| VIS-06 | Nos cartões, o texto de apoio apagado da célula fica só na Tabela (a regra existia, mas não pegava: o desenho grava a cor em rgb) e as demais partes do valor ganham espaço ("Fungicida AF26-02" colava) | `engine.CARTOES_CSS` | toda lista em Cartões |

## O que fica, por regra (tela, evidência e mudança exata)

### TAB-05 · ação com texto na célula (31 telas; 3 do Agrícola no menu)

- **Telas no menu:** AG-01 (Confirmar foco, Seguir monitorando), CA-02 (Conferir), SAF (Editar, Continuar: aplicar plano…), CMP (Abrir compra, Consultar pedidos), GE-08 (Autorizar bloco), ON-01 (Rever dados, Desenhar áreas…).
- **Fora do menu:** AG-05, AG-06, CA-04, CO-02 a CO-06, GE-04, GE-07, LO-02, LO-04, PL-02, PT-02 a PT-07, SU-06 a SU-09, VE-04, VE-06.
- **Mudança exata (motor, um PR próprio):**
  1. `menu_linha` passa a valer também sem `dele`: o motor acrescenta a coluna do ⋯ (cabeçalho `.g2th` vazio, célula `isDel` com `rm=true` e sem "Excluir");
  2. depois liga `menu_linha=True` por padrão.
- **Por que não neste lote:** os botões mudam de lugar em ~15 testes que clicam neles pelo texto (mip_fluxo, mip_correcoes, irr_estado, irr_fluxo, tabelas_irr, os_irrig_filtro, ben_fluxo, links_ocultos, saf_operacoes, acao_unica, componentes, ds_test, etapas_celular, saf_cmp_continuidade). É uma frente própria com os oráculos revistos um a um.

### TAB-07 · cartões de resumo acima da lista (31 telas)

- **No menu:**
  - Agrícola: AG-01det, CA-01det, CA-01x-os0420, CA-02, GE-03;
  - Suprimentos: IC;
  - Comercial: IV;
  - Crédito: GE-08;
  - Configurações: CF-05;
  - Onboarding e backoffice: BO-02, ON-01.
- **Fora do menu:** CA-01, CO-01, CO-02, CO-07, GE-01, GE-04, GE-05, LO-01 a LO-04, PL-01, PL-03, PL-04, PL-05, PT-06, SU-01, SU-03, SU-05 a SU-09, VE-04.
- **Mudança exata, tela a tela:**
  - tirar o `kpis([...])` do corpo;
  - a contagem que repete a lista vira filtro rápido (`qf=`) da grade;
  - a soma vai para a linha de total;
  - o indicador sem lugar na lista vai para o Painel do módulo (PAGR, PMAN, PSUP, PCOM; Crédito e Configurações não têm painel).
- **Por que não em lote:** alguns cartões trazem dado que a lista não mostra (ex.: "Saldo parado 70 ha · OS-0420 · Trator T1" no CA-01). Tirar sem levar o dado para outro lugar perde informação. O `engine.kpis` é a peça comum, mas a decisão de onde cada número vai é de cada tela.
- **IC e IV:** são telas de análise; os indicadores entre os blocos fazem o papel de painel do assunto. Os 3 primeiros cartões do IC repetem os filtros rápidos ("Comprar agora 4") e devem sair na mesma frente.

### CAB-1 e CAB-2 · cabeçalho das telas fora do menu (`ui37.py`, arquivo proibido)

Ver "Mudanças pendentes em arquivos proibidos".

### TAB-08 · tabela própria sem ⇅ e funil

- **OS-0424-ficha:** é a ficha impressa de preparo (papel). O cabeçalho já tem 40 px (TAB-10), mas não ordena nem filtra.
- **Proposta:** registrar como exceção de documento impresso, se o Codex concordar na revisão; não é pergunta ao proprietário.

### AGR-02 no Kanban da O.S. (achado pela bateria)

- O nome da raia ainda "desce": grava `trilha=` no endereço e mostra "Descer em …", mas desde a AGR-02 a trilha não recorta mais nada. O botão fica sem efeito.
- Neste lote, a seta da raia foi para a esquerda (TAB-09), o que não muda esse comportamento.
- **Mudança exata (`areas/processo_os.py`, `_kanban_raias` e `v.kb_raias`):** a raia ganha ▸/▾ que recolhe, como o grupo da Tabela; `desce` e `lab: 'Descer em …'` saem.
- **Teste:** `visoes2_formas_test.py` F2–F4 testa a trilha antiga e reprova igual na base e na candidata (teste obsoleto). Revisar junto com a mudança.

## Mudanças pendentes em arquivos proibidos (frente Cadastros)

| Arquivo | Telas | Regra | Mudança exata |
|---|---|---|---|
| `ui37.py` (`shell37`) | 37 telas fora do menu que abrem por link, mais 49 só por endereço | CAB-1, CAB-2 | Quando `fname` não está em `VOLTA37` e não há `crumbs_extra`: (1) pôr o mesmo `a.volta37` "‹ Módulo", com o módulo pelo prefixo (AG, CA, PL, IR → Agrícola; SU → Suprimentos; CO, VE, LO → Comercial; GE → o hub do item; PT → Portal; MB → App); (2) não escrever `ctx` (Fazenda · Safra) como texto no cabeçalho. O contexto vai para a faixa da FIL-01 (`faixa_filtros`), como nas telas do menu |
| `ui37.py` (`VOLTA37`) | CA-02 (Apontamentos), BO-02, ON-01, OS-0424-ficha | CAB-1 | CA-02 → ("Ordem de Serviço", "OS.dc.html"); BO-02 e ON-01 → ("Outros acessos", "MOD-OUT.dc.html"); a ficha → ("OS-0424", "CA-01det.dc.html") ou exceção de documento impresso |
| `areas/gestao.py` | GE-08 (Crédito) | TAB-07, TAB-05 | Tirar os 4 `kpis` do topo (dívida, serviço da dívida, capacidade, a liberar): somas na linha de total da `g_cre`; "A liberar" como filtro rápido. "Autorizar bloco" para o ⋯ (`menu_linha=True`, depois do motor) |
| `areas/gestao.py` | GE-01, GE-03, GE-04, GE-05 | TAB-07 | Mesma regra do TAB-07 acima, tela a tela |
| `areas/gestao.py` | GE-04, GE-07 | TAB-05 | "Importar retorno", "Propor pagamento", "Reabrir com motivo", "Verificar resultado", "Encerrar com evidência" para o ⋯ |
| `areas/cadastros.py` (`CADX_CSS`) | CD-01 a CD-08 | TAB-08, TAB-10 | Tirar `.cadx .g2hb{text-transform:none;letter-spacing:0;font-size:12px;white-space:nowrap;max-width:none;…;padding:10px 2px 10px 0}` e `.cadx .g2rola [role=row]{font-size:13.5px!important}`. Hoje o cabeçalho dos Cadastros sai em caixa normal e 12 px, e só tem 40 px porque o motor vence o padding (CAD-01 já prevê tirar o CADX_CSS) |
| `areas/cad_fazendas.py` | CD-01det (Talhão) | FIL-01 | O seletor "Talhão" fora da faixa vai para `ui37.faixa_filtros` |

## Provas (executado nesta branch)

Comandos executados de `tools/prototipo/v37/gen37/`, com `CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico`. Os resultados e as contagens estão no relatório da entrega e nos logs de `tabelas/`.
