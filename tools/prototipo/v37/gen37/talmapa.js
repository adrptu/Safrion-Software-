// ===== Talhões desenhados ou importados no Mapa (IN-04): gravam no mesmo cadastro de fazendas e talhões (CD-01, 'talhao-os-cd01-v1') =====
// Usa talgeo.js (área geodésica, validação, KML/GeoJSON). Funciona no mapa real (Lagoa Grande, MapLibre).
const TM_CKEY = 'talhao-os-cd01-v1';
function tmLer(){ try{ return JSON.parse(localStorage.getItem(TM_CKEY) || 'null') || {}; }catch(e){ return {}; } }
function tmGravar(st){ try{ localStorage.setItem(TM_CKEY, JSON.stringify(st)); return true; }catch(e){ return false; } }
// fazendas e talhões do cadastro: o que foi salvo no navegador + os registros de base que ainda não estão lá (mesma regra do CD-01)
function tmBase(){ const st = tmLer(); const cp = x => ({ id: x.id, v: Object.assign({}, x.v) });
  const faz = (st.faz || []).map(cp), tal = (st.tal || []).map(cp);
  M.cad0.faz.forEach(f => { if (!faz.some(x => x.id === f.id)) faz.push(cp(f)); });
  M.cad0.tal.forEach(t => { if (!tal.some(x => x.id === t.id)) tal.push(cp(t)); });
  return { st, faz, tal }; }
// nome de exibição: os pivôs da Lagoa Grande vêm do KML como PV01…; no mapa e nos avisos aparecem como "Pivô 1"
function tmNomeDe(t){ const p = M.lg.pivos.find(x => x.id === t.id); return p ? ('Pivô ' + String(p.rot).replace(/^P/, '')) : (t.v.t || t.id); }
// contorno atual de cada talhão ativo da fazenda: o salvo no cadastro (desenho ou arquivo) ou, nos pivôs, o círculo do KML
function tmAneis(faz){ const { st, tal } = tmBase(); const g = st.geom || {}; const out = [];
  tal.forEach(t => { if (t.v.faz !== faz || t.v.sit === 'Inativo') return;
    if (g[t.id]) out.push({ id: t.id, nome: tmNomeDe(t), ring: g[t.id], v: t.v });
    else if (faz === 'Lagoa Grande'){ const f = M.lg.geo.features.find(x => x.properties.id === t.id); if (f) out.push({ id: t.id, nome: tmNomeDe(t), ring: f.geometry.coordinates[0], v: t.v }); } });
  return out; }
function tmUser(id){ if (!id || isLG(id)) return null; const { st, tal } = tmBase(); const t = tal.find(x => x.id === id); return (t && (st.geom || {})[id]) ? t : null; }
function tmIdNovo(tal, faz){ const pre = faz === 'Lagoa Grande' ? 'LGT' : 'TN'; let n = 1; while (tal.some(t => t.id === pre + String(n).padStart(2, '0'))) n++; return pre + String(n).padStart(2, '0'); }
function tmNum(s){ const x = Number(String(s == null ? '' : s).trim().replace(/\./g, '').replace(',', '.')); return isFinite(x) ? x : NaN; }
// grava um contorno: talhão novo ou nova versão do contorno de um talhão existente; devolve id, versão e área
function tmSalvar(d){ const { st, faz, tal } = tmBase(); const ha = Math.round(tgAreaHa(d.ring) * 100) / 100; let id = d.alvo;
  if (id === 'novo'){ id = tmIdNovo(tal, d.faz); tal.push({ id, v: { t: d.nome, faz: d.faz, sis: d.sis || 'Sequeiro', setor: '', decl: d.decl, calc: ha, motivo: d.motivo || '', sit: 'Ativo', inat: '', ver: '', geo: 'poly', geo_t: '' } }); }
  const T = tal.find(t => t.id === id); if (!T) throw new Error('Talhão não encontrado no cadastro.');
  const vers = Object.assign({}, st.vers || {}); const vs = (vers[id] || []).slice(); const ver = 'v' + (vs.length + 1);
  vs.push([ver, M.hoje_iso, d.origem, ha]); vers[id] = vs;
  T.v.calc = ha; T.v.ver = ver; T.v.geo = 'poly';
  if (d.decl !== undefined && d.decl !== null && d.decl !== '') T.v.decl = d.decl;
  if (d.motivo) T.v.motivo = d.motivo; if (d.sis && d.alvo === 'novo') T.v.sis = d.sis;
  T.v.geo_t = d.origem + ' · ' + nfx(ha, 2) + ' ha · perímetro ' + nfx(tgPerimetro(d.ring) / 1000, 2) + ' km';
  const geom = Object.assign({}, st.geom || {}); geom[id] = d.ring;
  if (!tmGravar(Object.assign({}, st, { faz, tal, vers, geom }))) throw new Error('O navegador não deixou gravar: libere espaço ou permita o armazenamento do site.');
  return { id, ver, ha, nome: tmNomeDe(T) }; }
