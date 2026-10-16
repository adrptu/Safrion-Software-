# Revisão do Claude · PR #79 (IRR-ONDA0), HEAD ec650424, base 8aa0a17

Executado em 16/10/2026, navegador, dados sintéticos, render limpo dos dois lados (156 páginas). Veredito: **integrar depois de ajustes pequenos** (sem S1/S2; quatro S3 e vermelhos novos em testes antigos).

- `irr_onda0_rev_test.py`: PR **45/45**; base **16/45** (`rev_ec65.log`, `rev_base_8aa0a17.log`). V1 término 8/8 (base 1/8), V2 início/pausa/retomada/término 6/6 (4/6), V3 piso da ficha 4/4 (0/4; PV19 7,21 mm = 94 L/s × 3,6 × 16,0 h ÷ 751,1), V4 divergência 7/7 (0/7), V5 água × fertirrigação 2/2 (DEC-2609-10 preservada), V6 teclado 10/10, V7 390 px 5/5, V8 cenário salvo 2/2.
- Testes do Codex: 21/21; com o `irrigacao_estado.js` da base, 6/21.
- Regressão (`logs_pr/_resumo.txt`, `logs_base/_resumo.txt`): verdes ctl5, ficha_pivo(\_unit), outorga_unit, map_decisoes, os_irrig_filtro, os_v39_selo_agua, mapa9, paginas_scan. Vermelhos novos do PR: irr_estado_test 30/38 (base 38/38), irr_fluxo_test 20 + 7 falhas + quebra na linha 146 (base 33/33), tabelas_irr 97/106 (base 98/106). São oráculos do defeito antigo ou do piso R2 (achado F4).

## Achados

1. **F1 · S3 · término antecipado aceita volta completa a 0 h.** OS-0419, Iniciar, Confirmar término com 80 ha e 8.480 m³: a trilha grava "Término antecipado · 0,0 h de bombeamento · volta completa nos 80 ha", encerra e o déficit cai de 11,2 para 1,7 mm (`irrigacao_estado.js:442-447`, `areas/irrigacao.py:574`). Exigir área menor que a do setor e compatível com o tempo bombeado, ou motivo e conferência.
2. **F2 · S3 · relógio simulado global.** (a) Iniciar a OS-0419 leva o "agora" de todas as ordens a 20:02; a OS-0423 (janela 15:00–17:00) passa a iniciar às 20:04, fora da janela conferida e no horário de ponta; na base, 15:02 (`a6_relogio_global.py/.log`). (b) Cenário salvo com ordem em execução: término recusado com "Avance a simulação…", sem comando para isso. (c) "Confirmar término" depois do fim previsto não é alcançável pela tela. Linhas `irrigacao_estado.js:405, 413, 418, 425, 443, 448`. Relógio por ordem (`max(s.agora, irrUlt(o))`) sem gravar o global no início.
3. **F3 · S3 · tela e comando decidem diferente no limite.** A tela usa a estimativa arredondada (1.254 m³) e o comando a exata (1.253,96): com 1.291,6 m³ (+3,0 %) a tela oferece "Validar e encerrar" e o comando recusa pedindo motivo (`areas/irrigacao.py:585-586` × `irrigacao_estado.js:486-487`). Uma função de domínio só (ENG-011).
4. **F4 · S3 de processo · testes antigos não atualizados** (§3.6 base verde): irr_estado, irr_fluxo e tabelas_irr com os novos oráculos; as asserções antigas viram a contraprova na base.
5. **F5 · S4:** 0 m³ medido aparece como "aguardando a leitura" (`areas/irrigacao.py:512-513`).
6. **F6 · S4:** "Necessidade · bruta 13,4 mm" mostra o mínimo do pivô, não a necessidade (12,44 mm; `demandaBr` calculado e não usado); "Lâmina acima da necessidade" esconde "Abaixo do limiar"; ficha incompatível só no IR-02.
7. **F7 · S4:** rótulos "Confirmar término" × "Registrar término antecipado"; texto fixo com `role="status"` (`areas/irrigacao.py:448`).

Conferido sem achado: `irrNec` sai do `irrPerc` (sem fórmula duplicada), sem número fixo no lugar da ficha, papel conferido no domínio (`irrConferente`), aprovação agronômica intacta.
