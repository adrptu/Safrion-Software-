// Geometria de talhões (Mapa IN-04 e cadastro CD-01): área geodésica, perímetro, círculo do pivô, validação do polígono
// e leitura de KML e GeoJSON. Sem biblioteca externa. Coordenadas sempre [lon, lat] em graus (WGS 84 / SIRGAS 2000).
const TG_R = 6378137;
function tgRad(d){ return d * Math.PI / 180; }
// anel sem o ponto de fechamento repetido
function tgAberto(ring){ const r = (ring || []).slice(); if (r.length > 1){ const a = r[0], b = r[r.length - 1]; if (a[0] === b[0] && a[1] === b[1]) r.pop(); } return r; }
function tgFechado(ring){ const r = tgAberto(ring); return r.length ? r.concat([r[0].slice()]) : r; }
// área de um anel em m² pela fórmula do excesso esférico (a mesma do turf/area)
function tgAreaAnel(ring){ const r = tgAberto(ring); const n = r.length; if (n < 3) return 0; let s = 0;
  for (let i = 0; i < n; i++){ const p1 = r[i], p2 = r[(i + 1) % n], p3 = r[(i + 2) % n]; s += (tgRad(p3[0]) - tgRad(p1[0])) * Math.sin(tgRad(p2[1])); }
  return Math.abs(s * TG_R * TG_R / 2); }
function tgAreaHa(ring){ return tgAreaAnel(ring) / 10000; }
// distância em metros (haversine) e perímetro do anel
function tgDist(a, b){ const dLa = tgRad(b[1] - a[1]), dLo = tgRad(b[0] - a[0]); const h = Math.sin(dLa / 2) ** 2 + Math.cos(tgRad(a[1])) * Math.cos(tgRad(b[1])) * Math.sin(dLo / 2) ** 2;
  return 2 * TG_R * Math.asin(Math.min(1, Math.sqrt(h))); }
function tgPerimetro(ring){ const r = tgAberto(ring); let p = 0; for (let i = 0; i < r.length; i++) p += tgDist(r[i], r[(i + 1) % r.length]); return r.length > 2 ? p : 0; }
// pivô: círculo pelo centro e pelo raio (m) ou pela área (ha)
function tgCirculo(lon, lat, raio, n){ n = n || 72; const k = Math.cos(tgRad(lat)); const out = [];
  for (let i = 0; i < n; i++){ const a = 2 * Math.PI * i / n; out.push([lon + raio * Math.sin(a) / (111320 * k), lat + raio * Math.cos(a) / 110540]); }
  return tgFechado(out); }
function tgRaioDeHa(ha){ return Math.sqrt(ha * 10000 / Math.PI); }
// ponto dentro do anel (raio cruzando as arestas)
function tgDentro(pt, ring){ const r = tgAberto(ring); let ins = false;
  for (let i = 0, j = r.length - 1; i < r.length; j = i++){ const xi = r[i][0], yi = r[i][1], xj = r[j][0], yj = r[j][1];
    if (((yi > pt[1]) !== (yj > pt[1])) && (pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi) + xi)) ins = !ins; }
  return ins; }
function tgCruza(a, b, c, d){ const o = (p, q, r) => Math.sign((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]));
  return o(a, b, c) !== o(a, b, d) && o(c, d, a) !== o(c, d, b) && o(a, b, c) !== 0 && o(a, b, d) !== 0; }
// polígono que cruza a si mesmo não é aceito (área sem sentido)
function tgAutoCruza(ring){ const r = tgAberto(ring); const n = r.length; if (n < 4) return false;
  for (let i = 0; i < n; i++) for (let j = i + 2; j < n; j++){ if (i === 0 && j === n - 1) continue;
    if (tgCruza(r[i], r[(i + 1) % n], r[j], r[(j + 1) % n])) return true; }
  return false; }
function tgCaixa(ring){ const r = tgAberto(ring); let a = [180, 90, -180, -90]; r.forEach(p => { a = [Math.min(a[0], p[0]), Math.min(a[1], p[1]), Math.max(a[2], p[0]), Math.max(a[3], p[1])]; }); return a; }
function tgCentro(ring){ const r = tgAberto(ring); const c = r.reduce((s, p) => [s[0] + p[0], s[1] + p[1]], [0, 0]); return r.length ? [c[0] / r.length, c[1] / r.length] : [0, 0]; }
// sobreposição aproximada (ha) por amostragem numa grade de 40 × 40 sobre a caixa do polígono novo
function tgSobrepoeHa(novo, outro){ const a = tgCaixa(novo), b = tgCaixa(outro); if (a[2] < b[0] || b[2] < a[0] || a[3] < b[1] || b[3] < a[1]) return 0;
  const N = 40; let dentro = 0, ambos = 0;
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++){ const p = [a[0] + (a[2] - a[0]) * (i + 0.5) / N, a[1] + (a[3] - a[1]) * (j + 0.5) / N];
    if (tgDentro(p, novo)){ dentro++; if (tgDentro(p, outro)) ambos++; } }
  return dentro ? tgAreaHa(novo) * ambos / dentro : 0; }
