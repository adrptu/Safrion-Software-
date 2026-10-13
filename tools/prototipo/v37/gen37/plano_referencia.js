/* CONTROLE-02 / fatia 2. Retrato técnico e comparação; não publica nem autoriza orçamento/O.S.
 * A persistência depende do contrato CONF-D50/CF04. Este núcleo não escreve no cenário.
 * IDs de produto/fazenda usam as chaves de domínio do SAF atual (nomes), sem inventar UUIDs.
 */
const PlanoReferencia = (() => {
  'use strict';
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const cmp = (a, b) => a < b ? -1 : a > b ? 1 : 0;
  const chave = (...partes) => JSON.stringify(partes); // separadores em nomes não colidem
  function copia(v) {
    if (v === null || typeof v === 'string' || typeof v === 'boolean') return v;
    if (typeof v === 'number' && Number.isFinite(v)) return v;
    if (Array.isArray(v)) return v.map(copia); // listas ordenadas permanecem ordenadas
    if (v && Object.getPrototypeOf(v) === Object.prototype) {
      const out = {};
      Object.keys(v).sort(cmp).forEach(k => {
        if (k === '__proto__' || k === 'constructor' || k === 'prototype') throw new Error('Campo inválido no retrato.');
        out[k] = copia(v[k]);
      });
      return out;
    }
    throw new Error('O retrato contém valor ausente, não finito ou não serializável.');
  }
  function fixa(v) {
    if (v && typeof v === 'object') { Object.values(v).forEach(fixa); Object.freeze(v); }
    return v;
  }
  function texto(v, campo) {
    if (typeof v !== 'string' || !v.trim()) throw new Error(campo + ' sem identidade.');
    return v;
  }
  function retrato(contexto, entidades) {
    const contextoFixo = {fazenda: texto(contexto.fazenda, 'Fazenda'), safra: texto(contexto.safra, 'Safra')};
    const ids = new Set();
    const rows = entidades.map(e => {
      const tipo = texto(e.tipo, 'Entidade'), id = texto(e.id, 'Registro');
      const k = chave(tipo, id);
      if (ids.has(k)) throw new Error('Identidade repetida no retrato: ' + tipo + ' / ' + id);
      ids.add(k);
      if (!e.campos || Array.isArray(e.campos) || Object.getPrototypeOf(e.campos) !== Object.prototype) throw new Error('Campos inválidos no retrato.');
      return {tipo, id, campos: copia(e.campos)};
    }).sort((a, b) => cmp(chave(a.tipo, a.id), chave(b.tipo, b.id)));
    return fixa({schema: 1, contexto: contextoFixo, entidades: rows});
  }
  function normaliza(r) {
    if (!r || r.schema !== 1) throw new Error('Versão de retrato não suportada.');
    return retrato(r.contexto, r.entidades);
  }
  const bytes = r => JSON.stringify(normaliza(r));
  function comparar(anterior, atual) {
    const a = normaliza(anterior), b = normaliza(atual);
    if (a.contexto.fazenda !== b.contexto.fazenda || a.contexto.safra !== b.contexto.safra) throw new Error('As versões pertencem a fazendas ou safras diferentes.');
    const A = new Map(a.entidades.map(e => [chave(e.tipo, e.id), e]));
    const B = new Map(b.entidades.map(e => [chave(e.tipo, e.id), e]));
    const out = [];
    Array.from(new Set([...A.keys(), ...B.keys()])).sort(cmp).forEach(k => {
      const x = A.get(k), y = B.get(k), e = x || y;
      if (!x || !y) {
        out.push({tipo: e.tipo, id: e.id, estado: x ? 'removido' : 'incluído', antes: x ? x.campos : null, depois: y ? y.campos : null});
        return;
      }
      Array.from(new Set([...Object.keys(x.campos), ...Object.keys(y.campos)])).sort(cmp).forEach(campo => {
        const ha = own(x.campos, campo), hb = own(y.campos, campo);
        const va = x.campos[campo], vb = y.campos[campo];
        if (ha && hb && JSON.stringify(va) === JSON.stringify(vb)) return;
        const d = {tipo: e.tipo, id: e.id, campo, estado: ha && hb ? 'alterado' : ha ? 'removido' : 'incluído',
          antes: {presente: ha, valor: ha ? va : null}, depois: {presente: hb, valor: hb ? vb : null}};
        // Quantidades são pares valor/unidade. Nenhuma conversão presumida ou subtração.
        if (ha && hb && va && vb && typeof va === 'object' && typeof vb === 'object' && own(va, 'unidade') && own(vb, 'unidade') && va.unidade !== vb.unidade) d.unidadesIncompativeis = true;
        out.push(d);
      });
    });
    return fixa(out);
  }
  const pick = (o, ks) => Object.fromEntries(ks.filter(k => own(o, k) && o[k] !== undefined).map(k => [k, o[k]]));
  const medida = (v, unidade) => {
    const n = rpNum(v); // parser já usado pelo SAF, sem transformar ausência em zero
    if (n !== null && !Number.isFinite(n)) throw new Error('Quantidade inválida no plano: ' + unidade);
    return {valor: n, unidade};
  };
  function projetar(self, safra) {
    const s = safById(self, safra);
    if (!s) throw new Error('Safra não encontrada.');
    const fazenda = texto(s.v.faz, 'Fazenda');
    const entidades = [], planos = new Map(), configuracoes = new Map(), usados = new Set();
    const add = (tipo, id, campos) => entidades.push({tipo, id, campos});
    add('safra', safra, pick(s.v, ['nome', 'ini', 'fim']));
    cultRows(self, safra).forEach(c => {
      const v = c.v, pl = planById(v.plano);
      add('cultivo', c.id, Object.assign(pick(v, ['talhao', 'local', 'tipo', 'cult', 'var', 'plantio', 'colheita', 'ciclo', 'origem', 'plano']), {
        area: medida(v.area, 'ha'), meta: medida(v.meta, v.unm), ajustesLocais: (adjOf(self)[c.id] || {})
      }));
      if (pl) planos.set(pl.id, pl);
    });
    planos.forEach(pl => add('plano', pl.id, pick(pl, ['nome', 'cultura', 'versao'])));
    // ocorr já resolve gatilhos, ajustes locais, aceites de solo e rendimento. Nada é recalculado aqui.
    ocorr(self, safra).forEach(o => {
      const id = chave(o.c.id, o.a.id);
      add('atividade', id, {cultivo: o.c.id, atividade: o.a.id, plano: o.pl.id, nome: o.a.nome, operacao: o.a.op,
        gatilho: o.a.g, data: o.dt, incluida: o.incl, area: medida(o.area, 'ha'), horasPlanejadas: medida(o.rp.nec.hconj, 'h'),
        configuracoes: o.cfs.map(c => c.id).sort(cmp)});
      o.prods.forEach(p => add('produto', chave(o.c.id, o.a.id, p.nome), {
        cultivo: o.c.id, atividade: o.a.id, produto: p.nome, grupo: p.grupo,
        dose: medida(p.dose, p.un + '/ha'), quantidade: medida(p.q, p.un), preco: medida(p.preco, 'R$/' + p.un),
        origem: p.orig, laudo: p.laudo
      }));
      o.cfs.forEach(c => configuracoes.set(c.id, c));
    });
    configuracoes.forEach(c => {
      const v = cfgIn(c);
      const campos = pick(v, ['nome', 'seq']);
      [['rend', 'ha/h'], ['part', '%'], ['jan', 'h'], ['custo_h', 'R$/h'], ['diesel', 'L/h'], ['pess', 'pessoas'], ['troca', 'h']].forEach(([k, u]) => { campos[k] = medida(v[k], u); });
      campos.ativos = v.ativos.slice().sort(cmp);
      campos.recursos = v.rec;
      Object.keys(v.rec).forEach(k => { if (Number(v.rec[k]) > 0) usados.add(k); });
      add('configuracao', c.id, campos);
    });
    // Parâmetros de capacidade dos recursos usados; não captura os demais cadastros.
    ['g_recp_maq', 'g_recp_pes'].forEach(gid => {
      const g = GR(gid);
      if (g) g2rows(self, g).filter(r => usados.has(r.id)).forEach(r => {
        const campos = {nome: r.v.nome, pessoas: gid === 'g_recp_pes'};
        [['un', 'unidades'], ['jornada', 'h/dia'], ['turnos', 'turnos/dia'], ['disp', '%'], ['abs', '%']].forEach(([k, u]) => {
          if (own(r.v, k)) campos[k] = medida(r.v[k], u);
        });
        add('recurso', r.id, campos);
      });
    });
    if (usados.size) add('calendario', 'capacidade', {meses: D2.meses.map(m => m[0]).sort(cmp), diasUteis: D2.dias});
    return retrato({fazenda, safra}, entidades);
  }
  // Pré-condições de contexto. O futuro comando deve chamá-las de novo DENTRO da gravação
  // compartilhada; este resultado não é autorização permanente nem validação agronômica.
  function validarContexto(self, safra, ator, previa) {
    const responsavel=cenExige(ator,'gestor','Publicar referência do plano');
    const s=safById(self,safra);
    if(!s || self.state.saf!==safra) throw new Error('Escolha a safra da prévia antes de publicar. Nada foi alterado.');
    if(s.ro || s.v.estado==='Encerrada') throw new Error('Safra encerrada: as versões ficam disponíveis somente para consulta. Nada foi alterado.');
    if(!previa) throw new Error('Confira a prévia do plano antes de publicar. Nada foi alterado.');
    const atual=projetar(self,safra);
    if(bytes(previa)!==bytes(atual)) throw new Error('O plano mudou depois da prévia. Confira as diferenças e tente novamente; seu rascunho foi preservado.');
    return fixa({responsavel,atual});
  }
  // Prepara uma versão sem gravar. O comando compartilhado revalida contexto/domínio,
  // executa cenIdem e só então acrescenta esta versão na mesma gravação durável.
  function prepararVersao(publicadas, atual, esperada, por, em) {
    if (!Array.isArray(publicadas)) throw new Error('Histórico de versões inválido.');
    const r=normaliza(atual), ids=new Set();
    const anteriores=publicadas.map((p,i)=>{
      if (!p || p.id!=='R'+(i+1) || ids.has(p.id) || !p.por || !p.em) throw new Error('Histórico de versões inválido.');
      ids.add(p.id); comparar(p.retrato,r);
      return copia(p);
    });
    const ultima=anteriores.length?anteriores[anteriores.length-1]:null;
    if (esperada!==(ultima?ultima.id:null)) throw new Error('A referência mudou em outra aba. Confira a versão mais recente; seu rascunho foi preservado.');
    if (ultima && bytes(ultima.retrato)===bytes(r)) return fixa({nova:false,versao:ultima});
    texto(por,'Responsável'); texto(em,'Data da publicação');
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(em) || !Number.isFinite(Date.parse(em)) || new Date(em).toISOString()!==em) throw new Error('Data da publicação inválida.');
    return fixa({nova:true,versao:{id:'R'+(anteriores.length+1),por,em,retrato:r}});
  }
  return Object.freeze({retrato, comparar, bytes, projetar, validarContexto, prepararVersao});
})();
