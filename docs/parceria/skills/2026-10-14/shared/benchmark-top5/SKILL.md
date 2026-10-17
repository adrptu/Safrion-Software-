---
name: benchmark-top5
description: Pesquise cinco referências relevantes ao criar um produto ou módulo ainda não coberto pelo benchmark do projeto. Extraia práticas verificáveis e decisões de adoção; reutilize pesquisa atual em ajustes existentes.
---

# Benchmark de cinco referências — aprender antes de construir

## Pesquisa dirigida pela decisão

Comece pela pergunta que a mudança precisa resolver e pelos achados já registrados. Nova evidência pode atualizar uma prática sem refazer cinco pesquisas completas. Diferencie comportamento observado, afirmação comercial e inferência; ausência de acesso permanece limitação. Fonte de concorrente inspira, mas não substitui PRD, decisões NAV/DS, regras de domínio e validação de campo.

Compare esforço total, erro, recuperação e clareza por persona e contexto/safra. Menos cliques, mais recursos ou consenso de IAs não comprovam benefício. Registre adoção/adaptação/descarte na fonte existente e mantenha requisitos pendentes; não transforme lista de funções em novos menus ou amplie o produto pela pesquisa.


**Norte:** estudar referências relevantes, com evidência de fluxos, regras e práticas, e adaptar o que serve à tarefa. Buscar menos esforço e mais clareza (`ux-essencial`), sem presumir liderança, escala de uso ou superioridade sem dados.

Antes de um produto ou módulo novo, confira a pesquisa existente em `docs/benchmark.md` ou na fonte adotada pelo projeto ([assets/benchmark-template.md](assets/benchmark-template.md)). Reutilize achados atuais e pertinentes; pesquise só lacunas. Correção de bug e ajuste pequeno não reabrem um benchmark completo.

## Passo 1 — Classificar o software
Definir em uma linha: **categoria** (ex.: "CRM de vendas B2B"), **público** (PME, enterprise, consumidor), **plataforma** (web, mobile, ambos) e **módulo em foco** quando for funcionalidade específica (ex.: "pipeline de oportunidades").
Se o produto cruza categorias (ex.: ERP agrícola = ERP + gestão de safra), selecionar cinco referências que cubram ambas, explicando a seleção sem duplicar pesquisa por obrigação.

## Passo 2 — Escolher cinco referências
Escolha cinco referências pela adequação ao público/processo, práticas demonstradas e relevância no Brasil. Não afirmar que são as cinco maiores do mundo sem dados comparáveis e atuais de liderança. Explique o motivo de cada escolha.
Pesquise a categoria e tarefa com as ferramentas disponíveis; abra fontes primárias para confirmar capacidades, fluxos e preços. Rankings/reviews ajudam a descobrir candidatos, mas não provam comportamento. Registre URL e data.
Sem acesso às fontes, identifique hipóteses e pendências; não apresente lembrança como pesquisa executada nem invente ranking, cliques ou números de usuários.

## Passo 3 — Pesquisar cada player (o que extrair)
Fontes por ordem de valor: **central de ajuda/documentação** (revela fluxos e regras reais), **página de produto e tour**, **changelog/roadmap público** (o que estão priorizando), **vídeos de demo**, **avaliações G2/Capterra** (o que usuários amam e odeiam — as reclamações são nossas oportunidades), **API docs** (expõem o modelo de dados), **planos/preços** (o que é considerado essencial vs. avançado).

