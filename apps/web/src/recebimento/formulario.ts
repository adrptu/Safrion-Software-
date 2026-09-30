import {
  EsquemaDadosRecebimento,
  EsquemaErro,
  EsquemaRecibo,
  type DadosRecebimento,
  type ReciboContrato,
} from '@safrion/contracts';
import { MOTIVOS, UNIDADES, type CodigoUnidade, type MotivoDivergencia } from '@safrion/domain';

import { dataDoCampo } from '../formato/data';
import { compararDecimais, decimalDoCampo, positivo, somarDecimais } from '../formato/numero';

/**
 * Formulário de recebimento por documento (FO-18; contrato CMD-15 §7.1): campos como digitados, validação junto ao campo
 * e à linha, corpo do comando e leitura das respostas do POST e do GET. Puro, para o teste cobrir cada caminho; o
 * componente só liga isto à tela. Decimais ficam em texto do começo ao fim (nada de Number).
 */
export const COMANDO = 'estoque.receber-documento';
export const MAX_LINHAS = 50;

/** O que a tela precisa do cadastro (mesma forma de OpcoesRecebimento do banco, sem depender do pacote do servidor). */
export interface Referencia {
  readonly id: string;
  readonly nome: string;
}
export interface ProdutoOpcao extends Referencia {
  readonly unidade: string;
  readonly validade: 'controla' | 'nao_se_aplica';
  readonly lote: 'informado' | 'por_documento';
  readonly embalagens: readonly {
    readonly id: string;
    readonly nome: string;
    readonly fator: string;
    readonly versao: number;
  }[];
  readonly lotes: readonly { readonly codigo: string; readonly validade: string | null }[];
}
export interface Opcoes {
  readonly emitentes: readonly (Referencia & { readonly identificacao: string })[];
  readonly fazendas: readonly (Referencia & { readonly locais: readonly Referencia[] })[];
  readonly produtos: readonly ProdutoOpcao[];
  readonly responsaveis: readonly Referencia[];
}

export interface CamposLinha {
  /** Identificador local da linha na tela (chave do React e do erro); não vai ao servidor. */
  readonly id: string;
  readonly produto: string;
  readonly lote: string;
  /** dd/mm/aaaa, só quando o lote é novo e o produto controla validade. */
  readonly validade: string;
  readonly local: string;
  /** Código da unidade de medida (L, mL…) ou "emb:<id da conversão>". */
  readonly unidade: string;
  readonly documento: string;
  readonly apto: string;
  readonly quarentena: string;
  readonly bloqueado: string;
  readonly recusado: string;
  readonly motivo: string;
  readonly motivoTexto: string;
  readonly inspecaoResponsavel: string;
  readonly inspecaoPrazo: string;
  /** Produto real cadastrado, ou vazio para descrever. */
  readonly ocorrenciaProduto: string;
  readonly ocorrenciaDescricao: string;
  readonly ocorrenciaQuantidade: string;
  readonly ocorrenciaUnidade: string;
  readonly ocorrenciaDestino: string;
  readonly ocorrenciaResponsavel: string;
  readonly ocorrenciaPrazo: string;
}
export type CampoLinha = Exclude<keyof CamposLinha, 'id'>;

export interface CamposOrigem {
  readonly emitente: string;
  readonly tipo: string;
  readonly serie: string;
  readonly numero: string;
  /** dd/mm/aaaa. */
  readonly emissao: string;
  readonly recebimento: string;
  readonly fazenda: string;
}
export type CampoOrigem = keyof CamposOrigem;

export interface CamposRecebimento extends CamposOrigem {
  readonly linhas: readonly CamposLinha[];
}

export interface ErrosRecebimento {
  readonly origem: Partial<Record<CampoOrigem, string>>;
  readonly linhas: Readonly<Record<string, Partial<Record<CampoLinha, string>>>>;
  readonly geral?: string;
}

export const SEM_ERROS: ErrosRecebimento = { origem: {}, linhas: {} };

export function temErro(e: ErrosRecebimento): boolean {
  return (
    e.geral !== undefined ||
    Object.values(e.origem).some(Boolean) ||
    Object.values(e.linhas).some((l) => Object.values(l).some(Boolean))
  );
}

