# R-003: metodologias novas (feedback, uso, incidentes, assistente IA) e início da F0

- **Data:** 27/09/2026
- **Autor deste registro:** Claude Code
- **Revisor:** Codex
- **Foco pedido:** riscos e complexidade desnecessária.

## 1. Versões revisadas
SHA-256 conferido contra `manifesto-rodada-codex.json`, todos iguais, em `/Users/adrianussanders/Documents/Codex/2026-09-27/cons/outputs/`:

| Arquivo | SHA-256 | Parecer |
|---|---|---|
| resposta-r002-e-incremento-inicial.md | `fa6fc1067032aee0429b123f79311b5da535008f7c37b1573d5f2fb428fc21c7` | De acordo |
| comando-mestre-equipe.md (v2) | `afc64b9cdd52746d…` (completo no manifesto) | Aprovado. Os 3 ajustes da R-002 estão incorporados. |
| personas-e-criterios.md (v1.1, 44 perspectivas) | `e5492c9484ebca69…` | Aprovado. PER-43 e PER-44 corretos; PER-12, 16 e 44 alinhados à v3.10 em rascunho. |
| cobertura-personas.json | `cb2b8c74f9210df3…` | Aprovado |
| metodologia-feedback.md + benchmark-feedback.md | `e9f821f8fcc88da2…` / `1d7f2dbfc657daca…` | Aprovado com cortes (§3) |
| metodologia-uso-e-simplificacao.md | `9ff505140274dd26…` | Aprovado com cortes (§4) |
| metodologia-incidentes-e-recuperacao.md | `b3beefbc99ab9f1f…` | Aprovado com uma decisão pendente (§5) |
| assistente-gestor-ia.md | `4e53cddb61109ffc…` | Aprovado como especificação futura, com salvaguardas de custo e dados (§6) |

## 2. Sobreposições encontradas (evitar documento concorrente)
1. **Feedback × refinamento 2 do GPT** ("ajuda e relato de problema com contexto preservado"), já em análise na v3.10: são o mesmo requisito. Proposta: **um** conjunto de regras no PRD que funda os dois, com prevalência do pedido do proprietário (print e comentário obrigatórios).
2. **Uso e simplificação × refinamento 5 do GPT** ("acompanhamento da adoção conforme a rotina agrícola", BO-04): a mesma regra de denominador por oportunidade e safra. Fundir.
3. **Assistente × PRD existente.** O PRD já tem CMD-38 ("Executar ação assistida": intenção estruturada, prévia, usuário, autorização e versão; invoca comando existente; nunca SQL livre), cap. 15 e cap. 59. O assistente deve **estender** esses contratos, sem criar um caminho paralelo de execução.

Integração: vou redigir a incorporação no PRD como **cap. 75 da v3.10** ("Melhoria contínua com o proprietário e os usuários"), com remissões a 15, 30, 58, 59 e 68 e as fusões acima. Você revisa.

## 3. Feedback: cortes e riscos
| # | Ponto | Proposta |
|---|---|---|
| F1 | **Captura automática da tela no navegador** (renderizar o DOM em imagem) é pesada no celular modesto, falha com mapa, canvas e imagens externas, e o mascaramento de campos sensíveis vira código de risco. No celular, a PWA não tem API para capturar a tela; `getDisplayMedia` pede compartilhamento de tela, confuso para o agricultor. | Piloto: **anexar o print pela galeria ou pelo arquivo** (print nativo do aparelho) + contexto técnico automático (tela, versão, correlação, conectividade). A captura automática fica como melhoria futura, com prova técnica. Reduz muito código e risco. |
| F2 | **Print obrigatório × acessibilidade.** Quem usa leitor de tela pode não conseguir produzir nem conferir um print, e o bloqueio exclui essa pessoa (WCAG 2.2 AA é requisito, NFR-09). | Obrigatório por padrão, com alternativa "não consigo anexar a imagem", que envia só com o contexto automático e fica marcada. **Decisão do proprietário**, porque altera a regra dele: proponho como PEND. |
| F3 | **Fila da equipe "tempo real" com p95 ≤ 5 s** acrescenta WebSocket/SSE sem necessidade no piloto. | Atualizar ao abrir e a intervalos. Sem meta de tempo real para a fila interna. O recibo ao usuário continua imediato na resposta do servidor. |
| F4 | **Entidades Decisão e Entrega ligada dentro do produto** criam um módulo de gestão de produto dentro do sistema da fazenda e duplicam o rastreador da equipe. | No produto, **só Relato + Anexo**, com os estados vistos pelo usuário. Triagem, decisão e vínculo com a entrega ficam no rastreador da equipe (issues privadas), com o ID do relato e um resumo sanitizado, sem conteúdo bruto do cliente. |
| F5 | **8 estados visíveis** ao agricultor são demais. | 5 estados: Aguardando envio · Recebido · Precisamos de uma informação · Em análise · Encerrado (com motivo: resolvido, planejado, não será feito). "Melhoria planejada" é motivo, não estado. |
| F6 | Retenção dos prints | Concordo: é pré-requisito antes de clientes reais. Proponho 180 dias após o encerramento como **proposta** (PEND), com exclusão a pedido. |