// mesmas regras do cadastro do talhão + regras da geometria (sem cruzar a si mesmo, sem sobrepor outro talhão)
function tmValida(d, faz){ const e = {}; const ring = d.ring; const ha = ring ? tgAreaHa(ring) : 0;
  if (!ring || tgAberto(ring).length < 3) e.geo = 'Marque pelo menos 3 pontos.';
  else if (tgAutoCruza(ring)) e.geo = 'O contorno cruza a si mesmo: desfaça o último ponto ou redesenhe.';
  else if (ha < 0.1) e.geo = 'Área muito pequena (' + nfx(ha, 2) + ' ha): confira o desenho.';
  const { faz: fz, tal } = tmBase(); const F = fz.find(f => f.v.nome === faz);
  if (d.alvo === 'novo'){ const n = String(d.nome || '').trim(); if (!n) e.nome = 'Informe o nome do talhão.';
    else if (tal.some(t => t.v.faz === faz && (tgNome(t.v.t) === tgNome(n) || tgNome(tmNomeDe(t)) === tgNome(n)))) e.nome = 'Já existe ' + n + ' na ' + faz + '. Use outro nome.'; }
  const dec = tmNum(d.decl);
  if (!(dec > 0)) e.decl = 'Informe a área cultivável em ha (ex.: ' + nfx(ha, 1) + ').';
  else { if (ha > 0 && Math.abs(ha - dec) / dec > 0.01 && !d.motivo) e.motivo = 'Diferença de ' + nfx(Math.abs(ha - dec) / dec * 100, 1) + ' % entre a área cultivável e o contorno: escolha o motivo.';
    if (F && isFinite(Number(F.v.area)) && Number(F.v.area) > 0){ const soma = tal.filter(t => t.v.faz === faz && t.v.sit !== 'Inativo' && t.id !== d.alvo).reduce((s, t) => s + (Number(t.v.decl) || 0), 0) + dec;
      if (soma > Number(F.v.area) + 0.005) e.decl = 'Os talhões ativos da ' + faz + ' somariam ' + nfx(soma, 2) + ' ha; a fazenda tem ' + nfx(Number(F.v.area), 2) + ' ha.'; } }
  if (ring && !e.geo){ const sob = tmSobrepoe(ring, faz, d.alvo); if (sob.length) e.geo = 'O contorno sobrepõe ' + sob.join(', ') + ': ajuste o desenho para não contar a mesma área duas vezes.'; }
  return e; }
// sobreposição com os outros talhões da fazenda (tolerância: 2 % da menor área ou 0,3 ha, o maior)
function tmSobrepoe(ring, faz, exceto, extras){ const ha = tgAreaHa(ring); const out = [];
  tmAneis(faz).concat(extras || []).forEach(o => { if (o.id === exceto) return; const s = tgSobrepoeHa(ring, o.ring);
    if (s > Math.max(0.3, 0.02 * Math.min(ha, tgAreaHa(o.ring)))) out.push(o.nome + ' (' + nfx(s, 1) + ' ha)'); });
  return out; }
// enquadra o mapa num contorno (talhão salvo, aberto do cadastro ou da importação)
function tmEnquadra(ring){ if (!LGI.map || !ring) return; const b = tgCaixa(ring); try{ LGI.map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 80, maxZoom: 15.5, duration: 500 }); }catch(e){} }
// ---------- desenho ----------
function tmIniciar(self, alvo){ const nome = alvo && alvo !== 'novo' ? tmNomeDe(tmBase().tal.find(t => t.id === alvo) || { id: alvo, v: {} }) : '';
  self.setState({ dw: { modo: (alvo && isLG(alvo)) ? 'piv' : 'pol', pts: [], centro: null, raio: 0, alvo: alvo || 'novo', etapa: 'desenho', pivha: '' }, imp: null, tsel: [], px: null, mpa: null, selm: false, medir: false, cvis: false,
    g2toast: (nome ? 'Novo contorno de ' + nome + ': ' : 'Desenhar talhão: ') + 'clique nos cantos e feche no primeiro ponto ou em Concluir. Para pivô, clique no centro e na borda.' }); }
// cópia síncrona do desenho: cliques seguidos antes do novo desenho da tela não se sobrescrevem
function tmDw(self){ return self.__dw !== undefined ? self.__dw : self.state.dw; }
function tmSetDw(self, dw, extra){ self.__dw = dw; self.setState(Object.assign({ dw }, extra || {})); }
function tmRing(dw){ return dw.modo === 'piv' ? ((dw.centro && dw.raio > 0) ? tgCirculo(dw.centro[0], dw.centro[1], dw.raio) : null) : (dw.pts.length >= 3 ? tgFechado(dw.pts) : null); }
function tmClique(self, ll){ const dw = tmDw(self); if (!dw || dw.etapa !== 'desenho') return false; const p = [ll.lng, ll.lat];
  if (dw.modo === 'piv'){ if (!dw.centro) tmSetDw(self, Object.assign({}, dw, { centro: p })); else tmConcluir(self, Object.assign({}, dw, { raio: tgDist(dw.centro, p) })); return true; }
  // clique perto do primeiro ponto (até 12 px) fecha o polígono
  if (dw.pts.length >= 3 && LGI.map){ const a = LGI.map.project(dw.pts[0]), b = LGI.map.project(p); if (Math.hypot(a.x - b.x, a.y - b.y) <= 12){ tmConcluir(self, dw); return true; } }
  tmSetDw(self, Object.assign({}, dw, { pts: dw.pts.concat([p]) })); return true; }
