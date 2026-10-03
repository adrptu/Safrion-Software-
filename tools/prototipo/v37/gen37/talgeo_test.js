// Testes das funções puras de talgeo.js (JavaScriptCore): jsc talgeo_test.js
load('talgeo.js');
let ok = 0, falhas = [];
function chk(nome, cond, info){ if (cond) ok++; else falhas.push(nome + (info !== undefined ? ' · ' + JSON.stringify(info) : '')); print((cond ? 'OK  ' : 'FALHOU ') + nome); }
const Q = [[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01], [0, 0]];
chk('quadrado de 0,01° no equador ≈ 123,9 ha (excesso esférico)', Math.abs(tgAreaHa(Q) - 123.9) < 0.5, tgAreaHa(Q));
chk('anel com ou sem o ponto de fechamento dá a mesma área', Math.abs(tgAreaHa(Q) - tgAreaHa(Q.slice(0, 4))) < 1e-9);
chk('perímetro do quadrado ≈ 4.452 m', Math.abs(tgPerimetro(Q) - 4452.8) < 5, tgPerimetro(Q));
const C = tgCirculo(-46.5255, -17.7493, tgRaioDeHa(64));
chk('pivô de 64 ha desenhado pelo raio tem 64 ha (± 1 %)', Math.abs(tgAreaHa(C) - 64) / 64 < 0.01, tgAreaHa(C));
chk('raio de 64 ha = 451,4 m (igual ao KML do proprietário)', Math.abs(tgRaioDeHa(64) - 451.4) < 0.1, tgRaioDeHa(64));
chk('gravata (polígono que cruza a si mesmo) é recusada', tgAutoCruza([[0, 0], [1, 1], [1, 0], [0, 1]]) === true);
chk('quadrado não cruza a si mesmo', tgAutoCruza(Q) === false);
chk('pivô (72 lados) não cruza a si mesmo', tgAutoCruza(C) === false);
chk('ponto no meio está dentro; fora está fora', tgDentro([0.005, 0.005], Q) && !tgDentro([0.02, 0.005], Q));
const Q2 = Q.map(p => [p[0] + 0.005, p[1]]);
const sob = tgSobrepoeHa(Q2, Q); chk('quadrado deslocado pela metade sobrepõe ≈ 50 % (amostragem)', Math.abs(sob / tgAreaHa(Q2) - 0.5) < 0.04, sob);
chk('sem sobreposição longe', tgSobrepoeHa(Q.map(p => [p[0] + 1, p[1]]), Q) === 0);
chk('nome comparável sem acento e espaço duplo', tgNome('  Pivô   1 ') === 'PIVO 1');
chk('área declarada no texto: "Área: 64,5", "PIVÔ 1 - 64 ha", "Hectares: 30"', tgHaTexto('Área: 64,5') === 64.5 && tgHaTexto('PIVÔ 1 - 64 ha') === 64 && tgHaTexto('Pivô · área irrigada: 30') === 30);
chk('reserva legal vai para o cadastro da fazenda; pivô vira talhão; ponto sem área é ignorado',
  tgDestino({ ring: Q, pasta: 'RESERVA LEGAL', nome: 'RL 1' }) === 'Cadastro da fazenda' && tgDestino({ ring: C, pasta: 'PIVÔS', nome: 'PIVÔ 1' }) === 'Talhão' && tgDestino({ ring: null, pasta: '', nome: 'Sede' }) === 'Ignorar');
const gj = tgLerGeoJSON(JSON.stringify({ type: 'FeatureCollection', features: [
  { type: 'Feature', properties: { nome: 'Talhão Norte' }, geometry: { type: 'Polygon', coordinates: [Q] } },
  { type: 'Feature', properties: { name: 'Pivô 30', area_ha: 30 }, geometry: { type: 'Point', coordinates: [-46.5, -17.7] } },
  { type: 'Feature', properties: { name: 'Sede' }, geometry: { type: 'Point', coordinates: [-46.5, -17.7] } }] }));
chk('GeoJSON: polígono, pivô pela área da propriedade e ponto sem área', gj.length === 3 && gj[0].tipo === 'Polígono' && Math.abs(gj[0].ha - 123.9) < 0.5 && gj[1].tipo === 'Pivô' && Math.abs(gj[1].ha - 30) < 0.01 && gj[2].tipo === 'Ponto', gj.map(f => [f.nome, f.tipo, f.ha]));
let er = ''; try { tgLerGeoJSON('{nao é json'); } catch (e) { er = e.message; }
chk('GeoJSON ilegível dá erro que diz o que fazer', /não é JSON válido/.test(er), er);
er = ''; try { tgLer('mapa.kmz', 'PK..'); } catch (e) { er = e.message; }
chk('KMZ pede para salvar como .kml', /salve como \.kml/.test(er), er);
print('RESULTADO: ' + (falhas.length ? 'FALHOU' : 'OK') + ' ' + ok + '/' + (ok + falhas.length)); falhas.forEach(f => print(' - ' + f));
