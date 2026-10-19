# V66 · bateria completa e vermelhos

- **Bateria:** 187 testes na composição `5eb1ba7`, de 14/10 04:07 a 05:35, com 3 em paralelo e dados sintéticos. Uma linha por teste em `_resumo.txt`.
- **Correções posteriores:** testadas na candidata `ae8ddf1` (impacto abaixo), sem repetir a bateria (AGENTS §3.6).

## Vermelhos da bateria
| Teste | Classe | Situação na candidata |
|---|---|---|
| `agrofit` 1, `comercial_fluxo` AC-01, `inteligencia_nav`, `ma_menu` | Oráculo obsoleto: o Painel é o 1º cartão (PAINEL-01) | 18/18, menu 10/10, 27/27 e 10/10 (`7693ecd`, `340fd92`) |
| `agrofit` 3 | Oráculo com data fixa: o selo depende da idade do arquivo (mais de 7 dias = desatualizada); vermelho antigo da v63 | 18/18 (`7693ecd`) |
| `consumo_divergente` | Oráculo obsoleto (#80): a exposição virou a coluna "Em conferência" | 21/21 (`b82e5b6`) |
| `ma_planos`, `ma_atrito` (c)(d) | Oráculo obsoleto: os cartões saíram da Manutenção (MAN-LIMPA-01) | 18/18 e 13/13 (`340fd92`) |
| `talmapa`, `mapa_solo_texto`, `colheita_mapa` | O MapLibre não carregou: rede do proxy durante a bateria | 8/8, 9/9 e 7/7 repetidos |
| `ma_unica` AC-PCM-22 | Mediu 3 linhas com a tela ainda montando sob carga | 23/23 repetido |
| `ben_fluxo` completo | Estourou os 1500 s. Na repetição (3000 s): 223/224, com a AV no roteiro | Causa: regra local do Beneficiamento. Corrigido em `ae8ddf1`: roteiro 35/35 |
| `cotest` (13 falhas), `os_cenario`, `ostest`, `intest`, `psfix38`, `saf38`, `saftest`, `getest`, `vetest` | Vermelhos antigos, iguais aos da v63 | Sem mudança |

## Impacto na candidata (executado)
| Teste | Resultado |
|---|---|
| `man_limpa` | 9/9 |
| `botoes_retorno` | 6/6 |
| `regras_toque` | 5/5 |
| `painel_modulos` | 20/20 e `--ui` 61/61 |
| `painel_agricola` | 20/20 e `--ui` 24/24 |
| `nav_modulos` | 15/15 |
| `busca_unica` | 7/7 |
| `ma_rastreio` | 58/58 |
| `ma_correcoes_om` | 15/15 |
| `ma_correcoes_pm` | 12/12 |
| `ma_revisao` | 18/18 |
| `matest` | 40/40 |
| `ma_regras` | 150/150 |
| `ma_app_fluxo` | 24/24 |
| `ma_app` | 36/36 |
| `mbtest` | 0 falhas |
| `textos_soltos` | 263/263 |
| `paginas_scan` | 4/4 (147 páginas) |
| `ben_fluxo` completo (todos os modos) | 224/224 |

## Varredura visual (`visual_corte`) e brutos
- v66 × v63: único achado novo, o C4 "· Santa Rita" no MB-01. Era regressão minha e está corrigido (MB-01: 0 achados; VE-04 continua com os mesmos 8). O detector agora conta campo de formulário à esquerda.
- Os 9 vermelhos antigos dão o mesmo resultado na v63 e na v66.
- Brutos, origem, rc e sha256 em [`brutos/README.md`](brutos/README.md).