function tmProximoNome(piv){ const { tal } = tmBase(); const daFaz = tal.filter(t => t.v.faz === FAZ);
  if (piv){ const ns = M.lg.pivos.map(p => Number(String(p.rot).replace(/\D/g, '')) || 0).concat(daFaz.map(t => Number((/^Piv[oô] (\d+)$/i.exec(t.v.t) || [])[1]) || 0)); return 'Pivô ' + (Math.max.apply(null, ns.concat([0])) + 1); }
  const ns = daFaz.map(t => Number((/^Talh[aã]o (\d+)$/i.exec(t.v.t) || [])[1]) || 0); return 'Talhão ' + (Math.max.apply(null, ns.concat([0])) + 1); }
function tmConcluir(self, dw){ const ring = tmRing(dw);
  if (!ring){ self.setState({ g2toast: dw.modo === 'piv' ? 'Clique no centro e depois na borda do pivô, ou informe a área em hectares.' : 'Marque pelo menos 3 pontos para fechar o contorno.' }); return; }
  const ha = Math.round(tgAreaHa(ring) * 100) / 100; const T = dw.alvo !== 'novo' ? tmBase().tal.find(t => t.id === dw.alvo) : null;
  tmSetDw(self, Object.assign({}, dw, { etapa: 'form', ring, nome: T ? tmNomeDe(T) : tmProximoNome(dw.modo === 'piv'), sis: T ? (T.v.sis || 'Sequeiro') : (dw.modo === 'piv' ? 'Pivô central' : 'Sequeiro'),
    decl: T ? String(T.v.decl).replace('.', ',') : nfx(ha, 2).replace(/\./g, ''), motivo: '', err: {} })); }
function tmSalvarDesenho(self){ const dw = self.state.dw; if (!dw || dw.etapa !== 'form') return;
  const d = { alvo: dw.alvo, nome: String(dw.nome || '').trim(), faz: FAZ, sis: dw.sis, decl: tmNum(dw.decl), motivo: dw.motivo, ring: dw.ring, origem: 'Desenho no mapa' };
  const e = tmValida(Object.assign({}, d, { decl: dw.decl }), FAZ); if (Object.keys(e).length){ self.setState({ dw: Object.assign({}, dw, { err: e }) }); return; }
  try{ const r = tmSalvar(d); self.__dw = null; self.setState({ dw: null, tsel: [r.id], px: null, mpa: null, g2toast: r.nome + ' salvo no cadastro · contorno ' + r.ver + ' · ' + nfx(r.ha, 2) + ' ha' }); setTimeout(() => tmEnquadra(d.ring), 50); }
  catch(x){ self.setState({ dw: Object.assign({}, dw, { err: { geo: x.message } }) }); } }
// ---------- importação (KML ou GeoJSON) ----------
// nome todo em maiúsculas no arquivo ("PIVÔ 25") vira "Pivô 25"; nome escrito normalmente fica como está
function tmBonito(n){ n = String(n || '').trim(); return (n && n === n.toUpperCase() && /[A-ZÀ-Ý]/.test(n)) ? n.toLowerCase().replace(/(^|\s)(\S)/g, (m0, a, b) => a + b.toUpperCase()) : n; }
function tmCasar(f, faz){ const an = tmAneis(faz); const n = tgNome(f.nome);
  const pn = an.find(o => tgNome(o.nome) === n || tgNome(o.v.t) === n || (isLG(o.id) && tgNome((M.lg.pivos.find(p => p.id === o.id) || {}).nome) === n));
  if (pn) return pn.id; const c = f.centro || tgCentro(f.ring); const pc = an.find(o => tgDentro(c, o.ring)); return pc ? pc.id : null; }
