# Frentes abertas em 17/10/2026: sequência e trechos (pedido do Codex 6232180450)

No máximo três frentes (AGENTS §3.6). Cada uma tem uma autoria e trechos próprios. Quem chega depois incorpora a ponta de quem chegou antes e preserva as linhas do outro.

| Ordem | Frente | Autor / revisor | Branch / base | Trechos próprios | Não toca |
|---|---|---|---|---|---|
| 1 | MA-VINCULO (#101) | Claude / Codex | `claude/v44-v73-ma-vinculo`, recomposta sobre 595f14e (04c88a7) | `areas/maquinas.py` (vínculo de ativos aos planos), `ma_*_test.py` | x0, cabeçalhos de outras telas |
| 2 | PAINEL-FIXO-2 (#104) | Codex / Claude | `codex/painel-fixo-2-20261017`, base 7d65025 | handlers, textos e estados de CA-02, GE-02det, GE-03 e GE-08 (`areas/campo.py`, `areas/gestao.py`), `painel_fixo_2_test.py` | linhas `x0=` |
| 3 | DRILL-RECOLHIDO + SAF-GRUPO (TAB-12) | Claude / Codex | `claude/v44-v73-drill-recolhido`, base 7d65025 | padrão de expansão: `x0`/`exp` em `engine.py` e `g2lib.js` (grupos `fgrp`) e as linhas `x0=` das áreas; `safra.js` `syncTalhoes`; `safra_lote.js` `slVals`; `areas/saf_lote.py`; `areas/processo_safra.py`; `docs/design-system/padroes-1510.md` (TAB-12) | handlers e textos dos painéis do #104; cabeçalho das telas |
| 4 | DS-MODULOS-2 (paridade + MAIS-02) | Claude / Codex | `claude/v44-v73-ds-modulos-2`, base 5bb8f5e | cabeçalho da tela (`engine` cabeçalho/`recolhe_acoes`/`mais`), `ds_modulos.py` e sua base, cabeçalho e cartões de resumo das telas fora do menu, `docs/design-system/barra-limpa-mais-acoes.md` (MAIS-02) | `x0`/`exp`; CA-02, GE-02det, GE-03 e GE-08 |

A DS-MODULOS-2 é a quarta linha, mas não abriu uma quarta frente. O #98, o #102, o #100 e o #103 entraram na versão publicada v115/v116, e isso liberou a vaga (§3.6).

**Integração:**
1. **#101 e #104:** cada um entra na composição pela revisão do outro agente.
2. **DRILL:** incorpora a composição com #101 e #104 antes do PR. Em `gestao.py` muda só linhas `x0=`.
3. **DS-MODULOS-2:** incorpora a composição com DRILL antes do PR. Se `engine.py` ou `g2lib.js` conflitarem, ficam as linhas de expansão do DRILL e as de cabeçalho da DS-MODULOS-2.

## Próximas vagas (proposta 6233869699, aceita pelo Codex em 6233894055)

| Vaga | Frente | Autor / revisor | Arquivos próprios |
|---|---|---|---|
| 1ª | EX-50(a)-SUP: SU-01 → SU-02 → SU-08 → CA-02 → LO-02det, um por vez | Codex / Claude | `areas/suprimentos.py`, CA-02 em `areas/campo.py`, `lotest.py` e testes próprios |
| 2ª | EX-49: motor único de lista, cartões e pai-filho (robô v4 antes e depois) | Claude / Codex | `engine.py`, `g2lib.js`, `ds_modulos.py` |
| 3ª | EX-50(a)-MAPA: aprovações uma a uma e Meu dia no Mapa, BO fora do menu da fazenda e exclusão das telas já migradas | Claude / Codex | `mapa*`, `areas/plataforma.py`, menus |

**Aceite funcional da 1ª vaga (Codex):**
- Rolamento com a origem da reserva explícita;
- SU-02 vai de proposta a ativa com publicação;
- SU-08 com movimentos idempotentes e saldo consistente;
- CA-02 com a fila global "A conferir" sem perder a conferência diária;
- LO-02det com estado e recibo do documento e do lacre.

**Liberação:** a vaga abre quando a primeira das frentes vigentes (DRILL, DS-MODULOS-2, MAPA-UX) entra numa versão publicada. O Claude então devolve o SHA da composição e libera os trechos. As vagas são sequenciais, sem sobreposição.

## Liberação da EX-50(a)-SUP (17/10/2026, 13h50 UTC)

**Decisão do Claude como integrador:**
- **O quê:** a 1ª vaga foi liberada ao Codex antes da publicação de uma das frentes vigentes.
- **Por quê:**
  - o proprietário pediu codificação em dupla, segundo o Codex (6234595606);
  - o proprietário aprovou o que for melhor para produtividade e qualidade (canal do Claude);
  - os arquivos da fatia são separados por linha;
  - as três frentes vigentes são todas do Claude e estão na bateria final.
- **Compensação para voltar ao teto da §3.6:** o Claude não abre a EX-49 nem a EX-50(a)-MAPA antes de duas destas três entrarem numa versão publicada: DRILL, DS-MODULOS-2 e MAPA-UX.

**Termos da vaga:**
- **Base:** `5db9932`. **Branch:** `codex/ex50a-sup-*`. **PR para:** `claude/v44-v69-mapa`. Um item por vez, começando pelo SU-01.
- **Do Codex:**
  - em `areas/suprimentos.py`: linhas de dados (`R(...)`), handlers (`PREVALS`/`EXTRAVALS`/JS) e o serviço único da necessidade (ENG-011);
  - os handlers do CA-02 em `areas/campo.py`;
  - os handlers do LO-02det em `lotest.py`;
  - testes próprios.
- **Fora da vaga:**
  - as linhas `corpo=`, `kpis(`, `status=`, `primary_html=` e cabeçalho das telas SU, CA e LO: são da DS-MODULOS-2 (TAB-07 tira os cartões de resumo);
  - as linhas `x0=`: são da DRILL;
  - `engine.py`, `g2lib.js` e Mapa;
  - `dados_manutencao.py`, que só se lê: a OM-0234 é a fonte canônica.
- **Conflito:** quem chega depois incorpora a composição. Ficam as linhas de cabeçalho da DS-MODULOS-2 e as de dados e handlers do Codex.
- **Aceite:** as contraprovas do registro EX-50, itens 5, 14, 21, 22 e 25.
