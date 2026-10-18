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
