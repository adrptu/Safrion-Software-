# CONTROLE-02 · fatia 2 · núcleo do retrato técnico (em desenvolvimento)

Autor Codex; revisor/integrador Claude. Contrato aceito no PR47, comentários6147454736/6147460986. Base inspecionada: `3e3e0a89a0ff5ebdb27d850a3a9aa5ddf5f968a8` (v56). Fonte do produto: PRD RN-031/032/033, CMD-02/03/04 e AC-66; auditoria CONTROLE-01 item15. Nenhum requisito funcional completo é encerrado por esta entrega parcial.

O SAF ainda não guarda uma referência técnica publicada. Este delta prepara a cópia imutável dos valores do plano e a comparação por identidade/campo. Área10ha → 11ha aparece como alteração; reordenar as linhas não gera diferença. Ausente, null e zero permanecem distintos. Unidades diferentes são explicitadas sem subtração presumida.

`plano_referencia.js` usa os seletores SAF existentes (`cultRows`, `ocorr`, `cfgIn` e grades de recursos). Copia cultivos, planos/versões, atividades/gatilhos, produtos/doses, ajustes locais e parâmetros usados. Não recalcula demanda, não inclui estoque/reservas/realizado, não escreve cenário e não inventa publicação, data, ator ou aprovação para a semente. A referência técnica não autoriza orçamento nem O.S.

As chaves de fazenda e produto ainda são os nomes usados pelo domínio do protótipo. Cultivo, atividade, plano e configuração conservam os IDs existentes; chaves compostas são codificadas como arrays JSON para evitar colisão por separador. Identidade repetida é recusada. Essa limitação herdada não é apresentada como identificação definitiva do software real.

Validação executada: `python3 plano_referencia_unit_test.py`, a partir de `tools/prototipo/v37/gen37` com Node no PATH: **22/22**. O executor monta dados/grades e os seletores reais do SAF com dados sintéticos; substitui somente o destino HTML do gerador. Cobre imutabilidade após área/data/dose/catálogo, inclusão/retirada de insumo, recursos/calendário, ordem visual, isolamento, zero/ausência, unidade incompatível e recusa de número não finito. Confere também cenário e demanda inalterados. Bruto: `unit.txt`.

Pendentes para completar F2-01..06: comando atômico/recibo via CONF-D50/CF04, guardas de publicação (papel, versão esperada, encerramento e impedimentos), sinalização persistida “Orçamento a revisar”, gancho no SAF e painel de comparação/histórico com testes1440/390/teclado. `cenIdem` e a trilha CF04 não existem na base v56 recuperada; dependência solicitada ao Claude no6148886749. Não foi criado um segundo mecanismo de idempotência. **Este núcleo não está carregado na tela nem publica versões.** Sem jornada/UI nova a declarar testada.

Aplicado: retrato independente, comparação por identidade e referência técnica separada de autorização. Fora deste delta: publicação, UI e orçamento/realizado. Cortado: cópia de estoque/execução e nova conta de demanda, porque duplicariam fontes e confundiriam o plano com fatos operacionais.
