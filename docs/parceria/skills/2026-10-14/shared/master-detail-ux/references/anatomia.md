# Anatomia por nível

Referência adaptável. O SKILL.md define os princípios; não adicionar todos os elementos abaixo por obrigação.

| Nível | Estrutura essencial | Acrescentar quando útil |
|---|---|---|
| Menu | Módulo, entidade e localização atual | Empresa/fazenda ativa quando houver troca de contexto |
| Listagem | Identificação, estado, próximo passo, acesso ao detalhe | Busca, filtros, agrupamento, resumo e indicador que ajudem a escolher |
| Detalhe | Título, retorno, contexto, estado, ação primária, seções da entidade | Etapas reais, indicadores acionáveis, resumo de seção e ajuda curta |
| Sub-detalhe | Identificação, vínculo ao pai, estado e tarefa do item | Agrupamento, drill-down e totais pertinentes |

Exemplo: **Agrícola → Safras → Safra 2026/27 → Demanda de sementes**. Voltar da demanda devolve à safra e preserva o recorte da listagem. Uma seção recolhida mostra informação suficiente para decidir abri-la; não repete o detalhe inteiro.

Use tokens e tipografia do design system vigente, rótulos legíveis, formatos pt-BR e unidades explícitas. Não crie KPI, etapa, badge, frase de orientação ou rodapé fixo sem necessidade concreta. Confirmações e autosave seguem o risco e a semântica definidos em `ux-essencial`.