Para cada player, capturar:
1. **Objetos centrais e modelo de dados** — entidades, relações, campos obrigatórios, estados/ciclo de vida (ex.: lead → oportunidade → cliente; pedido: rascunho → confirmado → faturado → entregue).
2. **Fluxo principal** passo a passo — como o usuário faz a tarefa nº 1, quantos cliques, o que é pré-preenchido, o que é automático.
3. **Regras de negócio e validações** — o que o sistema impede, calcula, sugere ou exige (limites, aprovações, permissões por papel).
4. **Automações e inteligência** — gatilhos, sugestões, IA, lembretes, priorização, detecção de anomalias, previsões.
5. **Gestão e métricas** — dashboards padrão, KPIs, relatórios que o gestor usa, alertas.
6. **Etapas de onboarding/configuração** — o que pedem no primeiro uso, importação de dados, templates.
7. **Integrações e ecossistema** — o que conectam por padrão (pagamentos, fiscal, WhatsApp, e-mail, ERP, marketplaces).
8. **Diferencial** — prática diferenciada e evidência do benefício, sem presumir liderança.
9. **Reclamações recorrentes** — fricção, burocracia, lentidão, complexidade (nossa chance de fazer melhor).
10. **Padrões de UX específicos do setor** — convenções que o usuário do setor já espera (nomenclatura, atalhos, layouts) e que não devemos quebrar sem motivo.

## Passo 4 — Sintetizar
Cruzar os 5 e produzir:
- **Consenso** (4–5 referências fazem) → candidato a avaliar, não obrigação. Só adotar quando resolve a tarefa/persona do nosso escopo.
- **Boas práticas de 2–3 players** → avaliar; adotar se serve à tarefa principal.
- **Diferenciais únicos** → inspiração; adotar só o que cabe no essencialismo.
- **Reclamações comuns** → lista de "onde vamos ser melhores".
- **Modelo de dados de referência** unificado (entidades, estados, campos essenciais) — já no formato que `master-detail-ux` exige: por entidade, estados, ação primária por estado e seções do detalhe.
- **Fluxo de referência** da tarefa principal, já **reduzido** conforme `ux-essencial` (menos cliques, mais inferência, desfazer em vez de confirmar).
- **Glossário do setor** — usar as palavras que o usuário do setor usa.
- **Métricas de gestão** úteis à fatia e com dados confiáveis; não acrescentar dashboards só porque concorrentes têm.

## Passo 5 — Decidir e registrar
Atualizar a fonte do projeto com decisão: adotar agora / depois / adaptar / descartar, motivo e evidência. Ordenar por resultado para o usuário, risco, dependência e esforço; popularidade no mercado não supera a tarefa real. Registrar ADR somente quando houver decisão arquitetural material.

## Filtros ao incorporar (nossa filosofia vence)
- **Essencialismo**: avaliar utilidade, frequência por oportunidade e criticidade por persona/safra; não excluir tarefas raras essenciais por porcentagem arbitrária.
- **Fricção zero**: se o player exige várias telas, reduzir etapas sem perder decisões, aprovações e contexto. Cada campo do concorrente passa pela pergunta "o sistema pode inferir isso?".
- **Lógica e regras**: verificar fórmulas, unidades, legislação e premissas com fontes técnicas e requisitos locais; uma regra de concorrente não é evidência de correção para nossa operação.
- **Convenções do setor** (termos, ordem das etapas, documentos obrigatórios, regras fiscais/legais BR): respeitar.
- **Estética**: do design system vigente (`ux-essencial`), sem copiar a identidade deles.
- **Nunca copiar** textos, ícones, layouts ou marca; inspiração de funcionalidade e lógica é legítima, cópia de expressão não é.

## Checklist (antes de iniciar a Fase 1 de dev-ciclo-completo)
- [ ] Categoria, público e plataforma definidos em uma linha
- [ ] Cinco referências listadas com motivo e fontes (data da pesquisa)
- [ ] Os 10 itens capturados para cada player (ou marcado o que não foi encontrado)
- [ ] Consenso, diferenciais e reclamações sintetizados
- [ ] Modelo de dados e fluxo de referência escritos, já reduzidos pela nossa filosofia
- [ ] Métricas de gestão e glossário definidos
- [ ] Matriz de decisão preenchida e backlog inicial derivado dela
- [ ] Decisões registradas e resumo apresentado; continuar nas decisões técnicas autorizadas, perguntando apenas o que muda materialmente o negócio/desenho
