// PCM simplificado S4 · app × manutenção sem navegador (ma_app_test.py monta: perfis + cenário + regras da manutenção + JS do app + este arquivo).
// Cada caso parte do cenário inicial (CEN0) e confere o observável do aceite (AC-PCM-27 e §3.7 da ESPECIFICACAO). Saída: uma linha JSON.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const C = () => cenClone(CEN0);
// o que a tela faz: manMudar sobre uma cópia (erro não grava); aqui sem tela, a mesma semântica
const muda = (c, fn) => { const cc = cenClone(c); let r; try { r = fn(cc.man, cc) || {}; } catch (e) { r = { erro: String(e.message || e) }; } if (!r.erro && !r.nada) Object.assign(c, cc); return r; };
const app = (c, cmd, args, por, chave) => muda(c, (m, cc) => manAppCmd(cc, { chave: chave || manChave(), cmd, args, por }));
const OT = g2pf('Otávio');

caso('perfil e fila', () => {
  const c = C();
  ok('§3.7 · o app abre como Marcos (c.app.usuario) e o Ver como só troca c.app.usuario', mbUsuario(c) === 'Marcos' && c.app.usuario === 'Marcos', c.app);
  ok('AC-PCM-27 · Zé vê a OM-0233 na Minha fila; Marcos não vê OM', mbOmsDe(c.man, 'Zé').map(o => o.id).join() === 'OM-0233' && mbOmsDe(c.man, 'Marcos').length === 0, mbOmsDe(c.man, 'Zé').map(o => o.id));
  const d = C(); manLiberar(d.man, 'OM-0234', true, OT, { executante: 'Zé', tempo: '5' });   // a OM-0228 (João) já está Liberadas no seed
  const f = mbOmsDe(d.man, 'Zé').map(o => o.id);
  ok('§3.7 · Minha fila do Zé pela janela e depois pela criticidade (OM-0233 23/09 antes da OM-0234 28/09); a OM-0228 (João) não entra', f.join() === 'OM-0233,OM-0234', f);
  ok('§3.7 · passo do cartão: Liberadas → "Iniciar serviço"; Em execução com teste reprovado → "Teste pendente"', mbOmPasso(d.man, d.man.oms['OM-0234']).t === 'Iniciar serviço' && mbOmPasso(d.man, d.man.oms['OM-0233']).chip[0] === 'Teste pendente', [mbOmPasso(d.man, d.man.oms['OM-0233'])]);
});

caso('máquina herdada', () => {
  const c = C(); const k = mbAtvCurtos(c, c.man, 'Marcos');
  ok('MB-09 · Marcos: máquinas herdadas da OS-0421 alocada hoje (Trator 03 primeiro, depois o Pulverizador PJ-3030)', k.ids.join() === 'a03,a05' && k.os === 'OS-0421' && /OS-0421/.test(k.de), k);
  const z = mbAtvCurtos(c, c.man, 'Zé');
  ok('MB-09 · Zé: a máquina da OM dele (Trator T1)', z.ids.join() === 'a01', z);
  ok('AC-PCM-27 · MB-09 mostra "Não opere" com o Trator T1 bloqueado (motivo e OM)', /^Não opere · bloqueado/.test(mbCond(c.man.ativos.a01).t) && /OM-0233/.test(mbCond(c.man.ativos.a01).t) && mbCond(c.man.ativos.a03).t === 'Apto para operar', mbCond(c.man.ativos.a01));
});

caso('abastecimento pelo app', () => {
  const c = C(); const n0 = c.man.abast.length;
  const d = { aid: 'a03', tq: 'Comboio CB-01 · D-118', vol: '120', leit: '5126', op: 'Marcos', evid: 'foto do tíquete (simulada)', data: c.man.hoje, os: 'OS-0421' };
  ok('matriz · o operador (Marcos) registra achado, leitura e abastecimento; quem não está no cadastro de operadores, não', manPode(c.man, 'Marcos', 'registrar') === '' && !!manPode(c.man, 'Rui', 'registrar'), manPode(c.man, 'Rui', 'registrar'));
  const r = app(c, 'abastecer', { d }, 'Marcos', 'kab1'); const r2 = app(c, 'abastecer', { d }, 'Marcos', 'kab1');
  ok('MB-09 · com sinal grava já pela mesma função da web (AB-1043, por Marcos, leitura 5.126 h) e o toque repetido com a mesma chave não duplica', !r.erro && r.id === 'AB-1043' && c.man.abast.length === n0 + 1 && r2.nada && r2.repetido && c.man.ativos.a03.leit.val === 5126 && c.man.abast[n0].por === 'Marcos', [r, r2]);
  const e = app(c, 'abastecer', { d: Object.assign({}, d, { vol: '' }) }, 'Marcos');
  ok('MB-09 · faltou o volume: recusa com o campo e nada grava', e.erro && /volume/.test(e.erro) && c.man.abast.length === n0 + 1, e);
});

