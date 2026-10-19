# v137: integração dos PRs #117 e #120 do Codex (18/10/2026)

Revisor e integrador: Claude. Os dois PRs entram na composição `claude/v44-v135-osagrupa` depois da v137 publicada (`aa506fc2`).

| PR | HEAD | O que muda | Executado | Contraprova |
|---|---|---|---|---|
| #117 | `45150906` | Oráculos do `filtros_cultura_test` (F2 a 1440 e 390 px) e do `tabelas_irr_test` (TABR-CTX-02) | No render da v137: 11/11 e 106/106 | O `filtros_cultura_test` da base `75e77324` reprova o F2 nos mesmos dados: o T2 não está nas opções |
| #120 | `c9a01ca0` | `frentes_agenda.js`: o deslocamento consome só o turno, a espera fica no destino e a operação ocupa turno ∩ janela (A1 do Claude) | `frentes_agenda_unit` 21/21 em UTC e em America/Sao_Paulo | O núcleo `05604b2f` reprova o teste novo ("viagem chega antes da janela e espera no destino") |

**Sonda do revisor** (`logs/pr120/sonda_a1.js`), com 6 casos nos dois núcleos:
- **Contraexemplo do A1:** passa a caber. Chega às 9h, espera 1h e opera das 10h às 12h.
- **Chegada depois da janela:** inviável.
- **Viagem que atravessa a noite:** pausa de 14h.
- **Janela no dia seguinte:** espera de 10h dentro do turno e pausa de 14h.
- **Viagem sem turno:** motivo próprio.
- **Sem deslocamento:** sem mudança.

O núcleo da agenda ainda não está ligado a nenhuma página: o render não muda e o artefato não precisa de nova publicação.

## Saída dos testes (PR #72) e oráculos desatualizados (revisão automática do Codex no PR #47)

**Proteção de saída do PR #72.** Antes, o processo podia terminar com código 0 mesmo com verificação falha ou sem nenhuma verificação. Agora `intest.py`, `solo_os_test.py` e `solo_rev_test.py` terminam com 1 nesses casos. Só entrou a proteção; os oráculos atuais ficaram como estão.

| Teste | Verde | Com falha proposital | Vazio |
|---|---|---|---|
| `solo_os_test` | 18/18, saída 0 | 18/19, saída 1 | — |
| `solo_rev_test` | 22/22, saída 0 | 22/23, saída 1 | — |
| `intest` | não executável: o teste está vermelho de verdade (oráculos do Mapa antigo, ver abaixo) | — | 0/0: saída 1 com a proteção, saída 0 sem ela |

O `intest` cobre o Mapa antigo: 9 abas, rótulo em `foreignObject` e NDWI. No Mapa atual ele falha em 6 verificações e para num erro de script ao tocar no T7 (`logs/pr72/intest.log`). Ele fica vermelho e visível. A correção dos oráculos não entrou nesta mudança.

**Oráculos desatualizados** (achados P2 do revisor automático no `d482c334`; reproduzidos antes da correção):

| Teste | Antes | Depois | Causa |
|---|---|---|---|
| `tabelas_cad_irr_unit` | 44/51 | 52/52 | O ambiente de teste não trazia a `g2ordk`, que a `g2fkeys` passou a chamar (C15–C19). Operações e rendimentos saíram do CD-02 para o CD-08 (A1) |
| `usar_os_unit_test` | 19/24 | 25/25 | A demonstração das Frentes (OS-0584 a 0597) entra nos candidatos do AG-07. A O.S. da demonstração tem a cultura planejada, conferida à parte (U1b) |
| `alocacao_unit_test` | 20/21 | 21/21 | O Trator 03 também atende a demonstração (OS-0595 a 0597). Ao cancelar a OS-0430, ele perde só os blocos dela |
