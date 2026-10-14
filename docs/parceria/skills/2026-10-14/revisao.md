# Skills da equipe — candidata 14/10/2026

Pedido direto de Adrianus: atualizar todas as skills próprias das IAs pelas evoluções e definições desde a criação. Autoria Codex; revisão solicitada ao Claude real. Não altera autoria do protótipo nem encerra o conjunto vigente.

## Escopo e mudanças

20 skills: 16 compartilhadas e quatro específicas do Gemini. 27 arquivos alterados entre instruções, metadados, templates, adaptador e teste; 53 arquivos no pacote completo, incluindo assets preservados. `changes.patch` compara com a instalação anterior; `manifest.json` identifica a candidata.

- Dupla Codex/Claude implementa e revisa, com contratos separados, revisor integrando, retorno imediato, recibos e leitura antes de reenvio. Gemini critica decisões materiais; Grok permanece retirado.
- Contexto/rascunho/foco, uma primária por contexto ativo, retorno real de salvar/cancelar, NAV/DS existentes, corte de quotas e etapas artificiais.
- Ausente/zero, parcial/completo, estados/percentuais, área única/acumulada, razões/denominadores, MIP, agregação explícita e desfazer delimitado.
- Evidência da mesma candidata, isolamento, checks proporcionais, preservação de provas; protótipo incremental, auditoria integral no gatilho correto, transição Next e conferência PRD.
- Autorizações existentes, executor local/remoto comprovado e marketing adiado, sem duplicar números mutáveis de orçamento.
- Catálogo fechado do Gemini passa a incluir todas as 16 compartilhadas e as quatro próprias; somente seleção explícita é carregada, limites/autenticação/raízes preservados.

## Verificação

20/20 skills válidas no quick_validate oficial; zero links locais ausentes; 17/17 testes do adaptador com raízes candidatas (sem rede/auth), incluindo todas as 20 seleções individuais, hashes, UTF-8, limite conjunto, escape por symlink e falhas de autenticação. Os erros iniciais eram runtime Python 3.9/dependência YAML; corrigido usando Python 3.12 e YAML já disponível, sem instalar dependência.

Gemini real Pro/HIGH analisou pacote mínimo UX/domínio, resposta STOP 17TPavi2LfeJlOAP79CJiAE. `gemini-decisao.md` registra as três sugestões e decisões: delimitar desfazer, preservar master-detail do proprietário admitindo painel/expansão e explicitar agregação. Não revisou todos os arquivos nem executou testes do produto.

## Distribuição e revisão solicitada

`shared/` corresponde à fonte local ~/.agents/skills; Claude local usa links para essa fonte e Codex a descobre. `gemini/` corresponde a work/gemini-team/skills. O adaptador é entregue junto para leitura/revisão, sem alteração de credenciais ou ampliação de acesso. Este diretório é um pacote versionado de distribuição/revisão; os arquivos de instrução não são carregados todos juntos.

Claude: revise fonte completa e delta, em especial contradições remanescentes, proporcionalidade, autoria/gatilhos e controles do adaptador. Não integrar o próprio PR; esta candidata é de Codex. Devolva um parecer consolidado nesta PR. Após aceite, integre e atualize as cópias próprias disponíveis em sua sessão existente, preservando customizações e rascunhos; confira hashes e informe caminhos/skills realmente carregadas. Não declarar instalação no claude.ai web ou em outro host sem evidência. Preserve o trabalho de feedback global/Plans em curso.

Para portar o pacote para outra sessão: copiar somente os diretórios de skills próprios após comparar versões; referências/assets seguem o mesmo diretório; apontar links locais para uma única fonte. Nunca copiar settings, tokens, credenciais, plugins ou controles. Instalação local não significa que uma sessão remota já recarregou as instruções.
