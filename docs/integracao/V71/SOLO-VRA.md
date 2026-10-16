# SOLO-VRA · Recomendação por talhão pelo boletim e pela meta, zonas e arquivo para a máquina

> Proprietário, 16/10/2026: "Como está a recomendação de correção de solo e adubação baseado na análise de solo, escolha do boletim desejado e recomendação em função da produtividade desejada? por talhão. E envio do arquivo para as máquinas executarem em agricultura de precisão, taxa variável."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: SOLO-VRA / o agrônomo escolhe o boletim, recebe calagem, gessagem, P, K e N por talhão pela meta de produtividade, por zona quando o laudo é em grade, e entrega ao operador o arquivo de taxa variável conferido / agrônomo (RT) e operador de máquina
Requisitos do PRD e fora do escopo: cap. 35 (AGR-010…012, AGR-018, ACAG-07/08), cap. 36 (TV-007, 36.4–36.6), CAL-10, cap. 41 (aprovação individual); fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-v69-mapa a partir de 86c9066 / dados_solo.py, solo.js, areas/analise_solo.py, aba Prescrição da O.S. (areas/processo_os.py), prescricao.js (novo), solo_vra_unit.js e solo_vra_test.py (novos)
Aceite e comando de verificação: A1–A10 abaixo / node solo_vra_unit.js; python3 -B solo_vra_test.py; mais os testes de solo e da O.S. tocados
Estado / impedimento / próximo passo: especificado; revisão do Codex 6215849218 (3 S2 + ajustes) incorporada nesta versão; começa depois da autoria ativa (Cadastros) e dos riscos da Onda 0 (EX-32..36), uma autoria por agente (§3.6)
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
4. **Zonas e estados espaciais** (PRD 36.1, 36.3, 36.4, TV-003 e TV-005; revisão do Codex 6215849218).
   - **Área-alvo = prescrita + excluída + pendente,** três conjuntos disjuntos, em hectares geodésicos (nunca em graus; a mesma área geodésica do `talgeo.js`).
   - **Estados diferentes, nunca trocados entre si:**
     - **dose zero técnica:** a regra calculou 0;
     - **não aplicar (exclusão):** APP, carreador, área marcada;
     - **sem dado (pendente):** sem suporte amostral.
   - O total é Σ (dose × área) **só da área prescrita**. Área pendente ou excluída não recebe dose por preenchimento.
   - **Topologia conferida, não só a soma de áreas:** sem buraco nem sobreposição entre zonas, e toda zona dentro do talhão.
   - **Mapa de calor = reuso condicionado, não prova agronômica.** A interpolação do mapa só vira zona de prescrição quando o laudo declara:
     - suporte amostral (grade ou desenho dirigido, com pontos);
     - método e parâmetros;
     - resolução compatível;
     - incerteza.
   - **Sem essas condições:**
     - amostra composta do talhão dá dose uniforme;
     - a grade nominal do mapa não vira falsa grade de prescrição;
     - a área sem suporte fica pendente.
   - **No protótipo,** os pontos do quadrado unitário (`dados_solo.py`) são sintéticos e aparecem rotulados assim. Nada aqui é recomendação de campo.
   - A tela compara com a dose uniforme (quantidade e custo).
5. **Nutriente → produto.** A regra calcula nutriente (P₂O₅, K₂O, N; calcário pelo PRNT).
   - A dose do produto vem da conversão explícita: garantia ou composição do produto, fonte, unidade e versão do cadastro. Ela fica visível na memória antes do total e do arquivo.
   - Composição ausente bloqueia a dose daquele produto, com o motivo; nunca vira 0 nem 100 %.
   - O PRNT é aplicado uma vez só.
   - Trocar o produto (outra garantia ou outro PRNT) refaz a dose do produto e cria versão nova, que pede revisão.
   - O arquivo leva a dose **do produto** e guarda no manifesto a do nutriente.
