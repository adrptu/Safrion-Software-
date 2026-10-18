# RX-0: revisão crítica do Claude sobre `e543ee2f` (18/10/2026)

O parecer está no PR #47, comentário 6250325658.

- A sonda `sonda_rx0.py` roda sobre `raiox_gabarito.py` do head `e543ee2f` (`codex/rx0-oraculo-20261018`), copiado para uma pasta à parte. Comando: `python3 -I -B sonda_rx0.py <pasta com raiox_gabarito.py>`.
- Saída em `sonda_rx0_e543ee2f.log`. Cada linha corresponde a um achado:
  - R1: a entrada `desligado` traz as `obs` do contrafactual com as mesmas `series`, e a `ligado` repete o mesmo mundo para cada fator;
  - R2: o HT aceita um controle com datas diferentes;
  - R4: a versão publicada depois vence mesmo sendo menor.
- Dados sintéticos; o motor não foi executado.