/** Data civil de hoje (AAAA-MM-DD) para dd/mm/aaaa, sem passar por Date. */
export function dataParaCampo(civil: string): string {
  return /^\d{4}-\d{2}-\d{2}$/.test(civil)
    ? `${civil.slice(8, 10)}/${civil.slice(5, 7)}/${civil.slice(0, 4)}`
    : '';
}

export function linhaVazia(id: string, contexto: { readonly local: string }): CamposLinha {
  return {
    id,
    produto: '',
    lote: '',
    validade: '',
    local: contexto.local,
    unidade: '',
    documento: '',
    apto: '',
    quarentena: '',
    bloqueado: '',
    recusado: '',
    motivo: '',
    motivoTexto: '',
    inspecaoResponsavel: '',
    inspecaoPrazo: '',
    ocorrenciaProduto: '',
    ocorrenciaDescricao: '',
    ocorrenciaQuantidade: '',
    ocorrenciaUnidade: '',
    ocorrenciaDestino: '',
    ocorrenciaResponsavel: '',
    ocorrenciaPrazo: '',
  };
}

/**
 * Documento novo: só o contexto vem preenchido (emitente, fazenda e local quando únicos; recebido hoje). Quantidade, lote
 * e validade nunca vêm do documento anterior (contrato CMD-15 §7.1).
 */
export function recebimentoVazio(opcoes: Opcoes, hoje: string, idLinha: string): CamposRecebimento {
  const fazenda = opcoes.fazendas.length === 1 ? (opcoes.fazendas[0]?.id ?? '') : '';
  return {
    emitente: opcoes.emitentes.length === 1 ? (opcoes.emitentes[0]?.id ?? '') : '',
    tipo: 'nfe',
    serie: '',
    numero: '',
    emissao: '',
    recebimento: dataParaCampo(hoje),
    fazenda,
    linhas: [linhaVazia(idLinha, { local: localUnico(opcoes, fazenda) })],
  };
}

/** Local da fazenda quando ela tem um só: vem do contexto e aparece só para leitura. */
export function localUnico(opcoes: Opcoes, fazenda: string): string {
  const locais = opcoes.fazendas.find((f) => f.id === fazenda)?.locais ?? [];
  return locais.length === 1 ? (locais[0]?.id ?? '') : '';
}

export const produtoDe = (opcoes: Opcoes, id: string) => opcoes.produtos.find((p) => p.id === id);

/** Unidades da linha: as de medida da mesma dimensão da base (a base primeiro) e as embalagens do produto. */
export function unidadesDoProduto(
  p: ProdutoOpcao | undefined,
): { readonly valor: string; readonly rotulo: string }[] {
  if (!p || !Object.hasOwn(UNIDADES, p.unidade)) return [];
  const dimensao = UNIDADES[p.unidade as CodigoUnidade].dimensao;
  const medidas = (Object.keys(UNIDADES) as CodigoUnidade[])
    .filter((u) => UNIDADES[u].dimensao === dimensao)
    .sort((a, b) => Number(b === p.unidade) - Number(a === p.unidade))
    .map((u) => ({ valor: u, rotulo: ROTULOS[u] ?? u }));
  return [...medidas, ...p.embalagens.map((e) => ({ valor: `emb:${e.id}`, rotulo: e.nome }))];
}
const ROTULOS: Partial<Record<CodigoUnidade, string>> = { m3: 'm³', sc60: 'sc 60 kg' };

/**
 * Validade da linha: o lote de fabricante que já existe manda (a data dele, ou "não se aplica"), mesmo que a política do
 * produto tenha mudado depois; lote novo segue a política do produto (contrato CMD-15 §5; Codex 06:56Z).
 */
export type RegraValidade =
  | { readonly tipo: 'do_lote'; readonly validade: string | null }
  | { readonly tipo: 'informar' }
  | { readonly tipo: 'nao_se_aplica' };