6. **Arquivo.** A prescrição nasce na O.S. da atividade, na modalidade Uniforme ou Por zona. Formatos:
   - **Shapefile** (.zip com .shp, .shx, .dbf, .prj e .cpg): campos ZONA, ESTADO, PRODUTO, DOSE e UN; SIRGAS 2000 (EPSG:4674). Área pendente ou excluída vai com ESTADO e sem dose.
   - **ISOXML** (TASKDATA.XML, ISO 11783-10): tarefa com zonas de tratamento poligonais.
     - O DDI e a escala da taxa (por exemplo, massa por área) vêm do perfil da máquina e da fonte normativa, não de constante no código.
     - Estrutura e DDI ainda **não foram conferidos contra o esquema**: nenhuma alegação de conformidade até a validação externa e o teste no terminal.
   - **Manifesto externo ao pacote** (recibo à parte, não dentro dos bytes que ele identifica). Leva:
     - O.S., versão, produto, unidade e nutriente;
     - área prescrita, excluída e pendente;
     - total e perfil;
     - SHA-256 da prescrição canônica e SHA-256 do pacote.
   - O sistema relê o próprio arquivo (TV-007), mas a releitura não basta como oráculo: o total confere com uma conta independente.
   - **Perfil de máquina.** Monitor, formato, unidade, dose mínima e máxima por produto, e a situação na matriz do PRD 36.5 e TV-012.
     - Perfil não homologado gera só "simulação". Ter o ZIP ou o XML não dá selo executável.
     - Dose fora dos limites do implemento bloqueia a geração, com a zona e o limite; o sistema não ajusta sozinho (PRD 36.4).
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
| A5 | Laudo em grade com suporte declarado; e casos de topologia: buraco, sobreposição, zona fora do talhão, exclusão, pendente e dose zero | zonas pelas classes; área-alvo = prescrita + excluída + pendente (disjuntas, em ha geodésicos); total = Σ dose × área **prescrita**; buraco, sobreposição e zona fora do talhão reprovam. **Contraprova aritmética** (talhão 10 ha, 2 excluídos, 3 sem dado, 5 a 200 kg/ha): 1.000 kg, nunca 2.000 |
| A5b | Amostra composta do talhão; laudo sem suporte amostral declarado | dose uniforme; a grade do mapa de calor não vira zona; área sem suporte fica pendente |
| A6 | Shapefile | o .zip tem os 5 arquivos; DBF com ZONA, ESTADO, DOSE (do produto) e UN; .prj SIRGAS 2000; releitura devolve as mesmas zonas, estados e doses, e o total confere com a conta independente |
| A6b | Nutriente → produto (sintético) | alvo de 60 kg/ha de nutriente com produto de fração 0,20 → 300 kg/ha de produto (escrever 60 entregaria 12); composição ausente bloqueia com motivo (nem 0 nem 100 %); troca de composição refaz a dose e cria versão; PRNT uma vez |
| A7 | ISOXML | TASKDATA.XML com tarefa e zonas poligonais; DDI e escala vindos do perfil; relido com as mesmas doses; **sem** alegação de conformidade até a validação contra o esquema e no terminal |
| A8 | Dose fora do mínimo ou máximo do implemento; zona fora do talhão; perfil não homologado | os dois primeiros bloqueiam com zona e limite; o terceiro gera só "simulação", sem selo executável |
| A9 | Dose alterada depois de aprovada | v2 criada, aprovação pedida de novo, v1 "substituição não confirmada" até a confirmação |
| A10 | Manifesto | externo ao pacote; SHA-256 da prescrição canônica e do pacote; áreas prescrita, excluída e pendente; a O.S. mostra arquivo, versão, destinatário e confirmação |

**Contraprova:** a versão publicada antes (sem referência nem arquivo) reprova A1, A5, A6 e A7. Os aceites A1–A10 são propostos; viram teste só depois da revisão do Codex sobre esta versão.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Tabelas oficiais dos boletins no software real | curadoria do RT com fonte, edição, erratas e direito de uso (PRD 35) |
| Envio por telemetria | o proprietário autorizar conta e contrato com o fornecedor |
| Retorno da aplicação (as-applied) e conciliação (PRD 36.7) | fatia seguinte, depois do arquivo homologado num monitor real |
| Homologação no monitor real | o proprietário informar marca e modelo dos monitores; teste no terminal |
| Suavização e fusão de zonas pequenas | pedido ou achado no teste com o monitor |
| Recomendação foliar | protocolo por cultura decidido |
