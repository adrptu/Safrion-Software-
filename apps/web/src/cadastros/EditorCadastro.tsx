'use client';
import {
  COMANDOS_CADASTRO as C,
  EsquemaDadosCriarFazenda,
  EsquemaDadosEditarFazenda,
  EsquemaDadosCriarTalhao,
  EsquemaDadosEditarTalhao,
  EsquemaDadosAlterarSituacaoTalhao,
  FUSO_PADRAO,
  FUSOS_BRASIL,
  lerAreaPtBr,
  normalizarNome,
  type ReciboContrato,
} from '@safrion/contracts';
import type { OpcaoFazenda } from '@safrion/db/web';
import Link from 'next/link';
import { useId, useRef, useState, type SubmitEvent } from 'react';
import { novaIntencao } from './intencao';
import type { IntencaoGuardada } from './pendencias';
import { useCadastroComando } from './useCadastroComando';
import s from './cadastro.module.css';

export interface EdicaoCadastro {
  readonly tipo: 'fazenda' | 'talhao' | 'situacao';
  readonly id?: string;
  readonly versao?: number;
  readonly nome?: string;
  readonly fuso?: string;
  readonly fazenda?: string;
  readonly areaDeclaradaHa?: string;
  readonly situacao?: 'ativo' | 'inativo';
}
interface Props {
  readonly edicao: EdicaoCadastro;
  readonly fazendas: readonly OpcaoFazenda[];
  readonly usuarioId: string;
  readonly organizacaoId: string;
  readonly volta: string;
  readonly confirmado: (recibo: ReciboContrato, g: IntencaoGuardada) => void;
  readonly cancelar: () => void;
  readonly inicial?: IntencaoGuardada;
}
/** O cadastro rápido mantém o talhão montado; criar a fazenda nunca confirma o talhão. */
export function EditorCadastro(p: Props) {
  const id = useId();
  const form = useRef<HTMLFormElement>(null);
  const [campos, setCampos] = useState<Record<string, string>>(
    () =>
      p.inicial?.campos ?? {
        nome: p.edicao.nome ?? '',
        fuso: p.edicao.fuso ?? FUSO_PADRAO,
        fazenda: p.edicao.fazenda ?? '',
        area: p.edicao.areaDeclaradaHa ? p.edicao.areaDeclaradaHa.replace('.', ',') : '',
        situacao: p.edicao.situacao ?? 'ativo',
      },
  );
  const [erros, setErros] = useState<Record<string, string>>({});
  const [novaFazenda, setNovaFazenda] = useState(false);
  const [criadas, setCriadas] = useState<OpcaoFazenda[]>([]);
  const comando = useCadastroComando(p.usuarioId, p.organizacaoId, p.confirmado, p.inicial);
  const tipo = p.edicao.tipo;
  const editando = p.edicao.id !== undefined;
  const travado = comando.ocupado || comando.pendente !== null;
  const opcoes = [...p.fazendas, ...criadas.filter((f) => !p.fazendas.some((x) => x.id === f.id))];
  const titulo =
    tipo === 'situacao'
      ? `${campos['situacao'] === 'ativo' ? 'Reativar' : 'Inativar'} talhão`
      : `${editando ? 'Salvar' : 'Criar'} ${tipo === 'fazenda' ? 'fazenda' : 'talhão'}`;
  const fusos = [
    ...FUSOS_BRASIL,
    ...Intl.supportedValuesOf('timeZone').filter((f) => !(FUSOS_BRASIL as readonly string[]).includes(f)),
  ];
  const mudar = (chave: string, valor: string) => {
    if (travado) return;
    setCampos((c) => ({ ...c, [chave]: valor }));
    setErros((e) => Object.fromEntries(Object.entries(e).filter(([k]) => k !== chave)));
  };
  function enviar(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    if (travado) return;
    const area = tipo === 'talhao' ? lerAreaPtBr(campos['area'] ?? '') : null;
    if (area && !area.ok) {
      setErros({ area: area.mensagem });
      form.current?.querySelector<HTMLInputElement>('[name="area"]')?.focus();
      return;
    }
    const data =
      tipo === 'fazenda'
        ? { nome: campos['nome'], fuso: campos['fuso'] }
        : tipo === 'talhao'
          ? { nome: campos['nome'], fazenda: campos['fazenda'], areaDeclaradaHa: area?.ok ? area.valor : '' }
          : { situacao: campos['situacao'] };
    const esquema =
      tipo === 'fazenda'
        ? editando
          ? EsquemaDadosEditarFazenda
          : EsquemaDadosCriarFazenda
        : tipo === 'talhao'
          ? editando
            ? EsquemaDadosEditarTalhao
            : EsquemaDadosCriarTalhao
          : EsquemaDadosAlterarSituacaoTalhao;
    const v = esquema.safeParse(data);
    if (!v.success) {
      const mensagens: Record<string, string> = {};
      for (const erro of v.error.issues) {
        const campo = String(erro.path[0] ?? 'nome');
        mensagens[campo] =
          campo === 'nome'
            ? 'Informe um nome com 1 a 80 caracteres.'
            : campo === 'fazenda'
              ? 'Escolha uma fazenda.'
              : campo === 'fuso'
                ? 'Escolha um fuso da lista.'
                : 'Confira este campo.';
      }
      setErros(mensagens);
      form.current?.querySelector<HTMLElement>(`[name="${Object.keys(mensagens)[0] ?? 'nome'}"]`)?.focus();
      return;
    }
    const commandType =
      tipo === 'fazenda'
        ? editando
          ? C.editarFazenda
          : C.criarFazenda
        : tipo === 'talhao'
          ? editando
            ? C.editarTalhao
            : C.criarTalhao
          : C.alterarSituacaoTalhao;
    const intencao = novaIntencao(
      commandType,
      tipo === 'fazenda' ? 'farm' : 'field',
      p.edicao.id ?? crypto.randomUUID(),
      comando.versaoAtual ?? p.edicao.versao ?? 0,
      v.data,
      crypto.randomUUID(),
    );
    comando.enviar({
      intencao,
      campos,
      contexto: { tipo, titulo, volta: p.volta },
      criadaEm: new Date().toISOString(),
    });
  }
  const campoTexto = (chave: string, rotulo: string, decimal = false) => (
    <div className="campo" data-erro={erros[chave] ? '' : undefined}>
      <label htmlFor={`${id}-${chave}`}>{rotulo}</label>
      <input
        id={`${id}-${chave}`}
        name={chave}
        type="text"
        value={campos[chave] ?? ''}
        autoComplete="off"
        inputMode={decimal ? 'decimal' : 'text'}
        aria-invalid={Boolean(erros[chave])}
        aria-describedby={erros[chave] ? `${id}-${chave}-erro` : undefined}
        onChange={(e) => {
          mudar(chave, e.target.value);
        }}
        onBlur={() => {
          if (chave === 'nome') mudar(chave, normalizarNome(campos[chave] ?? ''));
        }}
      />
      {erros[chave] ? (
        <p className="erro" id={`${id}-${chave}-erro`}>
          {erros[chave]}
        </p>
      ) : null}
    </div>
  );
  return (
    <>
      {novaFazenda ? (
        <section aria-label="Cadastrar fazenda">
          <h3>Cadastrar fazenda</h3>
          <EditorCadastro
            edicao={{ tipo: 'fazenda' }}
            fazendas={[]}
            usuarioId={p.usuarioId}
            organizacaoId={p.organizacaoId}
            volta={p.volta}
            cancelar={() => {
              setNovaFazenda(false);
            }}
            confirmado={(_, g) => {
              const f = {
                id: g.intencao.targetId,
                nome: normalizarNome(g.campos['nome'] ?? ''),
                fuso: g.campos['fuso'] ?? FUSO_PADRAO,
              };
              setCriadas((atual) => [...atual, f]);
              setCampos((atual) => ({ ...atual, fazenda: f.id }));
              setNovaFazenda(false);
              // O pai continua com nome/área digitados; a nova fazenda aparece no campo, sem criar talhão sozinho.
              requestAnimationFrame(() => {
                form.current?.querySelector<HTMLInputElement>('[name="nome"]')?.focus();
              });
            }}
          />
        </section>
      ) : null}
      <form ref={form} className={s.formulario} hidden={novaFazenda} onSubmit={enviar} noValidate>
        <fieldset disabled={travado}>
          {tipo === 'situacao' ? (
            <p>
              {campos['situacao'] === 'inativo'
                ? 'O talhão ficará disponível para consulta, sem novos usos.'
                : 'O talhão voltará a permitir novos usos.'}
            </p>
          ) : (
            <>
              {tipo === 'talhao' ? (
                <div className="campo" data-erro={erros['fazenda'] ? '' : undefined}>
                  <label htmlFor={`${id}-fazenda`}>Fazenda</label>
                  <select
                    name="fazenda"
                    id={`${id}-fazenda`}
                    value={campos['fazenda'] ?? ''}
                    aria-invalid={Boolean(erros['fazenda'])}
                    aria-describedby={erros['fazenda'] ? `${id}-fazenda-erro` : undefined}
                    onChange={(e) => {
                      mudar('fazenda', e.target.value);
                    }}
                  >
                    <option value="">Escolher fazenda</option>
                    {opcoes.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.nome}
                      </option>
                    ))}
                  </select>
                  {erros['fazenda'] ? (
                    <p className="erro" id={`${id}-fazenda-erro`}>
                      {erros['fazenda']}
                    </p>
                  ) : null}
                  <button
                    type="button"
                    className="link-acao"
                    onClick={() => {
                      setNovaFazenda(true);
                    }}
                  >
                    Cadastrar fazenda
                  </button>
                </div>
              ) : null}
              {campoTexto('nome', 'Nome')}
              {tipo === 'talhao' ? (
                campoTexto('area', 'Área declarada (ha)', true)
              ) : (
                <div className="campo">
                  <label htmlFor={`${id}-fuso`}>Fuso horário</label>
                  <select
                    name="fuso"
                    id={`${id}-fuso`}
                    value={campos['fuso']}
                    onChange={(e) => {
                      mudar('fuso', e.target.value);
                    }}
                  >
                    {fusos.map((f) => (
                      <option key={f} value={f}>
                        {f.replace('America/', '').replaceAll('_', ' ')}
                      </option>
                    ))}
                  </select>
                  {erros['fuso'] ? <p className="erro">{erros['fuso']}</p> : null}
                </div>
              )}
            </>
          )}
        </fieldset>
        {comando.mensagem ? (
          <div className={s.aviso} role="status">
            <p>{comando.mensagem}</p>
            {comando.sessao ? (
              <Link href={`/entrar?destino=${encodeURIComponent(p.volta)}`}>Entrar novamente</Link>
            ) : null}
          </div>
        ) : null}
        <div className={`rodape-acao ${s.acoes ?? ''}`}>
          <button type="button" className="botao" onClick={p.cancelar}>
            Voltar
          </button>
          {comando.pendente ? (
            <button
              type="button"
              className="botao botao-primario"
              disabled={comando.ocupado}
              aria-busy={comando.ocupado}
              onClick={() => {
                if (comando.naoLocalizado) comando.repetir();
                else void comando.consultar();
              }}
            >
              {comando.ocupado
                ? 'Aguarde…'
                : comando.naoLocalizado
                  ? 'Reenviar mesmo cadastro'
                  : 'Consultar recibo'}
            </button>
          ) : (
            <button
              type="submit"
              className="botao botao-primario"
              disabled={travado}
              aria-busy={comando.ocupado}
            >
              {comando.versaoAtual !== null ? 'Reaplicar minhas alterações' : titulo}
            </button>
          )}
        </div>
      </form>
    </>
  );
}
