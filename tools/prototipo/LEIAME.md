# Protótipo navegável v3.7 (Canvas v10) — fonte do gerador

Cópia de preservação da fonte que gera as 145 telas do protótipo publicado como Canvas v10 (27/09/2026). Até esta cópia, a fonte existia só na sessão do Claude no Mac do proprietário.

- `v37/gen37/`: gerador (`build.py`, `engine.py`, `ui37.py`, `areas/*.py`, `cenario.js`, `g2lib.js`, `safra.js`), sondas de QA (`_probe/*.py`, `support.js`) e as telas geradas (`project/*.dc.html` e o `canvas.json` publicado).
- `v37/*.json`: catálogo, menu, mapa do menu, fluxos, FO e matriz que o gerador lê em `v37/`. Vieram de `v37/_base` (26/09/2026), a única cópia existente.
- Fora desta cópia: capturas, PDFs, renders, medições, saídas de sonda e arquivos `*_backup.py`.

## Regenerar

```bash
cd tools/prototipo/v37/gen37 && python3 build.py
```

Com Python 3.12, a regeneração reproduz as 145 telas `*.dc.html` idênticas byte a byte às publicadas. O `canvas.json` guardado é o publicado: ele traz `attachments` e a data de `createdOnFiles` da publicação, que o build não recria.

Não é código de produto nem entra na aplicação. A autoria da navegação nova é do Grok (NAV-F1-A); esta fonte é a referência do Canvas v10.
