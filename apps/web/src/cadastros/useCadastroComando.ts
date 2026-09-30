'use client';

import type { ReciboContrato } from '@safrion/contracts';
import { useRef, useState } from 'react';
import { desfechoDaConsulta, desfechoDoEnvio, type Desfecho } from './intencao';
import { apagarIntencao, armazemLocal, gravarIntencao, type IntencaoGuardada } from './pendencias';

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
    inicial ? 'Há um envio sem confirmação. Consulte o recibo para continuar.' : '',
  );
  const [naoLocalizado, setNaoLocalizado] = useState(false);
  const [sessao, setSessao] = useState(false);
  const [versaoAtual, setVersaoAtual] = useState<number | null>(null);

  function aplicar(d: Desfecho, g: IntencaoGuardada) {
    setSessao(d.tipo !== 'resolvido' && d.sessao);
    if (d.tipo === 'incerto') {
      setMensagem(d.mensagem);
      setNaoLocalizado(d.naoLocalizado);
      return;
    }
    // Sessão encerrada exige navegar para entrar: a intenção guardada conserva os campos nessa travessia.
    // Após entrar, a recuperação consulta o recibo antes do mesmo reenvio, sem criar chave nova.
    if (d.tipo === 'nao_gravado' && d.sessao) {
      setMensagem(
        'Sua sessão terminou. Seus dados estão guardados. Entre novamente para conferir e continuar.',
      );
      setNaoLocalizado(false);
      return;
    }
    apagarIntencao(armazemLocal(), usuarioId, organizacaoId, g.intencao.chave);
    setPendente(null);
    setNaoLocalizado(false);
    if (d.tipo === 'nao_gravado') {
      setMensagem(d.mensagem);
      return;
    }
    if (d.recibo.outcome === 'confirmed') {
      setMensagem('Cadastro confirmado.');
      confirmado(d.recibo, g);
      return;
    }
    if (d.recibo.outcome === 'version_conflict') {
      setVersaoAtual(d.recibo.resultingVersion);
      setMensagem(
        `Outra pessoa alterou este registro. Versão atual: ${String(d.recibo.resultingVersion ?? 'indisponível')}. Seus campos foram preservados.`,
      );
      return;
    }
    setMensagem(d.recibo.nextAction ?? 'Cadastro recusado. Confira os campos e tente novamente.');
  }

  async function postar(g: IntencaoGuardada, repeticao: boolean) {
    if (trava.current) return;
    trava.current = true;
    setOcupado(true);
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
    trava.current = false;
    setOcupado(false);
    aplicar(d, g);
  }

  function enviar(g: IntencaoGuardada) {
    if (trava.current || pendente) return;
    if (!gravarIntencao(armazemLocal(), usuarioId, organizacaoId, g)) {
      setMensagem(
        'O navegador não conseguiu guardar o envio. Libere espaço ou armazenamento e tente novamente. Nada foi enviado.',
      );
      return;
    }
    setPendente(g);
    setNaoLocalizado(false);
    void postar(g, false);
  }
  async function consultar() {
    if (!pendente || trava.current) return;
    const g = pendente;
    trava.current = true;
    setOcupado(true);
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
    trava.current = false;
    setOcupado(false);
    aplicar(d, g);
  }
  return {
    pendente,
    ocupado,
    mensagem,
    sessao,
    versaoAtual,
    naoLocalizado,
    enviar,
    consultar,
    repetir: () => {
      if (pendente && naoLocalizado) void postar(pendente, true);
    },
  };
}
