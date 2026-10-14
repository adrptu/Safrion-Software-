# -*- coding: utf-8 -*-
"""PCM simplificado · rastreio F01–F111 (ESPECIFICACAO §4): cada função do inventário tem destino e existe nele.
Cada linha do §4 vira uma verificação: na tela (Chrome, tela MA e app), no código gerado (project/*.dc.html) ou na regra (window.__man).
"Sai" confere a ausência; 1b/1c confere a ponte rotulada "(simulado · …)" ou registra que fica para o passo (sem fingir que existe).
Ao fim confere que F01..F111 aparecem todas, uma vez cada (cada F tem destino).
Uso (de gen37/, depois de build.py e montar_render.py): python3 ma_rastreio_test.py"""
import sys, os, re, json, time
from ma_lib import MA
from ui37 import MENU2
from areas.maquinas import REDIRECIONA

HERE = os.path.dirname(os.path.abspath(__file__)); PJ = os.path.join(HERE, 'project')
SRC = {f: open(os.path.join(PJ, f), encoding='utf-8').read() for f in os.listdir(PJ) if f.endswith('.dc.html')}
MAS = SRC['MA.dc.html']
m = MA(1440, 1000); J = m.J
T = {}
ABRE = "(()=>{let n=0; [...document.querySelectorAll('#ma-painel button[aria-expanded=false], main .ma-bl>button[aria-expanded=false]')].forEach(b=>{b.click(); n++;}); return n;})()"
def cap(nome, ancora, perfil='Otávio', limpa=False, abrir=True, extra=None):
    m.ir(ancora, perfil=perfil, limpa=limpa)
    if abrir:
        for _ in range(3):
            if not J(ABRE): break
            time.sleep(.3)
    if extra: extra()
    T[nome] = (m.body() or '') + '\n' + (m.pan() or '')
    return T[nome]
FS = []; RES = []
def F(ids, destino, cond, info=''):
    ids = [x.strip() for x in ids.split(',')]
    FS.extend(ids); RES.append((ids, destino, bool(cond)))
    m.ok(cond, ' · '.join(ids) + ' → ' + destino, info)
