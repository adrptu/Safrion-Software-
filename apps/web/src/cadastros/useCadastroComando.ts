'use client';

import type { ReciboContrato } from '@safrion/contracts';
import { useRef, useState } from 'react';
import { desfechoDaConsulta, desfechoDoEnvio, type Desfecho } from './intencao';
import {
  apagarFluxo,
  armazemLocal,
  atualDoFluxo,
  comTravaCadastro,
  gravarIntencao,
  guardarFalha,
  prepararCorrecao,
  type IntencaoGuardada,
} from './pendencias';

/** Uma tentativa só se encerra com recibo correspondente ou recusa certa do primeiro envio. */
export function useCadastroComando(
  usuarioId: string,
  organizacaoId: string,
  confirmado: (recibo: ReciboContrato, guardada: IntencaoGuardada) => void,
  inicial?: IntencaoGuardada,
) {
  const [pendente, setPendente] = useState<IntencaoGuardada | null>(inicial ?? null);
  const [ocupado, setOcupado] = useState(false);
  const trava = useRef(false);
  const [mensagem, setMensagem] = useState(
    inicial?.falha?.mensagem ??
      (inicial ? 'Há um envio sem confirmação. Consulte o recibo para continuar.' : ''),
  );
  const [naoLocalizado, setNaoLocalizado] = useState(false);
  const [sessao, setSessao] = useState(false);
  const [versaoAtual, setVersaoAtual] = useState<number | null>(null);
  const [falhaDePersistencia, setFalhaDePersistencia] = useState(false);

  function recuperar(g: IntencaoGuardada) {
    setPendente(g);
    setNaoLocalizado(false);
    setMensagem(
      g.falha?.tipo === 'corrigir'
        ? 'Nada deste pedido foi gravado. Corrija os dados antes de enviar um novo pedido.'
        : g.falha?.tipo === 'somente_consulta'
          ? 'O resultado anterior continua incerto. Este conteúdo não pode ser reenviado; consulte o recibo.'
          : 'Há um envio sem confirmação. Consulte o recibo para continuar.',
    );
  }
  function preservarFalha(g: IntencaoGuardada, falha: NonNullable<IntencaoGuardada['falha']>) {
    const salva = guardarFalha(armazemLocal(), usuarioId, organizacaoId, g, falha);
    recuperar(salva ?? { ...g, falha });
    setFalhaDePersistencia(!salva);
    if (!salva)
      setMensagem(
        'Não foi possível guardar a recuperação. Nenhum novo envio está liberado. Mantenha esta aba aberta e tente guardar novamente.',
      );
  }
  function aplicar(d: Desfecho, g: IntencaoGuardada) {
    setSessao(d.tipo !== 'resolvido' && d.sessao);
    if (d.tipo === 'corrigir') {
      preservarFalha(g, {
        tipo: 'corrigir',
        mensagem: d.mensagem,
        correlacao: d.correlacao,
      });
      return;
    }
    if (d.tipo === 'incerto' && d.bloqueioPermanente) {
      preservarFalha(g, { tipo: 'somente_consulta', ...d.bloqueioPermanente });
      return;
    }
    if (d.tipo === 'incerto') {
      // Um 404 posterior nunca remove a proibição de repetir o conteúdo.
      setMensagem(
        g.falha
          ? 'O resultado anterior continua incerto. Consulte o recibo; o reenvio deste conteúdo está bloqueado.'
          : d.mensagem,
      );
      setNaoLocalizado(!g.falha && d.naoLocalizado);
      return;
    }
    if (d.tipo === 'nao_gravado' && d.sessao) {
      setMensagem(
        'Sua sessão terminou. Seus dados estão guardados. Entre novamente para conferir e continuar.',
      );
      setNaoLocalizado(false);
      return;
    }
    // Um recibo correspondente continua autoritativo, inclusive depois da falha de um reenvio.
    if (!apagarFluxo(armazemLocal(), usuarioId, organizacaoId, g)) {
      setMensagem(
        'Resultado recebido, mas a limpeza local falhou. Consulte o recibo novamente antes de iniciar outro pedido.',
      );
      setNaoLocalizado(false);
      return;
    }
    setPendente(null);
    setNaoLocalizado(false);
    setFalhaDePersistencia(false);
    if (d.tipo === 'nao_gravado') {
      setMensagem(d.mensagem);
      return;
    }
    if (d.recibo.outcome === 'confirmed') {
      setMensagem('Cadastro confirmado.');
      confirmado(d.recibo, g);
    } else if (d.recibo.outcome === 'version_conflict') {
      setVersaoAtual(d.recibo.resultingVersion);
      setMensagem(
        `Outra pessoa alterou este registro. Versão atual: ${String(d.recibo.resultingVersion ?? 'indisponível')}. Seus campos foram preservados.`,
      );
    } else setMensagem(d.recibo.nextAction ?? 'Cadastro recusado. Confira os campos e tente novamente.');
  }
  async function exclusiva(g: IntencaoGuardada, executar: () => Promise<void>) {
    if (trava.current) return;
    trava.current = true;
    setOcupado(true);
    try {
      await comTravaCadastro(
        typeof navigator === 'undefined' ? undefined : navigator.locks,
        usuarioId,
        organizacaoId,
        g,
        executar,
      );
    } catch (erro: unknown) {
      setMensagem(
        erro instanceof Error
          ? erro.message
          : 'Não foi possível proteger este envio. Nenhum novo pedido foi iniciado.',
      );
    } finally {
      trava.current = false;
      setOcupado(false);
    }
  }
  /** Chamado apenas dentro da trava e depois de a intenção estar guardada. */
  async function postar(g: IntencaoGuardada, repeticao: boolean) {
    setMensagem('Enviando cadastro…');
    let d: Desfecho;
    try {
      const resposta = await fetch(`/api/v1/comandos/${g.intencao.commandType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: g.intencao.corpo,
      });
      const corpo: unknown = await resposta.json().catch(() => null);
      d = desfechoDoEnvio(resposta.status, corpo, g.intencao, repeticao);
    } catch {
      d = desfechoDoEnvio(0, null, g.intencao, repeticao);
    }
    aplicar(d, g);
  }
  function enviar(g: IntencaoGuardada) {
    if (trava.current || falhaDePersistencia || (pendente && pendente.falha?.tipo !== 'corrigir')) return;
    const origem = pendente;
    void exclusiva(origem ?? g, async () => {
      if (origem) {
        const preparo = prepararCorrecao(armazemLocal(), usuarioId, organizacaoId, origem, g);
        if (preparo.tipo === 'impedido') {
          setMensagem(preparo.mensagem);
          return;
        }
        recuperar(preparo.guardada);
        // Outra aba, ou uma interrupção antes do POST: consulta primeiro, nunca presume que não enviou.
        if (preparo.tipo === 'existente') return;
        await postar(preparo.guardada, false);
      } else {
        const existente = atualDoFluxo(armazemLocal(), usuarioId, organizacaoId, g);
        if (existente) {
          recuperar(existente);
          return;
        }
        if (!gravarIntencao(armazemLocal(), usuarioId, organizacaoId, g)) {
          setMensagem(
            'O navegador não conseguiu guardar o envio. Libere espaço ou armazenamento e tente novamente. Nada foi enviado.',
          );
          return;
        }
        recuperar(g);
        await postar(g, false);
      }
    });
  }
  async function retomar(repetir: boolean) {
    if (!pendente) return;
    const lembrada = pendente;
    await exclusiva(lembrada, async () => {
      let g = atualDoFluxo(armazemLocal(), usuarioId, organizacaoId, lembrada);
      if (!g) {
        setMensagem('Este envio mudou em outra aba ou não está disponível. Reabra a lista de cadastros.');
        setNaoLocalizado(false);
        return;
      }
      if (g.intencao.chave !== lembrada.intencao.chave) {
        recuperar(g);
        return;
      }
      // Uma falha de gravação do sinal deve ser recuperada antes de qualquer nova operação.
      if (lembrada.falha && !g.falha) {
        const salva = guardarFalha(armazemLocal(), usuarioId, organizacaoId, g, lembrada.falha);
        if (!salva) {
          preservarFalha(g, lembrada.falha);
          return;
        }
        g = salva;
        setFalhaDePersistencia(false);
      }
      setFalhaDePersistencia(false);
      setPendente(g);
      if (g.falha?.tipo === 'corrigir') {
        recuperar(g);
        return;
      }
      if (repetir) {
        if (!g.falha && naoLocalizado) await postar(g, true);
        else recuperar(g);
        return;
      }
      setMensagem('Consultando recibo…');
      let d: Desfecho;
      try {
        const r = await fetch(
          `/api/v1/intencoes/${g.intencao.commandType}/${encodeURIComponent(g.intencao.chave)}`,
          { cache: 'no-store' },
        );
        const corpo: unknown = await r.json().catch(() => null);
        d = desfechoDaConsulta(r.status, corpo, g.intencao);
      } catch {
        d = desfechoDaConsulta(0, null, g.intencao);
      }
      aplicar(d, g);
    });
  }
  return {
    pendente,
    ocupado,
    mensagem,
    sessao,
    versaoAtual,
    naoLocalizado,
    corrigivel: pendente?.falha?.tipo === 'corrigir' && !falhaDePersistencia,
    correlacao: pendente?.falha?.correlacao ?? pendente?.origem?.correlacao,
    falhaDePersistencia,
    enviar,
    consultar: () => retomar(false),
    repetir: () => {
      void retomar(true);
    },
  };
}