caso('sem sinal: abastecer e reenvio', () => {
  const c = C(); muda(c, (m, cc) => mbSinal(cc, false)); const n0 = c.man.abast.length;
  const d = { aid: 'a05', tq: 'Comboio CB-01 · D-118', vol: '80', leit: '1550', op: 'Marcos', evid: '', data: c.man.hoje };
  const r = app(c, 'abastecer', { d }, 'Marcos', 'kof1'); const r2 = app(c, 'abastecer', { d }, 'Marcos', 'kof1');
  ok('§3.7 · sem sinal o abastecimento fica no aparelho (fila com a chave do aparelho), o servidor não muda e o duplo toque não duplica a fila',
    r.fila && c.man.abast.length === n0 && c.app.manFila.length === 1 && c.app.fila.join() === 'MAN|kof1' && r2.nada && c.app.manFila.length === 1, [r, r2, c.app.fila]);
  const p = manAppProj(c);
  ok('§3.7 · a cópia do aparelho mostra o lançamento e a leitura nova (o operador vê o que fez)', p.abast.length === n0 + 1 && p.ativos.a05.leit.val === 1550 && c.man.ativos.a05.leit.val !== 1550, p.ativos.a05.leit);
  const s = muda(c, (m, cc) => mbSinal(cc, true));
  ok('AC-PCM-27 · na volta do sinal a fila vai uma vez só: 1 lançamento no servidor, fila vazia e recibo do envio', !s.erro && c.man.abast.length === n0 + 1 && !c.app.manFila.length && !c.app.fila.length && /1 registro da manutenção enviado/.test(s.msg) && /recibo REC-7742/.test(s.msg), s);
  const s2 = muda(c, (m, cc) => mbSinal(cc, true)); c.app.manFila = [{ chave: 'kof1', cmd: 'abastecer', args: { d }, por: 'Marcos', om: '', rv: null, fase: null, at: '10:00', desc: 'x' }];
  const s3 = muda(c, (m, cc) => manAppSinal(cc));
  ok('AC-PCM-27 · reenvio da mesma chave (fila repetida) não duplica: o recibo da chave já existe', c.man.abast.length === n0 + 1 && s3.n === 0 && !s3.conf.length && /Nada pendente/.test(s2.msg), [s2, s3]);
});

caso('sem sinal: OM-0233 do começo ao fim', () => {
  const c = C(); muda(c, (m, cc) => mbSinal(cc, false));
  const a = app(c, 'tentativa', { om: 'OM-0233', i: 3, r: 'Aprovado', evid: 'foto (simulada)' }, 'Zé');
  const b = app(c, 'concluir', { om: 'OM-0233', leit: '4320', horas: '6,5', apl: {} }, 'Zé');
  const p = manAppProj(c);
  const d = app(c, 'apto', { om: 'OM-0233' }, 'Zé');
  ok('AC-PCM-27 · sem sinal: teste, concluir e declarar apto ficam no aparelho (validados na cópia), o servidor segue Em execução', a.fila && b.fila && d.fila && c.app.manFila.length === 3 && c.man.oms['OM-0233'].etapa === 'Em execução' && p.oms['OM-0233'].etapa === 'Em conferência', [a, b, d]);
  const s = muda(c, (m, cc) => mbSinal(cc, true));
  ok('AC-PCM-27 · na volta: os 3 entram em ordem; OM-0233 Em conferência, Trator T1 apto (por Zé), nenhum conflito', !s.erro && c.man.oms['OM-0233'].etapa === 'Em conferência' && c.man.ativos.a01.cond === 'Apto' && /Zé/.test(c.man.oms['OM-0233'].aptidao.por) && !(c.man.appConf || []).length && /3 registros da manutenção enviados/.test(s.msg), [s, c.man.appConf]);
  const e = app(C(), 'tentativa', { om: 'OM-0233', i: 3, r: 'Aprovado', evid: 'foto' }, 'Marcos');
  ok('matriz · Marcos não executa a OM-0233: "Ação de Zé, executante"', e.erro && /Ação de Zé, executante/.test(e.erro), e);
  const x = C(); x.man.oms['OM-0233'].executante = 'João';
  ok('MB-09det · Teste desabilitado com o motivo para quem não tem a habilidade (João)', /Testar reparo/.test(manPode(x.man, 'João', 'teste', { o: x.man.oms['OM-0233'] })), manPode(x.man, 'João', 'teste', { o: x.man.oms['OM-0233'] }));
  const y = C(); muda(y, (m, cc) => mbSinal(cc, false)); const f = app(y, 'concluir', { om: 'OM-0233', leit: '4320', horas: '6,5' }, 'Zé');
  ok('§3.7 · sem sinal a regra é a mesma: concluir sem teste aprovado é recusado no campo e nada vai para a fila', f.erro && /teste aprovado/.test(f.erro) && !y.app.manFila.length, f);
});

