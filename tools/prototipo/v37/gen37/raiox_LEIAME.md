# RX-0 — fechamento diagnóstico C2.2

Base de revisão: Codex 9b74b375, parecer Claude 6253895754 e sonda 778c56fc. O ajuste final somente torna não atribuível a evidência de insuficiência, não seleção e população ausente; preserva níveis e resultados por safra.

## Resultado executado

640 populações sintéticas, duas safras,80 sementes por alvo/safra,quatro alvos,16 talhões. Fonte v3.1 SHA256 cb481aab9dc714712f2c2d8e348231891837022195d70c871fa1df8b2b665a25. Entrada SHA256 bb069cfb26fbd1102c263cabb0d30e74068714439861fd0fc40eefacd50b456f.

1280 combinações: insuf640,nulo468,fraca141,moderada31;forte/grupo/não selecionado/não avaliável zero. Fraca:54 próprias e87 herdadas;moderada:18 próprias e13 herdadas. Placebo:4 fracas próprias e9 herdadas;nenhuma moderada. O 64/77 anterior foi erro de soma,retificado pelo Claude6253895754.

Evidência própria exige representante nas duas safras. Mate em pelo menos uma é herdada do grupo e não comprova efeito do fator. Insuficiência,não seleção e ausência de população têm evidência não atribuível. Modelo vazio é insuficiência,sem beta artificial. Precedência: população ausente,grupo,insuficiência,não seleção,combinador v3.1.

## Limites

Antracnose e cochonilha não têm janelas suficientes para dar poder ao motor neste pacote. Placebo é parcialmente agrupado com qs/molh. Direção dos efeitos permanece não avaliável. Zero forte no v3.1 é abstenção diagnóstica após achado,não certificado de recuperação causal nem validação independente. Não ajustar o gerador para forçar aprovação. RX-1 não iniciado.

## Reprodução e provas

Sondas de Claude em docs/integracao/V73/rx0-revisao no commit778c56fc recuperam fontes e geram entradas. raiox_unit.js aceita --motor-input e --recombinar; recombinação exige SHA da fonte igual ao bruto e não refaz fits. Suíte v3.1 passou em9b74b375. Ajuste final: igualdade integral dos640 resultados e1280 níveis;640 insuf não atribuíveis,12 etiquetas antes herdadas corrigidas. Fontes/brutos locais preservados em /private/tmp/rx0-a4; isso não comprova disponibilidade remota desses brutos.

Revisão/integração final pelo Claude; sem merge pelo autor. Este fechamento é do ensaio RX-0,não do protótipo,produto ou HML.
