---
name: master-detail-ux
description: Organize entidades de gestão em Menu, Listagem, Detalhe e Sub-detalhe, com estado visível, próximo passo e contexto preservado. Use ao criar ou revisar módulos, cadastros, navegação, telas e fluxos de gestão.
---

# Master-detail: localizar, entender e agir

## Origem, destino e contexto ativo

Cada tela esclarece origem/contexto, estado atual, ação possível, consequência/destino e recuperação. Modal ou subdetalhe ativo concentra a primária; a tela de fundo não compete. Preserve rascunho, filtros, foco e posição ao abrir/fechar ou voltar. Drill-down temporário pode substituir o recorte visível sem sobrescrever preferências persistidas.

Classificar funções da pessoa não cria novos menus. Reutilize a navegação acordada; corte submenus, telas intermediárias e ações equivalentes. Painéis, mapas e alternâncias de visualização não exigem entidades ou níveis artificiais. Preserve visão global necessária e acesso ao detalhe; estado de negócio não é inferido apenas de cor, percentual ou existência de dados.


**Menu → Listagem → Detalhe → Sub-detalhe.** Toda entidade de gestão tem listagem e detalhe. A estrutura organiza o trabalho; não exige adicionar componentes sem função.

## Princípios

1. **Estado visível:** mostrar a situação com vocabulário consistente e texto, sem depender só de cor. Barra de etapas e percentual apenas quando representam progresso real e ajudam a decidir.
2. **Próximo passo com verbo:** indicar a ação adequada ao estado e à permissão. Deixar claro onde está no processo, o que falta e como avançar. Se estiver impedida, mostrar a causa e quem pode resolver, sem oferecer execução inválida. Avançar conserva o contexto e não dispara sozinho a operação da etapa seguinte.
3. **Uma ação primária por contexto ativo:** posição consistente e acessível. Secundárias junto do conteúdo a que pertencem; destrutivas separadas. Manter a primária alcançável em tela longa; repetir em rodapé apenas se a distância justificar, sem cobrir dados, campo ativo, teclado virtual ou controles. Conferir toque, teclado e posição após erros.
4. **Contexto preservado:** título, vínculo ao pai e retorno claro; voltar conserva filtros, posição e estado útil. Detalhe pode ser página, painel ou expansão acessível com referência estável; no celular, não exige empilhar rotas quando o detalhe pode permanecer no contexto.
5. **Vocabulário e cores consistentes:** usar os mesmos nomes e tokens do design system para o mesmo significado; classificação não se confunde com estado.

## Por nível

- **Menu:** entidades agrupadas por tarefa/domínio; localização atual evidente e acesso conforme permissão.
- **Listagem:** localizar e comparar registros; identificação, estado, informação que determina a escolha e próximo passo. Ações rápidas são permitidas quando simples, autorizadas e coerentes com o processo, sem eliminar o detalhe. Tabelas seguem `tabelas-interativas`.
- **Detalhe:** executar no contexto da entidade; cabeçalho, estado, ação primária e seções necessárias. Indicadores, stepper, resumo e explicação aparecem somente se ajudam a decisão; não são quotas obrigatórias.
- **Sub-detalhe:** aprofundar um item preservando vínculo ao pai; mostrar dados, ações e totais que façam sentido nesse recorte.

Anatomia e exemplos em [references/anatomia.md](references/anatomia.md), quando precisar desenhar os níveis.

## Aplicação

Em módulo novo, antes de código, mostre uma tabela curta com entidades, estados, ação primária por estado e seções do detalhe. Siga sem esperar aprovação, salvo dúvida que mude materialmente o desenho. Em sistema existente, identifique entidade/nível e reaproveite o padrão; não refatore frentes alheias ao pedido.

Rotas refletem a entidade e seu detalhe (`/entidades`, `/entidades/:id`) conforme o roteador do projeto. Estado navegável pode ir à URL, mas nunca segredos ou conteúdo sensível. Criação rápida mantém contexto e oferece acesso imediato ao registro criado.

Login, onboarding, landing page, wizard linear, configuração simples e pagamento podem não representar entidades de gestão; aplique `ux-essencial` e explique em uma frase por que o master-detail não se aplica.

## Encerramento

Passe o [checklist](references/checklist.md) e o corte de `minimalismo-essencial`. Entregue três listas curtas: aplicado, deixado de fora e cortado, com motivo. Não remover estado, próximo passo, retorno, acessibilidade ou controles necessários para tornar a tela menor.
