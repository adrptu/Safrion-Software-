# PR #129 (EX-53 D11, metas): revisão e integração do Claude, 19/10/2026

- **Autoria:** Codex. **Revisão e integração:** Claude.
- **HEAD revisado:** `72c39889e972af69732a92ca941416ac24ec65dc`, juntado à composição `0cff1901` (`claude/v44-v135-osagrupa`).
- **Achados:** revisão anterior no HEAD `d45949c8` (6259709212 e 6259763258).

## Achados e desfecho
| Achado | Severidade | Desfecho |
|---|---|---|
| **F1:** o rótulo do talhão no Mapa › Custos levava a dica inteira da meta e cortava ("R$ 10.573 · +0,0 % · Me…") | S3 | Corrigido em `72c39889`. O rótulo volta a "valor · desvio", e a dica da meta passa para a fonte da legenda. Foto: `fotos/mapa_custos_meta_1440.png` |
| **F2:** histórico de versões vazio sem texto | S4 | Corrigido. A seção mostra "Nenhuma versão ainda". Foto: `fotos/cf06_sem_versao_1440.png` |
| **F3:** a 390 px, `×` e "Salvar meta" com 32 px de altura | S4 | O painel da CF-01 na v141 é igual, então o defeito é anterior ao PR e vai para a base verde. Foto: `fotos/cf06_editor_390.png` |
| **F4:** oráculo A15 do `config_test` (arquivo do Claude) | Teste obsoleto | Atualizado neste commit. A entrada das Configurações passa a ter 5 cartões, com "Metas e limites" em segundo, como no `ui37.MENU2`. No `d45949c8` o oráculo antigo dava 89/90; no HEAD da junção, o novo dá 90/90 |

## Testes executados no render da junção (`0cff1901` + `72c39889`, dados sintéticos)
| Teste | Resultado |
|---|---|
| `metas_unit`, `metas_comando`, `ex53_metas`, `ex53_m5_cartao`, `ex53_f1c` | PASS |
| `config_unit` · `inteligencia_unit` | 226/226 · 35/35 |
| `config_test` · `config_regressao` | 90/90 · 6/6 |
| `inteligencia_nav` · `painel03` · `nav_modulos` · `plataforma` | 28/28 · 54/54 · 15/15 · 22/22 |
| `mapa_mux_f2` · `mapa9` · `map_decisoes` · `mapa_faixa` · `mapa_camadas` | 29/29 · 13/13 · 18/18 · 25/25 · PASS |
| `paginas_scan` · `links_ocultos` · `textos_soltos` | 5/5 (147 páginas) · 16/16 · 267/267 |
| Sondas do revisor (`logs/sondas.py`): conflito entre abas, teclado, Mapa e IC com meta | 8/9. Falha só a de 390 px (F3, anterior ao PR) |
| Histórico vazio (`logs/f2.py`) | OK |

Os brutos estão em `logs/`.
