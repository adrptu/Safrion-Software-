# SOLO-VRA · Recomendação por talhão pelo boletim e pela meta, zonas e arquivo para a máquina

> Proprietário, 16/10/2026: "Como está a recomendação de correção de solo e adubação baseado na análise de solo, escolha do boletim desejado e recomendação em função da produtividade desejada? por talhão. E envio do arquivo para as máquinas executarem em agricultura de precisão, taxa variável."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: SOLO-VRA / o agrônomo escolhe o boletim, recebe calagem, gessagem, P, K e N por talhão pela meta de produtividade, por zona quando o laudo é em grade, e entrega ao operador o arquivo de taxa variável conferido / agrônomo (RT) e operador de máquina
Requisitos do PRD e fora do escopo: cap. 35 (AGR-010…012, AGR-018, ACAG-07/08), cap. 36 (TV-007, 36.4–36.6), CAL-10, cap. 41 (aprovação individual); fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-v69-mapa a partir de 86c9066 / dados_solo.py, solo.js, areas/analise_solo.py, aba Prescrição da O.S. (areas/processo_os.py), prescricao.js (novo), solo_vra_unit.js e solo_vra_test.py (novos)
Aceite e comando de verificação: A1–A10 abaixo / node solo_vra_unit.js; python3 -B solo_vra_test.py; mais os testes de solo e da O.S. tocados
Estado / impedimento / próximo passo: especificado; começa quando a frente Cadastros ou a frente Mapa for publicada (limite de três frentes, §3.6)
```

## Situação em 16/10 (conferida no código)

| Parte | Hoje |
|---|---|
| Laudo por talhão, índices, validação | pronto (AG-02) |
| Calagem por V% e PRNT | pronta, com "Por quê" |
| Gessagem 20–40 cm | só demonstração (D-03) |
| K pela meta | só soja, meta de 2.400 a 4.800 kg/ha (D-02) |
| P, N, micronutrientes | não geram dose |
| Escolha do boletim | não existe: uma regra só, "Demonstração — tabela regional a decidir"; o campo Fonte do AG-04 é texto |
| Mapa de calor por indicador | pronto (Mapa › Análises de solo) |
| Dose por zona | ilustração fixa na REC-014; laudo por zona não sugere (D-15) |
| Arquivo para a máquina | não existe; "Gerar prescrição" só mostra mensagem |

## Decisões dos agentes (delegação do proprietário)

1. **Referência por fazenda e cultura.** O agrônomo escolhe a referência (publicação, edição, tabela, região, extrator, faixa de meta) numa lista. As tabelas são dados (`dados_solo.py`), nunca código. No protótipo, os valores são de demonstração e aparecem marcados assim. Sem referência escolhida, nada é sugerido e a tela diz por quê.
   - *Dano evitado:* tabela de outra região ou cultura aplicada sem ninguém ver.
2. **Meta do talhão é a do Planejar safra.** Não se pede de novo.
   - Meta fora da faixa da tabela não gera dose. É o que exige o AGR-012: sem extrapolação.
3. **Nutrientes por referência:**
   - calagem pelo V₂ da referência;
   - P₂O₅ e K₂O pela classe do teor × meta;
   - N pela meta, nas culturas em que a tabela tem N. Na soja, a tabela diz 0 (inoculação).
   - A gessagem continua demonstração até a curadoria (PRD 35, pendência registrada).
4. **Zonas.** Laudo em grade gera zonas pelas classes da referência no nutriente da linha:
   - as zonas vêm do mapa de calor que já existe (mesma interpolação);
   - laudo único do talhão dá dose uniforme;
   - a área das zonas soma a área do talhão; o total é Σ dose × área;
   - a tela compara com a dose uniforme (quantidade e custo).
5. **Arquivo.** A prescrição nasce na O.S. da atividade, na modalidade Uniforme ou Por zona. Formatos:
   - **Shapefile** (.zip com .shp, .shx, .dbf, .prj e .cpg): campos ZONA, PRODUTO, DOSE e UN; SIRGAS 2000 (EPSG:4674);
   - **ISOXML** (TASKDATA.XML, ISO 11783-10): tarefa com zonas de tratamento poligonais. A taxa usa o DDI 6, massa por área em mg/m² (1 kg/ha = 100 mg/m²), ou o DDI 1, volume por área (1 L/ha = 100 mm³/m²).
   - **Manifesto** com O.S., versão, produto, unidade, área, total, perfil de máquina e SHA-256 da prescrição e do pacote.
   - O sistema relê o próprio arquivo antes de liberar o download (TV-007).
6. **Perfil de máquina.** Cada perfil tem monitor, formato, unidade e dose mínima e máxima por produto, com a situação da matriz do PRD 36.5.
   - **Perfil não homologado** gera arquivo marcado "simulação", nunca executável (PRD 36.5).
   - **Dose fora dos limites do implemento** bloqueia a geração. A tela mostra a zona e o limite e não ajusta a dose sozinha (PRD 36.4).
7. **Aprovação.** A prescrição faz parte da aprovação individual da O.S. (cap. 41).
   - Mudar a dose depois de aprovada cria nova versão e pede nova aprovação.
   - O arquivo anterior fica "substituição não confirmada" até o operador confirmar a importação da nova versão.
8. **Envio.** No protótipo, por download (pendrive), com "Confirmar importação no monitor" pelo operador.
   - Enviar o arquivo não aciona a máquina (PRD 36.6).
   - Telemetria (Operations Center, Stara, FieldView) exige conta e contrato e fica com o proprietário.

## Aceite

| ID | Caso | Oráculo |
|---|---|---|
| A1 | Mesmo talhão, referência A → B | dose de K e P muda; o "Por quê" cita publicação, edição e tabela; sem referência: nada sugerido, com motivo |
| A2 | P baixo e meta dentro da faixa; meta no limite inferior, no superior e fora | dose da linha certa nos limites; fora: "fora da faixa", nada sugerido (ACAG-08) |
| A3 | Milho com meta X; soja | N pela linha da meta; soja sem N, com o motivo da tabela |
| A4 | Calagem com V₂ da referência | CAL-10 (AC-27) continua passando; PRNT usado uma vez |
| A5 | Laudo em grade | zonas pelas classes; Σ área = área do talhão (±0,5 %); total = Σ dose × área; comparativo com a uniforme |
| A6 | Shapefile | o .zip tem os 5 arquivos; DBF com DOSE na unidade do produto; .prj SIRGAS 2000; reimportado pelo sistema devolve as mesmas zonas e doses |
| A7 | ISOXML | TASKDATA.XML com TSK, TZN, PDV e polígonos; DDI e conversão de unidade conferidos; relido pelo sistema com as mesmas doses |
| A8 | Dose fora do mínimo ou máximo do implemento; zona fora do talhão; perfil não homologado | os dois primeiros bloqueiam com zona e limite; o terceiro gera só "simulação" |
| A9 | Dose alterada depois de aprovada | v2 criada, aprovação pedida de novo, v1 "substituição não confirmada" até a confirmação |
| A10 | Manifesto | SHA-256 da prescrição e do pacote; a O.S. mostra arquivo, versão, destinatário e confirmação |

**Contraprova:** a versão publicada antes (sem referência nem arquivo) reprova A1, A5, A6 e A7.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Tabelas oficiais dos boletins no software real | curadoria do RT com fonte, edição, erratas e direito de uso (PRD 35) |
| Envio por telemetria | o proprietário autorizar conta e contrato com o fornecedor |
| Retorno da aplicação (as-applied) e conciliação (PRD 36.7) | fatia seguinte, depois do arquivo homologado num monitor real |
| Homologação no monitor real | o proprietário informar marca e modelo dos monitores; teste no terminal |
| Suavização e fusão de zonas pequenas | pedido ou achado no teste com o monitor |
| Recomendação foliar | protocolo por cultura decidido |