caso('sem sinal: conflito', () => {
  const c = C(); muda(c, (m, cc) => mbSinal(cc, false));
  app(c, 'tentativa', { om: 'OM-0233', i: 3, r: 'Aprovado', evid: 'foto (simulada)' }, 'Zé'); app(c, 'concluir', { om: 'OM-0233', leit: '4320', horas: '6,5' }, 'Zé');
  const rv0 = c.man.oms['OM-0233'].rv || 0;
  const o1 = muda(c, (m) => manRetirada(m, 'OM-0233', 0, 'Garantia', 'Concessionária Case IH', OT));   // no escritório, Otávio dá destino à bomba usada
  const s = muda(c, (m, cc) => mbSinal(cc, true)); const o = c.man.oms['OM-0233'];
  ok('AC-PCM-27 · OM mudada no escritório: os registros do app viram "Conflito a resolver · Otávio" e nada é aplicado em silêncio', !o1.erro && o.rv === rv0 + 1 && o.etapa === 'Em execução' && (c.man.appConf || []).length === 2 && o.conflitoApp === 2
    && manSelos(c.man, o).some(x => x.t === 'Conflito a resolver' && x.dono === 'Otávio') && /2 conflitos a resolver/.test(s.msg) && !c.app.manFila.length, [s, c.man.appConf, o.conflitoApp]);
  const z = muda(c, (m) => manAppConfAplicar(m, 'CA-001', g2pf('Zé')));
  ok('AC-PCM-27 · resolver o conflito é do Otávio (Zé recusado)', z.erro && /Ação do Otávio/.test(z.erro), z);
  const dz = muda(c, (m) => manAppConfDescartar(m, 'CA-002', '', OT));
  ok('AC-PCM-27 · descartar pede motivo', dz.erro && /motivo/.test(dz.erro), dz);
  const ap = muda(c, (m) => manAppConfAplicar(m, 'CA-001', OT)); const ap2 = muda(c, (m) => manAppConfAplicar(m, 'CA-002', OT));
  ok('AC-PCM-27 · Otávio aplica sobre o estado de agora (mesma função, autor Zé): teste aprovado e OM-0233 Em conferência; o selo sai', !ap.erro && !ap2.erro && c.man.oms['OM-0233'].etapa === 'Em conferência' && c.man.oms['OM-0233'].exec.por.indexOf('Zé') === 0
    && !c.man.oms['OM-0233'].conflitoApp && !manSelos(c.man, c.man.oms['OM-0233']).some(x => x.t === 'Conflito a resolver') && manAppConfAbertos(c.man).length === 0, [ap, ap2]);
  const r2 = muda(c, (m) => manAppConfAplicar(m, 'CA-001', OT));
  ok('AC-PCM-27 · conflito já decidido não é aplicado de novo', r2.erro && /não encontrado/.test(r2.erro), r2);
});

caso('MB-04 → achado', () => {
  const c = C(); const n0 = Object.keys(c.man.achados).length;
  const d = { aid: 'a03', origem: 'Relato', comp: 'Hidráulico', sint: 'Vazamento no comando da barra', crit: 'Média', sug: 'Restrito', evid: '1 foto (simulada)', os: 'OS-0421' };
  const r = app(c, 'achado', { d }, 'Marcos', 'kac1'); const q = c.man.achados[r.id];
  ok('AC-PCM-27 · MB-04 Equipamento com máquina grava achado de origem Relato, ligado à O.S., visível em Sem ordem (SM-0153)', !r.erro && r.id === 'SM-0153' && q.estado === 'Sem ordem' && q.os === 'OS-0421' && q.origem === 'Relato' && q.por === 'Marcos' && Object.keys(c.man.achados).length === n0 + 1 && /ligado à OS-0421/.test(r.msg), [r, q]);
  const r2 = app(c, 'achado', { d: Object.assign({}, d, { sint: 'Pingando de novo' }) }, 'Marcos');
  ok('§3.2 · a mesma máquina e componente com achado aberto pergunta Somar ou Registrar novo (nada grava)', r2.nada && r2.rep === 'SM-0153' && Object.keys(c.man.achados).length === n0 + 1, r2);
  const r3 = app(c, 'achado', { d: Object.assign({}, d, { sint: 'Pingando de novo', rep: 'somar' }) }, 'Marcos');
  ok('§3.2 · Somar acrescenta a ocorrência ao SM-0153', !r3.erro && c.man.achados['SM-0153'].oc.length === 2, r3);
  const y = C(); muda(y, (m, cc) => mbSinal(cc, false)); const f = app(y, 'achado', { d }, 'Marcos', 'kac2');
  const s = muda(y, (m, cc) => mbSinal(cc, true));
  ok('AC-PCM-27 · sem sinal o achado fica no aparelho e entra uma vez na volta (SM-0153 em Sem ordem)', f.fila && !s.erro && y.man.achados['SM-0153'] && y.man.achados['SM-0153'].estado === 'Sem ordem' && !y.app.manFila.length, [f, s]);
});

print(JSON.stringify(R));
