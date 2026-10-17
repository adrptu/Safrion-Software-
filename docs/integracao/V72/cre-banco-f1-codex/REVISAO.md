# CRE-BANCO F1 — Bens e avaliações da ficha do grupo

Autor: Codex. Revisor e integrador: Claude. Base de código: `5511cf3cdfdc5043eec716a4524bb0d79f054d28`.
Contrato PR47: 6224692594; crítica/aceite 6224704795; permissão explicitada 6224754522 e validada 6224758072.
Referência: `docs/integracao/V71/CREDITO-BANCO.md`, C19 e invariantes pertinentes de C2/C3/C12. Esses critérios completos não estão encerrados por esta fatia.

O produtor abre Crédito → Documentos → Bens e avaliações. A lista começa vazia. Pode incluir um bem, declarar ou deixar pendente o valor e abrir o detalhe para atualizar a declaração ou confirmar sua vigência. Salvar fica neste navegador; nenhuma autorização ou envio a credor ocorre.

| Entidade / nível | Estado | Ação | Detalhe |
| --- | --- | --- | --- |
| Bem / lista e detalhe da ficha | Pendente | Completar e salvar declaração | Tipo, valor em R$, data, responsável, fonte |
| Declaração / detalhe | Declarado | Atualizar declaração ou confirmar vigência | Origem, idade, quem registrou, confirmações, histórico |
| Perfil sem direção / consulta | Sem permissão de escrita | Consultar origem e histórico | Motivo explícito; comando revalida papel |

Valores persistidos como texto decimal canônico, com validação pt-BR, sem cálculo em float. Zero não é ausência. Confirmação registra quem/quando sem reescrever o valor, a data original, a fonte ou o declarante. Atualização conserva a declaração anterior com metadados e confirmações. A data de referência da demonstração é explicitamente 16/10/2026; não é relógio nem histórico do software real.

Permissão da especificação: direção ou financeiro. O catálogo atual ainda não possui financeiro: apenas direção está ligada nesta F1, inclusive Proprietário de teste. Gestor não herda autorização implícita. Não é a alçada de enviar dossiê. Perfis locais de demonstração não substituem autenticação/autorização no servidor.

## Verificação executada

No executor local, Python 3 + Node do runtime Codex; dados sintéticos e armazenamento isolado em cada teste:

```sh
cd tools/prototipo/v37/gen37
python3 -B credito_ficha_build.py /tmp/credito-ficha-generated.js
node credito_ficha_unit.js
node credito_ficha_motor_unit.js /tmp/credito-ficha-generated.js
node --check /tmp/credito-ficha-generated.js
```

- Domínio: **18/18**, contra **0/18 na base**, que ainda não possui os comandos da ficha. `anterior.log` guarda o motivo de cada falha.
- Motor real da GE08 gerada: **12/12**. Inclui criar/reabrir, centavos, R$12.500.000, ordenação numérica, confirmação, troca/perda de papel, conflito com outra edição, erro/quota preservando rascunho, troca de visão preservando filtro e regressão do gravador/identidade de documentos automáticos.
- AST dos dois Python alterados/adicionados e sintaxe do script gerado conferidas. Sem dependência nova. O restante do diff de produto é só GE08 e novas funções `credFicha*`; funções legadas de documentos foram preservadas.
- Brutos e hashes acompanham esta nota. Isso é Node/geração, **não navegador**. O primeiro build teve erro sintático no argumento `def`, corrigido com o formato de campo do motor; a extração inicial capturava também o script externo vazio, corrigida para `data-dc-script`. Os resultados finais são das fontes identificadas no manifesto.

## Gate ainda aberto — Claude real

Revisão crítica, execução 1440/390, teclado/Enter/Escape/foco/rolagem do formulário, modo Cartões, uma primária por contexto, estado vazio, consulta sem papel, falha de armazenamento com tentativa de salvar novamente e regressões `credito_*` pertinentes. Codex não executou navegador: bloqueio de ferramenta anterior preservado, sem contorno. Publicar somente após os aceites pertinentes. Não autoaprovar nem integrar.

Aplicado: lista/detalhe do motor e seta de abertura; campos na mesma operação; estados textuais; foco/rascunho pelo motor; origem/histórico; moeda tipada e armazenamento transacional do formulário.

Deixado de fora: montagem/congelamento/exportação/consentimentos de dossiês, corte histórico por data-base, pessoas, imóveis, contratos anteriores e safras; quatro cartões MOD-CRE e papel financeiro exigem autoria/fatias próprias. Nenhuma dessas pendências é removida do registro vigente.

Cortado: KPIs de contratos na ficha; campos de histórico vazios na inclusão; primária global que levava o produtor ao portal do credor. O link de dossiê na consulta do contrato agora fica na visão interna GE08. Sem novas telas vazias nem novo menu.

Limites: persistência de protótipo para o único grupo de demonstração, sem multi-tenant ou prova de atomicidade entre abas simultâneas. Revisão de item detecta edição obsoleta e grava sobre a leitura mais recente, mas não substitui transação do banco. Armazenamento corrompido/versão desconhecida é preservado e bloqueia gravação. Não há remoção destrutiva nesta fatia. Conjunto do protótipo ainda incompleto; sem gatilho PRD final/auditoria integral/Next/HML/produção.
