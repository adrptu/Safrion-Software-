# PR #127 · revisão e integração (Claude, 19/10/2026)

O PR #127 é do Codex e mexe só em `ben_fluxo_test.py`. Revisão no HEAD `0b1c1593`, base `1802dec2`, destino `claude/v44-v135-osagrupa`. Integração em `32d6b262`.

## O que muda (só teste)
- **M3:** na chegada pelo "Ver na Manutenção", exige "Bloqueado" no resumo da Situação do ativo.
- **M4:** abre a Situação e exige o motivo do bloqueio. A seção nasce recolhida desde a TAB-12.
- **EP-390:** abre o Estoque de produto com `?view=cartoes` e conta os cartões do motor (`role=listitem` da "Lista em cartões"). A classe `.pr-card` não existe mais no PROD.

## Provas executadas (`logs/`)
| Prova | Resultado |
|---|---|
| `ben_fluxo` completo no `0b1c1593` (render do `4872d732`) | 225/225 |
| Modos manutenção e celular no render da v141 (`262662af`, composição atual) | 15/15 |
| Modos manutenção e celular no `376d7888` (primeiro commit do PR) | 15/15 |
| Contraprova: o oráculo antigo (`4872d732`) no mesmo render | 12/14, reprova exatamente o M3 e o EP-390 |
| Contraexemplo 1: a13 Apto | "Bloqueado" não aparece em lugar nenhum da página |
| Contraexemplo 2: Estoque de produto a 1440 px | Tabela 0 cartões, Cartões 3 cartões |
| Contraexemplo 3: Estoque de produto a 390 px | A Tabela também vira cartões (3); é o comportamento do motor no celular |

Conclusão dos contraexemplos: os oráculos novos discriminam.

**Observação:** a primeira execução completa no `376d7888` parou depois de 4 modos (62/62) porque o disco desta máquina encheu. A execução de 225/225 é a refeita no `0b1c1593`.