function tmLerArq(self, nome, txt){ let fs;
  try{ fs = tgLer(nome, txt); }catch(e){ self.setState({ imp: { etapa: 'arq', err: e.message } }); return; }
  const rows = fs.map((f, i) => { const r = { i, nome: f.nome, tipo: f.tipo, pasta: f.pasta, ha: f.ha, decl: f.decl, ring: f.ring, centro: f.centro || null, dest: 'nao', av: '', alvo: null };
    const destino = tgDestino(f);
    if (destino === 'Ignorar') r.av = f.tipo === 'Ponto' ? 'Ponto sem área: não vira talhão (informe a área em ha no nome ou na descrição para virar pivô).' : 'Linha não vira talhão.';
    else if (destino === 'Cadastro da fazenda') r.av = 'Perímetro, reserva, APP ou água não vira talhão.';
    else if (tgAutoCruza(f.ring)) r.av = 'O contorno cruza a si mesmo: corrija no arquivo.';
    else { r.alvo = tmCasar(f, FAZ); r.dest = r.alvo ? ('upd:' + r.alvo) : 'novo'; }
    return r; });
  const t = rows.filter(r => r.ring); if (!t.length){ self.setState({ imp: { etapa: 'arq', err: 'O arquivo não tem polígono nem pivô com área. Exporte os talhões como polígonos.' } }); return; }
  self.setState({ imp: { etapa: 'rev', arq: nome, rows, err: '' }, dw: null, tsel: [], px: null, mpa: null });
  // enquadra o mapa nas feições do arquivo
  if (LGI.map){ let b = [180, 90, -180, -90]; t.forEach(r => { const c = tgCaixa(r.ring); b = [Math.min(b[0], c[0]), Math.min(b[1], c[1]), Math.max(b[2], c[2]), Math.max(b[3], c[3])]; });
    try{ LGI.map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 40, duration: 500 }); }catch(e){} } }
// avisos de cada linha conforme o destino escolhido (sobreposição com os talhões que ficam e com as outras linhas novas)
function tmAvisosImp(rows){ const ficam = []; rows.forEach(r => { if (r.dest === 'novo' && r.ring) ficam.push({ id: 'imp' + r.i, nome: r.nome, ring: r.ring }); });
  return rows.map(r => { if (!r.ring || r.dest === 'nao') return ''; const alvo = r.dest.indexOf('upd:') === 0 ? r.dest.slice(4) : null;
    const sob = tmSobrepoe(r.ring, FAZ, alvo, ficam.filter(x => x.id !== 'imp' + r.i)); return sob.length ? ('Sobrepõe ' + sob.join(', ') + '.') : ''; }); }
function tmImportar(self){ const imp = self.state.imp; if (!imp || !imp.rows) return; const av = tmAvisosImp(imp.rows); const ruins = imp.rows.filter((r, i) => r.dest !== 'nao' && av[i]);
  if (ruins.length){ self.setState({ imp: Object.assign({}, imp, { err: ruins.length + (ruins.length > 1 ? ' linhas sobrepõem' : ' linha sobrepõe') + ' talhões: escolha "Não importar" ou corrija o arquivo.' }) }); return; }
  const sel = imp.rows.filter(r => r.dest !== 'nao'); if (!sel.length){ self.setState({ imp: Object.assign({}, imp, { err: 'Nenhuma linha para importar: escolha o destino de pelo menos uma.' }) }); return; }
  let nov = 0, upd = 0, dif = 0; const nomes = tmBase().tal.filter(t => t.v.faz === FAZ).map(t => tgNome(t.v.t));
  try{ sel.forEach(r => { const origem = (/\.kml$/i.test(imp.arq) ? 'KML ' : 'GeoJSON ') + imp.arq;
      if (r.dest === 'novo'){ let nm = tmBonito(r.nome); while (nomes.indexOf(tgNome(nm)) >= 0) nm = nm + ' (importado)'; nomes.push(tgNome(nm));
        const dec = Math.round((r.decl || tgAreaHa(r.ring)) * 100) / 100; const ha = tgAreaHa(r.ring); const mot = Math.abs(ha - dec) / dec > 0.01 ? 'Documento desatualizado' : '';
        tmSalvar({ alvo: 'novo', nome: nm, faz: FAZ, sis: r.tipo === 'Pivô' ? 'Pivô central' : 'Sequeiro', decl: dec, motivo: mot, ring: r.ring, origem }); nov++; }
      else { const id = r.dest.slice(4); const T = tmBase().tal.find(t => t.id === id); tmSalvar({ alvo: id, ring: r.ring, origem });
        if (T && Number(T.v.decl) > 0 && Math.abs(tgAreaHa(r.ring) - Number(T.v.decl)) / Number(T.v.decl) > 0.01 && !T.v.motivo) dif++; upd++; } }); }
  catch(x){ self.setState({ imp: Object.assign({}, imp, { err: x.message }) }); return; }
  self.setState({ imp: null, g2toast: 'Importado para o cadastro: ' + [nov ? nov + (nov > 1 ? ' talhões novos' : ' talhão novo') : '', upd ? upd + (upd > 1 ? ' contornos atualizados' : ' contorno atualizado') : ''].filter(Boolean).join(' · ')
    + (dif ? ' · ' + dif + (dif > 1 ? ' com diferença de área: informe o motivo no cadastro' : ' com diferença de área: informe o motivo no cadastro') : '') }); }
