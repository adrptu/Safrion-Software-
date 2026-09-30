p='areas/mobile.py'; s=open(p,encoding='utf-8').read()
def rep(a,b,tag,n=1):
    global s
    c=s.count(a); assert c==n, f'{tag}: {c}'
    s=s.replace(a,b)
rep("  Recomendação seguinte fora da política = OS-0422 (13,5 mm > 12,0 mm).", "  Próximo ciclo = OS-0422 (13,5 mm em 2 passadas de 6,75 mm · janela a definir), sem aprovação do agrônomo.", 'doc')
rep("Irrigação · água por política',[", "Irrigação · água',[", 'titulo', n=2)
rep("chips(etapa('Liberadas'),tag(f'política {POL[\"id\"]}'),tag(IRR['lib'])),", "chips(etapa('Liberadas'),tag('necessidade do balanço'),tag(IRR['lib'])),", 'mb01')
rep("chips(etapa('Liberadas'),tag(f'política {POL[\"id\"]}')),", "chips(etapa('Liberadas'),tag('necessidade do balanço')),", 'mb02')
rep("""      + card('Autorização por política',[
          kv('Política/versão',f'{POL["id"]} · lâmina máx. {br(POL["lamina_max"])} mm · intervalo mín. {POL["intervalo_min"]} · validade {POL["validade"]}'),
          chips(chip(f'Autorizada pela política · {IRR["au"]}','green'),tag(IRR['lib'])),
          note('Evento rastreável, sem assinatura diária. Água só-água: <b>sem materiais</b>, sem requisição, sem custódia e sem devolução.')],state='blue',
          desc='Confira o limite da política antes de iniciar.')""",
"""      + card('Lâmina que a cultura precisa',[
          kv('Origem',f'balanço de 23/09 · déficit 11,2 mm → {br(P["lamina_aplicada"])} mm brutos em 1 passada (máx. {br(POL["lamina_max"])} mm por passada)'),
          chips(chip(f'Liberada sem aprovação · {IRR["au"]}','green'),tag(IRR['lib'])),
          note('Água sem produto: <b>sem materiais</b>, sem requisição, sem custódia e sem devolução.')],state='blue',
          desc='Confira a lâmina antes de iniciar.')""", 'mb08-card')
rep("say('Próximo setor','Sem outro setor liberado hoje · a OS-0422 (13,5 mm) aguarda revisão individual.','pivot','Ver o próximo setor liberado'))",
    "say('Próximo setor','Sem outro setor liberado hoje · a OS-0422 (13,5 mm em 2 passadas) libera quando a janela for definida.','pivot','Ver o próximo setor liberado'))", 'mb08-prox')
rep("""      + card('Se a recomendação sair da política',[
          note(f'Recomendação seguinte de <b>13,5 mm (OS-0422) &gt; máx. {br(POL["lamina_max"])} mm</b>: sem autorização automática — a tarefa nasce <b>A liberar</b> aguardando revisão individual, e a política não se altera por aprovar a exceção.'),
          note('Fertirrigação (OS-0418) mantém aprovação individual do agrônomo, com materiais e requisição próprios.')],state='yellow',
          desc='Saiba o que muda quando a lâmina passa do limite.')""",
"""      + card('Próximo ciclo',[
          note(f'<b>13,5 mm (OS-0422)</b> passam do máximo de {br(POL["lamina_max"])} mm por passada: o sistema divide em <b>2 passadas de 6,75 mm</b>. Sem aprovação; libera quando a janela for definida.'),
          note('Só a fertirrigação (OS-0418) vai ao agrônomo, com materiais e requisição próprios.')],state='gray',
          desc='Veja como fica a próxima lâmina.')""", 'mb08-prox-card')
rep("emit('MB-08','Irrigação de hoje','OS-0419 · Pivô 2 · água por política · sem emissão manual',", "emit('MB-08','Irrigação de hoje','OS-0419 · Pivô 2 · água · sem emissão manual',", 'mb08-emit')
rep("vstep([(f'Autorização por política · {IRR[\"au\"]}','done'),", "vstep([(f'Lâmina pelo balanço · {IRR[\"au\"]}','done'),", 'recibo-step')
rep("kv('Autorização',f'{IRR[\"au\"]} · política {POL[\"id\"]} · memória do limite'),", "kv('Origem da lâmina',f'{IRR[\"au\"]} · balanço de 23/09 · memória de cálculo'),", 'recibo-kv')
rep("note(f'<b style=\"color:{INK};\">{O419[\"id\"]} · água por política</b> não aparece aqui:", "note(f'<b style=\"color:{INK};\">{O419[\"id\"]} · água</b> não aparece aqui:", 'mb05')
open(p,'w',encoding='utf-8').write(s); print('patch mobile irrigação ok')
