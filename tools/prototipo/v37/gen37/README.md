# Gerador do protótipo (gen37)

Protótipo de validação, não é produto (AGENTS.md §3.5). Dados sintéticos sempre (`SAFRION_DADOS=sintetico`).

## Montar
```
cd tools/prototipo/v37/gen37
python3 build.py && python3 montar_render.py     # project/ e _render/; o log do build não pode ter "FALHA"
```
Montagem de um commit qualquer, uma vez só (cache com trava contra montagem dupla):
```
../ferramentas/render_cache.sh <commit>          # imprime o caminho do _render/ guardado
../ferramentas/render_cache.sh <commit> .        # e copia project/ e _render/ do cache para esta pasta
```
- Chave: `<sha>-<SAFRION_DADOS>-<gerador>` (gerador = versão do Python + receita da montagem). Monta numa worktree destacada do
  commit (árvore limpa), só com dados sintéticos; build com erro ou "FALHA" não entra.
- Artefato imutável: manifesto sha256 conferido a cada chamada e pasta só leitura; alterado, é recusado.
- O cache fica em `$SAFRION_RENDER_CACHE` (padrão: `render-cache/` no rascunho da sessão; fora dela, `${TMPDIR:-/tmp}/safrion-render-cache`).

## Testar
Um teste de navegador por vez na sua trava:
```
env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpX.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>
```
- **Quais rodar:** `python3 ../ferramentas/testes_afetados.py <base> <cabeça> --motivos` lista os testes que a mudança pode afetar
  (`--lista` sai no formato `nome|VAR=v|comando`). A bateria completa continua valendo a cada marco.
- **Esperas:** `goto` e as esperas longas dos testes terminam quando a página assenta; timer e rede seguem o relógio das esperas
  fixas (crédito) e a soma das esperas nunca passa da de antes. `SAFRION_ESPERA=fixa` volta às esperas fixas (para comparar
  ou isolar um teste instável). Contraprova da espera: `cdp_espera_test.py` (navegador) e `cdp_unit_test.py`.

Detalhes, medição e equivalência: [`../ferramentas/ACELERA.md`](../ferramentas/ACELERA.md).