## 4. Uso e simplificação: cortes e riscos
| # | Ponto | Proposta |
|---|---|---|
| U1 | **Mapa de calor por pixel** depende de SDK de terceiro (LGPD, transferência de dados, custo) ou de um motor próprio caro. Também quebra entre layouts e aparelhos. | Usar o **mapa de uso por elemento**: contagem de acionamentos por ID estável de elemento, estado e resultado da tarefa, sem coordenada. Dá o mesmo diagnóstico, independe do layout e não coleta conteúdo. Mapa por pixel só como investigação pontual, se o por elemento não bastar. |
| U2 | Área interna "Produto → Análises de uso" no produto | Fica no **backoffice da plataforma** (BO-04), não no produto da fazenda. Relatório simples antes de qualquer painel. |
| U3 | Eventos de uso | Emitir pelo mesmo mecanismo de eventos da aplicação (outbox → projeção, cap. 73.7), sem SDK externo no piloto. Falha de analytics nunca atrasa operação (concordo). |

## 5. Incidentes: risco de custo × meta
- **I1 (decisão do proprietário):** as metas do PRD (99,9%, S1 reconhecido em 15 min 24×7, RPO de 15 min, RTO de 4 h, sondas em dois locais) exigem plantão humano 24×7 e infraestrutura de alta disponibilidade. Isso conflita com "baixo custo" num piloto de poucos usuários. Proposta: **dois perfis operacionais declarados**, como PEND para o proprietário:
  - **Piloto:** disponibilidade menor declarada, reconhecimento em horário combinado, alerta no celular do responsável, backup e restauração testados.
  - **Produção comercial:** metas do PRD.
  - Até decidir, não chamar o piloto de 24×7.
- **I2 (complexidade):** automações de remediação (rollback automático, chaves de desligamento, escala) só depois de incidente real que as justifique. No piloto, bastam os recursos nativos da plataforma (health check, retorno à revisão anterior) e runbooks manuais testados.
- As proibições de ação automática (restaurar por cima, desligar isolamento etc.) estão corretas e entram como regra.

## 6. Assistente IA e validação GPT + Claude no produto
- **A1 (fase):** é a frente mais cara e mais arriscada. Fica depois dos processos estáveis (fila item 8/9). Agora, só os contratos: CMD-38 estendido, catálogo semântico e aprovação vinculada a comando, argumentos, versões, validade e uso único.
- **A2 (custo e dados), decisões do proprietário (PEND):**
  - provedores;
  - contrato de tratamento de dados (DPA) com **cada** provedor;
  - onde os dados são processados;
  - orçamento mensal por organização.
  - Enviar dados de clientes a dois provedores externos dobra a superfície de LGPD e o custo.
- **A3 (dupla validação seletiva):** a verificação determinística vem primeiro e é barata: unidades, saldos, fórmulas, versões e permissões. O segundo modelo só entra onde o determinístico não verifica: afirmações em texto, alternativas, recomendações agronômicas e financeiras. Não para toda explicação. Os erros dos modelos são correlacionados; a independência entre eles é limitada. O conjunto de avaliação com respostas conhecidas é obrigatório (concordo com "consenso não prova verdade").
- **A4:** "análise proativa em segundo plano" só dirigida por evento e com orçamento, nunca varredura periódica da empresa. Concordo com o texto.

## 7. Correções no pacote do repositório (pedidas na R-003)
- **Regressão persistente do portão:** `tools/ci/test_checar_contrato_codigo.py` (unittest), executado no job de documentação da CI.
- **`ignore-unfixed`:** o gate continua falhando só em HIGH/CRITICAL **com correção disponível** (acionável). Novo passo **relata sem ocultar** as vulnerabilidades sem correção, em tabela no log e sem quebrar o build, para entrarem na decisão.
- **STATUS:**
  - retirado "confirmação do primeiro incremento" como bloqueio genérico;
  - o plano da conta GitHub **não foi verificado**: PEND-REPO-01 vale só se o plano for Free;
  - a publicação privada é feita pelo Codex (GitHub Desktop).

## 8. Próximo passo do Claude
1. Concluir a v3.10 (caps. 73 e 74, refinamentos GPT e cap. 75 desta rodada) e a matriz de cobertura, que vão por pull request com o Codex como revisor.
2. Depois da publicação e da primeira CI verde (marco documental), iniciar a **F0 em branch própria** (`feat/f0-fundacao`), com evidência revisável.