// nome comparável: sem acento, maiúsculo, espaços simples ("PIVÔ 1" = "Pivô 1")
function tgNome(s){ return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().replace(/\s+/g, ' ').trim(); }
// área declarada num texto do KML ("64 ha", "Área: 64,5", "hectares 30")
function tgHaTexto(s){ const t = String(s || '').replace(/<[^>]+>/g, ' '); const m = /(\d+(?:[.,]\d+)?)\s*(?:ha\b|hectares?)/i.exec(t) || /(?:área|area|ha)\s*[:=]\s*(\d+(?:[.,]\d+)?)/i.exec(t) || /:\s*(\d+(?:[.,]\d+)?)\s*$/.exec(t.trim());
  return m ? Number(m[1].replace(',', '.')) : null; }
function tgCoords(txt){ return String(txt || '').trim().split(/\s+/).map(x => x.split(',').map(Number)).filter(p => p.length >= 2 && isFinite(p[0]) && isFinite(p[1])).map(p => [p[0], p[1]]); }
// KML: Placemark com Polygon (contorno externo) vira polígono; Point com área no nome ou na descrição vira pivô (círculo)
function tgLerKML(texto){ let doc; try{ doc = new DOMParser().parseFromString(texto, 'text/xml'); }catch(e){ throw new Error('Arquivo KML ilegível.'); }
  if (!doc || doc.getElementsByTagName('parsererror').length) throw new Error('Arquivo KML ilegível: confira se é o .kml (não o .kmz compactado).');
  const pms = [...doc.getElementsByTagName('Placemark')]; if (!pms.length) throw new Error('Nenhuma feição no KML.'); const out = [];
  const txtDe = (el, tag) => { const x = el.getElementsByTagName(tag)[0]; return x ? x.textContent : ''; };
  pms.forEach((pm, i) => { const nome = (txtDe(pm, 'name') || ('Feição ' + (i + 1))).trim(); const desc = txtDe(pm, 'description');
    const pastas = []; let p = pm.parentNode; while (p && p.nodeName){ if (p.nodeName === 'Folder'){ const n = [...p.childNodes].find(c => c.nodeName === 'name'); if (n) pastas.unshift(n.textContent.trim()); } p = p.parentNode; }
    const pols = [...pm.getElementsByTagName('Polygon')];
    if (pols.length){ let best = null, bestA = -1; pols.forEach(pg => { const ob = pg.getElementsByTagName('outerBoundaryIs')[0] || pg; const ring = tgCoords(txtDe(ob, 'coordinates')); const a = tgAreaHa(ring); if (a > bestA){ best = ring; bestA = a; } });
      if (best && best.length >= 3) out.push({ nome, pasta: pastas.join(' › '), tipo: 'Polígono', ring: tgFechado(best), ha: tgAreaHa(best), decl: tgHaTexto(desc) }); return; }
    const pt = tgCoords(txtDe(pm, 'coordinates'))[0]; const ls = pm.getElementsByTagName('LineString').length;
    if (pt && !ls){ const ha = tgHaTexto(desc) || tgHaTexto(nome);
      if (ha) out.push({ nome, pasta: pastas.join(' › '), tipo: 'Pivô', centro: pt, ring: tgCirculo(pt[0], pt[1], tgRaioDeHa(ha)), ha: ha, decl: ha });
      else out.push({ nome, pasta: pastas.join(' › '), tipo: 'Ponto', centro: pt, ring: null, ha: 0, decl: null }); return; }
    out.push({ nome, pasta: pastas.join(' › '), tipo: 'Linha', ring: null, ha: 0, decl: null }); });
  return out; }
