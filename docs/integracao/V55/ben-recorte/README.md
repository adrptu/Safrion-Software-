# V55 · regressão do recorte do BEN (6cce975 × base 47ff754), executada

- **Comparação:** recorte 6cce975 (BEN fora da navegação, `BEN_PUBLICADO=False`) contra a base 47ff754 (a composição sem o recorte).
- **Como rodou:** `roda.sh` rodou os mesmos testes nos dois lados, um navegador por vez, com dados sintéticos. Cada lado tem os logs por teste e o `_resumo.txt` na sua pasta (`base-47ff754/` e `recorte-6cce975/`).
- **Varredura de DOM:** `varre_ben.py`, com os JSON dos dois lados.

| Teste | Base 47ff754 | Recorte 6cce975 | Leitura |
|---|---|---|---|
| links_ocultos | 11/0 | **14/0** | L4a-c novos: o BEN está oculto e nenhuma tela visível aponta para `BEN.dc.html` |
| varre_ben (DOM, 1440 e 390 px) | 194 estados · **21** elementos que levam ao BEN | 192 estados · **0** | Cobre cargas, lotes do PROD, linhas do COLH, Estoque, O.S. e MA |
| producao_unit · ben_unit | 121/121 · 168/168 | 121/121 · 168/168 | iguais |
| producao_fluxo | 66/66 | 66/66 | igual |
| tabelas_est · tabelas_ben · tabelas_os · tabelas_saf | 34 · 12 · 38 · 24 | 34 · 12 · 38 · 24 | iguais |
| esttest 1–4 | 24 · 23 · 19 · 13 | 24 · 23 · 19 · 13 | iguais |
| est_cenario · est_fix1 · est_fix2 | 15 · 13 · 11 | 15 · 13 · 11 | iguais |
| cafe_apurar (unit e navegador) | 16/16 e 10/10 | 16/16 e 10/10 | igual |
| ma_unica | 23/23 | 23/23 | igual (a ligação MA ↔ linha de packing não leva ao BEN) |
| acao_unica familias | 8/0 | 8/0 | igual |
| acoes_duplicadas | 142 páginas · 0 | 142 páginas · 0 | igual |
| varredura | 142/142 | 142/142 | igual |
| etapas_celular faixa | FALHA 16 (CMP e outras) | FALHA 16 (34 telas, em vez de 35: o BEN saiu) | vermelho da base, a mesma asserção |
| ben_fluxo | 172/172 | **2/13** | **Esperado pelo recorte, não é regressão.** As falhas exigem a faixa "Cargas e recebimento \| Beneficiamento", o destaque do menu no BEN e o próximo passo "Abrir ordem de beneficiamento" no CARGA. É exatamente o que o recorte tira. O teste do BEN volta a valer quando `BEN_PUBLICADO=True`, depois da rodada 3 |

Nenhum teste fora do BEN mudou de resultado. As linhas iguais foram conferidas nos logs dos dois lados.
