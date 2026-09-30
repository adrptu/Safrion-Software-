# Safrion — cópia delimitada de continuidade

**BACKUP NÃO APROVADO.** Este pacote preserva fontes e registros existentes; sua verificação cobre integridade de cópia, manifesto, CRC do ZIP e inspeção estática delimitada. Não constitui aprovação de produto, arquitetura, protótipo, código, segurança operacional, homologação, produção nem instalação de skills no Grok. Pareceres já existentes mantêm apenas o escopo e a versão que identificam.

Não é uma nova fonte canônica. O PRD, os protocolos e o código versionados no repositório continuam sendo as fontes vigentes. Antes de retomar, concilie os arquivos preservados com o commit, a issue nº 1 e o checkpoint atuais; não sobrescreva trabalho mais recente.

## Conteúdo e origem

- `conteudo/` conserva os caminhos relativos do workspace: comando mestre, proposta e parecer delimitados da entrada do Grok, resposta de navegação, pacote de skills expandido e recibos de preparação/transferência, além dos quatro executores/testes Gemini pedidos.
- `skills-locais/` conserva cinco diretórios de dependências declaradas pelo catálogo de `gemini-consult.py`: dev-infra, dev-testes, dev-revisao, negocios-ecossistema e growth-receita-implantacao. As quatro skills específicas do Gemini ficam no caminho original dentro de `conteudo/work/gemini-team/skills/`.
- `manifesto.json` registra, para cada arquivo copiado, origem absoluta, caminho no pacote, bytes e SHA-256. As 50 fontes foram copiadas sem alteração de conteúdo. Este README é o único texto novo de orientação.
- O pacote de design anterior contém 19 arquivos, mais seu recibo `validacao.json` externo ao ZIP original: os 20 estão preservados. O ZIP anterior não foi aninhado; seus hashes continuam nos recibos originais. A cópia desses recibos não comprova upload ou instalação.

## Limites para recuperação sem Mac

Este backup por si só não torna o executor remoto operacional. Os executores ainda usam caminhos `/Users/...`, `/private/tmp/...`, SDK/runtimes locais, manifests de ensaios e configuração local de autenticação. É necessário adaptar esses caminhos e reconstruir dependências no executor de destino, com revisão e prova de execução; nada foi executado, instalado, autenticado ou enviado ao preparar esta cópia.

Não foram incluídos `.config`, credenciais, tokens, chaves, `.env`, runtimes, binários, caches, node_modules, snapshots temporários, bancos, dados de clientes, manifests de execuções (`executor-f0c-manifest.json`, `executor-hml-manifest.json`), `executor-runtime.json`, logs volumosos/runs ou todo o histórico local. Esses arquivos de execução não são substituídos por este pacote.

As fontes e contratos de autoria Claude, incluindo o gerador atual Canvas v10 e CMD-15, ficam a cargo do autor e não integram este recorte. A resposta textual de navegação do Grok é um registro de resposta, não uma exportação do código do protótipo. O acesso ao chat/artefato não equivale a uma cópia recuperável das fontes.

Os assets das skills são exemplos estáticos; não representam a configuração pronta do Safrion. `dev-infra/assets/docker-compose.yml` contém a credencial fictícia de exemplo `app/app`; não deve ser usado como configuração de ambiente. `tabelas-interativas/assets/tabela.js` conserva um byte NUL preexistente no literal `EMPTY_KEY`, em código UTF-8. Ambos foram preservados fielmente, não executados nem corrigidos. O Design System Safrion prevalece sobre exemplos M3.

## Verificação

O recibo `validacao.json`, ao lado do ZIP, registra os hashes finais do pacote e do manifesto, a conferência byte a byte de fontes/cópias/entradas do ZIP, CRC, contagens e regras da varredura estática. A varredura por padrões não prova ausência de todo segredo possível; a seleção foi limitada aos arquivos de código, especificação e recibos solicitados, sem acesso a contas ou diretórios de credenciais.

Para retomar, valide o SHA-256 do ZIP e os arquivos contra `manifesto.json`, recupere em pasta separada e confira o estado canônico atual antes de qualquer integração. Não trate os caminhos absolutos de origem como caminhos de instalação.
