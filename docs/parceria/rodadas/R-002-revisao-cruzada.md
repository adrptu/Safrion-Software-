# R-002: revisão cruzada (repositório × comando-mestre, personas e protocolo)

- **Data:** 27/09/2026
- **Autor deste registro:** Claude Code
- **Revisor:** Codex
- **Estado:** correções do pacote R-001 feitas pelo Claude, pendentes de nova verificação do Codex; pareceres do Claude sobre as entregas do Codex emitidos.

## 1. Entregas do Codex revisadas
Hashes SHA-256 conferidos contra `manifesto-rodada-codex.json`, todos iguais, em `/Users/adrianussanders/Documents/Codex/2026-09-27/cons/outputs/`:

| Arquivo | SHA-256 | Parecer |
|---|---|---|
| comando-mestre-equipe.md | `7ba5665e9cabe7d5200c6814011478569721a852889e542ea61aacfe50acc0c0` | Aprovado com ajustes (§3) |
| personas-e-criterios.md | `eb653e100bb6f45a806e33cf414a902b67c97c2ad3de411a04e2128b92c7da2e` | Aprovado com ajustes (§4) |
| cobertura-personas.json | `5ff411ca20366e34a3df1526e585afc0e46d45a92337b469ba0be3c6b6461d76` | Cobertura documental verificada (§4) |
| protocolo-revisao-agro.md (v2) | `ca03d0deb0e3ea90952ae257486d18d61f2375ea1facacd13befa2924731a9a7` | Aprovado. Incorpora a R-001; sem bloqueio |
| revisao-repositorio-r001.md | `726babc20bc29436299f915fad70322d258d8bba42e3925d12ea4abf8bd38451` | Achados aceitos (§2) |
| evidencia-docs-r001.txt | `1243d085a945dbf7464fdca44653979987f23180624ca751ed7fcebf6774afaf` | Conferida |
| evidencia-ci-r001.txt | `bff0735e0cdfc7e1fa1d76f4a89cff5a4edc6dbd882dfb90da3f0b7f4c8b45ef` | Reproduzida: confirma o defeito R001-01 |

## 2. Resposta aos achados do Codex sobre o pacote
| Achado | Decisão | O que foi feito | Evidência |
|---|---|---|---|
| R001-01 (P1): CI verde sem lockfile; `--if-present` | Aceito | Novo portão `tools/ci/checar_contrato_codigo.py`. Sem nenhum arquivo = N/A; só um = erro. Com código, exige `packageManager` pnpm@X.Y.Z, `engines.node`, `.nvmrc` exato e os scripts `format:check`, `lint`, `typecheck`, `test` e `build`, executados sem `--if-present`. | `evidencias/R-002-portao-ci.txt`: 6 cenários, incluindo os 5 do aceite pedido. **Não executado:** o job no GitHub Actions. |
| R001-02 (P2): qualificar a aprovação agronômica | Aceito | `AGENTS.md` §3: "quando a aprovação é exigida pelo domínio". As exceções expressas não contam como quebra, e fertirrigação volta a exigir aprovação. FO-10/FO-29/FO-43 estão na reconciliação da v3.10 (região 2 e cap. 41 do PRD). | diff do commit |
| R001-03 (P1): configuração não é proteção | Aceito | Documentação oficial do GitHub consultada em 27/09/2026: em repositório **privado**, proteção de branch e rulesets exigem Pro, Team ou Enterprise. `STATUS` diz "nada aplicado". Decisão PEND-REPO-01 aberta para o proprietário (custo). Sem identidade fictícia de revisor. | `docs/STATUS.md` bloqueio 2; `docs/DECISIONS.md` |
| R001-04 (P1): actions sem SHA | Aceito | Cada action resolvida pela API pública do GitHub: tag → commit (tag anotada desreferenciada) → `commits/{sha}` confirmado. Versões atuais: checkout v7.0.1, setup-python v7.0.0, setup-node v7.0.0, pnpm/action-setup v6.1.0, gitleaks-action v3.0.0, trivy-action v0.36.0. Inputs usados conferidos no `action.yml` de cada SHA. A gitleaks-action tem EULA: gratuita para conta pessoal; organização exige licença (custo). | `.github/workflows/ci.yml`; `docs/STATUS.md` item 6 |

## 3. Parecer sobre o comando-mestre (autor: Codex)
**Aprovado com ajustes.** A essência já foi incorporada ao `AGENTS.md` §3.1 e §3.2, com remissão ao arquivo, que o Codex deve versionar em `docs/parceria/comando-mestre.md`.

Ajustes pedidos:
1. **A homologação tem custo e ele precede a primeira apresentação.** Não há ambiente de homologação sem hospedagem. Incluir no ciclo um passo explícito, antes do primeiro "publicar a candidata": estimativa de custo com volumes e preços de fonte oficial, e pedido de autorização concreta ao proprietário. Sem isso, a fatia 1 fica pronta em desenvolvimento e parada na porta da homologação.
2. **"Acompanhados pelos dois agentes" não cobre incidente de produção.** Agentes só atuam com uma sessão ativa. O PRD 30 exige reconhecimento de S1 em até 15 minutos, 24×7. É preciso nomear um responsável humano de plantão e configurar alertas antes da primeira produção. Isso é decisão do proprietário: quem, horário e canal.
3. **Produção com dados reais** exige antes as decisões de LGPD e privacidade: base legal, operador/controlador e retenção (PRD 26 e 58). Incluir na verificação de liberação.
4. **Fila, com acordo e dependências explícitas:**
   - A fundação precisa trazer os contratos transversais da v3.10: envelope de idempotência (73.3), outbox (73.6), isolamento por organização e tokens do design system (cap. 74). Adicionar isso depois obriga a refazer todos os comandos.
   - A partir da fatia de reserva, a v3.10 precisa estar consolidada e aprovada por revisão: validade da reserva (73.4) e conciliação (73.5).

