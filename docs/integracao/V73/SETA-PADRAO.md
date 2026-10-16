# SETA-PADRAO · Seta única de abrir e de ir (TAB-11)

```text
ID / resultado útil / persona: SETA-PADRAO (TAB-11) · uma seta só, fina e cinza, para abrir/recolher e para ir ao detalhe, em todas as telas · quem usa qualquer lista, árvore ou seção do protótipo
Requisitos do PRD e fora do escopo: PRD cap. 74 (DS) e padroes-1610 (TAB-04, TAB-08, TAB-09); fora: lista suspensa (▾ no fim), ordenação do cabeçalho (⇅ ▲ ▼), › de trilha e de texto corrido, › no fim de atalho de texto (BOT-08)
Autor / revisor / integrador: Claude / Codex / Codex (regime leve, AGENTS §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: c9ffa08 · engine.py, g2lib.js, safra.js, areas/{maquinas,processo_planos,processo_safra,colheita,analise_solo}.py, areas/processo_os.py (só o painel da O.S., _painel), testes listados abaixo
Aceite e comando de verificação: seta_padrao_test.py verde a 1440 e 390 e vermelho na base; regressão sem vermelho novo; galeria olhada
Estado / impedimento / próximo passo: ver "Resultado" abaixo
```

## Pedido

Proprietário, 16/10/2026, com a captura do CD-01 (Fazendas e talhões): "mude o estilo do drill down daquele preto para a setinha mais intuitiva e amigável dos debaixo, melhore ela e implemente como nosso padrão em tudo."

Na captura, o grupo "Santa Rita" tinha o triângulo preto cheio de texto (▾, 13 px, #15201A) e os talhões tinham a seta fina cinza (›, SVG de 14 px, #9AA59E).

## Regra (TAB-11)

Texto completo em `docs/design-system/padroes-1610.md` § TAB-11. Resumo:
- **um desenho:** chevron SVG de 16 px, traço de 1,75 px, cor do texto secundário (#65736A);
- **abrir/recolher:** dentro de um botão nativo com `aria-expanded`; fechado aponta para a direita, aberto gira 90° (120 ms; parado com `prefers-reduced-motion`); nome "Abrir …"/"Recolher …";
- **ir ao detalhe:** a mesma seta, parada; quem navega é a linha;
- **alvo:** 24 px no mouse, 44 px no toque; a seta de ir e a linha sem seta guardam a mesma largura;
- **interação:** hover verde (VIS-02), anel de foco verde de 2 px, Enter e Espaço alternam;
- **sem dica** (TAB-04, 15/10).

**Peça única:** `engine.seta`, `engine.seta_abrir`, `engine.seta_ir`, `engine.SETA_VAZIO`, `engine.SETA_CSS` (HTML) e `g2seta(aberta, nome)` no `g2lib` (estado e nome).

## Decisões tomadas sozinho

| Decisão | Por quê |
|---|---|
| Cor #65736A (texto secundário), não o #9AA59E da seta antiga das filhas | O #9AA59E dá 2,55:1 sobre o branco, abaixo dos 3:1 de componente de interface (WCAG 1.4.11). O #65736A é o token de texto secundário da DS (4,9:1) e continua cinza. |
| Sem dica na seta | A TAB-04 (proprietário, 15/10) tirou a dica da seta: "a seta é óbvia, e a dica cobria a linha de baixo" (`g2dicaTexto` ignora `.g2car`). A dica curta "Abrir/Recolher" pedida na tarefa contraria essa decisão escrita; fica para o proprietário decidir. |
| Nome acessível "Abrir …"/"Recolher …" em toda seta | Antes havia "Expandir …", "Mostrar …" e "Ocultar …" conforme a tela. A TAB-04 já dizia "Abrir …"/"Recolher …". |
| "Expandir tudo"/"Recolher tudo" com a mesma seta | Era um terceiro desenho (setas para cima e para baixo). Agora a seta mostra o estado das linhas: direita com linhas recolhidas, baixo com tudo aberto. |
| Lista suspensa fica com ▾ no fim | TAB-09: lista suspensa não é seta de abrir. |
| Faixa de etapas no estreito ("Etapa 2 de 4 · … ▾") fica | Abre uma folha com a lista (como lista suspensa), não abre conteúdo ali mesmo. |
| › no fim de atalho de texto ("Planejar ›", "Ficha no app ›") fica | É rótulo de navegação dentro do texto do botão (BOT-08), não a seta de linha; fora do escopo pedido. |
