# Extratos das fontes da SOLO-FOLHA-NIVEIS

Para que serve: conferir as faixas e os localizadores citados em `../../SOLO-FOLHA-NIVEIS.md` contra o original. O PDF completo da CER04 tem 65 MB e passa do limite da web do Codex (R2, comentário 6221505413): baixe-o pelo terminal (`curl -LO <URL do PDF>`), confira o SHA-256 abaixo e extraia só as páginas da tabela com os comandos do fim.

**Os extratos não são versionados.** As duas obras são distribuídas em acesso aberto pela Infoteca-e da Embrapa, mas a ficha da CER04 diz "Todos os direitos reservados", e os extratos somam 8,9 MB. Ficam no repositório só a citação, as páginas e o SHA-256 do original; quem confere refaz o extrato a partir do original.

## CER04 · Cerrado: correção do solo e adubação

- **Obra:** Sousa, D. M. G.; Lobato, E. (ed. técnicos). _Cerrado: correção do solo e adubação_. 2. ed. Brasília, DF: Embrapa Informação Tecnológica, 2004. 416 p. ISBN 85-7075-230-4. PDF da impressão de 2017 (ficha da obra: 1ª impressão da 2ª edição em 2004).
- **Origem:** [registro na Infoteca](https://www.infoteca.cnptia.embrapa.br/infoteca/handle/doc/555355) · [PDF](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/555355/1/Cerrado-Correcao-solo-adubacao-ed-02-8a-impressao-2017.pdf), baixado em 16/10/2026.
- **PDF original:** 420 páginas, 65.398.995 bytes, SHA-256 `986b1a7c5d4e75f950b56e54d9351334d36f44b9934ecd5da3ebbeeb70f475aa`.
- **Páginas:** a do PDF é a impressa + 2. A impressa foi conferida pelo número no rodapé de cada página (`… impressao_2017.indd N`).

| Ordem no extrato | Impressa | PDF     | Conteúdo citado                                                                      |
| ---------------- | -------- | ------- | ------------------------------------------------------------------------------------ |
| 1                | 36       | 38      | Tab. 3: classes de textura pela argila                                               |
| 2                | 84       | 86      | V₂ de 50 % (sequeiro) e 60 % (irrigado)                                              |
| 3–5              | 247–249  | 249–251 | Cap. 10, Tab. 1: folha, época e número de folhas                                     |
| 6–7              | 252–253  | 254–255 | Cap. 10, Tab. 2: macronutrientes na folha (café, mamão pecíolo, feijão, soja, milho) |
| 8                | 254      | 256     | Cap. 10, Tab. 3: micronutrientes na folha                                            |
| 9                | 324      | 326     | Perenes, Tab. 3: P (Mehlich-1) por argila                                            |
| 10               | 326      | 328     | Perenes, Tab. 5: K por CTC ou argila                                                 |
| 11–12            | 353–354  | 355–356 | Mamão: V₂ 50 %, Mg mínimo, gessagem (m > 20 % ou Ca < 0,5 até 60 cm)                 |
| 13–17            | 392–396  | 394–398 | Anexo 6 (culturas anuais), Tab. 1 a 14                                               |

- **Extrato local (não versionado):** 17 páginas na ordem da tabela, SHA-256 `261f15107ba959a599e22514b9d66351f36805aba33ab5bebd803ca7bffeb31e` (muda se for refeito, ver abaixo).
  - **Atenção:** as tabelas do Anexo 6 e do cap. 10 não têm camada de texto no PDF; os números se conferem na imagem da página.

## SOJ20 · Tecnologias de produção de soja

- **Obra:** Embrapa Soja. _Tecnologias de produção de soja_. Londrina: Embrapa Soja, jun. 2020 (Sistemas de Produção, 17; ISSN 2176-2902).
- **Origem:** [PDF na Infoteca](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1123928/1/SP-17-2020-online-1.pdf), baixado em 16/10/2026.
- **PDF original:** 348 páginas, SHA-256 `a3bc85a7fbe29a6630583803fa54da38614c36da225b7e216ccb363ff166701e`. O PDF não tem rótulos de página (`/PageLabels`): a página do PDF é a impressa.

| Ordem no extrato | Impressa = PDF | Conteúdo citado                                                                                                                               |
| ---------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 1                | 139            | V₂ por estado (PR e SP 70 %; MS 60 %; demais do Cerrado 50 %); fólio "139" no alto da página                                                  |
| 2                | 148            | Amostragem da folha: 3º ou 4º trifólio sem pecíolo; R1–R2 (determinado); R2, até o início de R3 com V8/V10 (indeterminado); chamada da Tab. 7 |
| 3                | 149            | Tab. 7 (folha sem pecíolo) e Tab. 8 (PR); fólio "149" no alto da página                                                                       |

- **Extrato local (não versionado):** 3 páginas, SHA-256 `a4481dcf04f68b4116756bdfddcc49444080bbcd08e0db1f6aaffc0ea24ce912`.

## Como foi feito

Ferramentas do poppler, sem recomprimir nem alterar o conteúdo das páginas:

```text
pdfseparate -f <p> -l <p> <original>.pdf <página>.pdf   (uma vez por página da tabela acima)
pdfunite <páginas em ordem> <extrato>.pdf
pdftotext -layout <extrato>.pdf <extrato>.txt
```

O SHA-256 do extrato muda se ele for refeito, porque o `pdfunite` grava metadados novos. A prova de origem é o SHA-256 do original junto com os números das páginas.
