# AGRO-06 — entrada dos 15 analitos
Contrato Claude PR47/6228621408. Codex autor; Claude revisor/integrador.
Base f3ceb3cdc965ce620ed9ffcbbcfd7ec82ec936e3. Correção A1–A4 sobre a10656a74164c01fee6bf3a19fecf82d602fd93a.
Entidade Laudo de solo → listagem/detalhe → Registrar laudo.

O formulário oferece os 15 analitos da base. Ausente difere de zero. O exemplo possui cinco resultados; os demais campos permanecem vazios. Método/limite/qualificador ficam na mesma linha expansível.

## Correções após revisão Claude a883ad1 / 6229066182
- Qualificador: lista Valor medido / Abaixo do limite, valores canônicos vazio e <. Residual desconhecido é recusado antes do comando, nunca convertido em resultado quantificado.
- P e K: método somente leitura deriva sempre do extrator atual; serialização usa ext, inclusive após carregar exemplo e trocar extrator.
- Detalhes sem valor: recusa no painel preserva rascunho. Método derivado de P/K não é detalhe editável; LD/qualificador continuam exigindo valor.
- Summary: alvo CSS mínimo24px desktop/44px celular. Claude aplica seta TAB-11 na composição.

## Verificação executada
agro06_analitos_unit.js passou: 15 nomes, ausência/zero/LD0, extrator P/K, qualificadores desconhecidos recusados, soloKmg real retorna não calculável com <, handler real recusa antes de cenMudar e preserva painel/valores. CSS/markup verificados estaticamente.
Contraprovas comportamentais: a10656a falha3/3 (qualificador desconhecido, método divergente, detalhes descartados); candidata passa3/3.
Python AST e node --check do JS completo passaram.
Sem DOM/E2E nesta correção: bloqueio do navegador Codex preservado. Claude deve retestar afetado a1440/390, teclado, alvo calculado, exemplo/troca extrator, registro/validação e detalhe. Provas anteriores do autor/revisor não equivalem a reteste desta candidata.

## Escopo e integração
Nenhuma alteração solo.js, cálculo de dose, aprovação, OCR/upload. SOLO-UNID é contrato separado6229291265.
TAB-11 Ver original não tocado. Aplicado: metadados com validação e rascunho preservado. Fora: layouts/importação/demais observações S4 de domínio. Cortado: qualificador livre e método P/K independente, pois contradiziam contrato do domínio. Não houve descarte de nove analitos no exemplo antigo: essa afirmação anterior foi corrigida.
