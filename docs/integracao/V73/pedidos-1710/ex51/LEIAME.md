# EX-51 · Fluxo conectado entre módulos: pacote do proprietário (17/10/2026)

O proprietário enviou ao Claude, para Claude e Codex melhorarem e implantarem juntos: "Melhore essas sugestões unindo forças você e códex e implantem da melhor forma possível."

| Arquivo | O que é |
|---|---|
| `prompt-safrion-fluxo-conectado.md` | Pedido, o que foi medido, as oito regras (R1–R8), o catálogo de eventos, as quebras prioritárias, a jornada OS-0502, as fatias F1–F5 e o aceite |
| `anexo-fluxo-achados.md` | Números do robô v5 e as cinco cadeias (A–E), com etapas, 96 quebras (ID, evidência, proposta, esforço, prioridade), o que já funciona e as ideias das telas que saem |
| `anexo-robo-v5.html`, `anexo-robo-v5-resumo.py` | O robô de passagens e o resumo, para repetir a medida antes e depois |
| `fluxo-conectado-safrion.html` | A especificação viva com demonstração clicável. É referência de ideias, não código a copiar |
| `prompt-safrion-excelencia-ex51.md` | O prompt-mestre na versão que inclui o EX-51 |

- **Cópia fiel, com uma exceção.** Em `anexo-fluxo-achados.md` e em `fluxo-conectado-safrion.html`, dois nomes de chave de armazenamento local (as atribuições literais das chaves do cenário e das compras) viraram `CEN_LS` e `SOL_LS`. Nenhum dos dois é segredo; o Gitleaks os acusava como falso positivo (regra `generic-api-key`). O conteúdo e as evidências não mudam.
- **A medida é anterior a muita coisa.** Foi feita no protótipo 1792184197-5a81 (artefato v108). Desde então entraram, entre outras, as versões v110–v127: SU-01, SU-02, SU-08, CA-02 (fila de conferência), LO-02det e o design system nos demais módulos. Por isso cada quebra é validada de novo no código atual.
- **Decisões do proprietário de 17/10 que já respondem parte das quebras:** exclusão das telas ocultas depois de migrar funções e links; financeiro no ERP (E-6 e E-8); portal mínimo fora do menu.
