# Pedidos do proprietário de 16/10/2026: fontes sem parecer

Esta pasta guarda as fontes dos três pedidos, copiadas sem alteração dos arquivos que o proprietário anexou no canal do Claude em 16/10/2026. **Não há parecer do Claude aqui.** As avaliações independentes de cada agente ficam em outras pastas e só são lidas depois que as duas estiverem prontas.

- **Base:** `b9898643662715a3f7b17bf7797d44e81e5e4a3d`, ponta de `claude/v44-v69-mapa` em 16/10. É a fonte vigente do protótipo.
- **Versão publicada citada nos pedidos:** artefato 1792184197-5a81.
- **Hashes:** `SHA256SUMS`, conferidos contra os anexos originais na cópia.

| Pedido | Arquivo | Anexo original |
|---|---|---|
| Raio-X do alvo | `raiox-alvo-pedido.md` | `eafb3d12-prompt-safrion-raio-x-do-alvo.md` |
| Mapa com UX/UI de excelência | `mapa-ux-pedido.md` | `0ad3237e-prompt-safrion-mapa-ux.md` |
| Mapa: inventário D1–D30 e 15 oportunidades | `mapa-ux-anexo-analise.md` | `3744923e-anexo-mapa-analise.md` |
| Resolver em 1 clique | `resolve-1-clique-pedido.md` | `c61a935a-prompt-safrion-resolve-em-1-clique.md` |
| Insumos × estoque e compras: 21 melhorias | `resolve-1-clique-anexo-insumos.md` | `96275553-anexo-insumos-analise.md` |

## Gabarito do Raio-X (12 de 14)

- O enunciado do gabarito está em `raiox-alvo-pedido.md`, linhas 19–25 (efeitos plantados e o resultado de 25/09) e linha 249 (a forma de entregar).
- A simulação que o produz é `docs/integracao/V71/insumos/pragas-no-tempo.html`, já versionada na base.
  - SHA-256 `8b9e105e7ee7e9f0692c2264b3f41fe45bcb3da1bec3916f23e8a0e72a717f15`.
  - Esse hash é igual ao do anexo `714f7525-pragas-no-tempo.html` que o proprietário mandou em 16/10.
- O artefato privado do Raio-X (versão 3) não está no repositório. O pedido o cita só como referência.

## Onde está o código de cada recorte (fonte vigente)

Todos os caminhos ficam em `tools/prototipo/v37/gen37/`. Foram localizados por `git grep` na base. Os anexos citam linhas do HTML publicado (`*.dc.html`), não estas fontes, então cada afirmação precisa ser conferida aqui.

**Mapa (IN-04 e telas com talhão)**
- IN-04, camadas e MapLibre: `areas/inicio.py`, `talmapa.js` e `support.js`.
- CD-01 e CD-01det: `areas/cad_*.py`.
- PL-06: `areas/planejamento.py`.
- CA-01: `areas/campo.py`.
- AG-01det: `areas/agronomia.py`.

**Resolver em 1 clique**
- Motor do cenário (lote, disponível, liberação, reserva): `cenario.js` e `cenario.py`.
- O.S. (insumos, `osUsoItem`, `osc_ajustar`): `areas/processo_os.py`.
- Manutenção (`manSolicitar` e `manReceberSc`): `areas/maquinas.py` e `dados_manutencao.py`.
- Compras de materiais (`cmmDaOm` e a regra "Nunca safra ou cultura"): `dados_compras_mat.py`.
- Beneficiamento (`benAlocarCx`): `ben.js` e `dados_ben.py`.
- Decisão MIP com selos "Sem estoque": `areas/agronomia.py`.
- Papéis (`G2_PAPEIS`): `g2lib.js`, `areas/configuracoes.py` e `configuracoes.js`.

**Raio-X do alvo**
- Camada Pragas e doenças do mapa: `areas/inicio.py`.
- Vistorias e decisão MIP: `areas/agronomia.py`.
- Agrofit (AG-07): `areas/agronomia.py`.

O padrão `cad_*.py` agrupa vários arquivos. Para a lista exata: `git ls-tree -r --name-only b9898643662715a3f7b17bf7797d44e81e5e4a3d tools/prototipo/v37/gen37/areas`.

## Composição candidata

- `05947ad` = base + PR #81 (EST-ONDA0) + PRs #90 e #91 (crédito).
- Ainda não foi enviada; a bateria q30 está rodando.
- O EST-ONDA0 mexe em estoque e reserva. Quando entrar, as afirmações do anexo de insumos sobre o motor devem ser conferidas de novo nessa ponta.