export function regraDaValidade(p: ProdutoOpcao | undefined, codigoLote: string): RegraValidade {
  if (!p) return { tipo: 'informar' };
  if (p.lote === 'informado') {
    const existente = p.lotes.find((l) => l.codigo === codigoLote.trim());
    if (existente) return { tipo: 'do_lote', validade: existente.validade };
  }
  return p.validade === 'controla' ? { tipo: 'informar' } : { tipo: 'nao_se_aplica' };
}

/** Parcela conferida: vazio é zero; zero vale; negativo e texto não. */
export function parcelaDoCampo(
  texto: string,
): { readonly ok: true; readonly valor: string } | { readonly ok: false; readonly erro: string } {
  if (texto.replace(/\s/g, '') === '') return { ok: true, valor: '0' };
  if (/^\s*0+(?:,0+)?\s*$/.test(texto)) return { ok: true, valor: '0' };
  return decimalDoCampo(texto);
}

const inteira = (valor: string) => !valor.includes('.');

/** Divergência pela mesma regra do domínio: conferido diferente do documento, ou bloqueado ou recusado maior que zero. */
export function situacaoDaLinha(l: CamposLinha): {
  readonly divergente: boolean;
  readonly inspecao: boolean;
  readonly conferido: string | null;
  readonly comparacao: number | null;
} {
  const doc = decimalDoCampo(l.documento);
  const partes = [l.apto, l.quarentena, l.bloqueado, l.recusado].map(parcelaDoCampo);
  if (!doc.ok || partes.some((p) => !p.ok)) {
    return { divergente: false, inspecao: false, conferido: null, comparacao: null };
  }
  const valores = partes.map((p) => (p.ok ? p.valor : '0'));
  let conferido: string;
  try {
    conferido = somarDecimais(valores);
  } catch {
    return { divergente: false, inspecao: false, conferido: null, comparacao: null };
  }
  const comparacao = compararDecimais(conferido, doc.valor);
  const [, quarentena, bloqueado, recusado] = valores as [string, string, string, string];
  return {
    divergente: comparacao !== 0 || positivo(bloqueado) || positivo(recusado),
    inspecao: positivo(quarentena),
    conferido,
    comparacao,
  };
}

export const NOMES_DOS_MOTIVOS: Readonly<Record<MotivoDivergencia, string>> = {
  avaria: 'Avaria',
  validade: 'Validade',
  produto_diferente: 'Produto diferente',
  falta: 'Falta',
  sobra: 'Sobra',
  outro: 'Outro',
};

const ehMotivo = (v: string): v is MotivoDivergencia => (MOTIVOS as readonly string[]).includes(v);

type LinhaDados = DadosRecebimento['linhas'][number];

