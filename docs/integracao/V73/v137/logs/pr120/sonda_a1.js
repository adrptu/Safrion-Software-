// Sonda do revisor (Claude): contraexemplo do A1 e casos de borda extras, nos dois núcleos
const H=3600000, D=Date.UTC(2026,9,18);
const dir=process.argv[2]; const {frAgenda}=require(dir+'/frentes_agenda.js');
const base={inicio:D+7*H, velocidadeKmh:20, fonte:'sintética', turnos:[[D+7*H,D+17*H],[D+31*H,D+41*H]]};
const os=(id,ha,a,b,km)=>({id,areaHa:ha,rendimentoHaH:1,janelaInicio:D+a*H,janelaFim:D+b*H,kmAnterior:km});
const hh=t=>t===null?null:((t-D)/H);
const show=(n,r)=>console.log(n, r.status, r.motivo, JSON.stringify(r.linhas.map(l=>({id:l.id,ch:hh(l.chegada),ini:hh(l.inicio),fim:hh(l.fim),esp:l.esperaMs/H,pau:l.pausaMs/H}))));
show('A1 contraexemplo', frAgenda([os('A',1,7,17,0),os('B',2,10,12,20)],base));
show('E1 chega depois da janela', frAgenda([os('A',9,7,17,0),os('B',1,10,12,20)],base));
show('E2 viagem atravessa a noite', frAgenda([os('A',9.5,7,17,0),os('B',1,7,48,20)],base));
show('E3 janela no dia seguinte (espera em turno + pausa noturna)', frAgenda([os('A',1,7,17,0),os('B',1,33,40,20)],base));
show('E4 viagem sem turno', frAgenda([os('A',10,7,17,0),os('B',1,7,48,400)],{...base,turnos:[[D+7*H,D+17*H]]}));
show('E5 km 0 e janela já aberta', frAgenda([os('A',2,7,17,0),os('B',2,7,17,0)],base));
