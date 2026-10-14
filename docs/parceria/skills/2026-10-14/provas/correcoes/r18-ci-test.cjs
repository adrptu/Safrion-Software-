const fs=require('fs'),YAML=require(process.env.CI_YAML_MODULE||'yaml');
const s=fs.readFileSync(process.argv[2],'utf8'),c=[];const ck=(name,ok)=>c.push({name,ok:!!ok});let d={};try{d=YAML.parse(s);ck('YAML válido',true)}catch{ck('YAML válido',false)}
const refs=[...s.matchAll(/uses:\s*([^\s#]+)/g)].map(x=>x[1]);ck('Actions em SHA completo',refs.length&&refs.every(x=>/^[\w./-]+@[a-f0-9]{40}$/.test(x)));
ck('Workflow não concede escrita',!s.includes('pull-requests: write')&&!s.includes('security-events: write')&&s.includes('permissions: {}'));
ck('Cada job só lê contents',d.jobs&&Object.values(d.jobs).every(j=>JSON.stringify(j.permissions)==='{"contents":"read"}'));
const images=[...s.matchAll(/(?:image:\s*|^\s+)((?:ghcr.io\/)?(?:library\/)?(?:postgres|redis|aquasec\/trivy|semgrep\/semgrep|zricethezav\/gitleaks|google\/osv-scanner)(?:@sha256:[a-f0-9]{64}|:[\w.-]+)?)(?=\s|$)/gm)].map(x=>x[1]);ck('Seis imagens em digest',images.length===6&&images.every(x=>x.includes('@sha256:')));
ck('Scanner não recebe socket Docker',!s.includes('/var/run/docker.sock'));
ck('Checkout não persiste token',d.jobs&&Object.values(d.jobs).flatMap(j=>j.steps||[]).filter(s=>s.uses?.startsWith('actions/checkout@')).every(s=>s.with?.['persist-credentials']===false));
ck('Cobertura só no resumo',s.includes('comment-on: none'));console.log(JSON.stringify(c,null,2));console.log(`${c.filter(x=>x.ok).length}/${c.length}`);process.exit(c.every(x=>x.ok)?0:1);
