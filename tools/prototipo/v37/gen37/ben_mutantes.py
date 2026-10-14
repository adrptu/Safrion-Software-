# -*- coding: utf-8 -*-
"""Beneficiamento BEN-1 · mutantes (ESPECIFICACAO.md §11.4): cada mutante, sozinho, tem de derrubar ao menos uma verificação de ben_unit.js.
Aplica a troca no texto do motor (o mesmo de ben_unit_test.py) e roda os testes no node, sem navegador.
Uso: SAFRION_DADOS=sintetico python3 ben_mutantes.py   → uma linha por mutante e 'RESULTADO: OK n/n' (todos mortos)."""
import os, sys, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ben_unit_test import motor, node
M = [
 ('M01 elegibilidade da entrada desligada (R-A03)', "  const Q = benBase(c, L);\n  if (Q.q === 'Em inspeção')", "  const Q = { q: 'Liberado' };\n  if (Q.q === 'Em inspeção')"),
 ('M02 R-A07 sem a tolerância', "if (prCmp(tot, prSoma([proc, tol])) > 0)", "if (prCmp(tot, proc) > 0)"),
 ('M03 Fechar sem cenPodeEncerrar (custódia)', "const pe = cenPodeEncerrar(c, id); if (pe) throw new Error(pe);", ""),
 ('M04 Fechar sem as etapas exigidas', "if (et.length) throw new Error('Etapa exigida pendente", "if (false) throw new Error('Etapa exigida pendente"),
 ('M05 R-C02 caixas acima da custódia desligada', "if (cx > cust + 1e-9) throw new Error('Caixas acima da custódia", "if (false) throw new Error('Caixas acima da custódia"),
 ('M07 R-E05 sem comparar classe', "if (ped.classe !== L.classe) return 'Classe '", "if (false) return 'Classe '"),
 ('M08 R-E02 Liberar com Não conforme', "return res.sit === 'Conforme' ? ['Liberar', 'Manter bloqueio', 'Destinar']", "return true ? ['Liberar', 'Liberar como classe atingida', 'Manter bloqueio', 'Destinar']"),
 ('M08b R-E02 recusa do Liberar não conforme desligada', "if (dec === 'Liberar' && res && res.sit !== 'Conforme') throw", "if (false) throw"),
 ('M09 R-F02 sem o valor absoluto', "const sai = prSoma([prod, outro, desc, perda]); const dif = prSub(proc, sai); const faixa = benFaixa(proc, r); const ad = benAbs(dif);", "const sai = prSoma([prod, outro, desc, perda]); const dif = prSub(proc, sai); const faixa = benFaixa(proc, r); const ad = dif;"),
 ('M10 R-G06 sem o teto', "const porPct = prCmp(lp, r.par.alcada_kg) <= 0;", "const porPct = true;"),
 ('M11 R-G06 desligada', "const pct = prCmp(proc, 0) > 0 ? prDiv(prMul(ad, 100), proc) : 0; const passa = prCmp(ad, lim) > 0;", "const pct = prCmp(proc, 0) > 0 ? prDiv(prMul(ad, 100), proc) : 0; const passa = false;"),
 ('M12 R-F07 sem a alçada de dif0', "if (!b0.dentro && b1.dentro && al.passa &&", "if (false &&"),
 ('M13 perda identificada sem exigir evidência', "if (!String(k.ticket || '').trim()) throw new Error('Sem pesagem", "if (false) throw new Error('Sem pesagem"),
 ('M14 estorno que não devolve caixas', "x.it.consumido -= x.p.qtd; x.it.custodia += x.p.qtd;", ""),
 ('M15 estorno que não derruba a conferência', "if (o.ben.conf) { o.ben.conf = null; ca.push('conferência'); }", ""),
 ('M16 balanço somando o registro estornado', "function benValidos(o) { return (o.ben.sai || []).filter(s => !s.estorno); }", "function benValidos(o) { return (o.ben.sai || []); }"),
 ('M17 ID de lote olhando só os lotes', "Object.keys(P.lotes).forEach(ve); Object.values(c.ordens || {}).forEach(o => ((o.ben && o.ben.sai) || []).forEach(s => ve(s.lote)));", "Object.keys(P.lotes).forEach(ve);"),
 ('M18 chave (recibo) desligada', "function benRecibo(c, k, nome, imp) { if (!k || !k.chave) return null;", "function benRecibo(c, k, nome, imp) { return null;"),
 ('M19 versão esperada desligada', "function benVer(o, k) { if (k &&", "function benVer(o, k) { if (false &&"),
 ('M20 liberar sem o evento CMD-42', "benHist(o, quem, 'Versão ' + o.versao + ' da ordem autorizada (CMD-42)',", "(()=>0)(o, quem, 'Versão ' + o.versao + ' da ordem autorizada (CMD-42)',"),
 ('M21 número da REQ pela contagem (liberação e complemento: benReservaCx; o M21b da rodada 2 fundiu-se a este)', "if (!x) { const rid = cenProxId(c, 'reqs', 'REQ', 41);", "if (!x) { const rid = 'REQ-' + (41 + Object.keys(c.reqs).length);"),
 ('M23 R-E05 sem o limite do disponível', "if (prCmp(kg, S.disp) > 0) throw new Error('Acima do disponível", "if (false) throw new Error('Acima do disponível"),
 ('M24 fechar libera o lote (R-E01)', "q0: 'Em inspeção', cond: '', origem: ents.map", "q0: 'Liberado', cond: '', origem: ents.map"),
 ('M25 carência não herdada pela genealogia', "if (x.lote) out.push.apply(out, prOrigCampo(c, P.lotes[x.lote], vis)); else if (x.os) out.push(x);", "if (x.os) out.push(x);"),
 ('M26 liberar lote sem perfil (prLiberarLote)', "const quem = cenExigeUm(ator, ['qualidade', 'agronomo'], 'Liberar o lote ' + lid);", "const quem = 'Qualidade (Marta)';"),
 ('M27 em processo antes do Iniciar (BEN-D15)', "function benEmProc(o) { if (o.etapa !== 'Em execução' || o.ben.conc) return 0;", "function benEmProc(o) { if (o.etapa === 'Encerradas' || o.ben.conc) return 0;"),
 # revisão adversarial de 09/10 (BEN-REV-01..09 e S4): cada correção e cada regra sem proteção ganha um mutante
 ('M28 REV-01 decisões no lote preso numa ordem liberada', "  if (benPrende(c, L)) return [];", "  if (false) return [];"),
 ('M29 REV-01 benDecidir sem a trava da ordem liberada', "const pr = benPrende(c, L); if (pr) throw", "const pr = null; if (pr) throw"),
 ('M30 REV-01/02 Fechar sem reconferir o físico das entradas', "if (prCmp(f, e.kg) < 0) throw new Error('Fechar recusado", "if (false) throw new Error('Fechar recusado"),
 ('M31 REV-02 estorno de carga com o lote em processo', "const imp = prEstornoImpede(c, g); if (imp) throw new Error(imp);", ""),
 ('M32 REV-03 avaria no local de processo sem liberação', "function prLibProc(c, L) { if (!L ||", "function prLibProc(c, L) { return false; if (!L ||"),
 ('M33 REV-04 Reabrir zera a diferença declarada', "benBalMudou(o, quem); o.ben.dif0r = d0;", "benBalMudou(o, quem); o.ben.dif0r = null;"),
 ('M34 REV-04 Concluir depois de reabrir sem a gestão', "if (al.passa && !(typeof g2papel === 'function' && g2papel(ator, 'gestor'))) { o.ben.corrigido = true;", "if (false) { o.ben.corrigido = true;"),
 ('M35 REV-04 correção na conferência só com o dif0 vigente', "if (!ok(a)) return ok(b) ? b : null; if (!ok(b)) return a; return prCmp(benAbs(a), benAbs(b)) >= 0 ? a : b; }", "return ok(a) ? a : (ok(b) ? b : null); }"),
 ('M36 REV-05 ordem com 0 caixa', "if (cx < 1 && (r.saidas", "if (false && (r.saidas"),
 ('M37 REV-08 ordem no local do lote, não no da linha', "const lloc = ((BENC.linhas || {})[(r.ativos || [])[0]]) || Ls[0].local;", "const lloc = Ls[0].local;"),
 ('M38 REV-09 entrada parcial aceita', "if (prCmp(ents[i].kg, fis) !== 0) throw new Error('A ordem leva o lote inteiro", "if (prCmp(ents[i].kg, fis) > 0) throw new Error('A ordem leva o lote inteiro"),
 ('M39 REV-09 carga nova soma no lote da ordem', "&& !(typeof benOrdemAberta === 'function' && benOrdemAberta(c, x.id))", ""),
 ('M40 REV-07 decisão do lote sem perfil', "const quem = cenExigeUm(ator, BEN_QUAL, dec + ' · ' + lid);", "const quem = 'Marta (qualidade)';"),
 ('M41 REV-07 Fechar sem perfil', "const quem = cenExige(ator, 'producao', 'Fechar a ' + id);", "const quem = 'Igor (responsável de produção)';"),
 ('M42 REV-07 lote em duas ordens', "const ob = benOrdemAberta(c, L.id); if (ob) throw new Error(L.id + ' já está na '", "const ob = null; if (ob) throw new Error(L.id + ' já está na '"),
 ('M43 REV-07 fazendas misturadas', "if (fz.length > 1) throw new Error('Entradas de fazendas diferentes", "if (false) throw new Error('Entradas de fazendas diferentes"),
 ('M44 REV-07 lote reservado entra na ordem', "if (prCmp(prResLote(c, L.id), 0) > 0) return { t: L.id + ' reservado", "if (false) return { t: L.id + ' reservado"),
 ('M45 REV-07 entrada acima do físico', "if (kg !== undefined && kg !== null && prCmp(kg, fis) > 0) return", "if (false) return"),
 ('M46 REV-07 Retirar sem versão esperada', "benRecibo(c, k, 'benRetirar', imp); if (ja) return ja; benVer(o, k);", "benRecibo(c, k, 'benRetirar', imp); if (ja) return ja;"),
 ('M47 REV-07 Não conforme sem observação', "if (sit === 'Não conforme' && !ob) throw new Error", "if (false) throw new Error"),
 ('M48 REV-07 correção na conferência sem motivo', "if (!String(k.motivo || '').trim()) throw new Error('Correção na conferência: informe o motivo.');", ""),
 ('M49 REV-07 Concluir sem Produto', "if (!benValidos(o).some(s => s.fluxo === 'Produto' && s.classe)) throw", "if (false) throw"),
 ('M50 REV-07 justificar dentro da faixa', "if (b.dentro) throw new Error('Diferença ' + benKg(b.dif) + ' dentro da faixa", "if (false) throw new Error('Diferença ' + benKg(b.dif) + ' dentro da faixa"),
 ('M51 REV-07 Iniciar em A liberar', "if (o.etapa !== 'Liberadas') throw new Error(o.etapa === 'A liberar' ?", "if (o.etapa !== 'Liberadas' && o.etapa !== 'A liberar') throw new Error(o.etapa === 'A liberar' ?"),
 ('M52 REV-07 reclassificar sem motivo', "if (dec === 'Reclassificar' && !mot) throw", "if (false) throw"),
 ('M53 REV-07 bruto menor ou igual à tara', "if (prCmp(liq, 0) <= 0) throw new Error('Bruto '", "if (false) throw new Error('Bruto '"),
 ('M54 REV-07 Produto sem classe', "if ((def.classes || []).indexOf(k.classe) < 0) throw new Error('Escolha a classe: '", "if (false) throw new Error('Escolha a classe: '"),
 ('M55 S4 Conferir sem versão esperada', "if (o.ben.conf) throw new Error('Já feito: balanço conferido por ' + o.ben.conf.quem + '.'); benVer(o, k);", "if (o.ben.conf) throw new Error('Já feito: balanço conferido por ' + o.ben.conf.quem + '.');"),
 ('M56 S4 versão antes do "já feito" (toque repetido vira conflito)', "const quem = cenExige(ator, 'conferente', 'Conferir o balanço da ' + id); const o = benO(c, id);", "const quem = cenExige(ator, 'conferente', 'Conferir o balanço da ' + id); const o = benO(c, id); benVer(o, k);"),
 ('M57 S4 recusa do Liberar lote chama fruta de campo de lote do beneficiamento', "if (L.insp) throw new Error(lid + (L.benef ? ' é lote do beneficiamento (' + L.benef + ')' : ' tem a inspeção ' + L.insp)", "if (L.insp) throw new Error(lid + (true ? ' é lote do beneficiamento (' + L.benef + ')' : ' tem a inspeção ' + L.insp)"),
 # integração BEN na branch única (09/10): achados dos revisores
 ('M58 caixas da ordem nova reduzidas ao livre (a falta some do planejamento; rodada 1, BEN-D23)', "return { sug, livre, cx: sug }; }", "return { sug, livre, cx: livre >= 1 && sug > livre ? livre : sug }; }"),
 ('M59 cancelar fora de A liberar (reserva e entrega soltas)', "if (o.etapa !== 'A liberar') throw new Error('Cancele só em A liberar", "if (false) throw new Error('Cancele só em A liberar"),
 ('M60 cancelar sem motivo', "if (!mot) throw new Error('Informe o motivo do cancelamento.');", ""),
 ('M61 ordem cancelada continua prendendo o lote', "o.id !== fora && o.etapa !== 'Encerradas' && o.etapa !== 'Canceladas' &&", "o.id !== fora && o.etapa !== 'Encerradas' &&"),
 ('M63 falta de caixa sem a nota a conferir como saída (BEN-D23)', "benNfCx(c).forEach(nf => F.push(", "[].forEach(nf => F.push("),
 ('M64 nota de caixa já conferida continua oferecida como saída', "return (BENC.nfcx || []).filter(n => !feitas[n.rid]); }", "return (BENC.nfcx || []); }"),
 ('M65 complemento (e liberação) sem reserva no Estoque (rodada 1, S3)', "l.reservado += p.qtd; x.it.solicitado += p.qtd;", "x.it.solicitado += p.qtd;"),
 ('M66 complemento em outro lote troca o lote do item (BEN-REV-20261009-03)', "if (um) return [{ lote: um, qtd: n, x: linha(um) }];", "if (um) return [{ lote: um, qtd: n, x: (L && L[0] && !linha(um)) ? (L[0].it.lote = um, L[0]) : linha(um) }];"),
 ('M67 recusa por custódia sem a saída (complemento da ordem)', "'. Peça mais caixas na ordem (\"Pedir mais caixas\"); '", "'. Peça a entrega no Estoque; '"),
 ('M68 comando sobre ordem Cancelada vira "Já feito" (rodada 1, S4)', "function benViva(o, verbo) { if (o.etapa !== 'Canceladas') return;", "function benViva(o, verbo) { return;"),
 # BEN-REV-20261009-03 (S2): linha por lote no complemento; consumo, estorno e devolução no lote de origem
 ('M69 consumo sem as partes por lote (tudo na linha mais antiga)', "const q = Math.min(rest, x.it.custodia); if (!(q > 1e-9)) return;", "const q = x === T.L[0] ? rest : 0; if (!(q > 1e-9)) return;"),
 ('M70 estorno no lote da REQ da liberação, sem as partes do consumo', "function benPartes(c, o, s) { if ((s.cons || []).length) return s.cons;", "function benPartes(c, o, s) { const i1 = benReqItem(c, o); return [{ req: o.req, lote: i1.lote, qtd: s.cx, mv: s.mv || '' }];"),
 ('M71 Fechar olha só a REQ da liberação (custódia do complemento esquecida)', "const rs = Object.values(c.reqs || {}).filter(x => x.os === id && x !== r);", "const rs = [];"),
 ('M72 complemento ignora o lote das linhas da ordem (abre REQ nova no maior lote)', "const ordem = (L || []).map(x => x.it.lote).filter((v, i, a) => a.indexOf(v) === i).concat(", "const ordem = [].concat("),
 ('M62 cancelar sem perfil', "const quem = cenExigeUm(ator, ['producao', 'gestor'], 'Cancelar a ' + id);", "const quem = 'Igor (responsável de produção)';"),
 ('M73 recuperação conta a custódia inteira de qualquer ordem como sobra (rodada 2, S2)', ".map(b => ({ b, n: benCxSobra(c, b) }))", ".map(b => ({ b, n: Math.floor(benCxTot(c, b).cust + 1e-9) }))"),
 ('M74 sobra de ordem em execução ignora o que falta registrar', "function benKgAberto(o) { if (!benEh(o) || BEN_ABERTA.indexOf(o.etapa) < 0) return 0;", "function benKgAberto(o) { if (!benEh(o) || o.etapa !== 'Liberadas') return 0;"),
 ('M75 sobra com a fração vendável (subestima as caixas que a ordem usa)', "return prCmp(kg, 0) > 0 ? Number((prM(kg) + m - 1n) / m) : 0; }", "return prCmp(kg, 0) > 0 ? benCaixas(kg, benRota(o.ben.rota)) : 0; }"),
 ('M76 falta de caixa em ordem liberada manda Cancelar a ordem', "const fase = !o || o.etapa === 'A liberar' ? 'lib' : (o.etapa === 'Em conferência' ? 'conf' : 'exec');", "const fase = 'lib';"),
 # integração BEN, rodada 3 (BEN-D33..D35): cada regra nova tem o seu mutante; M87, M88 e M92 são da tela (tecla segurada, Esc e revalidação
 # do atalho) e ficam com o ben_fluxo_test (teclado T13-T16 e sobra S3/S4), que reprova sem a regra
 ('M77 sobra em conferência = a custódia inteira (BEN-D32 antiga)', "function benKgAberto(o) { if (!benEh(o) || BEN_ABERTA.indexOf(o.etapa) < 0) return 0;", "function benKgAberto(o) { if (!benEh(o) || ['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) return 0;"),
 ('M78 teto pelo piso (A1 da lente: ⌊kg ÷ 10⌋)', "return prCmp(kg, 0) > 0 ? Number((prM(kg) + m - 1n) / m) : 0; }", "return prCmp(kg, 0) > 0 ? Number(prM(kg) / m) : 0; }"),
 ('M79 a própria ordem como fonte (A6 da lente)', ".filter(b => b.id !== (o && o.id)).map(b => ({ b, n: benCxSobra(c, b) }))", ".map(b => ({ b, n: benCxSobra(c, b) }))"),
 ('M80 devolução sem divisão (tudo livre)', "  return { livre, volta: q - livre, disp: livre }; }", "  return { livre: q, volta: 0, disp: q }; }"),
 ('M81 "a entregar" ignora o dispensado', "return Math.max(0, it.solicitado - (it.dispensado || 0) - it.consumido - it.custodia); }", "return Math.max(0, it.solicitado - it.consumido - it.custodia); }"),
 ('M82 livre de um lote só', "function benLivreCx(c) { return benLotesCx(c).reduce((a, x) => a + x.livre, 0); }", "function benLivreCx(c) { return (benLotesCx(c)[0] || { livre: 0 }).livre; }"),
 ('M83 liberação e complemento sem dividir entre lotes', "if (um) return [{ lote: um, qtd: n, x: linha(um) }];", "if (um) return [{ lote: um, qtd: n, x: linha(um) }]; return null;"),
 ('M84 Fechar sem baixar a reserva não entregue', "if (ow > 1e-9) { l.reservado -= ow;", "if (false) { l.reservado -= ow;"),
 ('M85a entrega acima da reserva própria e do livre (usa a reserva de outra requisição)', "if (qtd > own + cenDisp(l) + 1e-9) throw", "if (false) throw"),
 ('M85b entrega baixa a reserva agregada (Math.max, sem a reserva própria)', "l.reservado = Math.max(0, l.reservado - Math.min(qtd, own));", "l.reservado = Math.max(0, l.reservado - qtd);"),
 ('M86 pré-preenchido da devolução = a custódia', "const p = benSobraLinhas(c, o).find(y => y.rid === x.rid); return p ? p.qtd : 0; }", "return Math.floor(x.it.custodia + 1e-9); }"),
 ('M89 falta pela necessidade da rota (reaplica a fração vendável; falso "Faltam N")', "return Math.max(0, Math.min(benCxUsoMax(o), T.sol - ((o.ben && o.ben.cxRepos) || 0) - cons) - T.cust - T.pend); }", "return Math.max(0, benCaixas(benKgAberto(o), benRota(o.ben.rota)) - T.cust - T.pend); }"),
 ('M90 entrega sem a trava física (estoque negativo depois do ajuste)', "if (qtd > l.fisico - l.quarentena + 1e-9) throw new Error('O lote ' + it.lote + ' não tem '", "if (false) throw new Error('O lote ' + it.lote + ' não tem '"),
 ('M91 gancho da devolução falha aberto sem o ben.js (devolve tudo ao livre em silêncio)', "if (ben && typeof benSobraDev !== 'function') throw new Error('Devolução de ' + prod + ' da ' + rid + ' (' + r.os + '): regra do beneficiamento ausente nesta página; nada foi gravado.'); const dv = ben ? benSobraDev(c, o, it, qtd, apto) : null;",
  "const dv = ben && typeof benSobraDev === 'function' ? benSobraDev(c, o, it, qtd, apto) : null;"),
 ('M93 conferência dentro da faixa traz só a sobra (2ª visita do almoxarife)', "if (o.etapa === 'Em conferência' && (o.ben.conf || prCmp(benKgAberto(o), benFaixa(benEntrada(o), benRota(o.ben.rota))) <= 0)) return", "if (o.etapa === 'Em conferência' && o.ben.conf) return"),
 ('M94 caixa em uso devolvida volta livre (sem a reserva da linha)', "if (dv.volta > 0) { l.reservado += dv.volta;", "if (false) { l.reservado += dv.volta;"),
 ('M95 Fechar não tira o não entregue do "a entregar"', "if (pe > 1e-9) x.it.dispensado = (x.it.dispensado || 0) + pe; });", "});"),
 # integração da rodada 3 na v56 (sonda de mutantes extras: sobreviviam aos testes de unidade; U57a-g os matam). O X20 (ordem sem caixa marcada
 # reservada) é equivalente: só a PACK-FRU v3 está aprovada e ela exige ao menos 1 caixa, então a ordem sem caixa não é alcançável
 ('M96 cenResTot não desconta a reserva-baixa (a linha encerrada volta a ter reserva própria)', "(m.tipo === 'reserva' ? (m.qtd || 0) : -(m.qtd || 0))", "(m.tipo === 'reserva' ? (m.qtd || 0) : 0)"),
 ('M97 cenResTot: base da REQ da semente não Reservada = 0 (a caixa em uso devolvida à REQ-030 fica sem reserva própria)', "(s0.estado === 'Reservada' ? i0.solicitado : (i0.entregue || 0))", "(s0.estado === 'Reservada' ? i0.solicitado : 0)"),
 ('M98 avaria não sai do "a entregar" (entrega sem reserva no lugar do Pedir mais caixas)', "if (!apto) return { livre: 0, volta: 0, disp: q,", "if (!apto) return { livre: 0, volta: 0, disp: 0,"),
 ('M99 recuperação em conferência sem Reabrir a execução', "(fase === 'conf' ? ' Na conferência não entra caixa: Reabrir a execução e, quando", "(fase === 'conf' ? ' Quando"),
 ('M100 selo "Sobra em custódia" pela custódia inteira', "if (o.etapa === 'Em conferência' && benCxSobra(c, o) > 0) out.push({ t: 'Sobra em custódia'", "if (o.etapa === 'Em conferência' && benCxTot(c, o).cust > 1e-9) out.push({ t: 'Sobra em custódia'"),
 # revisão adversarial da rodada 3 (A1..A7): cada correção tem o seu mutante
 ('M103 a reposição volta a contar no planejado (pedir a falta não a baixa; revisão A1)', "if (fx0 > 0) o.ben.cxRepos = (o.ben.cxRepos || 0) + Math.min(n, fx0);", ""),
 ('M104 caixa em uso devolvida bloqueada não fica ligada à linha (revisão A2)', "if (!apto && dv.uso > 0) { it.quarUso = (it.quarUso || 0) + dv.uso; m.uso = dv.uso; }", ""),
 ('M105 a quarentena de caixas em uso de ordem aberta vira fonte de outra ordem (revisão A2)', "qtd: Math.floor(l.quarentena - (l.quarRep || 0) - benQuarUso(c, l)", "qtd: Math.floor(l.quarentena - (l.quarRep || 0)"),
 ('M106 a quarentena reprovada (quarRep) volta a ser fonte que cobre (revisão A3)', "qtd: Math.floor(l.quarentena - (l.quarRep || 0) - benQuarUso(c, l)", "qtd: Math.floor(l.quarentena - benQuarUso(c, l)"),
 ('M107 a mensagem da devolução ignora a fase: ordem conferida diz "caixas em uso" (revisão A7)', "const cf = o.etapa === 'Em conferência' && !!(o.ben && o.ben.conf);", "const cf = false;"),
 ('M101 kg aberto zera com a conferência dada', "if (!benEh(o) || BEN_ABERTA.indexOf(o.etapa) < 0) return 0; const x = prSub(", "if (!benEh(o) || BEN_ABERTA.indexOf(o.etapa) < 0 || o.ben.conf) return 0; const x = prSub("),
 ('M102 só a 1ª nota de caixas é fonte', "benNfCx(c).forEach(nf => F.push(", "benNfCx(c).slice(0, 1).forEach(nf => F.push("),
]
U = open(os.path.join(HERE, 'ben_unit.js'), encoding='utf-8').read()
base = motor(); OK = []
for nome, de, para in M:
    n = base.count(de)
    if n != 1: OK.append(False); print(f'FALHA {nome}: trecho achado {n} vezes (o mutante não se aplica)'); continue
    r = node(base.replace(de, para) + U, 'ben_mutante.js'); out = r.stdout.strip().splitlines()
    try: res = json.loads(out[-1])
    except Exception: res = None
    mortos = [x['n'].split(' ')[0] for x in (res or []) if not x['ok']]
    morto = r.returncode != 0 or res is None or bool(mortos)
    OK.append(morto); print(('OK    ' if morto else 'FALHA ') + nome + ' → ' + (', '.join(mortos[:6]) if mortos else ('erro de execução' if morto else 'SOBREVIVEU')))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
