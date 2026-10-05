const {X,mk}=require('../motor345/h.js');
const s=mk('S2627',5); X.PREVALS(s,{});
console.log(X.g2rows(s,X.GR('g_saf')).map(r=>[r.id,r.v.nome,r.v.faz,r.v.estado,r.v.ini,r.v.fim,!!r.ro].join(' | ')).join('\n'));
console.log(JSON.stringify(X.g2rows(s,X.GR('g_recp_maq')).map(r=>[r.id,r.v])));
console.log(JSON.stringify(X.g2rows(s,X.GR('g_recp_pes')).map(r=>[r.id,r.v])));
console.log(X.D2.meses.map(m=>m.join(':')).join(' '), JSON.stringify(X.D2.dias), X.D2.hoje);
