// Teste de talgeo.js (CAMADA-SINTETICA-01; refeito sem coordenada real): área geodésica, círculo do pivô, perímetro, ponto dentro,
// sobreposição, contorno que cruza a si mesmo, leitura de GeoJSON e destino da feição importada.
// Os pivôs vêm de dados_lagoa_fonte (sintéticos fora do Mac). Uso (de gen37/): node talgeo_test.js
const fs = require('fs'), path = require('path'), vm = require('vm'), { execFileSync } = require('child_process');
const HERE = __dirname;
vm.runInThisContext(fs.readFileSync(path.join(HERE, 'talgeo.js'), 'utf8') + '\nglobalThis.TG={tgAreaHa,tgCirculo,tgRaioDeHa,tgPerimetro,tgDentro,tgSobrepoeHa,tgAutoCruza,tgFechado,tgLerGeoJSON,tgLer,tgDestino,tgHaTexto,tgNome};');
const DIR = execFileSync('python3', ['-c', 'import dados_lagoa_fonte as F; print(F.DIR)'], { cwd: HERE, encoding: 'utf8' }).trim();
const GJ = JSON.parse(fs.readFileSync(path.join(DIR, 'lagoa_pivos.geojson'), 'utf8'));
const PV = JSON.parse(fs.readFileSync(path.join(DIR, 'lagoa_s2_resumo.json'), 'utf8')).pivos;
const ok = []; const chk = (n, c, i) => { ok.push(!!c); console.log((c ? 'OK    ' : 'FALHOU ') + n + (c ? '' : ' · ' + JSON.stringify(i).slice(0, 300))); };
const anel = id => GJ.features.find(f => f.properties.id === id).geometry.coordinates[0];
// quadrado de lado L metros com centro (lon, lat)
const quad = (lon, lat, L) => { const k = 111320 * Math.cos(lat * Math.PI / 180), h = L / 2; return TG.tgFechado([[lon - h / k, lat - h / 110540], [lon + h / k, lat - h / 110540], [lon + h / k, lat + h / 110540], [lon - h / k, lat + h / 110540]]); };

// 1 · círculo de cada pivô: área ≈ declarada (< 1 %, ver camada_test item 5), igual ao círculo refeito pelo centro e pela área
const e1 = PV.map(p => Math.abs(TG.tgAreaHa(anel(p.id)) - p.ha) / p.ha), e1b = PV.map(p => Math.abs(TG.tgAreaHa(TG.tgCirculo(p.lon, p.lat, TG.tgRaioDeHa(p.ha))) - TG.tgAreaHa(anel(p.id))));
chk('1 23 pivôs: área do círculo ≈ ha declarado (< 1 %) e = círculo refeito (< 0,01 ha)', PV.length === 23 && Math.max(...e1) < 0.01 && Math.max(...e1b) < 0.01, [Math.max(...e1), Math.max(...e1b)]);
// 2 · perímetro ≈ 2πr
const e2 = PV.map(p => Math.abs(TG.tgPerimetro(anel(p.id)) - 2 * Math.PI * p.r_m) / (2 * Math.PI * p.r_m));
chk('2 perímetro do círculo ≈ 2πr (< 1 %)', Math.max(...e2) < 0.01, Math.max(...e2));
// 3 · centro dentro do próprio pivô e fora de todos os outros
const e3 = PV.filter(p => !TG.tgDentro([p.lon, p.lat], anel(p.id)) || PV.some(q => q.id !== p.id && TG.tgDentro([p.lon, p.lat], anel(q.id))));
chk('3 centro de cada pivô dentro do próprio círculo e fora dos outros', e3.length === 0, e3.map(p => p.id));
// 4 · pivôs vizinhos não se sobrepõem
let sob = 0; PV.forEach((p, i) => PV.slice(i + 1).forEach(q => { sob += TG.tgSobrepoeHa(anel(p.id), anel(q.id)); }));
chk('4 nenhum par de pivôs se sobrepõe (soma 0 ha)', sob === 0, sob);
// 5 · quadrado de 200 m no centro de um pivô: 4 ha, sobreposição ≈ 4 ha; o mesmo quadrado longe dos pivôs: 0
const p5 = PV[4], q5 = quad(p5.lon, p5.lat, 200), far = quad(p5.lon, p5.lat - 0.2, 200);
chk('5 quadrado de 200 m: 4 ha (< 1 %, mesma escala do item 1); dentro de ' + p5.id + ' sobrepõe ≈ 4 ha; longe, 0', Math.abs(TG.tgAreaHa(q5) - 4) / 4 < 0.01 && Math.abs(TG.tgSobrepoeHa(q5, anel(p5.id)) - 4) / 4 < 0.02 && TG.tgSobrepoeHa(far, anel(p5.id)) === 0,
  [TG.tgAreaHa(q5), TG.tgSobrepoeHa(q5, anel(p5.id))]);
// 6 · contorno em gravata cruza a si mesmo; círculo não
const g = q5.slice(0, 4); const gravata = TG.tgFechado([g[0], g[2], g[1], g[3]]);
chk('6 tgAutoCruza: gravata sim, círculo do pivô não', TG.tgAutoCruza(gravata) && !TG.tgAutoCruza(anel(p5.id)));
// 7 · GeoJSON da fazenda: 23 polígonos com a área; ponto com área nas propriedades vira pivô; arquivo inválido explica
const lidos = TG.tgLerGeoJSON(JSON.stringify(GJ)); const pt = TG.tgLerGeoJSON(JSON.stringify({ type: 'Feature', properties: { nome: 'Pivô novo', area_ha: 50 }, geometry: { type: 'Point', coordinates: [p5.lon, p5.lat - 0.2] } }))[0];
let erro = ''; try { TG.tgLerGeoJSON('{x'); } catch (e) { erro = e.message; }
chk('7 tgLerGeoJSON: 23 polígonos (ha ≈ declarado), ponto + area_ha = pivô de 50 ha, JSON inválido explica', lidos.length === 23 && lidos.every((f, i) => f.tipo === 'Polígono' && Math.abs(f.ha - PV[i].ha) / PV[i].ha < 0.01)
  && pt.tipo === 'Pivô' && Math.abs(TG.tgAreaHa(pt.ring) - 50) / 50 < 0.01 && /GeoJSON ilegível/.test(erro), [lidos.length, pt && pt.tipo, erro]);
// 8 · destino: reserva/APP/água vão ao cadastro da fazenda; pivô vira talhão; KMZ é recusado com orientação
let kmz = ''; try { TG.tgLer('fazenda.kmz', ''); } catch (e) { kmz = e.message; }
chk('8 tgDestino e KMZ: "Reserva legal" e "Outorga" → cadastro da fazenda; "Pivô 3" → talhão; .kmz recusado', TG.tgDestino({ ring: q5, nome: 'Reserva legal', pasta: '' }) === 'Cadastro da fazenda'
  && TG.tgDestino({ ring: q5, nome: 'Ponto', pasta: 'Outorga' }) === 'Cadastro da fazenda' && TG.tgDestino({ ring: q5, nome: 'Pivô 3', pasta: '' }) === 'Talhão' && /KMZ/.test(kmz), kmz);
console.log('RESULTADO: ' + ok.filter(Boolean).length + '/' + ok.length);
process.exit(ok.every(Boolean) ? 0 : 1);