// ---------- camadas no mapa ----------
function tmCamadas(self, m){ const vazio = { type: 'FeatureCollection', features: [] };
  m.addSource('tu', { type: 'geojson', data: vazio });
  m.addLayer({ id: 'tu-fill', type: 'fill', source: 'tu', paint: { 'fill-color': '#FFFFFF', 'fill-opacity': 0.12 } });
  m.addLayer({ id: 'tu-line', type: 'line', source: 'tu', paint: { 'line-color': ['case', ['get', 'sel'], '#15201A', '#FFFFFF'], 'line-width': ['case', ['get', 'sel'], 4, 2] } });
  m.addSource('imp', { type: 'geojson', data: vazio });
  m.addLayer({ id: 'imp-fill', type: 'fill', source: 'imp', paint: { 'fill-color': ['match', ['get', 'dest'], 'sim', '#4FC3F7', '#BDBDBD'], 'fill-opacity': 0.3 } });
  m.addLayer({ id: 'imp-line', type: 'line', source: 'imp', paint: { 'line-color': ['match', ['get', 'dest'], 'sim', '#0277BD', '#616161'], 'line-width': 2, 'line-dasharray': [2, 1] } });
  m.addSource('dw', { type: 'geojson', data: vazio });
  m.addLayer({ id: 'dw-fill', type: 'fill', source: 'dw', filter: ['==', ['get', 'k'], 'pol'], paint: { 'fill-color': '#FFD500', 'fill-opacity': 0.25 } });
  m.addLayer({ id: 'dw-line', type: 'line', source: 'dw', filter: ['in', ['get', 'k'], ['literal', ['pol', 'lin']]], paint: { 'line-color': '#FFD500', 'line-width': 3 } });
  m.addLayer({ id: 'dw-pt', type: 'circle', source: 'dw', filter: ['==', ['get', 'k'], 'pt'], paint: { 'circle-radius': ['case', ['get', 'first'], 7, 5], 'circle-color': '#FFFFFF', 'circle-stroke-color': '#15201A', 'circle-stroke-width': 2 } });
  m.on('click', (e) => { tmClique(self, e.lngLat); });
  m.on('click', 'tu-fill', (e) => { if (self.state.dw) return; const f = e.features && e.features[0]; if (f) self.setState({ tsel: [f.properties.id], px: null, mpa: null, imp: null }); });
  m.on('mouseenter', 'tu-fill', () => { if (!self.state.dw) m.getCanvas().style.cursor = 'pointer'; }); m.on('mouseleave', 'tu-fill', () => { if (!self.state.dw) m.getCanvas().style.cursor = ''; }); }
function tmSync(self){ const m = LGI.map; if (!m || !m.getSource('tu')) return; const st = self.state; const g = tmLer().geom || {}; const { tal } = tmBase();
  // contorno novo de um pivô substitui o círculo do KML; talhões novos entram na camada própria
  const gk = JSON.stringify(g); if (LGI.tmGk !== gk){ LGI.tmGk = gk;
    m.getSource('pv').setData({ type: 'FeatureCollection', features: M.lg.geo.features.map(f => g[f.properties.id] ? { type: 'Feature', properties: f.properties, geometry: { type: 'Polygon', coordinates: [g[f.properties.id]] } } : f) }); }
  const nov = tal.filter(t => t.v.faz === 'Lagoa Grande' && g[t.id] && !isLG(t.id) && t.v.sit !== 'Inativo'); const sel = (st.tsel || [])[0];
  m.getSource('tu').setData({ type: 'FeatureCollection', features: nov.map(t => ({ type: 'Feature', properties: { id: t.id, sel: sel === t.id }, geometry: { type: 'Polygon', coordinates: [g[t.id]] } })) });
  LGI.tmk = LGI.tmk || {};
  nov.forEach(t => { const c = tgCentro(g[t.id]); let mk = LGI.tmk[t.id];
    if (!mk){ const d = document.createElement('div'); d.className = 'lg-rot'; d.appendChild(document.createElement('b')); d.appendChild(document.createElement('span')); d.appendChild(document.createElement('i'));
      mk = LGI.tmk[t.id] = new maplibregl.Marker({ element: d, anchor: 'center' }).setLngLat(c).addTo(m); } else mk.setLngLat(c);
    const el = mk.getElement(); el.children[0].textContent = t.v.t; el.children[1].textContent = nfx(Number(t.v.calc) || 0, 1) + ' ha'; });
  Object.keys(LGI.tmk).forEach(id => { if (!nov.some(t => t.id === id)){ LGI.tmk[id].remove(); delete LGI.tmk[id]; } });
  // desenho em andamento e prévia do arquivo
  const dw = st.dw; const df = [];
  if (dw){ const ring = dw.etapa === 'form' ? dw.ring : tmRing(dw); if (ring) df.push({ type: 'Feature', properties: { k: 'pol' }, geometry: { type: 'Polygon', coordinates: [ring] } });
    if (dw.etapa === 'desenho'){ const pts = dw.modo === 'piv' ? (dw.centro ? [dw.centro] : []) : dw.pts;
      if (pts.length > 1 && dw.modo === 'pol') df.push({ type: 'Feature', properties: { k: 'lin' }, geometry: { type: 'LineString', coordinates: pts } });
      pts.forEach((p, i) => df.push({ type: 'Feature', properties: { k: 'pt', first: i === 0 }, geometry: { type: 'Point', coordinates: p } })); } }
  m.getSource('dw').setData({ type: 'FeatureCollection', features: df });
  const imp = st.imp; m.getSource('imp').setData({ type: 'FeatureCollection', features: ((imp && imp.rows) || []).filter(r => r.ring).map(r => ({ type: 'Feature', properties: { dest: r.dest === 'nao' ? 'nao' : 'sim' }, geometry: { type: 'Polygon', coordinates: [r.ring] } })) });
  const desenhando = !!(dw && dw.etapa === 'desenho'); m.getCanvas().style.cursor = desenhando ? 'crosshair' : '';
  try{ if (desenhando) m.doubleClickZoom.disable(); else m.doubleClickZoom.enable(); }catch(e){} }