function validarLinha(
  l: CamposLinha,
  numero: number,
  opcoes: Opcoes,
  locais: readonly Referencia[],
  erros: Partial<Record<CampoLinha, string>>,
): LinhaDados | null {
  const p = produtoDe(opcoes, l.produto);
  if (!p) erros.produto = 'Escolha o produto.';
  const porDocumento = p?.lote === 'por_documento';
  const codigo = l.lote.trim();
  if (p && !porDocumento) {
    if (codigo === '') erros.lote = 'Informe o lote do fabricante.';
    else if (codigo.length > 64) erros.lote = 'Use até 64 caracteres.';
  }
  const regra = regraDaValidade(p, codigo);
  let validade: string | null = null;
  if (regra.tipo === 'do_lote') validade = regra.validade;
  else if (regra.tipo === 'informar') {
    const v = dataDoCampo(l.validade);
    if (v === null) erros.validade = 'Informe a validade como dd/mm/aaaa.';
    validade = v;
  }
  if (!locais.some((x) => x.id === l.local)) erros.local = 'Escolha o local.';
  const unidades = unidadesDoProduto(p);
  if (p && !unidades.some((u) => u.valor === l.unidade)) erros.unidade = 'Escolha a unidade.';
  const embalagem = l.unidade.startsWith('emb:')
    ? p?.embalagens.find((e) => `emb:${e.id}` === l.unidade)
    : undefined;
  const contagem =
    !embalagem &&
    Object.hasOwn(UNIDADES, l.unidade) &&
    UNIDADES[l.unidade as CodigoUnidade].dimensao === 'contagem';
  const itens = contagem || embalagem !== undefined;

  const doc = decimalDoCampo(l.documento);
  if (!doc.ok) erros.documento = doc.erro;
  else if (itens && !inteira(doc.valor)) erros.documento = 'Esta unidade conta itens inteiros.';
  const parcelas = { apto: l.apto, quarentena: l.quarentena, bloqueado: l.bloqueado, recusado: l.recusado };
  const lidas: Record<string, string> = {};
  for (const [campo, texto] of Object.entries(parcelas) as [keyof typeof parcelas, string][]) {
    const r = parcelaDoCampo(texto);
    if (!r.ok) erros[campo] = r.erro;
    else if (itens && !inteira(r.valor)) erros[campo] = 'Esta unidade conta itens inteiros.';
    else lidas[campo] = r.valor;
  }
  // Nada conferido também é conferência: é falta (ou produto diferente), com o motivo exigido abaixo.
  const s = situacaoDaLinha(l);

  let motivo: MotivoDivergencia | undefined;
  if (s.divergente) {
    if (!ehMotivo(l.motivo)) erros.motivo = 'Escolha o motivo da divergência.';
    else {
      motivo = l.motivo;
      if (motivo === 'falta' && (s.comparacao ?? 0) >= 0)
        erros.motivo = '"Falta" só quando o conferido é menor que o documento.';
      if (motivo === 'sobra' && (s.comparacao ?? 0) <= 0)
        erros.motivo = '"Sobra" só quando o conferido é maior que o documento.';
      if (motivo === 'outro' && l.motivoTexto.trim() === '') erros.motivoTexto = 'Descreva o motivo.';
      if (l.motivoTexto.length > 200) erros.motivoTexto = 'Use até 200 caracteres.';
    }
  }

  let inspecao: LinhaDados['inspecao'];
  if (s.inspecao) {
    if (!opcoes.responsaveis.some((r) => r.id === l.inspecaoResponsavel))
      erros.inspecaoResponsavel = 'Escolha quem decide a inspeção.';
    const prazo = dataDoCampo(l.inspecaoPrazo);
    if (prazo === null) erros.inspecaoPrazo = 'Informe o prazo como dd/mm/aaaa.';
    else inspecao = { responsavel: l.inspecaoResponsavel, prazo };
  }

  let ocorrencia: LinhaDados['ocorrencia'];
  if (motivo === 'produto_diferente') {
    const real = l.ocorrenciaProduto;
    if (real !== '' && !opcoes.produtos.some((x) => x.id === real))
      erros.ocorrenciaProduto = 'Escolha o produto que chegou ou descreva.';
    if (real !== '' && real === l.produto)
      erros.ocorrenciaProduto = 'O produto que chegou é outro, não o do documento.';
    if (real === '' && l.ocorrenciaDescricao.trim() === '')
      erros.ocorrenciaDescricao = 'Escolha o produto que chegou ou descreva.';
    if (l.ocorrenciaDescricao.length > 160) erros.ocorrenciaDescricao = 'Use até 160 caracteres.';
    const q = decimalDoCampo(l.ocorrenciaQuantidade);
    if (!q.ok) erros.ocorrenciaQuantidade = q.erro;
    const unidade = l.ocorrenciaUnidade.trim();
    if (unidade === '' || unidade.length > 40)
      erros.ocorrenciaUnidade = 'Informe a unidade como foi contada.';
    const destino = l.ocorrenciaDestino;
    if (destino !== 'retido_para_decisao' && destino !== 'devolvido_na_entrega')
      erros.ocorrenciaDestino = 'Escolha o destino do que chegou.';
    if (!opcoes.responsaveis.some((r) => r.id === l.ocorrenciaResponsavel))
      erros.ocorrenciaResponsavel = 'Escolha quem responde pela ocorrência.';
    const prazo = l.ocorrenciaPrazo.trim() === '' ? null : dataDoCampo(l.ocorrenciaPrazo);
    if (l.ocorrenciaPrazo.trim() !== '' && prazo === null)
      erros.ocorrenciaPrazo = 'Informe o prazo como dd/mm/aaaa.';
    if (destino === 'retido_para_decisao' && prazo === null && !erros.ocorrenciaPrazo)
      erros.ocorrenciaPrazo = 'Retido para decisão precisa de prazo.';
    if (q.ok && (destino === 'retido_para_decisao' || destino === 'devolvido_na_entrega')) {
      ocorrencia = {
        produtoReal: real !== '' ? { produto: real } : { descricao: l.ocorrenciaDescricao.trim() },
        quantidade: q.valor,
        unidade,
        destino,
        responsavel: l.ocorrenciaResponsavel,
        ...(prazo === null ? {} : { prazo }),
      };
    }
  }

  if (Object.values(erros).some(Boolean) || !p || !doc.ok) return null;
  return {
    numero,
    produto: p.id,
    lote: porDocumento ? { interno: true } : { codigo },
    validade,
    local: l.local,
    unidade: embalagem
      ? { tipo: 'embalagem', conversao: embalagem.id, versao: embalagem.versao }
      : { tipo: 'medida', unidade: l.unidade as CodigoUnidade },
    documento: doc.valor,
    parcelas: {
      apto: lidas['apto'] ?? '0',
      quarentena: lidas['quarentena'] ?? '0',
      bloqueado: lidas['bloqueado'] ?? '0',
      recusado: lidas['recusado'] ?? '0',
    },
    ...(motivo ? { motivo } : {}),
    ...(motivo && l.motivoTexto.trim() !== '' ? { motivoTexto: l.motivoTexto.trim() } : {}),
    ...(inspecao ? { inspecao } : {}),
    ...(ocorrencia ? { ocorrencia } : {}),
  };
}

