# Pedidos do proprietário de 18/10/2026: excelência, ideias dos jogos (EX-52) e indicadores do Painel (EX-53)

**Mensagens do proprietário no canal do Claude:**
- "Melhore essas ideias junto com codex e implantem com excelência."
- "faça seu melhor com codex"
- "faça o melhor possivel junto com codex"

**Arquivos anexados, versionados aqui sem alteração.** A última versão de cada arquivo está nesta pasta, com o sha256 em `SHA256SUMS`.

| Arquivo | Conteúdo |
|---|---|
| `prompt-safrion-excelencia.md` | EX-01 a EX-57. Versão de 18/10, noite. Em relação à anterior, entram só o EX-56 e o EX-57 (resumos e lista de anexos). |
| `prompt-safrion-varredura-final.md` | EX-56: varredura final e encerramento do protótipo. Tem portão: só começa quando todos os outros EX estiverem decididos, implantados, revisados e aceitos. |
| `prompt-safrion-perenes-idade-ciclo.md` | EX-57: perenes com idade, fase e ciclo no plano agronômico. Gemini real obrigatório; parâmetros por cultura validados pelo RT. |
| `prompt-safrion-painel-indicadores.md` | EX-53: catálogo de indicadores do Painel, regras, captura D1 a D13, fatias F1 a F5 e aceite. |
| `prompt-safrion-ideias-jogos.md` | EX-52: oito ideias, J1 a J8. |
| `prompt-safrion-entrada-acoes-revisao.md` | Revisão das entradas e ações. |
| `prompt-safrion-fluxo-conectado.md` | EX-51: fluxo conectado. |
| `prompt-safrion-telas-ocultas.md` | EX-50: telas ocultas. |

**Método pedido nos prompts:**
1. Claude e Codex classificam cada item de forma independente: Adotar, Adaptar ou Rejeitar, com fórmula, fonte e dado conferidos no código.
2. A lista vai ao Codex sem a classificação do Claude. A do Claude fica selada por sha256 até o Codex publicar a dele.
3. Divergência se resolve pela fonte. O Gemini real entra só se houver divergência material de domínio.
4. O Codex registra o resultado no checkpoint.
5. Depois vem a implantação, por fatias, com revisão cruzada.

**A decisão do financeiro foi delegada aos dois agentes**, conforme o EX-51 e o EX-53: cada um propõe sozinho, usando os seis critérios do prompt, e o Codex registra a decisão. Até lá não se cria aba nova.