// ---------- valores da tela ----------
function tmVals(self, v){ const st = self.state; const real = !!v.map_lg; v.tm_ok = real; self.__dw = st.dw;
  // atalhos vindos do cadastro: #desenhar=ID, #importar, #talhao=ID
  if (!self.__tmhl){ self.__tmhl = 1; try{ window.addEventListener('hashchange', () => { self.__tmh = 0; self.setState({ tmh: Date.now() }); }); }catch(e){} }
  if (!self.__tmh){ self.__tmh = 1; let h = ''; try{ h = decodeURIComponent(location.hash || ''); }catch(e){}
    const md = /desenhar=([^&]+)/.exec(h), mi = /importar/.exec(h), mt = /talhao=([^&]+)/.exec(h);
    if (md || mi || mt) setTimeout(() => { if (md) tmIniciar(self, md[1]); else if (mi) self.setState({ imp: { etapa: 'arq', err: '' }, dw: null }); else { self.setState({ tsel: [mt[1]], px: null, mpa: null }); const go = (n) => { const a = tmAneis('Lagoa Grande').find(o => o.id === mt[1]); if (a && LGI.map) tmEnquadra(a.ring); else if (n < 20) setTimeout(() => go(n + 1), 300); }; go(0); } }, 0); }
  const sty = (on) => 'display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:700;color:#15201A;box-shadow:0 1px 3px rgba(21,32,26,.18);' + (on ? 'border:1px solid #1E7A4C;background:#E4F3E9;' : 'border:1px solid #E4E9E5;background:#FFFFFF;');
  v.r_des_st = sty(!!st.dw); v.r_des_on = st.dw ? 'true' : 'false'; v.r_imp_st = sty(!!st.imp); v.r_imp_on = st.imp ? 'true' : 'false';
  v.r_des = () => { if (self.state.dw) self.setState({ dw: null, g2toast: 'Desenho descartado.' }); else tmIniciar(self, 'novo'); };
  v.r_imp = () => self.setState({ imp: self.state.imp ? null : { etapa: 'arq', err: '' }, dw: null, tsel: [], px: null, mpa: null });
  // barra do desenho
  const dw = st.dw; v.tm_dbar = !!(real && dw && dw.etapa === 'desenho');
  const seg = (on) => 'font-family:inherit;font-size:12px;font-weight:700;padding:5px 11px;border-radius:999px;border:0;cursor:pointer;' + (on ? 'background:#1E7A4C;color:#fff;' : 'background:transparent;color:#15201A;');
  if (dw){ const ring = tmRing(dw); const ha = ring ? tgAreaHa(ring) : 0;
    v.tm_mpol_st = seg(dw.modo === 'pol'); v.tm_mpiv_st = seg(dw.modo === 'piv'); v.tm_mpol_on = dw.modo === 'pol' ? 'true' : 'false'; v.tm_mpiv_on = dw.modo === 'piv' ? 'true' : 'false';
    v.tm_mpol = () => self.setState({ dw: Object.assign({}, self.state.dw, { modo: 'pol', centro: null, raio: 0 }) }); v.tm_mpiv = () => self.setState({ dw: Object.assign({}, self.state.dw, { modo: 'piv', pts: [] }) });
    v.tm_dinfo = dw.modo === 'piv' ? (dw.centro ? 'Centro marcado: clique na borda ou informe a área' : 'Clique no centro do pivô')
      : (dw.pts.length ? dw.pts.length + (dw.pts.length > 1 ? ' pontos' : ' ponto') + (ring ? ' · ' + nfx(ha, 2) + ' ha · perímetro ' + nfx(tgPerimetro(ring) / 1000, 2) + ' km' : ' · marque mais ' + (3 - dw.pts.length)) : 'Clique no primeiro canto do talhão');
    v.tm_pivarea = dw.modo === 'piv' && !!dw.centro; v.tm_pivha = dw.pivha || '';
    v.tm_setpivha = (e) => { const ha2 = tmNum(e.target.value); const d0 = self.state.dw; if (ha2 > 0 && d0.centro) tmConcluir(self, Object.assign({}, d0, { raio: tgRaioDeHa(ha2), pivha: e.target.value })); else self.setState({ dw: Object.assign({}, d0, { pivha: e.target.value }) }); };
    v.tm_dundo = () => { const d0 = self.state.dw; self.setState({ dw: Object.assign({}, d0, d0.modo === 'piv' ? { centro: null, raio: 0 } : { pts: d0.pts.slice(0, -1) }) }); };
    v.tm_dok = () => tmConcluir(self, self.state.dw); v.tm_dcancel = () => self.setState({ dw: null, g2toast: 'Desenho descartado.' }); }
  // painel lateral: formulário do desenho, importação ou talhão novo selecionado
  const ut = tmUser((st.tsel || [])[0]); const form = !!(dw && dw.etapa === 'form'); const imp = st.imp;
  v.tm_open = real && (form || !!imp || !!ut); v.tm_form = form; v.tm_impa = !!(imp && imp.etapa === 'arq'); v.tm_impr = !!(imp && imp.etapa === 'rev'); v.tm_tal = !form && !imp && !!ut;
  v.tm_close = () => self.setState({ dw: null, imp: null, tsel: [] });
  const inp = (err) => 'font-family:inherit;font-size:13px;padding:7px 10px;border-radius:9px;background:#fff;width:100%;box-sizing:border-box;border:1px solid ' + (err ? '#B42318' : '#E4E9E5') + ';';
  if (form){ const e = dw.err || {}; const ha = tgAreaHa(dw.ring); const T = dw.alvo !== 'novo' ? tmBase().tal.find(t => t.id === dw.alvo) : null;
    v.tm_t = T ? 'Novo contorno · ' + tmNomeDe(T) : 'Talhão desenhado'; v.tm_sub = FAZ + ' · ' + nfx(ha, 2) + ' ha · perímetro ' + nfx(tgPerimetro(dw.ring) / 1000, 2) + ' km';
    const outros = tmAneis(FAZ).sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR', { numeric: true }));
    v.tm_aopts = [{ v: 'novo', t: 'Talhão novo' }].concat(outros.map(o => ({ v: o.id, t: 'Novo contorno de ' + o.nome }))); v.tm_alvo = dw.alvo;
    const set = (k) => (ev) => { const d0 = self.state.dw; const er = Object.assign({}, d0.err || {}); delete er[k]; if (k === 'decl') delete er.motivo; self.setState({ dw: Object.assign({}, d0, { [k]: ev.target.value, err: er }) }); };
    v.tm_setalvo = (ev) => { const a = ev.target.value; const d0 = self.state.dw; const T2 = a !== 'novo' ? tmBase().tal.find(t => t.id === a) : null;
      self.setState({ dw: Object.assign({}, d0, { alvo: a, nome: T2 ? tmNomeDe(T2) : tmProximoNome(d0.modo === 'piv'), sis: T2 ? (T2.v.sis || 'Sequeiro') : d0.sis, decl: T2 ? String(T2.v.decl).replace('.', ',') : nfx(tgAreaHa(d0.ring), 2).replace(/\./g, ''), err: {} }) }); };
    v.tm_novo = dw.alvo === 'novo'; v.tm_nome = dw.nome || ''; v.tm_setnome = set('nome'); v.tm_sis = dw.sis; v.tm_setsis = set('sis'); v.tm_sopts = ['Sequeiro', 'Pivô central', 'Gotejo'].map(x => ({ v: x, t: x }));
    v.tm_decl = dw.decl; v.tm_setdecl = set('decl'); v.tm_calc = nfx(ha, 2) + ' ha';
    const dec = tmNum(dw.decl); v.tm_temmot = dec > 0 && Math.abs(ha - dec) / dec > 0.01; v.tm_mot = dw.motivo || ''; v.tm_setmot = set('motivo');
    v.tm_mopts = [{ v: '', t: 'Escolha…' }].concat(M.motivos.map(x => ({ v: x, t: x })));
    v.tm_dif = v.tm_temmot ? ('Diferença de ' + nfx(Math.abs(ha - dec) / dec * 100, 1) + ' % entre a área cultivável e o contorno.') : '';
    ['nome', 'decl', 'motivo', 'geo'].forEach(k => { v['tm_he_' + k] = !!e[k]; v['tm_e_' + k] = e[k] || ''; });
    v.tm_st_nome = inp(e.nome); v.tm_st_decl = inp(e.decl); v.tm_st_mot = inp(e.motivo); v.tm_st_sel = inp(false);
    v.tm_salvar = () => tmSalvarDesenho(self); v.tm_redes = () => self.setState({ dw: Object.assign({}, self.state.dw, { etapa: 'desenho', err: {} }) }); v.tm_descartar = () => self.setState({ dw: null, g2toast: 'Desenho descartado.' }); }
  if (imp){ v.tm_t = 'Importar talhões'; v.tm_sub = imp.arq ? (imp.arq + ' · ' + FAZ) : ('KML ou GeoJSON · ' + FAZ); v.tm_ierr = imp.err || ''; v.tm_hasierr = !!imp.err;
    v.tm_arq = (ev) => { const f = ev && ev.target && ev.target.files && ev.target.files[0]; if (!f) return; const rd = new FileReader();
      rd.onload = () => tmLerArq(self, f.name, String(rd.result || '')); rd.onerror = () => self.setState({ imp: { etapa: 'arq', err: 'Não foi possível ler o arquivo. Tente de novo.' } }); rd.readAsText(f); };
    v.tm_outro = () => self.setState({ imp: { etapa: 'arq', err: '' } }); v.tm_importar = () => tmImportar(self);
    if (imp.rows){ const av = tmAvisosImp(imp.rows); const an = tmAneis(FAZ);
      const nomeDe = (id) => (an.find(o => o.id === id) || { nome: id }).nome;
      v.tm_rows = imp.rows.map((r, i) => { const opts = r.ring ? [{ v: 'novo', t: 'Talhão novo' }].concat(an.map(o => ({ v: 'upd:' + o.id, t: 'Novo contorno de ' + o.nome }))).concat([{ v: 'nao', t: 'Não importar' }]) : [{ v: 'nao', t: 'Não importar' }];
        const aviso = av[i] || (r.dest === 'nao' ? r.av : ''); const ruim = !!av[i];
        return { nome: r.nome, sub: [r.tipo, r.ring ? nfx(r.ha, 2) + ' ha' : '', r.decl ? 'declarado ' + nfx(r.decl, 2) + ' ha' : '', r.pasta].filter(Boolean).join(' · '),
          dest: r.dest, opts, hasAv: !!aviso, av: aviso, avst: 'font-size:12px;font-weight:700;color:' + (ruim ? '#B42318' : '#4B5A51') + ';',
          bst: r.dest === 'nao' ? 'opacity:.75;' : (ruim ? 'border-color:#B42318;' : 'border-left:4px solid #0277BD;'),
          set: (ev) => { const val = ev.target.value; const rs = self.state.imp.rows.map((x, j) => j === i ? Object.assign({}, x, { dest: val }) : x); self.setState({ imp: Object.assign({}, self.state.imp, { rows: rs, err: '' }) }); } }; });
      const c = { novo: 0, upd: 0, nao: 0 }; imp.rows.forEach(r => { c[r.dest === 'novo' ? 'novo' : (r.dest === 'nao' ? 'nao' : 'upd')]++; });
      v.tm_isum = [c.novo ? c.novo + (c.novo > 1 ? ' talhões novos' : ' talhão novo') : '', c.upd ? c.upd + (c.upd > 1 ? ' contornos atualizados' : ' contorno atualizado') : '', c.nao ? c.nao + ' fora da importação' : ''].filter(Boolean).join(' · ');
      v.tm_ibtn = 'Importar ' + (c.novo + c.upd) + ' para o cadastro'; v.tm_temimp = (c.novo + c.upd) > 0; }
    else { v.tm_rows = []; v.tm_isum = ''; v.tm_ibtn = ''; v.tm_temimp = false; } }
  if (!form && !imp && ut){ const g = (tmLer().geom || {})[ut.id]; const vs = (tmLer().vers || {})[ut.id] || []; const ult = vs[vs.length - 1] || [];
    v.tm_t = ut.v.t + ' · ' + nfx(Number(ut.v.calc) || 0, 2) + ' ha'; v.tm_sub = ut.v.faz + ' · ' + (ut.v.sis || 'Sequeiro') + ' · talhão sem cultivo na safra';
    v.tm_kv = [{ l: 'Contorno', t: (ult[0] || 'v1') + ' · ' + (ult[2] || '') + ' · ' + (ult[1] ? brIso(ult[1]) : '') }, { l: 'Área do contorno', t: nfx(Number(ut.v.calc) || 0, 2) + ' ha · perímetro ' + nfx(tgPerimetro(g) / 1000, 2) + ' km' },
      { l: 'Área cultivável', t: nfx(Number(ut.v.decl) || 0, 2) + ' ha' + (ut.v.motivo ? ' · ' + ut.v.motivo : '') }, { l: 'Satélite', t: 'entra na análise da próxima cena processada' }];
    v.tm_cad = 'CD-01det.dc.html#talhao=' + encodeURIComponent(ut.id); v.tm_redesenhar = () => tmIniciar(self, ut.id); }
  if (!v.tm_kv) v.tm_kv = []; if (!v.tm_rows) v.tm_rows = []; if (!v.tm_aopts) v.tm_aopts = []; if (!v.tm_sopts) v.tm_sopts = []; if (!v.tm_mopts) v.tm_mopts = [];
  if (v.tm_open) v.pan_open = false; }
