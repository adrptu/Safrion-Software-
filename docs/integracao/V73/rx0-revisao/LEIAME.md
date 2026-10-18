# RX-0: revisão crítica do Claude sobre `e543ee2f` (18/10/2026)

O parecer está no PR #47, comentário 6250325658.

- A sonda `sonda_rx0.py` roda sobre `raiox_gabarito.py` do head `e543ee2f` (`codex/rx0-oraculo-20261018`), copiado para uma pasta à parte. Comando: `python3 -I -B sonda_rx0.py <pasta com raiox_gabarito.py>`.
- Saída em `sonda_rx0_e543ee2f.log`. Cada linha corresponde a um achado:
  - R1: a entrada `desligado` traz as `obs` do contrafactual com as mesmas `series`, e a `ligado` repete o mesmo mundo para cada fator;
  - R2: o HT aceita um controle com datas diferentes;
  - R4: a versão publicada depois vence mesmo sendo menor.
- Dados sintéticos; o motor não foi executado.

## Reteste do head `8800c9e3` (18/10/2026)

- `sonda_rx0_reteste.py` sobre o `raiox_gabarito.py` do head `8800c9e3`; saída em `sonda_rx0_8800c9e3.log`.
- R1: só entradas factuais, uma por mundo, e o mundo com observação divergente é recusado.
- R2: o controle com datas diferentes sai como `datas_nao_pareadas`.
- R3: `nao_pareado`.
- R4: a versão fora de ordem é recusada, e no corte anterior a versão ainda indisponível não muda nada.

## Revisão do C2.1 emendado `5bdcd2f5` (18/10/2026)

- `sonda_rx0_5bdcd2f5.sh` reexecuta as 640 populações no motor v3.1 (`cb481aab…`) com o harness do Codex; saída em `sonda_rx0_5bdcd2f5.log`.
- Reproduz o resultado do Codex: 640 não selecionado, 468 nulo, 141 fraca, 31 moderada, 0 forte e 0 grupo.
- Os 640 "não selecionado" vêm todos de modelo vazio: antracnose e cochonilha têm de 12 a 24 janelas. O limiar exige 8 casos de cada lado, então nenhum fator chega ao modelo. Isso é falta de dado (`insuf`), não seleção. A lacuna está no C2.1 (autoria Claude), não no harness; a correção é o C2.2.
- Dos 31 moderados, 13 são herdados do grupo (o fator é só *mate* em pelo menos uma safra). Exemplo: 10 vezes "qs moderada" com a molhadura como representante nas duas safras.
- Placebo: 0 forte, 0 moderada; 4 fraca própria e 9 fraca herdada do grupo.