/** Confere o formulário inteiro; com erro, diz cada campo e linha e nada é enviado. */
export function validarRecebimento(
  c: CamposRecebimento,
  opcoes: Opcoes,
):
  | { readonly ok: true; readonly dados: DadosRecebimento }
  | { readonly ok: false; readonly erros: ErrosRecebimento } {
  const origem: Partial<Record<CampoOrigem, string>> = {};
  if (!opcoes.emitentes.some((e) => e.id === c.emitente)) origem.emitente = 'Escolha o emitente.';
  if (c.tipo !== 'nfe' && c.tipo !== 'outro') origem.tipo = 'Escolha o tipo do documento.';
  const numero = c.numero.trim();
  if (numero === '') origem.numero = 'Informe o número do documento.';
  else if (numero.replace(/^0+(?=\d)/, '').length > 20) origem.numero = 'Use até 20 caracteres.';
  if (c.serie.trim().replace(/^0+(?=\d)/, '').length > 8) origem.serie = 'Use até 8 caracteres.';
  const emissao = dataDoCampo(c.emissao);
  if (emissao === null) origem.emissao = 'Informe a emissão como dd/mm/aaaa.';
  const recebimento = dataDoCampo(c.recebimento);
  if (recebimento === null) origem.recebimento = 'Informe a data do recebimento como dd/mm/aaaa.';
  const fazenda = opcoes.fazendas.find((f) => f.id === c.fazenda);
  if (!fazenda) origem.fazenda = 'Escolha a fazenda.';

  const linhas: Record<string, Partial<Record<CampoLinha, string>>> = {};
  const dadosLinhas: LinhaDados[] = [];
  let geral: string | undefined;
  if (c.linhas.length === 0) geral = 'Adicione ao menos uma linha.';
  if (c.linhas.length > MAX_LINHAS) geral = `Um documento tem até ${String(MAX_LINHAS)} linhas.`;
  c.linhas.forEach((l, i) => {
    const e: Partial<Record<CampoLinha, string>> = {};
    const d = validarLinha(l, i + 1, opcoes, fazenda?.locais ?? [], e);
    if (Object.values(e).some(Boolean)) linhas[l.id] = e;
    else if (d) dadosLinhas.push(d);
  });
  const erros: ErrosRecebimento = { origem, linhas, ...(geral ? { geral } : {}) };
  if (temErro(erros) || emissao === null || recebimento === null || !fazenda) return { ok: false, erros };
  const dados: DadosRecebimento = {
    emitente: c.emitente,
    tipo: c.tipo === 'outro' ? 'outro' : 'nfe',
    serie: c.serie.trim(),
    numero,
    emissao,
    recebimento,
    fazenda: fazenda.id,
    linhas: dadosLinhas,
  };
  // Última barreira: o mesmo esquema do servidor. Se algo passou da validação da tela, nada é enviado.
  const conferido = EsquemaDadosRecebimento.safeParse(dados);
  if (!conferido.success) {
    return {
      ok: false,
      erros: { origem: {}, linhas: {}, geral: 'Confira os campos: o pedido não segue o contrato.' },
    };
  }
  return { ok: true, dados: conferido.data };
}