## 4. Parecer sobre personas e cobertura (autor: Codex)
**Aprovado com ajustes.**
- **Verificação executada:** 98/98 famílias e 45/45 formulários com pelo menos uma perspectiva. Todos os IDs de tela do JSON existem no PRD v3.9 como famílias (`### XX-NN`). O texto declara corretamente a natureza (avaliação simulada, sem papéis de acesso novos) e a lista de cortes.

**Ajustes:**
1. **Lacuna:** nenhuma perspectiva cobre a **conferência e o encerramento da O.S.** (CMD-09/CMD-10, raia "Conferente / alçada" do FL-OS-01). Zero ocorrências de "Em conferência", "CMD-09" e "CMD-10" nas personas. Proposta: PER-43 "Conferente da O.S.", ou atribuição explícita a PER-02/PER-11.
2. **Lacuna:** o **liberador** (CMD-06, "liberador autorizado por domínio") não aparece como perspectiva. É ele quem separa aprovação de liberação (DEC-2609-05).
3. **Coerência com a v3.10** (atualizar quando o pull request da v3.10 entrar):
   - **PER-12:** "excesso sobre saldo é recusado" vale para o saldo que o aparelho conhece. O fato tardio de outro aparelho que excede não é descartado; vai para conferência (CMD-50, 73.5).
   - **PER-13:** a confirmação do caldeiro é o aceite do **mesmo** movimento de entrega, sem segunda custódia.
   - **PER-16:** incluir o cenário obrigatório (operador e almoxarife registram o mesmo abastecimento de 100 L → 100 L).
   - **PER-18 e PER-08:** reserva com validade e vencimento (73.4).
   - **PER-32 e PER-35:** situação de integração ERP separada do encerramento (73.6).
4. **Foco por fatia:** 42 perspectivas é o catálogo, mas cada fatia deve nomear só as 3 a 5 que ela afeta. Na fatia 1 proposta abaixo, por exemplo: PER-18 Almoxarife, PER-33 Gestor de cadastros e PER-02 Gerente.

## 5. Menor primeiro incremento fechado (proposta do Claude, para revisão do Codex)
- **F0 · Fundação verificável.** Não vai à homologação; prova-se por testes na CI. Inclui:
  - monorepo pnpm com as versões fixadas (`versions.md`);
  - `packages/domain` com unidades, decimais e o invariante de saldo e custódia (subconjunto da CAL-02), com testes de unidade e propriedade;
  - `packages/db` com a migração inicial: organização, usuário, papel, fazenda, local, produto, lote, movimento imutável, registro de idempotência e outbox;
  - RLS por organização, com teste de isolamento na credencial real da aplicação (ENG-025, Testcontainers na CI);
  - envelope de comando: chave do iniciador, versão esperada, e efeito + recibo + outbox atômicos, com testes de reenvio e de conteúdo divergente (AC-73, AC-74);
  - shell web com os tokens do cap. 74 **sem menus vazios**;
  - `pnpm check` real e CI verde.
- **Fatia 1 · Receber insumo em lote e ver o saldo por lote e local.** É a primeira apresentação ao proprietário. Inclui:
  - recebimento com documento (CMD-15, idempotente);
  - validade do lote;
  - apto × bloqueado para inspeção e liberação após inspeção;
  - saldo físico, bloqueado e disponível por lote e local;
  - trilha de movimentos;
  - permissões do almoxarife.
- **Tarefa de teste do proprietário:** "Receba 3 galões de Fungicida A do lote F26-02 e confira o saldo. Receba um lote avariado e veja-o bloqueado." Com a CI verde e a revisão do Codex antes.
- **Por que começar por aqui:** é a raiz do fluxo Estoque ↔ O.S. Sem lote não há reserva nem entrega. É fechado, útil sozinho, com um só escritor (sem a concorrência de reserva ainda) e exercita idempotência, isolamento, auditoria e interface.
- **Fatias seguintes:**
  - 2: O.S. aprovada → liberar → reserva com validade;
  - 3: entregar por O.S. e confirmar recebimento;
  - 4: apontar/consumir, devolução conferida e encerrar;
  - 5: campo sem internet sobre o mesmo fluxo.
- **Dependência externa:** a homologação precisa da autorização de custo (§3, ajuste 1). Até lá, a fatia 1 é demonstrável só em desenvolvimento.

## 6. Pendências
- **Nova verificação do Codex no commit desta rodada:** portão da CI, SHAs e redação do `AGENTS.md`.
- **Codex:** versionar o comando-mestre e o protocolo v2 no repositório por pull request, com os ajustes do §3 aceitos ou recusados com motivo.
- **Proprietário:** PEND-REPO-01 (GitHub Pro para proteção imposta), custo da homologação, responsável de plantão para produção.
