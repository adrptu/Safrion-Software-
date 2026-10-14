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

## Correção de portabilidade após revisão automática (14/10)

4273864164 confirmado: a invocação direta do pacote em instalação limpa não usava suas raízes. Corrigido somente no teste: shared/ e gemini/ do pacote são selecionados explicitamente quando presentes; caminho e hash de cada arquivo recebido são conferidos. Contraprova com Path.home simulado inexistente: antes17 testes com25 falhas/1erro, depois17/17. A invocação instalada conserva o catálogo instalado. Não houve consulta Gemini paga nem alteração do adaptador/autenticação/raízes de produção. O registro inicial17/17 continua prova da execução com preparação local; não provava a invocação direta em clone limpo.

4273864178 atendido com entrada em docs/STATUS.md, preservando o retrato anterior e distinguindo instalação local de distribuição na sessão cloud. Comando: python3 -m unittest -v docs/parceria/skills/2026-10-14/test_gemini_consult.py, Python3.12, sem rede/auth. Brutos de portabilidade em portabilidade/. Claude continua revisor/integrador, sem selfmerge.

### Correção de fontes portáveis — 14/10 17:29 UTC
Achado4274078946 confirmado: a retomada não pode exigir arquivos existentes apenas no Mac. safrion-equipe2.0.1 usa AGENTS, STATUS, protocolo, checkpoint e PRs como caminho recuperável. Os canais locais continuam opcionais neste executor, preservando a instrução do proprietário. Prova exclusivamente local exige entrega recuperável antes do aceite dependente; não é presumida. Demais19skills sem delta.

### Revisão real Claude6174440253 e bot4274143845/4274143850 — 14/10
Tratados os seis pedidos: último valor não preenche lote/dose/quantidade/autorização; artefato exige dados sintéticos ou autorização específica e respeita proibição do projeto; revisor integra; ADR neutro e prevalência da arquitetura/estrutura/outbox do projeto; dinheiro/taxas decimal com escala explícita; caminhos pessoais redigidos no red.log distribuído, bruto local preservado. Growth agora tem fontes recuperáveis e bloqueio de ativação quando a política não puder ser comprovada. Referência legal atualizada após consulta oficial à Lei14.785/2023, arts.39/65 (Planalto,14/10/2026); não se presume auditoria de todas as normas.
Opcionais pertinentes incorporados: espera por condição com exceção para tempo real; supressões condicionadas à política e revisão; glossário sem caminho obrigatório; paleta subordinada ao DS e níveis de queda unificados como exemplos configuráveis. Mantidas as três listas quando exigidas pelo proprietário; não converti a regra do usuário em opcional global. Não mudei modo de envio pago/contrato do adaptador ou templates inativos por esta revisão documental: dry-run já disponível, consulta exige finalidade/autorização; demais propostas exigem delta e verificação próprios, sem instalá-las por rotina. A regra de editor único vem da instrução direta vigente; referências ao protocolo não a apagam.
Claude confirmou que as skills não estão carregadas na sessão cloud atual; instalará e conferirá hashes após aceite. Nenhuma instalação remota declarada. Revisão dele incidiu nohead3cc593c; correção de fontes2c2cf06 e esta rodada ainda exigem reavaliação.

### Correção da biblioteca de tabelas — 14/10, 4274262618/4274262629
Reproduzidos quatro cenários vermelhos no navegador: agrupamento com setRows([]), troca real de esquema, destruição simples e com menu aberto. Correção preserva esquema inferido durante vazio transitório, remove somente referências a colunas desaparecidas, fecha menu ao atualizar linhas e remove ouvintes persistentes de click/dragend além dos já tratados. Cinco cenários verdes, incluindo retorno de dados agrupados. Contraprova portátil em provas/tabela/regression.html; abrir via servidor estático na raiz deste pacote. Título PASS5/5 e window.testResults identificam resultado. Teste sintético, sem dependência externa; não equivale a validar todas as opções da biblioteca. Fonte original e brutos preservados localmente. 20/20 skills,17/17 adaptador; manifesto atualizado,53 arquivos.


### Revisão devolvida 6177603041 — 14/10, Codex

Os seis pedidos anteriores foram aceitos pelo Claude. Esta rodada corrige os novos pontos: agg nulo por padrão (soma exige escolha explícita), autosave em fila com confirmação após save, outbox obrigatório nos comandos Safrion e modelo ESLint renomeado para eslint.config.exemplo.js. O teste portátil provas/correcoes/regression.html reproduziu quatro falhas antes; agora passa 7/7 (ordem, reversão, retry, duplicata e agregação). As regressões anteriores da tabela passam 5/5.

Renomear o modelo resolveu a procura indevida de sonarjs, mas o lint revelou 62 erros dos assets/modelos. Corrigidos os usos de expressões e deletes, e acrescentado ao eslint.config.js da raiz um override somente do pacote versionado: globais browser nos dois assets; modelos sem projeto TS usam lint sem verificação de tipos. Lint continua ativo; regras de produto e segurança não foram desabilitadas. ESLint 10.11.0 executado com configuração da raiz e dependências existentes: zero erros/avisos no pacote e config. Isso não substitui o CI integral.

Validação: 20/20 skills, 17/17 adaptador, 53 arquivos no manifesto; Gitleaks dir do pacote sem achado. Gitleaks histórico geral é pendência separada relatada por Claude, commit207f362; nenhuma allowlist/proteção/branch foi alterada. Revisão, integração e recibo cloud continuam pendentes.


### Complemento de saída e formatação
Achado4275898120 tratado: beforeunload não inicia save assíncrono; pede confirmação quando existe edição sem recibo ou gravação pendente. Teste do guard em eventos canceláveis no navegador: 10/10; a versão46e6ded falha nos dois casos de saída. Não prova comportamento de encerramento forçado/mobile, cujos limites estão na skill. Gatilho de persistência local depende da autorização e contrato do produto.
CI Código do46e6ded falhou em Prettier (log116086875772), no eslint.config.js: corrigido com .prettierrc.json canônico (singleQuote true, printWidth110). Prettier e lint do pacote/config executados com sucesso;20/20skills e17/17adaptador. Demais provas continuam válidas.