/** Intenção imutável: a chave, o id do documento e o corpo exato. Reenviar é mandar isto de novo, byte a byte. */
export interface Intencao {
  readonly chave: string;
  readonly documentoId: string;
  readonly corpo: string;
}

export function novaIntencao(dados: DadosRecebimento, chave: string, documentoId: string): Intencao {
  return {
    chave,
    documentoId,
    corpo: JSON.stringify({
      idempotencyKey: chave,
      target: { type: 'receipt_document', id: documentoId, expectedVersion: 0 },
      data: dados,
    }),
  };
}

/**
 * O que a tela faz com uma resposta:
 * - `resolvido`: recibo terminal validado e correspondente à intenção (confirmado, rejeitado ou conflito);
 * - `nao_gravado`: recusa certa de um PRIMEIRO envio (nada foi gravado), que libera corrigir e enviar com nova chave;
 * - `incerto`: qualquer outra coisa. Chave, corpo e campos continuam travados; só um recibo correspondente resolve.
 */
export type Desfecho =
  | { readonly tipo: 'resolvido'; readonly recibo: ReciboContrato }
  | { readonly tipo: 'nao_gravado'; readonly mensagem: string; readonly sessao: boolean }
  | {
      readonly tipo: 'incerto';
      readonly mensagem: string;
      readonly sessao: boolean;
      /** A consulta disse "ainda não localizado": reenviar o mesmo é o próximo gesto. */
      readonly naoLocalizado: boolean;
    };

/** Recibo validado pelo contrato e da mesma intenção (comando, chave e documento); senão null. */
export function reciboDaIntencao(corpo: unknown, intencao: Intencao): ReciboContrato | null {
  const r = EsquemaRecibo.safeParse(corpo);
  if (!r.success) return null;
  const x = r.data;
  return x.commandType === COMANDO &&
    x.idempotencyKey === intencao.chave &&
    x.targetType === 'receipt_document' &&
    x.targetId === intencao.documentoId
    ? x
    : null;
}

const codigoDoErro = (corpo: unknown): string | null => {
  const e = EsquemaErro.safeParse(corpo);
  return e.success ? e.data.codigo : null;
};

export const INCERTO =
  'O envio pode ter chegado ao servidor, mas a resposta não voltou. Consulte o recibo antes de qualquer outra coisa; nada é gravado duas vezes.';
const SESSAO_INCERTA =
  'Sua sessão terminou. Entre de novo para conferir o envio pendente; ele continua guardado neste navegador.';

/**
 * Resposta do POST. Recibo correspondente resolve. Num primeiro envio, 400/401/403/413/415 e chave reutilizada são certezas
 * de que nada foi gravado; num reenvio de intenção incerta não provam nada e a incerteza continua (Codex 06:29Z).
 */
export function desfechoDoEnvio(
  status: number,
  corpo: unknown,
  intencao: Intencao,
  reenvio: boolean,
): Desfecho {
  const recibo = reciboDaIntencao(corpo, intencao);
  if (recibo && (status === 200 || status === 409 || status === 422)) return { tipo: 'resolvido', recibo };
  const codigo = codigoDoErro(corpo);
  if (!reenvio) {
    if (status === 401)
      return {
        tipo: 'nao_gravado',
        mensagem: 'Sua sessão terminou. Entre de novo e confirme.',
        sessao: true,
      };
    if (status === 403)
      return { tipo: 'nao_gravado', mensagem: 'Seu papel não permite receber documento.', sessao: false };
    if (status === 413)
      return { tipo: 'nao_gravado', mensagem: 'O documento passou do tamanho permitido.', sessao: false };
    if (status === 400 || status === 415 || (status === 409 && codigo === 'IDEMPOTENCY_KEY_REUSED')) {
      return {
        tipo: 'nao_gravado',
        mensagem: 'O servidor não aceitou o pedido. Confira os campos e confirme de novo.',
        sessao: false,
      };
    }
  }
  return {
    tipo: 'incerto',
    mensagem: status === 401 ? SESSAO_INCERTA : INCERTO,
    sessao: status === 401,
    naoLocalizado: false,
  };
}