// GeoJSON: Polygon e MultiPolygon (o maior) viram polígono; Point com área nas propriedades vira pivô
function tgLerGeoJSON(texto){ let j; try{ j = JSON.parse(texto); }catch(e){ throw new Error('GeoJSON ilegível: o arquivo não é JSON válido.'); }
  const fs = j.type === 'FeatureCollection' ? (j.features || []) : (j.type === 'Feature' ? [j] : (j.type ? [{ type: 'Feature', properties: {}, geometry: j }] : []));
  if (!fs.length) throw new Error('Nenhuma feição no GeoJSON.'); const out = [];
  fs.forEach((f, i) => { const pr = f.properties || {}; const g = f.geometry || {};
    const nome = String(pr.name || pr.nome || pr.NOME || pr.Name || pr.talhao || pr.id || ('Feição ' + (i + 1))).trim();
    const decl = [pr.area_ha, pr.ha, pr.hectares, pr.area, pr.AREA_HA].map(Number).find(x => isFinite(x) && x > 0) || null;
    if (g.type === 'Polygon' || g.type === 'MultiPolygon'){ const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
      let best = null, bestA = -1; polys.forEach(pc => { const ring = (pc && pc[0] || []).map(p => [p[0], p[1]]); const a = tgAreaHa(ring); if (a > bestA){ best = ring; bestA = a; } });
      if (best && best.length >= 3) out.push({ nome, pasta: '', tipo: 'Polígono', ring: tgFechado(best), ha: tgAreaHa(best), decl }); return; }
    if (g.type === 'Point'){ const pt = [g.coordinates[0], g.coordinates[1]];
      if (decl) out.push({ nome, pasta: '', tipo: 'Pivô', centro: pt, ring: tgCirculo(pt[0], pt[1], tgRaioDeHa(decl)), ha: decl, decl });
      else out.push({ nome, pasta: '', tipo: 'Ponto', centro: pt, ring: null, ha: 0, decl: null }); return; }
    out.push({ nome, pasta: '', tipo: g.type || 'Sem geometria', ring: null, ha: 0, decl: null }); });
  return out; }
// MAPA-REAL F1 (proprietário, 18/10/2026: "quero baixar uma fazenda real kml para fazer os testes"): o .kmz que o Google Earth exporta é um zip
// com o doc.kml dentro. Abre no navegador (DecompressionStream 'deflate-raw'), sem biblioteca e sem rede: o arquivo não sai do aparelho.
async function tgKmzTexto(buf){ const u = new Uint8Array(buf), dv = new DataView(u.buffer, u.byteOffset, u.byteLength); let e = -1;
  for (let i = u.length - 22; i >= Math.max(0, u.length - 65557); i--){ if (dv.getUint32(i, true) === 0x06054b50){ e = i; break; } }
  if (e < 0) throw new Error('KMZ ilegível: o arquivo não é um .kmz válido.');
  const n = dv.getUint16(e + 10, true); let p = dv.getUint32(e + 16, true), alvo = null;
  for (let k = 0; k < n && p + 46 <= u.length; k++){ if (dv.getUint32(p, true) !== 0x02014b50) break;
    const met = dv.getUint16(p + 10, true), csz = dv.getUint32(p + 20, true), nl = dv.getUint16(p + 28, true), xl = dv.getUint16(p + 30, true), cl = dv.getUint16(p + 32, true), off = dv.getUint32(p + 42, true);
    const nome = new TextDecoder().decode(u.subarray(p + 46, p + 46 + nl));
    if (/\.kml$/i.test(nome) && (!alvo || /(^|\/)doc\.kml$/i.test(nome))) alvo = { met, csz, off };
    p += 46 + nl + xl + cl; }
  if (!alvo) throw new Error('O KMZ não tem arquivo .kml dentro.');
  if (dv.getUint32(alvo.off, true) !== 0x04034b50) throw new Error('KMZ ilegível: o arquivo não é um .kmz válido.');
  const ini = alvo.off + 30 + dv.getUint16(alvo.off + 26, true) + dv.getUint16(alvo.off + 28, true), dados = u.subarray(ini, ini + alvo.csz);
  if (alvo.met === 0) return new TextDecoder().decode(dados);
  if (alvo.met !== 8) throw new Error('KMZ com compactação não suportada: abra no Google Earth e salve como .kml.');
  if (typeof DecompressionStream !== 'function') throw new Error('Este navegador não abre KMZ: abra no Google Earth e salve como .kml.');
  return await new Response(new Blob([dados]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).text(); }
function tgLer(nomeArq, texto){ const n = String(nomeArq || '').toLowerCase();
  if (/\.kmz$/.test(n)) throw new Error('KMZ é compactado: o texto do .kml vem de tgKmzTexto (leitura assíncrona do arquivo).');
  if (/\.kml$/.test(n) || /^\s*</.test(texto)) return tgLerKML(texto);
  return tgLerGeoJSON(texto); }
// o que a feição importada vira: talhão (polígono ou pivô) ou registro da fazenda (perímetro, reserva, APP, água)
const TG_FAZ = /reserva|\bapp\b|perimetro|perímetro|\bcar\b|outorga|agua|água|limite|imovel|imóvel|arrendo|po[cç]o|nascente/i;
function tgDestino(f){ if (!f.ring) return 'Ignorar'; return TG_FAZ.test(tgNome(f.pasta + ' ' + f.nome)) ? 'Cadastro da fazenda' : 'Talhão'; }
