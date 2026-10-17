# AGRO-06 — entrada dos 15 analitos
Contrato Claude PR47/6228621408. Codex autor; Claude revisor/integrador.
Base f3ceb3cdc965ce620ed9ffcbbcfd7ec82ec936e3.
Entidade Laudo de solo → listagem/detalhe → Registrar laudo.

O formulário oferecia só seis analitos, inclusive ao carregar exemplo. Agora oferece pH, P, MO, Ca, Mg, K, H+Al, Al, S, B, Cu, Fe, Mn, Zn e Argila, coerentes com a base existente. Valores ausentes continuam omitidos; zero explícito permanece resultado. Unidade existente do exemplo é mantida mesmo fora das opções padrão. Método, limite e qualificador acompanham cada resultado até soloRegistrar, com campos opcionais expansíveis na linha. P e K usam o extrator selecionado quando não há método específico; método informado prevalece.

Não altera solo.js, cálculo, validação/aprovação, importação/OCR nem upload. O laudo continua Aguardando validação pelo comando existente. Ordem é o painel padrão desta fatia, não um catálogo de layouts por laboratório. Não valida cientificamente valores/unidades de demonstração.

## Verificação executada
Node agro06_analitos_unit.js: helpers reais de entrada/serialização; 15 nomes únicos, inicial vazio, omissão de ausentes, zero, decimal com vírgula, unidade/método/limite/qualificador, extrator P/K, inválido preservado para validação pelo domínio e ausência de mutação. Passou.
Python AST e node --check do JS completo da tela passaram.
DOM/teclado/mobile/E2E não executados: bloqueio anterior do navegadorCodex preservado. Claude deve verificar formulário a390/1440, expandir detalhes por teclado, preservar foco/rascunho, exemplo15 e registro/retorno ao detalhe pelo domínio real antes de integrar/publicar. Testes existentes de solo pertinentes devem rodar na composição; nenhum resultado proposto é declarado executado.

## Integração
A TAB-11 de Claude altera summary Ver original em _painel_laudo: não tocado. Novo details por analito usa summary nativo e não duplica ícone.
Aplicado: resultado e seus metadados na mesma linha, campos de valor/unidade sempre visíveis.
Fora: layouts por laboratório e importação em lote, que exigem contrato próprio.
Cortado: descarte dos nove analitos e metadados ao usar exemplo/registrar.