def tem(k, *xs): return all(x.upper() in T[k].upper() for x in xs)   # rótulos em caixa alta pelo CSS
def nao(k, *xs): return not any(x.upper() in T[k].upper() for x in xs)
def emsrc(*xs, f='MA.dc.html'): return all(x in SRC[f] for x in xs)
try:
    cap('so', 'vis=semordem', limpa=True); cap('or', 'vis=ordens'); cap('at', 'vis=ativos'); cap('ab', 'vis=ativos&modo=abastecimentos'); cap('pl', 'vis=planos')
    cap('a01', 'ativo=a01'); cap('a02', 'ativo=a02'); cap('a11', 'ativo=a11'); cap('pm01', 'plano=PM-01'); cap('pm02', 'plano=PM-02')
    cap('om34', 'om=OM-0234'); cap('om33', 'om=OM-0233'); cap('om33ze', 'om=OM-0233', perfil='Zé'); cap('om28', 'om=OM-0228'); cap('om30', 'om=OM-0230')
    cap('ach', 'achado=INSP-104'); cap('venc', 'venc=PM-02|a03|s1')
    cap('cond11', 'ativo=a11', extra=lambda: (m.clk('Mudar condição'), time.sleep(.3)))
    cap('mais', 'vis=semordem', extra=lambda: m.clk('Mais ações'))
    nlin_pl = len(m.linhas(0)) if m.ir('vis=planos') is None else 0
    row_btn = {}
    for a in ('vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=ativos&modo=abastecimentos', 'vis=planos'):
        m.ir(a); row_btn[a] = J("[...document.querySelectorAll('[role=row][data-rid] button')].filter(b=>b.getClientRects().length&&!b.classList.contains('g2car')).length")
    m.ir('vis=ordens'); idlink = J("[...document.querySelectorAll('[role=row] a[href*=\"#om=\"],[role=row] a[href^=\"#om=\"]')].length")
    etp = 0
    for a in ('vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=planos', 'plano=PM-01'):
        m.ir(a); etp += J("document.querySelectorAll('.etp-ind,nav[aria-label=\"Telas da manutenção\"]').length") or 0
    m.ir('vis=ordens'); m.clk('Kanban'); kan = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"]>*')].filter(e=>e.getClientRects().length).length")
    m.ir('vis=semordem'); m.clk('Gerar 3 ordens preventivas'); m.ir('vis=semordem'); so2 = m.body(); m.ir('ativo=a03'); a03 = m.body() + m.pan()
    exe = J("(()=>{ try{ const M=window.__man; const c=M.manClone(M.manGet()); c.oms['OM-0237'].executante=''; M.manLiberar(c,'OM-0237',false,'Otávio',{executante:'',tempo:'4'}); return 'liberou'; }catch(e){ return e.message; } })()")
    cap('om35', 'om=OM-0235')
    gerar_rows = [r for r in (m.linhas(0) or [])]
    # ---------- F01–F111 ----------
    g = [x for x in MENU2 if x[0] == 'Manutenção'][0]
    F('F01', 'menu com 4 subitens da mesma tela (13/10, pedido do proprietário); Índice sem MA-01..05 nem PM', g[2] == [('Painel','PMAN.dc.html'),('Pendências sem ordem','MA.dc.html#vis=semordem'),('Ordens de manutenção','MA.dc.html#vis=ordens'),('Ativos e disponibilidade','MA.dc.html#vis=ativos'),('Planos preventivos','MA.dc.html#vis=planos')] and not re.search(r'(MA-0[1-5]|PM)\.dc\.html', SRC['Main.dc.html']))
    F('F02, F03', 'Sai: faixa e "3 etapas" do PM', etp == 0 and 'Telas da manutenção' not in MAS and nao('pm01', 'Etapa 1', 'Biblioteca de planos'), etp)
    F('F04', 'detalhe do plano: "‹ Planos" e "Publicar vN"', tem('pm01', '‹ Planos') and "'Publicar v'+" in MAS)
    F('F05', 'menu ⋯ do cabeçalho com Restaurar', tem('mais', 'Restaurar demonstração'))
    F('F06, F07', 'endereços e redirecionamentos; Tab preso só no painel aberto pelo usuário', len(REDIRECIONA) == 7 and all(f in SRC for f in REDIRECIONA) and "pan_role" in MAS and 'complementary' in MAS)
    F('F08, F09, F10', 'visão Planos (grade, filtro Grupo, "4 ativos sem plano"); filtro "Sem plano" em Ativos', tem('pl', '4 ativos sem plano', 'Todos os grupos', 'PM-10') and tem('at', 'Sem plano'))
    F('F11, F12, F13, F14, F15, F16, F17, F19, F20, F23, F24', 'detalhe do plano e painéis Serviço, Novo/Editar plano e Publicar',
      tem('pm01', 'Incluir serviço', 'Editar plano', 'Versões', 'Inativar plano', 'tarefas') and all(x in MAS for x in ('id="sv_nome"', 'id="np_nome"', 'id="vk_data"', 'Novo plano')))
    F('F18', 'expandir por serviço; "Expandir tudo" sai', 'Mostrar checklist e peças de' in MAS and nao('pm01', 'Expandir tudo'))
    F('F21', 'detalhe do plano › Ativos vinculados só leitura (sem Gerar)', tem('pm01', 'ATIVOS VINCULADOS · SÓ LEITURA') and 'Gerar' not in T['pm01'].split('ATIVOS VINCULADOS')[1].split('Versões')[0])
    F('F22', 'painel Vínculo com marco pré-preenchido (D-41)', 'o marco é a última execução do serviço' in MAS and 'manMarcoSug' in MAS)
    # MAN-LIMPA-01 (14/10): os cartões saem da tela de trabalho (indicadores no Painel); o recorte vai pela faixa Filtros (Tipo, Criticidade, Grupo)
    F('F25, F26', 'Sem ordem com a faixa Filtros (Tipo) e sem cartões; selo de impedimentos; filtro "Com conflito" em Ordens', tem('so', 'Todos os tipos', '1 ativo bloqueado') and nao('so', 'VENCIDAS SEM ORDEM') and tem('or', 'Com conflito'))
    F('F27, F28, F29', 'Sem ordem (até 30 d) e bloco "O que vence" do ativo', tem('so', 'Até 30 d', 'Vencida') and tem('a02', 'O que vence'))
    F('F30', 'item com OM sai de Sem ordem; o ativo mostra a OM', 'PM-02 v2' not in so2 and 'OM-0235' in a03 and tem('at', 'OM-0234 · A liberar'))
    F('F31, F32', 'painel do vencimento; primária de Sem ordem; sem "Ver ordens"', tem('venc', 'Gerar ordem preventiva') and 'Gerar 3 ordens preventivas' in T['so'] and nao('so', 'Ver ordens ›'))
    F('F33, F55, F83', 'OM › Janela e equipe › Impacto na produção (AL)', tem('om34', 'Impacto na produção', 'lido da alocação do PCP'))
    F('F34', '"Mover janela" para toda OM a liberar/liberada', tem('om34', 'Mover janela') and tem('om28', 'Mover janela'))
    F('F35', '1b: "Pedir decisão da gerência" (fica para o 1b; hoje a ponte "Liberar mesmo assim")', tem('om34', 'Liberar mesmo assim'))
    F('F36, F37, F38', 'sem o cartão "Aptos agora"; colunas Leitura e Condição; filtro de condição', nao('at', 'APTOS AGORA') and tem('at', 'LEITURA', 'CONDIÇÃO', 'Bloqueado 1'))
    F('F39, F40', 'agenda lida de AL no detalhe; "Elegíveis" sai', tem('a01', 'AGENDA DA SEMANA (O.S. › RECURSOS)') and 'Elegíve' not in MAS)
    F('F41', 'colunas Próxima manutenção e Em aberto', tem('at', 'PRÓXIMA MANUTENÇÃO', 'EM ABERTO'))
    F('F42, F44', 'Sai: uso 30 d fixo', 'Uso 30 d' not in MAS and 'Horas trabalhadas 30 d' not in MAS)
    F('F43, F54', 'painel Condição (Bloquear, Restringir, Encerrar restrição, responsável técnico)', tem('cond11', 'Encerrar restrição', 'Trocar responsável técnico', 'Bloquear') and 'Restringir' in MAS and tem('a01', 'RESPONSÁVEL TÉCNICO'))
    F('F45, F46, F57, F82, F102', 'Sai: navegação repetida e selos fixos', not any(x in MAS for x in ('1 bloqueio ativo', '3 de alta criticidade', '1 desvio a investigar', '1 bloqueado · 1 restrito')))
    F('F47, F48', 'Sem ordem › Tipo Inspeção (antes o chip Achados) sem o cartão; bloco Achados do ativo', nao('so', 'ACHADOS CRÍTICOS SEM AÇÃO') and tem('so', 'Inspeção') and tem('a02', 'Achados'))
    F('F49', '"Registrar achado" (Sem ordem e ativo) com componente; app MB-04', tem('so', 'Registrar achado') and tem('a02', 'Registrar achado') and emsrc('Componente', 'Pode operar?', f='MB-04.dc.html'))
    F('F50, F51, F52', 'painel do achado: Vincular · Gerar com o achado · Criar ordem corretiva · Fechar sem serviço', tem('ach', 'Vincular à OM-0234', 'Criar ordem corretiva', 'Fechar sem serviço') and tem('so', 'Gerar ordem preventiva com NC-0912'))
    F('F53', 'IDs como links #om=', (idlink or 0) > 0 and '#om=' in MAS)
    F('F56', 'Sai: KPI-PCM-07 fixo (Pareto)', 'Pareto' not in MAS)
    F('F58', 'Sai: cartões de fase (fase só nos chips)', (kan or 0) == 5 and tem('or', 'A liberar 1', 'Em conferência 1') and nao('or', 'ORDENS EM EXECUÇÃO'))
    F('F59, F60, F61', 'Ordens: chips de fase, Lista e Kanban (ícones com nome; o Kanban abre pelo ícone), colunas Pendência e Executante', (kan or 0) == 5 and tem('or', 'PENDÊNCIA', 'EXECUTANTE'))
    F('F62', 'comando só no painel (nenhum botão nas linhas)', all(v == 0 for v in row_btn.values()), row_btn)
    F('F63', 'Sai: link de bloco', 'Ver todas as ordens' not in MAS)
    F('F64, F65, F84, F85, F93', 'painel da OM: cabeçalho, faixa de continuidade, primária', tem('om34', 'OM-0234 · Trator 02', 'VEIO DE', 'ESTÁ AQUI', 'FALTA', 'PRÓXIMA AÇÃO'))
    F('F66', '"Liberar serviço" exige executante (com uma pessoa habilitada, ela vem pré-escolhida: AC-PCM-31)', "'Falta: executante'" in MAS and 'Liberar serviço' in MAS and exe == 'liberou', exe)
    F('F67', '1b: selo "Falta peça" com dono (SC → CMP#sol= no 1b)', 'Falta peça' in T['om35'])
    F('F68, F69, F78', 'Módulo no 1b/1c; até lá pontes rotuladas para o Otávio', all(x in MAS for x in ('Solicitar compra (simulado · Compras recebe no 1c)', 'Registrar recebimento (simulado · papel do Almoxarifado)', 'Resolver sobras (simulado · papel do Almoxarifado)')))
    F('F70', 'painel da OM; cartão do MB-01', tem('om33', 'OM-0233 · Trator T1') and emsrc('mbOmCard', 'Continuar serviço', f='MB-01.dc.html'))
    F('F71, F86', 'tarefas por tipo; "Incluir tarefa" em Corretiva e Pendência', tem('om33', 'Serviço', 'Teste', 'Incluir tarefa'))
    F('F72', 'Sai: pré-marcar como feito', 'Marcar pendentes' not in MAS and 'Marcar todos' not in MAS)
    F('F73, F74, F97', 'função única de leitura; trava e aviso na conclusão; decisão no painel da leitura', tem('om33ze', 'Leitura do horímetro') and all(x in MAS for x in ('Confirmar troca de contador', 'Concluir com esta leitura', 'Descartar')))
    F('F75', 'chip "Previsto" ou valor digitado', tem('om33ze', 'Previsto (6,5 h)'))
    F('F76', 'Peças: Planejado · Situação · Aplicado', all(x in MAS for x in ('Planejado', 'Situação', 'Aplicado')))
    F('F77, F90', '"Concluir serviço", uma regra', tem('om33', 'Concluir serviço'))
    F('F79, F92', '"Encerrar ordem · R$ x", uma regra', "'Encerrar ordem · '" in MAS)
    F('F80, F81', 'Origem no painel; Pendência por "Não feito"', tem('om33', 'Origem', 'SM-0147') and "'Pendência da '" in MAS)
    F('F87', 'Sai: só mensagem (cada resposta grava)', 'Registrar avanço' not in MAS and 'Salvar checklist' not in MAS)
    F('F88, F89', 'Teste com tentativas; Declarar apto / Manter', tem('om33', '1ª tentativa · Reprovado') and "'Declarar '" in MAS and "'Manter '" in MAS)
    F('F91', 'peças retiradas exigidas no Encerrar', tem('om33', 'Peças retiradas', 'Bomba hidráulica usada') and 'destino e responsável de ' in MAS)
    F('F94', 'Sai: tanque fixo', 'Tanque Sede 38' not in MAS)
    # revisão 09/10 (A10): a coluna passou de "Consumo L/h" a "Consumo" e a unidade (L/h ou km/L, pelo contador) vai na célula
    F('F95, F96', 'modo Abastecimentos; painel da leitura; app MB-09', tem('ab', 'AB-1042', 'CONSUMO', '16,4 L/h') and emsrc('Registrar abastecimento', 'Salvar e registrar outro', f='MB-09.dc.html'))
    F('F98, F99', 'Sai: conferir/desvio fixos (desvio é filtro e achado)', 'Investigar desvio' not in MAS and tem('at', 'Desvio de consumo'))
    F('F100, F101', '"Corrigir com estorno"; coluna Consumo', 'Corrigir com estorno' in MAS and tem('at', 'CONSUMO'))
    F('F103, F104', 'MB-01, MB-09 "Máquina", MB-09det = painel da OM, MB-04 → achado; sem sinal',
      emsrc('mbOmsDe', f='MB-01.dc.html') and emsrc('Não opere', 'manAppCmd', f='MB-09.dc.html') and emsrc('Anexar foto e registrar', 'manAppSinal', f='MB-09det.dc.html') and emsrc("'achado'", f='MB-04.dc.html'))
    lk = [f for f, s in SRC.items() if 'MA.dc.html#om=OM-0233' in s and f != 'MA.dc.html']; lk2 = [f for f, s in SRC.items() if 'MA.dc.html#ativo=' in s and f != 'MA.dc.html']
    F('F105, F106, F109, F111', 'links de fora direto ao registro (MA#om=, MA#ativo=, …)', len(lk) >= 2 and len(lk2) >= 1, [lk, lk2])
    F('F107, F108', 'CD-03 e O.S. leem a condição única; calibração no CD-03', emsrc('c3man', 'Leitura do horímetro', f='CD-03.dc.html') and emsrc('osManCond', f='OS.dc.html'))
    F('F110', '1c: Compras recebe a SC de manutenção (fica para o 1c; hoje "Solicitar compra (simulado · Compras recebe no 1c)")', 'Compras recebe no 1c' in MAS)
    # cada F01..F111 aparece uma vez
    todos = ['F%02d' % i if i < 100 else 'F%d' % i for i in range(1, 112)]
    falta = [x for x in todos if x not in FS]; dup = sorted({x for x in FS if FS.count(x) > 1})
    m.ok(not falta and not dup and len(FS) == 111, f'cobertura: F01..F111 com destino, uma vez cada ({len(set(FS))}/111)', [falta, dup])
    m.sem_erro('fim')
finally:
    rc = m.fim()
sys.exit(rc)