/** Resposta do GET: só o recibo correspondente resolve; "ainda não localizado" habilita reenviar o mesmo. */
export function desfechoDaConsulta(status: number, corpo: unknown, intencao: Intencao): Desfecho {
  const recibo = reciboDaIntencao(corpo, intencao);
  if (recibo && (status === 200 || status === 409 || status === 422)) return { tipo: 'resolvido', recibo };
  if (status === 404 && codigoDoErro(corpo) === 'RECIBO_NAO_LOCALIZADO') {
    return {
      tipo: 'incerto',
      mensagem:
        'Recibo ainda não localizado. Reenvie o mesmo documento: se ele já tiver chegado, volta o mesmo recibo, sem duplicar.',
      sessao: false,
      naoLocalizado: true,
    };
  }
  if (status === 401)
    return { tipo: 'incerto', mensagem: SESSAO_INCERTA, sessao: true, naoLocalizado: false };
  return {
    tipo: 'incerto',
    mensagem: 'Não deu para consultar agora. O envio continua guardado; consulte de novo em instantes.',
    sessao: false,
    naoLocalizado: false,
  };
}

/** Motivo da rejeição registrada, em português, e onde ele aparece na tela. */
export function motivoDaRejeicao(codigo: string | null): {
  readonly mensagem: string;
  readonly campo?: CampoOrigem;
} {
  switch (codigo) {
    case 'DOCUMENTO_JA_RECEBIDO':
      return {
        mensagem: 'Este documento do emitente já foi recebido. Confira em Recebimentos.',
        campo: 'numero',
      };
    case 'EMITENTE_NAO_ENCONTRADO':
      return { mensagem: 'Emitente não encontrado. Recarregue a página.', campo: 'emitente' };
    case 'FAZENDA_NAO_ENCONTRADA':
      return { mensagem: 'Fazenda não encontrada. Recarregue a página.', campo: 'fazenda' };
    case 'RESPONSAVEL_NAO_ENCONTRADO':
      return { mensagem: 'Um responsável escolhido não está mais ativo. Escolha outro.' };
    case 'VALIDADE_DIFERENTE_DO_LOTE':
      return { mensagem: 'A validade não é a do lote já recebido. Confira o lote e a data.' };
    case 'VALIDADE_OBRIGATORIA':
      return { mensagem: 'Este produto controla validade: informe a data do lote.' };
    case 'VALIDADE_NAO_SE_APLICA':
      return { mensagem: 'Este produto não tem validade: deixe a data em branco.' };
    case 'LOTE_TIPO_DIFERENTE':
    case 'LOTE_INTERNO_COLIDE':
      return { mensagem: 'O código do lote já pertence a outro tipo de lote. Confira o código.' };
    case 'UNIDADE_INCOMPATIVEL':
    case 'CONVERSAO_NAO_ENCONTRADA':
    case 'CONVERSAO_INVALIDA':
      return { mensagem: 'A unidade de uma linha não serve para o produto. Recarregue e escolha de novo.' };
    case 'QUANTIDADE_FORA_DA_ESCALA':
      return { mensagem: 'Uma quantidade tem casas decimais demais para a unidade.' };
    case 'LOCAL_NAO_ENCONTRADO':
    case 'LOCAL_FORA_DA_FAZENDA':
      return { mensagem: 'O local de uma linha não é da fazenda do documento.' };
    case 'PRODUTO_NAO_ENCONTRADO':
      return { mensagem: 'Um produto não está mais disponível. Recarregue a página.' };
    default:
      return { mensagem: 'O recebimento foi recusado. Confira os dados e confirme de novo.' };
  }
}
