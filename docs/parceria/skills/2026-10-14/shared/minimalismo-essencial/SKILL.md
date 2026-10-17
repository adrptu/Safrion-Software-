---
name: minimalismo-essencial
description: Simplifique interfaces, fluxos e artefatos de produto preservando a tarefa, segurança, acessibilidade e regras de negócio. Use ao criar ou revisar telas e quando pedirem reduzir cliques, campos, etapas, código ou documentação.
---

# Só o que ajuda a tarefa


No Safrion, leia `.claude/skills/padrao-safrion/SKILL.md`, `AGENTS.md` §4 e o catálogo vigente em `docs/design-system/` antes de aplicar esta skill. O padrão aprovado vale para todas as telas do mesmo tipo (DEC-1610-12); inventarie as ocorrências e combine os recortes de autoria, sem sobrescrever trabalho alheio. As sugestões genéricas abaixo não substituem o DS.

## Simplificação que preserva o trabalho

Cadastros devem reutilizar contexto confiável, seleção rápida e autocomplete acessível dentro das permissões. Campos da mesma tarefa ficam juntos, com validação local e confirmação clara. Não repartir preenchimento entre cards, submenus ou wizards sem etapa real. Resumo, card, tooltip e rodapé só permanecem quando ajudam uma decisão ou recuperação que ainda não está atendida.

No código e nos documentos, referencie contratos e design system vigentes em vez de copiá-los. Remova instruções obsoletas que contradizem a regra nova; não acumule adendos incompatíveis. Encerrar uma correção não exige nova infraestrutura, pesquisa completa ou auditoria integral sem motivo material.


Cada elemento deve ajudar o usuário a agir, entender, decidir ou recuperar-se de erro, ou ser necessário ao funcionamento e aos controles do processo. Menos elementos não prova melhor usabilidade: medir conclusão, tempo, erro e esforço.

## Teste de essencialidade

1. Qual tarefa, pessoa ou controle depende deste elemento?
2. Ele acrescenta informação ou ação que não existe em outro lugar?
3. É possível reutilizar contexto confiável ou calcular, mantendo visibilidade, correção e aprovação exigida?
4. Se sair da tela, a pessoa ainda encontra e executa a tarefa com clareza e acessibilidade?
5. Há evidência suficiente sobre seu uso, considerando persona, permissão, oportunidade, safra e sazonalidade?

Classifique como **essencial**, **sob demanda** ou **ruído**. Baixa frequência isolada não justifica remover cancelamento, recuperação, auditoria, acessibilidade nem tarefas sazonais. Sem exposição/oportunidade de uso, a métrica não mede desinteresse.

## Direção visual

- Uma ação primária por contexto ativo; secundárias úteis junto de seu contexto, sem competição.
- Título curto e linguagem do usuário; ajuda curta quando evita erro ou dúvida real. Não impor zero explicações a pessoas que precisam de orientação.
- Campos necessários ao processo, com rótulo visível e unidade acessível. Não esconder campo obrigatório só para cumprir uma quota.
- Colunas para localizar, comparar e decidir; dados complementares no detalhe. Indicadores apenas quando sustentam uma decisão.
- Eliminar decoração, duplicações, cards sem agrupamento útil, mensagens repetidas e ações sem cenário real.
- Preservar estado, próximo passo e retorno do `master-detail-ux`; atalhos não substituem controles acessíveis no celular.

## Metas de concisão e exceções

Uma ação primária por contexto ativo é regra. Quantidade de campos, colunas, indicadores e secundárias depende da decisão e da tarefa; não imponha quotas que escondam dados ou fabriquem etapas. Corte redundância antes de deslocar informação necessária para outro lugar. Preserve unidades, aprovações, visão global, origem e recuperação.

Microcopy: verbo + objeto nos botões; erro = o que houve + como corrigir, preferindo até duas frases; vazio = uma frase e uma ação; unidade junto do campo. Evitar exclamações, emojis, jargão e palavras de cortesia repetidas nos controles. Não abreviar a ponto de perder sentido.

Ficam fora por padrão: boas-vindas decorativas, cards só para enquadrar, descrições que repetem o título, ícones sem função, várias ações equivalentes e confirmação repetida sem mudança de risco. Exceções legítimas incluem obrigação vigente, consequência grave ou irreversível, convenção do setor, acessibilidade e identificação de ambiente/sessão.

## Três saídas

1. **Automatizar** cálculos ou preenchimento confiável, com resultado visível/revisável. Rascunho automático não confirma operação de negócio; IA respeita aprovação específica.
2. **Mover para sob demanda** quando a ação é útil mas secundária, mantendo descoberta e acesso compatíveis com a persona.
3. **Remover** ruído comprovado, preservando requisitos, rastreabilidade, integridade e recuperação.

Mudanças funcionais seguem o ciclo de revisão e homologação do projeto. Registrar decisão na tarefa/PRD/rodada existente; não criar um documento paralelo só para listar cortes.

## Aplicar além da tela

PRD mantém resultado, regras, estados, exceções, permissões e aceite observável. Código usa a menor solução clara, sem abstrações para necessidades hipotéticas. Fluxograma mostra decisões que mudam a jornada; subprocessos repetidos viram referências. Testes protegem comportamentos, sem redundância artificial. Fonte única por regra.

## Procedimento final

Inventarie o que importa ao fluxo, classifique e execute os cortes com justificativa. Reveja somente elementos cuja utilidade esteja em dúvida; não faça cortes por ritual. Só reintroduza ruído removido com evidência de necessidade. Verifique que a tarefa continua completa, acessível e segura; reverifique o comportamento afetado. Entregue três listas curtas: **aplicado**, **deixado de fora**, **cortado**, com motivo.

Não cortar por estética: aprovações exigidas, isolamento/permissões, unidades, incerteza relevante, distinção entre rascunho/pendente/aceito, contexto de ambiente, avisos necessários ou caminhos de recuperação.

