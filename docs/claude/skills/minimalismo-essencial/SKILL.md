---
name: minimalismo-essencial
description: Simplifique interfaces, fluxos e artefatos de produto preservando a tarefa, segurança, acessibilidade e regras de negócio. Use ao criar ou revisar telas e quando pedirem reduzir cliques, campos, etapas, código ou documentação.
---

# Só o que ajuda a tarefa

Cada elemento deve ajudar o usuário a agir, entender, decidir ou recuperar-se de erro, ou ser necessário ao funcionamento e aos controles do processo. Menos elementos não prova melhor usabilidade: medir conclusão, tempo, erro e esforço.

## Teste de essencialidade

1. Qual tarefa, pessoa ou controle depende deste elemento?
2. Ele acrescenta informação ou ação que não existe em outro lugar?
3. É possível reutilizar contexto confiável ou calcular, mantendo visibilidade, correção e aprovação exigida?
4. Se sair da tela, a pessoa ainda encontra e executa a tarefa com clareza e acessibilidade?
5. Há evidência suficiente sobre seu uso, considerando persona, permissão, oportunidade, safra e sazonalidade?

Classifique como **essencial**, **sob demanda** ou **ruído**. Baixa frequência isolada não justifica remover cancelamento, recuperação, auditoria, acessibilidade nem tarefas sazonais. Sem exposição/oportunidade de uso, a métrica não mede desinteresse.

## Direção visual

- Uma ação primária; secundárias úteis junto de seu contexto, sem competição.
- Título curto e linguagem do usuário; ajuda curta quando evita erro ou dúvida real. Não impor zero explicações a pessoas que precisam de orientação.
- Campos necessários ao processo, com rótulo visível e unidade acessível. Não esconder campo obrigatório só para cumprir uma quota.
- Colunas para localizar, comparar e decidir; dados complementares no detalhe. Indicadores apenas quando sustentam uma decisão.
- Eliminar decoração, duplicações, cards sem agrupamento útil, mensagens repetidas e ações sem cenário real.
- Preservar estado, próximo passo e retorno do `master-detail-ux`; atalhos não substituem controles acessíveis no celular.

## Metas de concisão e exceções

Uma ação primária é regra. Como metas iniciais, buscar até duas secundárias visíveis, título de até quatro palavras, criação com até cinco campos, listagem com até seis colunas e painel com até quatro indicadores. São sinais para revisar, não limites que autorizam esconder informação necessária ou quebrar uma tarefa em etapas. Exceder quando o processo, a persona, a acessibilidade ou o design system justificar; explicar brevemente na revisão existente.

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

Inventarie o que importa ao fluxo, classifique e execute os cortes com justificativa. Tente cortar mais um elemento; mantenha-o se passar no teste de essencialidade. Só reintroduza ruído removido com evidência de necessidade. Verifique que a tarefa continua completa, acessível e segura; reverifique o comportamento afetado. Entregue três listas curtas: **aplicado**, **deixado de fora**, **cortado**, com motivo.

Não cortar por estética: aprovações exigidas, isolamento/permissões, unidades, incerteza relevante, distinção entre rascunho/pendente/aceito, contexto de ambiente, avisos necessários ou caminhos de recuperação.
