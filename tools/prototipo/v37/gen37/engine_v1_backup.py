import re, html
import json, os, datetime
ROOT=os.path.dirname(os.path.abspath(__file__))
P=os.path.join(ROOT,'project'); os.makedirs(P,exist_ok=True)

INK='#15201A'; MUTED='#65736A'; LINE='#E4E9E5'; BG='#F4F6F3'; SURF='#FFFFFF'; ACC='#1E7A4C'; ACCS='#E4F3E9'; SH='0 1px 2px rgba(21,32,26,.04), 0 10px 24px -18px rgba(21,32,26,.22)'
SIDE='#0F241A'; SIDE_TX='#D3E2D8'; SIDE_MUTED='#86A08F'; DISP="'Sora', 'Manrope', system-ui, sans-serif"
YEL='#8A5A00'; YELS='#FFF3D6'; RED='#B42318'; REDS='#FDE8E6'; GRAY='#5B6660'; GRAYS='#EEF1EE'
FONT="'Manrope', system-ui, sans-serif"
MODS=['Cadastros','Indicadores','Agronomia','PCP','PCM','PCE','Compras','Campo','Irrigação','Oficina','Estoque','Colheita','Beneficiamento','Vendas','Mercado','Logística']

ICONS={
 'Início':'M3 10l9-7 9 7v10a2 2 0 0 1-2 2h-4v-7H9v7H5a2 2 0 0 1-2-2z',
 'Cadastros':'M12 2l9 5-9 5-9-5 9-5zM3 12l9 5 9-5M3 17l9 5 9-5',
 'Agronomia':'M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 20 3c1 2 2 4.5 2 8.5S16.8 21 12.5 21zM2 21c0-3 1.85-5.36 5.08-6',
 'PCP':'M3 5h18v16H3zM16 3v4M8 3v4M3 10h18',
 'PCM':'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z',
 'Compras':'M6 6h15l-1.5 9h-12zM6 6L5 2H2M10 20a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM19 20a1 1 0 1 1-2 0 1 1 0 0 1 2 0z',
 'Campo':'M9 4l6 2 6-2v14l-6 2-6-2-6 2V6zM9 4v14M15 6v14',
 'Irrigação':'M12 2.7s6 6.3 6 10.3a6 6 0 0 1-12 0c0-4 6-10.3 6-10.3z',
 'Oficina':'M20 7h-3a2 2 0 0 1-2-2V2M9 22H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2h-3M9 15l3 3-3 3M14 21h-4',
 'Colheita':'M12 22V9M12 9c-3 0-5-2-5-5 3 0 5 2 5 5zM12 9c3 0 5-2 5-5-3 0-5 2-5 5zM12 15c-3 0-5-2-5-5 3 0 5 2 5 5zM12 15c3 0 5-2 5-5-3 0-5 2-5 5z',
 'Beneficiamento':'M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8',
 'Vendas':'M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8zM7 7h.01',
 'Logística':'M1 3h15v13H1zM16 8h4l3 3v5h-7zM7.5 21a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM18.5 21a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
 'Controle':'M3 3v18h18M7 14l4-4 4 4 5-6',
 'Mercado':'M3 17l6-6 4 4 8-8M14 7h7v7',
}
ICONS.update({'Indicadores':ICONS['Controle'],'PCE':ICONS['PCP'],'Estoque':ICONS['Beneficiamento'],
 'lista':'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01',
 'doc':'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8',
 'calc':'M4 2h16v20H4zM8 6h8M8 10h2M12 10h2M16 10h2M8 14h2M12 14h2M16 14h2M8 18h2M12 18h6',
 'lab':'M9 3h6M10 3v6L4 20a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1L14 9V3',
 'trend':'M3 17l6-6 4 4 8-8M14 7h7v7',
 'map':'M9 4l6 2 6-2v14l-6 2-6-2-6 2V6zM9 4v14M15 6v14',
 'users':'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
 'pivot':'M12 12m-9 0a9 9 0 1 0 18 0 9 9 0 1 0-18 0M12 3v9l6 6',
 'cash':'M2 7h20v10H2zM12 12m-3 0a3 3 0 1 0 6 0 3 3 0 1 0-6 0M6 12h.01M18 12h.01',
 'clock':'M12 12m-9 0a9 9 0 1 0 18 0 9 9 0 1 0-18 0M12 7v5l3 3',
 'alert':'M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0zM12 9v4M12 17h.01',
 'cart':'M6 6h15l-1.5 9h-12zM6 6L5 2H2M10 20a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM19 20a1 1 0 1 1-2 0 1 1 0 0 1 2 0z',
 'box':'M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8',
 'card':'M2 5h20v14H2zM2 10h20M6 15h4',
 'fuel':'M3 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18M3 22h12M15 10h2a2 2 0 0 1 2 2v5a2 2 0 0 0 4 0V9l-3-3M5 10h8',
 'scale':'M12 3v18M4 7h16M6 7l-3 7a3 3 0 0 0 6 0zM18 7l-3 7a3 3 0 0 0 6 0z',
 'tag':'M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8zM7 7h.01',
 'truck':'M1 3h15v13H1zM16 8h4l3 3v5h-7zM7.5 21a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM18.5 21a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
 'check':'M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11',
 'grid':'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
 'drop':'M12 2.7s6 6.3 6 10.3a6 6 0 0 1-12 0c0-4 6-10.3 6-10.3z',
 'wrench':'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z',
 'leaf':'M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 20 3c1 2 2 4.5 2 8.5S16.8 21 12.5 21zM2 21c0-3 1.85-5.36 5.08-6',
 'calendar':'M3 5h18v16H3zM16 3v4M8 3v4M3 10h18',
 'layers':'M12 2l9 5-9 5-9-5 9-5zM3 12l9 5 9-5M3 17l9 5 9-5',
})
def icon(name,size=16,color='currentColor'):
    if name=='Mapa': name='map' if 'map' in ICONS else 'Início'
    d=ICONS.get(name,'M4 4h16v16H4z')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink: 0;"><path d="{d}"/></svg>'
MODHOME={'Indicadores':'Indicadores.dc.html','PCE':'HomePCE.dc.html','Estoque':'HomeEstoque.dc.html','Início':'Main.dc.html','Mapa':'Main.dc.html','Cadastros':'HomeCadastros.dc.html','Agronomia':'HomeAgronomia.dc.html','PCP':'HomePCP.dc.html','PCM':'HomePCM.dc.html','Compras':'HomeCompras.dc.html','Campo':'HomeCampo.dc.html','Irrigação':'HomeIrrigacao.dc.html','Oficina':'HomeOficina.dc.html','Colheita':'HomeColheita.dc.html','Beneficiamento':'HomeBeneficiamento.dc.html','Vendas':'HomeVendas.dc.html','Mercado':'Mercado.dc.html','Logística':'HomeLogistica.dc.html','Controle':'Indicadores.dc.html'}
PHREF={'Expedicao.dc.html':None,'OSCampoLista.dc.html':'Programacao.dc.html','Realizado.dc.html':'Operacoes.dc.html','MapaFazenda.dc.html':'Vistoria.dc.html','Pagamento.dc.html':None,'Analises.dc.html':'Diagnostico.dc.html','Diagnostico.dc.html':'Solo.dc.html','Solo.dc.html':'Calculo.dc.html','Prescricao.dc.html':'Calculo.dc.html','Calculo.dc.html':'Safra.dc.html','PlanosManutencao.dc.html':'PlanoManutencao.dc.html','PlanoManutencao.dc.html':'Maquina.dc.html','Indicadores.dc.html':'Realizado.dc.html','Politicas.dc.html':'Cobertura.dc.html','Cobertura.dc.html':'CompraLiquida.dc.html','Inventario.dc.html':'Almoxarifado.dc.html','Recebimento.dc.html':'Almoxarifado.dc.html','HomePCE.dc.html':'Cobertura.dc.html','HomeEstoque.dc.html':'MobileAlmox.dc.html','Monitoramento.dc.html':'Vistoria.dc.html','Vistoria.dc.html':'OSCampo.dc.html','MobileVistoria.dc.html':'Vistoria.dc.html','MobileHoje.dc.html':'MobileOS.dc.html','MobileOS.dc.html':'Apontamento.dc.html','MobileOcorrencia.dc.html':'MobileOS.dc.html','MobileCaixa.dc.html':'Balanco.dc.html','MobileAlmox.dc.html':'MobileHoje.dc.html','Prescricao.dc.html':'OSCampo.dc.html','Analises.dc.html':'OSCampoLista.dc.html','Operacao.dc.html':'Planos.dc.html','Talhao.dc.html':'MapaFazenda.dc.html','Insumo.dc.html':'CompraLiquida.dc.html','Talhoes.dc.html':'Talhao.dc.html','Main.dc.html':'Safra.dc.html','Maquinas.dc.html':'Maquina.dc.html','Maquina.dc.html':'Maquinas.dc.html','Planos.dc.html':'Plano.dc.html','Plano.dc.html':'Planos.dc.html','Diagnostico.dc.html':'Solo.dc.html','Solo.dc.html':'Calculo.dc.html','Safras.dc.html':'Safra.dc.html','Safra.dc.html':'Programacao.dc.html','Calculo.dc.html':'CompraLiquida.dc.html','Programacao.dc.html':'Frota.dc.html','Carga.dc.html':'Programacao.dc.html','Frota.dc.html':'Orcamento.dc.html','Orcamento.dc.html':'CompraLiquida.dc.html','PCM.dc.html':'OSManutencao.dc.html','OSManutencao.dc.html':'OSOficina.dc.html','CompraLiquida.dc.html':'Cotacoes.dc.html','Cotacoes.dc.html':'Pagamento.dc.html','Pagamento.dc.html':'Almoxarifado.dc.html','Almoxarifado.dc.html':'OSCampoLista.dc.html','OSCampoLista.dc.html':'MapaFazenda.dc.html','OSCampo.dc.html':'Apontamento.dc.html','Balanco.dc.html':'Pivos.dc.html','OSOficina.dc.html':'PCM.dc.html','Beneficiamento.dc.html':'Oferta.dc.html','Oferta.dc.html':'Expedicao.dc.html','Expedicao.dc.html':'Realizado.dc.html','Realizado.dc.html':'MapaFazenda.dc.html','MapaFazenda.dc.html':'OSCampo.dc.html','Apontamento.dc.html':'OSCampoLista.dc.html','Abastecimento.dc.html':'OSOficina.dc.html','Colheita.dc.html':'Beneficiamento.dc.html','LinkFornecedor.dc.html':'Cotacoes.dc.html','LinkCliente.dc.html':'Oferta.dc.html',
 'HomeCadastros.dc.html':'Talhoes.dc.html','HomeAgronomia.dc.html':'Diagnostico.dc.html','HomePCP.dc.html':'Programacao.dc.html','HomePCM.dc.html':'PCM.dc.html','HomeCompras.dc.html':'Cotacoes.dc.html','HomeCampo.dc.html':'OSCampoLista.dc.html','HomeIrrigacao.dc.html':'Balanco.dc.html','HomeOficina.dc.html':'OSOficina.dc.html','HomeColheita.dc.html':'Colheita.dc.html','HomeBeneficiamento.dc.html':'Beneficiamento.dc.html','HomeVendas.dc.html':'Oferta.dc.html','HomeLogistica.dc.html':'Expedicao.dc.html','Mercado.dc.html':'Mercado.dc.html'}

# ---- destinos por texto de botão (o que leva a outra tela) ----
PARENT={'Talhoes.dc.html':'HomeCadastros.dc.html','Talhao.dc.html':'Talhoes.dc.html','Insumo.dc.html':'Insumos.dc.html','Operacoes.dc.html':'HomeCadastros.dc.html','Operacao.dc.html':'Operacoes.dc.html','Maquinas.dc.html':'HomeCadastros.dc.html','Maquina.dc.html':'Maquinas.dc.html','Planos.dc.html':'HomeAgronomia.dc.html','Plano.dc.html':'Planos.dc.html','Insumos.dc.html':'HomeCadastros.dc.html','Diagnostico.dc.html':'HomeAgronomia.dc.html','Safras.dc.html':'HomeAgronomia.dc.html','Safra.dc.html':'Safras.dc.html','Solo.dc.html':'Diagnostico.dc.html','Prescricao.dc.html':'Solo.dc.html','Analises.dc.html':'HomeAgronomia.dc.html','Calculo.dc.html':'Safra.dc.html','Programacao.dc.html':'HomePCP.dc.html','Carga.dc.html':'HomePCP.dc.html','Frota.dc.html':'HomePCP.dc.html','Orcamento.dc.html':'HomePCP.dc.html','PCM.dc.html':'HomePCM.dc.html','OSManutencao.dc.html':'PCM.dc.html','CompraLiquida.dc.html':'HomeCompras.dc.html','Cotacoes.dc.html':'CompraLiquida.dc.html','Pagamento.dc.html':'Cotacoes.dc.html','Almoxarifado.dc.html':'HomeEstoque.dc.html','OSCampoLista.dc.html':'HomeCampo.dc.html','OSCampo.dc.html':'OSCampoLista.dc.html','Balanco.dc.html':'HomeIrrigacao.dc.html','Pivos.dc.html':'HomeIrrigacao.dc.html','OSOficina.dc.html':'HomeOficina.dc.html','Beneficiamento.dc.html':'HomeBeneficiamento.dc.html','Oferta.dc.html':'HomeVendas.dc.html','Expedicao.dc.html':'HomeLogistica.dc.html','Mercado.dc.html':'Mercado.dc.html','Monitoramento.dc.html':'HomeAgronomia.dc.html','Vistoria.dc.html':'Monitoramento.dc.html','PrevisaoColheita.dc.html':'HomeColheita.dc.html','PlanoSemanal.dc.html':'HomePCP.dc.html','Semana.dc.html':'Indicadores.dc.html','Politicas.dc.html':'HomePCE.dc.html','Cobertura.dc.html':'HomePCE.dc.html','Inventario.dc.html':'HomeEstoque.dc.html','Recebimento.dc.html':'HomeEstoque.dc.html','Indicadores.dc.html':'Main.dc.html','PlanosManutencao.dc.html':'HomePCM.dc.html','PlanoManutencao.dc.html':'PlanosManutencao.dc.html','Realizado.dc.html':'Indicadores.dc.html','MapaFazenda.dc.html':'Indicadores.dc.html'}
MPARENT={'LinkFornecedor.dc.html':'Cotacoes.dc.html','Apontamento.dc.html':'MobileOS.dc.html','Abastecimento.dc.html':'MobileHoje.dc.html','Colheita.dc.html':'MobileHoje.dc.html','LinkCliente.dc.html':'Oferta.dc.html','MobileHoje.dc.html':'Main.dc.html','MobileOS.dc.html':'MobileHoje.dc.html','MobileOcorrencia.dc.html':'MobileHoje.dc.html','MobileCaixa.dc.html':'MobileHoje.dc.html','MobileAlmox.dc.html':'MobileHoje.dc.html','MobileVistoria.dc.html':'MobileHoje.dc.html','ContagemFrutos.dc.html':'PrevisaoColheita.dc.html'}
BTNHREF={'Ver plano do modelo':'PlanoManutencao.dc.html','Aplicar à máquina':'Maquina.dc.html','Ver biblioteca':'PlanosManutencao.dc.html','Cotar 9 faltas':'CompraLiquida.dc.html','Ver compra líquida':'CompraLiquida.dc.html','Ver políticas':'Politicas.dc.html','Aprovar ajustes (2)':'Inventario.dc.html','Confirmar entrada':'Almoxarifado.dc.html','Aprovar exceções (3)':'Politicas.dc.html','Ler QR':'MobileAlmox.dc.html','O.S. corretiva':'OSCampo.dc.html','Alterar O.S.':'OSCampo.dc.html','Adiar 7 d':'Programacao.dc.html','Vistoriar':'MobileVistoria.dc.html','Gerar O.S. corretiva':'OSCampo.dc.html','Alterar O.S. 0431':'OSCampo.dc.html','Nova vistoria':'MobileVistoria.dc.html','Ver rota':'MobileVistoria.dc.html','Adiar 7 dias':'Programacao.dc.html','Ver no mapa':'MapaFazenda.dc.html','Ver no celular':'MobileVistoria.dc.html','Coletar':'OSCampoLista.dc.html','Ver correção':'Solo.dc.html','Reprogramar O.S. 0420':'Programacao.dc.html','Liberar':'OSCampo.dc.html','Ver prescrição':'Prescricao.dc.html','Abrir O.S. 0425':'OSCampo.dc.html','Gerar O.S. de coleta':'OSCampoLista.dc.html',
 'Abrir O.S. 0288':'OSCampo.dc.html','Abrir no celular':'Apontamento.dc.html','Abrir talhão':'Talhao.dc.html','Ver detalhe':'Talhao.dc.html',
 ('Diagnostico.dc.html','Ver detalhe'):'Realizado.dc.html','Ver correção e adubação':'Solo.dc.html','Ver O.S. 0233':'OSManutencao.dc.html','Ver PCM':'PCM.dc.html',
 'Ver programação':'Programacao.dc.html','Aceitar 14 + 10 mm':'Pivos.dc.html','Manter 24 mm':'Pivos.dc.html','Criar vistoria':'OSCampo.dc.html','Criar vistoria na mancha':'OSCampo.dc.html',
 'Reprogramar O.S.':'Programacao.dc.html','Enviar oferta':'LinkCliente.dc.html','Contratar frete':'Frota.dc.html','Terceirizar':'Frota.dc.html',('Frota.dc.html','Terceirizar'):'Orcamento.dc.html',
 'Antecipar':'OSManutencao.dc.html','Programar':'OSManutencao.dc.html','Abrir O.S.':'OSManutencao.dc.html','Ligar pivôs da noite':'Pivos.dc.html',
 ('Safra.dc.html','Ver'):'Calculo.dc.html','Ver O.S.':'OSCampo.dc.html','Reprogramar':'Programacao.dc.html','Aprovar':'Balanco.dc.html','Fechar':'Cotacoes.dc.html','Expedir':'Expedicao.dc.html',
}
# ---- painéis laterais: '+ X' e ações que pedem 1–5 campos ----
DRAWERS={'Editar atividade por idade':dict(title='Editar atividade do plano perene',sub='o gatilho resolve contra a data de plantio (ou florada, poda, colheita) de cada parcela',fields=[('Ano de cultivo','Ano 1 · formação'),('Gatilho','Idade 7'),('Operação','Adubação'),('Insumo','Ureia 46 %'),('Dose por planta (g)','60'),('Tolerância (dias)','10')],confirm='Salvar',done='✓ Atividade salva'),'Editar parâmetros':dict(title='Editar parâmetros da operação',sub='vale para novos planos; planos publicados não mudam',fields=[('Largura de trabalho (m)','30'),('Velocidade (km/h)','14'),('Eficiência de campo (%)','70'),('Máquina padrão','Pulverizador 02 · 30 m'),('Motivo','Ajuste da fazenda')],confirm='Salvar',done='✓ Parâmetros salvos · rendimento 29,4 ha/h'),'Ajustar atividade':dict(title='Ajustar atividade neste talhão',sub='o molde não muda; o ajuste vale só para este talhão nesta safra e exige motivo',fields=[('Atividade','Fungicida 2ª aplicação'),('Ação do ajuste','Aumentar dose'),('Insumo','Fungicida B'),('Dose/ha','0,6 L'),('Motivo','Pressão de doença no histórico')],confirm='Salvar ajuste',done='✓ Ajuste salvo · cálculo do talhão atualizado'),'+ Ajuste':dict(title='Novo ajuste neste talhão',sub='incluir ou excluir produto, mudar dose ou época; motivo obrigatório; bula valida dose e carência',fields=[('Atividade','Plantio'),('Ação do ajuste','Incluir produto'),('Insumo','Nematicida biológico'),('Dose/ha','2 L'),('Motivo','Nematoide acima do NC (laudo 12/08)')],confirm='Adicionar ajuste',done='✓ Ajuste adicionado · cálculo e demanda atualizados'),'+ O.S. neste talhão':dict(title='Nova O.S. neste talhão',sub='nasce programada; o PCP confere máquina e janela',fields=[('Talhão','T2 · 298 ha'),('Operação','Dessecação'),('Data','23/09/2026'),('Máquina','Pulverizador 02 · 30 m'),('Insumo','Glifosato 480'),('Dose/ha','2,5 L')],confirm='Criar O.S.',done='✓ O.S. 0432 criada · Programação avisada'),'Trocar cartão':dict(title='Trocar cartão da assinatura',sub='cobrança automática todo dia 1; sem cartão válido a indicação automática pausa em 10 dias',fields=[('Número do cartão','•••• •••• •••• 4421'),('Validade','08/28'),('Nome no cartão','FERTISUL LTDA')],confirm='Salvar cartão',done='✓ Cartão atualizado'),'+ Fazenda':dict(title='Nova fazenda',sub='sem CAR a fazenda fica em rascunho e nenhum talhão pode ser ativado',fields=[('Nome da fazenda','Boa Vista'),('CNPJ ou CPF','12.345.678/0001-90'),('Matrícula do imóvel','8.421'),('CAR','MT-5107925-8A3F…'),('Município e UF','Sorriso · MT'),('Área total (ha)','420')],confirm='Criar fazenda',done='✓ Fazenda criada'),'+ Dividir talhão':dict(title='Dividir talhão em parcelas',sub='cada parcela vira unidade de safra, O.S., apontamento, custo e previsão; o talhão continua a unidade do mapa, do solo e do pivô',fields=[('Talhão','T2 · 298 ha'),('Divisão por','Por área (%)'),('Número de parcelas','3'),('Áreas (ha)','100 · 100 · 98'),('Motivo','Escalonar colheita')],confirm='Dividir',done='✓ 3 parcelas criadas'),'Editar parcela':dict(title='Editar parcela',fields=[('Parcela','T9-A'),('Área (ha)','0,26'),('Plantio previsto','22/09/2026'),('Cultura','Alface americana'),('Divisão por','Por área (%)')],confirm='Salvar',done='✓ Parcela salva'),'Editar atividade':dict(title='Editar atividade',sub='mudar aqui altera o molde; safras já copiadas não mudam',fields=[('Gatilho','DAP 25'),('Operação','Cobertura'),('Máquina padrão','Distribuidor 01'),('Insumo','KCl 60 %'),('Dose/ha','120 kg')],confirm='Salvar',done='✓ Atividade salva'),'Editar revisão':dict(title='Editar revisão do plano',sub='vale para as máquinas deste modelo a partir da próxima revisão',fields=[('Intervalo','500 h'),('Itens','óleo hidráulico e filtros · filtro de combustível'),('Peças (kit)','óleo Hy-Gard 40 L · filtros (2)'),('Mão de obra (h)','4'),('Motivo','Ajuste da fazenda'),('Complemento','óleo hidráulico a 500 h por poeira')],confirm='Salvar',done='✓ Revisão salva'),'Editar atividade da operação':dict(title='Editar atividade da operação',sub='padrão da fazenda; o plano copia daqui',fields=[('Atividade','Fungicida 1ª aplicação'),('Máquina padrão','Pulverizador 24 m'),('Rendimento (ha/h)','25'),('Insumo padrão','Fungicida'),('Unidade','L/ha'),('Gatilho padrão','DAP 35'),('Motivo','Máquina diferente do padrão')],confirm='Salvar',done='✓ Atividade salva'),'+ Plano por modelo':dict(title='Novo plano por modelo',sub='nasce do plano nativo da categoria; edite intervalos e kits com motivo',fields=[('Marca','Case IH'),('Modelo','Axial-Flow 7250'),('Categoria','Colhedora'),('Base','Plano nativo · colhedora axial')],confirm='Criar plano',href='PlanoManutencao.dc.html'),'+ Revisão':dict(title='Nova revisão do plano',fields=[('Intervalo','2.000 h ou 24 meses'),('Itens','óleo e filtros da transmissão, correias'),('Peças (kit)','filtro RE 2 un · óleo 40 L'),('Mão de obra (h)','6')],confirm='Adicionar revisão',done='✓ Revisão adicionada'),'Editar política':dict(title='Política do item · MAP 11-52',sub='vem do grupo Fertilizantes; edite só o que for diferente',fields=[('Política','Lote a lote pela necessidade datada'),('Cobertura por entrega','Antes do 1º uso (dias)'),('Antecedência antes do 1º uso (dias)','20'),('Ritmo máximo (cargas/dia)','2'),('Tempo de segurança (dias)','15'),('Limite do depósito (t)','120'),('Limite de exposição (R$ · LMI da apólice)','300.000'),('Risco de roubo','Classe B'),('Prazo do grupo (dias) · jul–out','45'),('Margem de prazo (dias)','5'),('Múltiplo de compra','carga 36 t')],confirm='Salvar',done='✓ Política salva'),
 '+ Atividade':dict(title='Nova atividade',sub='vira O.S. com data quando a safra for programada',fields=[('Gatilho','DAP 45'),('Operação','Pulverização'),('Máquina padrão','Pulverizador 01'),('Insumo','Fungicida C'),('Dose/ha','0,3 L')],confirm='Adicionar atividade',done='✓ Atividade adicionada'),
 '+ Operação':dict(title='Nova operação',sub='nasce do catálogo nativo; edite o que for diferente na sua fazenda',fields=[('Grupo de cultura','Grãos'),('Fase','4 · Tratos culturais'),('Nome da operação','Aplicação de bioinsumos'),('Máquina padrão','Pulverizador 24 m')],confirm='Criar operação',href='Operacao.dc.html'),
 '+ Atividade da operação':dict(title='Nova atividade da operação',sub='padrões da fazenda; o plano agronômico usa estes valores',fields=[('Atividade','Fungicida 4ª aplicação'),('Máquina padrão','Pulverizador 24 m'),('Rendimento (ha/h)','25'),('Insumo padrão','Fungicida'),('Unidade','L/ha'),('Gatilho padrão','DAP 80')],confirm='Adicionar atividade',done='✓ Atividade adicionada'),
 '+ Item':dict(title='Adicionar peça ou serviço',fields=[('Peça ou serviço','Filtro de óleo 2ª unidade'),('Quantidade','1'),('Origem','Almoxarifado · lote F26-02')],confirm='Adicionar',done='✓ Item adicionado'),
 '+ Talhão':dict(title='Vincular talhão à safra',sub='cultura, variedade e plano vêm do diagnóstico',fields=[('Talhão','T5 · 180 ha'),('Cultura','Soja'),('Plano','Soja padrão'),('Plantio previsto','20/10/2026')],confirm='Vincular',done='✓ T5 vinculado'),
 'Editar':dict(title='Editar máquina',fields=[('Nome','Trator 01'),('Modelo','John Deere 6155J'),('Ano','2021'),('Horímetro atual','4.812 h')],confirm='Salvar',done='✓ Salvo'),
 'Ajustar':dict(title='Ajustar rendimento',sub='só se a sua máquina render diferente do padrão',fields=[('Operação','Plantio'),('ha/h efetivo','4,4'),('Motivo','Máquina diferente do padrão'),('Complemento','Plantadeira de 24 linhas')],confirm='Salvar ajuste',done='✓ Ajustado'),
 'Simular':dict(title='Simular nivelamento',fields=[('Antecipar T2 para','08/10/2026'),('Turno extra (h/dia)','2'),('Terceirizar plantadeira (dias)','5')],confirm='Simular',done='✓ Faltam 40 h em out'),
 'Simular preço':dict(title='Simular preço de venda',fields=[('Soja (R$/sc)','118'),('Milho (R$/sc)','58'),('Câmbio (R$/US$)','5,42')],confirm='Recalcular margem',done='✓ Margem R$ 4.930/ha'),
 'Corrigir leitura':dict(title='Corrigir leitura de sensor',fields=[('Sensor','Umidade P1 · 30 cm'),('Leitura correta (% CAD)','58'),('Motivo','Sonda deslocada')],confirm='Corrigir',done='✓ Balanço recalculado'),
 'Contrapropor':dict(title='Contraproposta',fields=[('Cliente','Armazém Geral'),('Preço (R$/sc)','129'),('Condição','FOB · à vista'),('Validade','2 dias')],confirm='Enviar contraproposta',done='✓ Enviada'),
 'Transferir':dict(title='Transferir lote',fields=[('Lote','L27-012 · 3.400 sc'),('De','Armazém 1'),('Para','Armazém 2'),('Quantidade (sc)','1.200')],confirm='Transferir',done='✓ Transferido'),
 'Criar alerta de preço':dict(title='Novo alerta de preço',fields=[('Item','Soja · CEPEA'),('Condição','acima de'),('Preço (R$/sc)','135'),('Avisar por','WhatsApp')],confirm='Criar alerta',done='✓ Alerta criado'),
 'Importar nota fiscal (XML)':dict(title='Importar nota fiscal',sub='itens, lotes e validade entram no estoque sozinhos',fields=[('Arquivo XML','NFe_12877.xml'),('Depósito','Galpão 1')],confirm='Importar',done='✓ NF 12.877 · 3 itens'),
 'Ver dossiê':dict(title='Dossiê para aprovação',content='<div style="font-size: 13px; display: flex; flex-direction: column; gap: 6px;">'+''.join(f'<div>✓ {x}</div>' for x in ['Safra 2026/27: 1.240 ha, cultura e variedade por talhão','Orçamento COE/COT e PMV por talhão','Produtividade real das 3 últimas safras','Estoque de produto e contratos de venda','Matrícula, CAR e CCIR dos imóveis','Fluxo de caixa da safra com vencimentos','Histórico de crédito e pagamentos','Consentimento LGPD assinado em 12/08'])+'</div>',confirm='Baixar PDF',done='✓ PDF gerado'),
 'Ver tabela da cultura':dict(title='Tabela de adubação · soja (Cerrado)',sub='Embrapa Cerrado, Sousa & Lobato (2004) · Mehlich-1',content='<table style="width: 100%; border-collapse: collapse; font-size: 12.5px;"><tr><th style="text-align:left; padding: 6px;">Classe de P</th><th style="text-align:left; padding: 6px;">P₂O₅ kg/ha</th><th style="text-align:left; padding: 6px;">K₂O kg/ha (K médio)</th></tr><tr><td style="padding: 6px;">muito baixo</td><td style="padding: 6px;">120 + corr.</td><td style="padding: 6px;">120</td></tr><tr><td style="padding: 6px;">baixo</td><td style="padding: 6px;">100</td><td style="padding: 6px;">100</td></tr><tr><td style="padding: 6px;">médio</td><td style="padding: 6px;">80</td><td style="padding: 6px;">80</td></tr><tr><td style="padding: 6px;">adequado</td><td style="padding: 6px;">60 (manutenção 20 kg/t)</td><td style="padding: 6px;">60</td></tr><tr><td style="padding: 6px;">alto</td><td style="padding: 6px;">40</td><td style="padding: 6px;">40</td></tr></table>',confirm='Usar esta tabela',done='✓ Tabela aplicada'),
 'Ligar pivôs da noite':dict(title='Ligar pivôs da noite',sub='O.S. 0418 e 0419 · janela 21h30–23h40 · 100 % noturno',fields=[('Lâmina e horário · Pivô 1','8 mm · 1,0 h · 21h30'),('Lâmina e horário · Pivô 2','14 mm · 2,1 h · 21h30')],confirm='Ligar às 21h30',done='✓ Programados'),
}
# ---- ações que só mostram resultado na própria tela ----
MSGS={'Expedir carga 10':'✓ Carga 10 expedida · romaneio 0010 e NF-e emitidos · estoque baixado · 10 de 25 cargas','Enviar dossiê e pagar':'✓ Dossiê enviado ao Banco Terra (blocos autorizados) · aprovação em até 24 h · à vista reservado','Usar no ajuste de T2':'✓ Rizotec 2 L/ha incluído no plantio de T2 (ajuste: nematoide) · bula validada: dose, carência 0 d','Emitir receituário':'✓ Receituário agronômico 0451 emitido para T2 · Fox Xpro 0,5 L/ha · ART vinculada','Comparar selecionados':'✓ Comparação: Fox Xpro R$ 96/ha (FRAC 7+3+11) × Aproach Prima R$ 71/ha (FRAC 11+3) × Unizeb Gold R$ 38/ha (M03) · rotação recomenda M03 na 3ª','Atualizar AGROFIT':'✓ Base AGROFIT sincronizada · 18/09/2026 · 2.114 produtos · 41 registros alterados','Aplicar os ajustes a T4':'✓ 3 ajustes copiados para T4 com os mesmos motivos · cálculo de T4 atualizado','Aprovar com estas condições':'✓ Crédito aprovado · o produtor recebe CET, garantias e prazo · pedido vira firme','Recusar':'✓ Recusa registrada com motivo · o produtor vê a próxima condição disponível','Contrapropor':'✓ Contraproposta enviada · o produtor compara lado a lado','Enviar proposta':'✓ Proposta enviada · a fazenda compara custo total em 1 tela · resultado por WhatsApp','Enviar proposta de compra':'✓ Proposta enviada · Santa Rita compara o líquido por saca','Enviar proposta de crédito':'✓ Proposta enviada · o produtor vê CET e garantias lado a lado','Salvar perfil':'✓ Perfil salvo · indicações automáticas recalculadas','Contestar resultado':'✓ Pedido enviado · a fazenda responde em 2 dias','Baixar dossiê (PDF)':'✓ Dossiê 0102 gerado · válido 7 dias · consentimento LGPD registrado','Reclassificar agora':'ABC recalculada: 12 itens A (78 % do valor) · 3 críticos (PCM) · 2 mudaram de classe','Gerar agenda do mês':'Agenda de contagem gerada: 14 contagens em outubro, fora das datas de O.S.','+1 lagarta':'Ponto 4 · lagartas 6/pano · NC 20 · abaixo','+1 percevejo':'Ponto 4 · percevejos 3/pano · NC 2 · ACIMA → O.S. corretiva sugerida','Foto do sintoma':'Foto anexada ao ponto 4 · ferrugem: 1 pústula','Estande 11/m':'Estande 11 pl/m · alvo 13 · 85 % · ok','Próximo ponto':'Ponto 5 · 96 m · seta no mapa','Falar':'Gravando… 12 s · O.S. 0412 · T1 · GPS ok','Tirar foto':'Foto anexada à O.S. 0412 (1)','Ler QR do insumo':'QR lido · Glifosato 480 · lote G26-03 · 780 L reservados','Ler QR da máquina':'QR lido · Pulverizador 02 · horímetro 1.412 h','Sim, parou':'Corretiva urgente aberta · Pulverizador 02 · O.S. de campo travada · PCP realocando','Não, segue':'Inspeção na próxima parada · O.S. de campo segue','Confirmar data':'Parada confirmada · 14/10 · Trator 01','Liberar 0413':'O.S. 0413 liberada · João avisado · Glifosato reservado','Fechar cotação':'Pedido 0088 fechado com Fertisul · R$ 496.000 · entrega 03/10','Aprovar 8 mm':'Lâmina aprovada · O.S. 0418 · Pivô 1 liga às 21h30','Entregar':'Retirada registrada · Marcos · calcário 375 t · O.S. 0420','Receber NF':'NF 12.877 recebida · 3 itens · lotes e validade gravados','Inventário':'Inventário cíclico da classe A agendado para 25/09 · 12 itens',
 'Foto':'Foto anexada à O.S. 0420 (1)','Ocorrência':'Ocorrência gravada por voz · 12 s','Apontar parcial':'Parcial apontada: 186 ha · 7,2 h · horímetro 4.819',
 'Reenviar':'Reenviado por WhatsApp e e-mail · link válido por 2 dias','Rastrear':'Carga 9 · BR-163 km 412 · chegada prevista 16:40','Canhoto':'Canhoto assinado · foto anexada à NF 12.844',
 'Ler QR':'QR lido · filtro de óleo lote F26-02 baixado da O.S. 0231','Liberar (QR)':'QR gerado · Marcos retira calcário 375 t no pátio','Atualizar':'Histórico atualizado com a safra 2025/26',
 'Escolher arquivo':'talhoes_2026.kml selecionado · 7 polígonos','Importar KML, KMZ, SHP, GeoJSON':'7 polígonos lidos · 6 novos · 1 conflito de área (T3)','Buscar no CAR / SIGEF':'CAR MT-5107925-… encontrado · 3 polígonos importados',
 'Trocar método':'Método trocado: use o seletor no topo da tela',
}
HEIGHTS={'Agrofit.dc.html': 1720, 'Solo.dc.html': 2300, 'Talhoes.dc.html': 1560, 'MapaFazenda.dc.html': 1580, 'Mercado.dc.html': 1390, 'Carga.dc.html': 1660, 'Frota.dc.html': 1000, 'Realizado.dc.html': 960, 'Orcamento.dc.html': 920, 'Diagnostico.dc.html': 2080, 'Safra.dc.html': 1200, 'OSCampo.dc.html': 940, 'Balanco.dc.html': 960, 'Programacao.dc.html': 960, 'Beneficiamento.dc.html': 1130, 'Cotacoes.dc.html': 920, 'Oferta.dc.html': 980, 'PCM.dc.html': 930, 'Maquina.dc.html': 1190, 'Plano.dc.html': 1050, 'Calculo.dc.html': 920, 'CompraLiquida.dc.html': 1050, 'Almoxarifado.dc.html': 900, 'OSCampoLista.dc.html': 900, 'OSManutencao.dc.html': 920, 'OSOficina.dc.html': 990, 'Expedicao.dc.html': 900, 'Pivos.dc.html': 900, 'Pagamento.dc.html': 1140, 'Insumos.dc.html': 900, 'Maquinas.dc.html': 900, 'HomeAgronomia.dc.html': 1560, 'HomeCompras.dc.html': 940, 'HomeCadastros.dc.html': 1060, 'Talhao.dc.html': 2020, 'Insumo.dc.html': 1290, 'Operacoes.dc.html': 2400, 'Operacao.dc.html': 1320, 'Prescricao.dc.html': 1470, 'Analises.dc.html': 1040, 'MobileHoje.dc.html': 844, 'MobileOS.dc.html': 844, 'MobileOcorrencia.dc.html': 844, 'MobileCaixa.dc.html': 900, 'MobileAlmox.dc.html': 844, 'Main.dc.html': 980, 'Colheita.dc.html': 860, 'Monitoramento.dc.html': 1180, 'Vistoria.dc.html': 1560, 'MobileVistoria.dc.html': 844, 'Politicas.dc.html': 1360, 'Cobertura.dc.html': 1160, 'Inventario.dc.html': 980, 'Recebimento.dc.html': 980, 'HomePCE.dc.html': 1020, 'HomeEstoque.dc.html': 960, 'Indicadores.dc.html': 1080, 'PlanosManutencao.dc.html': 1090, 'PlanoManutencao.dc.html': 1320, 'ContagemFrutos.dc.html': 940, 'Escalonamento.dc.html': 1490, 'HomeBeneficiamento.dc.html': 840, 'HomeCampo.dc.html': 840, 'HomeColheita.dc.html': 840, 'HomeIrrigacao.dc.html': 970, 'HomeLogistica.dc.html': 840, 'HomeOficina.dc.html': 840, 'HomePCM.dc.html': 850, 'HomePCP.dc.html': 980, 'HomeVendas.dc.html': 840, 'IdadeCultura.dc.html': 1210, 'MobileIrrigacao.dc.html': 980, 'ParceiroAssinatura.dc.html': 1170, 'ParceiroBI.dc.html': 970, 'ParceiroCotacao.dc.html': 1080, 'ParceiroCredito.dc.html': 1340, 'ParceiroInicio.dc.html': 1050, 'ParceiroNegocios.dc.html': 1010, 'ParceiroOferta.dc.html': 1070, 'PlanoEntregas.dc.html': 1700, 'PlanoPerene.dc.html': 1250, 'PlanoSemanal.dc.html': 980, 'PlanoTalhao.dc.html': 1400, 'PrevisaoColheita.dc.html': 960, 'Semana.dc.html': 1030}
GROUPS=[('Base',['Mapa','Mercado','Cadastros']),('Planejar',['Agronomia','PCP','PCM','PCE']),('Executar',['Campo','Irrigação','Oficina','Estoque','Colheita','Beneficiamento','Logística']),('Comprar e vender',['Compras','Vendas']),('Controlar',['Indicadores'])]
ROLE={'Base':('#EEF1EE','#5B6660'),'Planejar':('#E7EDF8','#2F55A4'),'Executar':('#E4F3E9','#1E7A4C'),'Comprar e vender':('#F1EAF8','#6B3FA0'),'Controlar':('#FDEEDF','#B9580F')}
MODROLE={m:gname for gname,ms in GROUPS for m in ms}
ROLETXT={'Mapa':'Base · central geográfica de desempenho','Indicadores':'Controlar · conferir, aprender e atualizar cadastros','PCE':'Planejar · políticas e cobertura de estoque','Estoque':'Executar · almoxarifado, contagens e produto','Agronomia':'Planejar · o quê e quanto','PCP':'Planejar · quando e com quem','PCM':'Planejar · manutenção das máquinas','Campo':'Executar · operações agrícolas','Irrigação':'Executar · irrigação diária','Oficina':'Executar · manutenção','Colheita':'Executar · colheita','Beneficiamento':'Executar · beneficiamento e estoque','Logística':'Executar · expedição','Compras':'Comprar · só o que falta','Vendas':'Vender · por link','Mercado':'Base · preços, sazonalidade e alertas','Controle':'Controlar · realizado × planejado','Cadastros':'Base · o que existe na fazenda','Início':'Hoje'}
def roletag(module):
    grp=MODROLE.get(module,'Base'); bg,fg=ROLE[grp]
    return f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; background: {bg}; color: {fg}; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap;">{esc(ROLETXT.get(module,grp))}</span>'
def navgroups(module):
    out=''
    for gname,ms in GROUPS:
        bg,fg=ROLE[gname]
        out+=f'<div style="display: flex; align-items: center; gap: 8px; padding: 10px 12px 4px; font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: {SIDE_MUTED};"><span style="width: 6px; height: 6px; border-radius: 999px; background: {fg};"></span>{esc(gname)}</div>'
        out+=''.join(navlink(m,m==module) for m in ms)
    return out
ROW=None
from catalogo_operacoes import CAT, GRUPOS, FASES, contar as _contar_ops

# ================= interatividade: registro de widgets por tela + motor de estado genérico =================
CUR=None; FIRST_TBL=[None]; MSGW=[None]; RS=[None]; DRAWN={}
WIDGETS=[]; EXTRA=[]; _WN=[0]
def HL(s): return '{{ '+s+' }}'
def wid(p): _WN[0]+=1; return f'{p}{_WN[0]}'
def reg(**w): WIDGETS.append(w); return w['id']
def wget(i): return next(w for w in WIDGETS if w['id']==i)
def _reset_screen(f):
    global CUR; CUR=f; FIRST_TBL[0]=None; MSGW[0]=None; RS[0]=None; DRAWN.clear(); WIDGETS.clear(); EXTRA.clear()
ITEM_ON=lambda: f'display: block; width: 100%; text-align: left; padding: 8px 12px; border: 0; border-radius: 8px; background: {ACCS}; color: {ACC}; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer; text-transform: none; letter-spacing: 0; white-space: nowrap;'
ITEM_OFF=lambda: f'display: block; width: 100%; text-align: left; padding: 8px 12px; border: 0; border-radius: 8px; background: transparent; color: {INK}; font-family: inherit; font-size: 13px; font-weight: 500; cursor: pointer; text-transform: none; letter-spacing: 0; white-space: nowrap;'
LIST_ST=lambda right=False: f'position: absolute; top: calc(100% + 6px); {"right: 0;" if right else "left: 0;"} z-index: 25; min-width: 200px; background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; box-shadow: 0 12px 32px -8px rgba(21,32,26,.28); padding: 6px; flex-direction: column; gap: 2px; display: flex;'
CMENU_ST=lambda: f'position: absolute; top: 102px; left: 14px; z-index: 25; width: 270px; background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; box-shadow: 0 12px 32px -8px rgba(21,32,26,.28); padding: 8px; flex-direction: column; gap: 2px; display: flex;'
GCHIP_ST=lambda: f'display: inline-flex; align-items: center; gap: 6px; padding: 3px 4px 3px 10px; border-radius: 999px; background: {INK}; color: #fff; font-size: 12px; font-weight: 700;'
CHIP_ON=lambda: f'font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 7px 14px; border-radius: 999px; border: 1px solid {ACC}; background: {ACC}; color: #fff; cursor: pointer;'
CHIP_OFF=lambda: f'font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 7px 14px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer;'
SEG_ON=lambda: f'font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 6px 14px; border-radius: 999px; border: 0; cursor: pointer; background: {SURF}; color: {INK}; box-shadow: 0 1px 2px rgba(21,32,26,.12); white-space: nowrap; display: inline-flex; align-items: center; gap: 6px;'
SEG_OFF=lambda: f'font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 6px 14px; border-radius: 999px; border: 0; cursor: pointer; background: transparent; color: {MUTED}; box-shadow: none; white-space: nowrap; display: inline-flex; align-items: center; gap: 6px;'
TOAST_ST=lambda: f'position: absolute; left: 248px; bottom: 22px; z-index: 40; background: {INK}; color: #fff; padding: 11px 16px; border-radius: 12px; font-size: 13px; font-weight: 600; box-shadow: 0 12px 32px -8px rgba(21,32,26,.4); max-width: 520px;'
DRAWER_ST=lambda: 'position: absolute; inset: 0; z-index: 30; display: flex; justify-content: flex-end;'
BTN_ST=lambda primary=False,small=False: (f"padding: {'7px 14px' if small else '11px 20px'}; border-radius: 10px; font-size: {'13px' if small else '14px'}; font-weight: 700; font-family: inherit; cursor: pointer; line-height: 1.25; letter-spacing: -.005em; white-space: nowrap; "
        + (f"background: {ACC}; color: #fff; border: 1px solid {ACC}; box-shadow: 0 1px 2px rgba(30,122,76,.25);" if primary else f"background: {SURF}; color: {INK}; border: 1px solid {LINE};"))
def msgbtn(text,message,primary=False,small=True):
    """botão que age na própria tela: mostra o resultado numa mensagem (toast)."""
    if MSGW[0] is None:
        MSGW[0]=reg(type='msg',id=wid('q'),opts=[],msgs=[],tst=TOAST_ST())
        EXTRA.append(f'<div role="status" style="{HL(MSGW[0]+"_tst")}">{HL(MSGW[0]+"_text")}</div>')
    w=wget(MSGW[0]); i=len(w['opts']); w['opts'].append(text); w['msgs'].append(message)
    return f'<button type="button" onClick="{HL(MSGW[0]+"_p"+str(i))}" style="{BTN_ST(primary,small)}">{esc(text)}</button>'
def drawer_button(text,d,primary=False,small=True):
    """'+ X' e afins: abre painel lateral; confirmar leva ao detalhe (href) ou adiciona a linha/mostra resultado."""
    if text in DRAWN: did=DRAWN[text]
    else:
        did=wid('d'); DRAWN[text]=did
        reg(type='drawer',id=did,mst=DRAWER_ST(),label=text,done=d.get('done',''))
        body=''.join(field(l,v,ph=(v=='')) for l,v in d.get('fields',[])) + d.get('content','')
        if d.get('href'):
            ok=f'<a href="{d["href"]}" style="text-decoration: none; display: inline-block; {BTN_ST(True)}">{esc(d["confirm"])}</a>'
        else:
            ok=f'<button type="button" onClick="{HL(did+"_add")}" style="{BTN_ST(True)}">{esc(d["confirm"])}</button>'
        EXTRA.append(f'<div style="{HL(did+"_st")}"><button type="button" aria-label="Fechar" onClick="{HL("closeAll")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.35); cursor: pointer;"></button>'
                     f'<aside style="position: relative; width: 440px; height: 100%; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 24px 26px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
                     f'<div style="display: flex; align-items: center; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 20px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">{esc(d["title"])}</h2><button type="button" aria-label="Fechar" onClick="{HL("closeAll")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
                     + (f'<div style="font-size: 13px; color: {MUTED};">{esc(d["sub"])}</div>' if d.get('sub') else '')
                     + f'<div style="display: flex; flex-direction: column; gap: 12px;">{body}</div><div style="flex-grow: 1;"></div><div style="display: flex; justify-content: flex-end;">{ok}</div></aside></div>')
    return f'<button type="button" onClick="{HL(did+"_open")}" style="{BTN_ST(primary,small)}">{HL(did+"_btn")}</button>'
def seg_buttons(opts,active=0,icons=None,on=None,off=None):
    """controle segmentado registrado; devolve (id, [botões]) para compor livremente."""
    s=wid('s'); reg(type='seg',id=s,opts=list(opts),dflt=active,on=on or SEG_ON(),off=off or SEG_OFF())
    bs=[f'<button type="button" onClick="{HL(s+"_p"+str(i))}" style="{HL(s+"_s"+str(i))}">{(icons[i] if icons else "")}{esc(o)}</button>' for i,o in enumerate(opts)]
    return s,bs
def seg(opts,active=0,icons=None):
    s,bs=seg_buttons(opts,active,icons)
    return '<div role="group" aria-label="Visão" style="display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px;">'+''.join(bs)+'</div>'
def pick(opts,default=0,none=None,tbl=None,match=None,label=None,right=False,on=None,off=None,chipx=True):
    """seletor com lista (pílula de contexto, recorte, agrupar): devolve (id, html do botão+lista)."""
    p=wid('p'); reg(type='pick',id=p,opts=list(opts),dflt=default,none=(default if none is None else none),mst=LIST_ST(right),ion=ITEM_ON(),ioff=ITEM_OFF(),bon=on or CHIP_ON(),boff=off or CHIP_OFF(),tbl=tbl,rows=(wget(tbl)['rows'] if tbl else None),match=match,cst='')
    items=''.join(f'<button type="button" role="option" onClick="{HL(p+"_p"+str(i))}" style="{HL(p+"_i"+str(i))}">{esc(o)}</button>' for i,o in enumerate(opts))
    x=f'<span style="{HL(p+"_cst")}"><button type="button" aria-label="Limpar" onClick="{HL(p+"_clear")}" style="border: 0; background: transparent; color: inherit; cursor: pointer; font-size: 13px; padding: 0 0 0 4px;">×</button></span>' if chipx else ''
    btnhtml=f'<button type="button" aria-haspopup="listbox" onClick="{HL(p+"_open")}" style="{HL(p+"_bst")}">{(esc(label)+": ") if label else ""}<span style="font-weight: 700;">{HL(p+"_label")}</span>{x} <span aria-hidden="true" style="font-size: 10px;">▾</span></button>'
    return p,f'<span style="position: relative; display: inline-flex;">{btnhtml}<div role="listbox" style="{HL(p+"_st")}">{items}</div></span>'
def selcell(label='Selecionar',chiptext='Selecionado'):
    """célula de escolha em tabela: 'Selecionado' no escolhido, botão nos demais; a escolha muda ao clicar."""
    if RS[0] is None: RS[0]=reg(type='rowsel',id=wid('r'),opts=[],dflt=0,on='',off='')
    w=wget(RS[0]); k=len(w['opts']); w['opts'].append(str(k))
    return (f'<span style="{HL(RS[0]+"_c"+str(k))}">{chip(chiptext,"green")}</span>'
            f'<span style="{HL(RS[0]+"_b"+str(k))}"><button type="button" onClick="{HL(RS[0]+"_p"+str(k))}" style="{BTN_ST(False,True)}">{esc(label)}</button></span>')
def toggle(text,keep,on=None,off=None):
    """botão liga/desliga que filtra linhas da primeira tabela da tela (keep = índices visíveis quando ligado)."""
    t=wid('x'); reg(type='toggle',id=t,tbl=FIRST_TBL[0],rows=(wget(FIRST_TBL[0])['rows'] if FIRST_TBL[0] else []),keep=list(keep),on=on or CHIP_ON(),off=off or CHIP_OFF())
    return f'<button type="button" aria-pressed="false" onClick="{HL(t+"_p")}" style="{HL(t+"_s")}">{esc(text)}</button>'
ENGINE_JS = r"""
class Component extends DCLogic {
  constructor(p) { super(p); this.state = { sel: {}, open: null, sort: {}, msg: {}, added: {} }; }
  renderVals() {
    const st = this.state, v = {}, self = this;
    const set = (patch) => self.setState(patch);
    const selOf = (w) => (st.sel[w.id] === undefined ? w.dflt : st.sel[w.id]);
    v.closeAll = () => set({ open: null });
    const vis = {};
    for (const w of SPEC) {
      const cur = selOf(w);
      const toggleOpen = () => set({ open: st.open === w.id ? null : w.id });
      if (w.type === 'seg' || w.type === 'chips') {
        w.opts.forEach((o, i) => {
          v[w.id + '_s' + i] = (i === cur ? w.on : w.off);
          v[w.id + '_v' + i] = (i === cur);
          v[w.id + '_p' + i] = () => set({ sel: Object.assign({}, st.sel, { [w.id]: i }), open: null });
        });
      }
      if (w.type === 'pick') {
        v[w.id + '_label'] = (cur >= 0 && w.opts[cur] !== undefined) ? w.opts[cur] : '';
        v[w.id + '_open'] = toggleOpen;
        v[w.id + '_st'] = w.mst + (st.open === w.id ? '' : 'display: none;');
        v[w.id + '_bst'] = (cur !== w.none ? w.bon : w.boff);
        v[w.id + '_cst'] = (w.cst || '') + (cur !== w.none ? '' : 'display: none;');
        v[w.id + '_clear'] = () => set({ sel: Object.assign({}, st.sel, { [w.id]: w.none }), open: null });
        w.opts.forEach((o, i) => {
          v[w.id + '_p' + i] = () => set({ sel: Object.assign({}, st.sel, { [w.id]: i }), open: null });
          v[w.id + '_i' + i] = (i === cur ? w.ion : w.ioff);
        });
      }
      if (w.type === 'menu') { v[w.id + '_open'] = toggleOpen; v[w.id + '_st'] = w.mst + (st.open === w.id ? '' : 'display: none;'); }
      if (w.type === 'sort') {
        const s = st.sort[w.id] || { c: w.dflt, d: !!w.desc };
        const om = String(st.open || '');
        const openCol = (om.indexOf(w.id + 'm') === 0) ? parseInt(om.slice(w.id.length + 1), 10) : -1;
        for (let i = 0; i < w.n; i++) {
          v[w.id + '_a' + i] = (i === s.c ? (s.d ? '▼' : '▲') : '⇅');
          v[w.id + '_h' + i] = (i === s.c ? w.hon[i] : w.hoff[i]);
          v[w.id + '_p' + i] = () => set({ sort: Object.assign({}, st.sort, { [w.id]: { c: i, d: (i === s.c ? !s.d : false) } }), open: null });
          v[w.id + '_m' + i] = () => set({ open: (om === w.id + 'm' + i ? null : w.id + 'm' + i) });
        }
        v[w.id + '_mst'] = w.mst + (openCol >= 0 ? '' : 'display: none;');
        v[w.id + '_mcol'] = openCol >= 0 ? w.cols[openCol] : '';
        for (let i = 0; i < w.n; i++) {
          v[w.id + '_mv' + i] = (openCol === i);
          const mw = SPEC.find((x) => x.type === 'multi' && x.tbl === w.id && x.col === i);
          const cnt = mw ? (st.sel[mw.id] || []).length : 0;
          v[w.id + '_f' + i] = cnt ? ('· ' + cnt) : '';
        }
        v[w.id + '_mclear'] = () => { const s2 = Object.assign({}, st.sel); SPEC.forEach((x) => { if (x.type === 'multi' && x.tbl === w.id && x.col === openCol) s2[x.id] = []; }); set({ sel: s2, open: null }); };
        v[w.id + '_asc'] = () => set({ sort: Object.assign({}, st.sort, { [w.id]: { c: openCol, d: false } }), open: null });
        v[w.id + '_desc'] = () => set({ sort: Object.assign({}, st.sort, { [w.id]: { c: openCol, d: true } }), open: null });
        v[w.id + '_grp'] = () => { const p = {}; if (w.group) { p[w.group] = w.cols.filter((c) => c).indexOf(w.cols[openCol]); } set({ sel: Object.assign({}, st.sel, p), open: null }); };
      }
      if (w.type === 'drawer') {
        v[w.id + '_open'] = () => set({ open: w.id });
        v[w.id + '_st'] = w.mst + (st.open === w.id ? '' : 'display: none;');
        v[w.id + '_add'] = () => set({ open: null, added: Object.assign({}, st.added, { [w.id]: true }) });
        v[w.id + '_row'] = (st.added[w.id] ? '' : 'display: none;');
        v[w.id + '_btn'] = (st.added[w.id] && w.done) ? w.done : w.label;
      }
      if (w.type === 'msg') {
        w.opts.forEach((o, i) => { v[w.id + '_p' + i] = () => set({ msg: Object.assign({}, st.msg, { [w.id]: w.msgs[i] }), open: null }); });
        v[w.id + '_text'] = st.msg[w.id] || '';
        v[w.id + '_tst'] = w.tst + (st.msg[w.id] ? '' : 'display: none;');
      }
      if (w.type === 'cards' || w.type === 'rowsel') {
        w.opts.forEach((o, i) => {
          v[w.id + '_p' + i] = () => set({ sel: Object.assign({}, st.sel, { [w.id]: i }), open: null });
          v[w.id + '_s' + i] = (i === cur ? w.on : w.off);
          v[w.id + '_c' + i] = (i === cur ? '' : 'display: none;');
          v[w.id + '_b' + i] = (i === cur ? 'display: none;' : '');
        });
      }
      if (w.type === 'multi') {
        const curm = st.sel[w.id] || [];
        w.opts.forEach((o, i) => {
          v[w.id + '_p' + i] = () => { const s = (st.sel[w.id] || []).slice(); const k = s.indexOf(i); if (k >= 0) s.splice(k, 1); else s.push(i); set({ sel: Object.assign({}, st.sel, { [w.id]: s }) }); };
          v[w.id + '_i' + i] = (curm.indexOf(i) >= 0 ? w.ion : w.ioff);
          v[w.id + '_c' + i] = (curm.indexOf(i) >= 0 ? '☑' : '☐');
        });
        v[w.id + '_n'] = curm.length ? (curm.length + ' de ' + w.opts.length) : 'todos';
        v[w.id + '_clear'] = () => set({ sel: Object.assign({}, st.sel, { [w.id]: [] }) });
      }
      if (w.type === 'toggle') {
        const on = !!st.sel[w.id];
        v[w.id + '_p'] = () => set({ sel: Object.assign({}, st.sel, { [w.id]: !on }) });
        v[w.id + '_s'] = on ? w.on : w.off;
      }
      if (w.tbl && w.rows) {
        const arr = vis[w.tbl] || (vis[w.tbl] = w.rows.map(() => true));
        let m = null;
        if (w.type === 'toggle') m = st.sel[w.id] ? w.keep : null;
        else if (w.type === 'multi') { const cm = st.sel[w.id] || []; m = cm.length ? cm : null; }
        else if (w.match) m = w.match[cur];
        w.rows.forEach((r, ri) => {
          let ok = true;
          if (m === null || m === undefined) ok = true;
          else if (w.type === 'toggle') ok = m.indexOf(ri) >= 0;
          else if (w.type === 'multi') ok = m.some((i) => w.cells[ri] === w.opts[i]);
          else if (Array.isArray(m)) ok = m.some((x) => r.indexOf(x) >= 0);
          else ok = r.indexOf(m) >= 0;
          arr[ri] = arr[ri] && ok;
        });
      }
    }
    for (const t in vis) {
      vis[t].forEach((ok, ri) => { v[t + '_r' + ri] = ok ? '' : 'display: none;'; });
      v[t + '_count'] = vis[t].filter(Boolean).length;
      v[t + '_clear'] = () => { const s2 = Object.assign({}, st.sel); SPEC.forEach((w) => { if (w.tbl === t && w.type === 'toggle') s2[w.id] = false; else if (w.tbl === t && w.type === 'pick') s2[w.id] = w.none; else if (w.tbl === t && w.type === 'chips') s2[w.id] = 0; else if (w.tbl === t && w.type === 'multi') s2[w.id] = []; }); set({ sel: s2, open: null }); };
    }
    return v;
  }
}
"""
def engine():
    """script do artboard: spec dos widgets desta tela + motor; limpa o registro para a próxima tela."""
    spec=json.dumps(WIDGETS,ensure_ascii=False).replace('</','<\\/')
    return 'const SPEC = '+spec+';\n'+ENGINE_JS
def extra_html(): return ''.join(EXTRA)
def navlink(m,act):
    return (f'<a href="{MODHOME.get(m,"#")}" style="display: flex; align-items: center; gap: 10px; padding: 7px 12px; border-radius: 10px; font-size: 13px; text-decoration: none; color: {"#fff" if act else SIDE_TX}; background: {ACC if act else "transparent"}; font-weight: {700 if act else 500};">{icon(m,17,"#fff" if act else SIDE_MUTED)}{esc(m)}</a>')
def openlink(href=None):
    href=href or ROW or TABLEHREF.get(CUR) or '#'
    return f'<a href="{href}" aria-label="Abrir" style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 8px; color: {MUTED}; text-decoration: none; font-size: 18px;">›</a>'
def act(text=None,href=None,urgent=False,open=False,menu=False,edit=None):
    """Célula de ação de linha: botão pequeno (opcional) e, quando a linha abre um detalhe, a seta › sempre na borda direita."""
    b=''
    if menu:
        m=wid('m'); reg(type='menu',id=m,mst=LIST_ST(True))
        if edit:
            d=DRAWERS.get((CUR,edit)) or DRAWERS.get(edit)
            if d and edit not in DRAWN: drawer_button(edit,d)
            ehole=HL(DRAWN[edit]+'_open') if edit in DRAWN else HL('closeAll')
        else: ehole=HL('closeAll')
        items=f'<button type="button" onClick="{ehole}" style="{ITEM_ON()}">Editar</button>'+''.join(f'<button type="button" onClick="{HL("closeAll")}" style="{ITEM_OFF()}{" color: "+RED+";" if t=="Excluir" else ""}">{t}</button>' for t in ('Duplicar','Mover para cima','Mover para baixo','Excluir'))
        b=f'<span style="position: relative; display: inline-flex;"><button type="button" aria-label="Mais ações" aria-haspopup="menu" onClick="{HL(m+"_open")}" style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 8px; color: {MUTED}; border: 0; background: transparent; cursor: pointer; font-size: 18px; letter-spacing: 1px;">⋯</button><div role="menu" style="{HL(m+"_st")}">{items}</div></span>'
    elif text:
        st=(f"padding: 7px 14px; border-radius: 10px; font-size: 13px; font-weight: 700; font-family: inherit; cursor: pointer; line-height: 1.25; white-space: nowrap; text-decoration: none; display: inline-block; background: {SURF}; "
            + (f"color: {RED}; border: 1px solid {RED};" if urgent else f"color: {INK}; border: 1px solid {LINE};"))
        dest=href or ROW or TABLEHREF.get(CUR) or BTNHREF.get((CUR,text)) or BTNHREF.get(text)
        if dest: b=f'<a href="{dest}" style="{st}">{esc(text)}</a>'
        elif (DRAWERS.get((CUR,text)) or DRAWERS.get(text)): b=drawer_button(text,DRAWERS.get((CUR,text)) or DRAWERS.get(text),False,True).replace(BTN_ST(False,True),st)
        elif (MSGS.get((CUR,text)) or MSGS.get(text)): b=msgbtn(text,MSGS.get((CUR,text)) or MSGS.get(text),False,True).replace(BTN_ST(False,True),st)
        else: b=f'<button type="button" style="{st}">{esc(text)}</button>'
    arrow=openlink(href) if open else ''
    return f'<div style="display: flex; align-items: center; justify-content: {"flex-end" if open else "flex-start"}; gap: 8px; white-space: nowrap;">{b}{arrow}</div>'
def legend(items):
    return '<div style="display: inline-flex; gap: 14px; align-items: center; font-size: 12px; color: '+MUTED+'; font-weight: 600;">'+''.join(f'<span style="display: inline-flex; align-items: center; gap: 6px;"><span style="width: 10px; height: 10px; border-radius: 3px; background: {c};"></span>{esc(t)}</span>' for c,t in items)+'</div>'
def toolrow(left,right=''):
    return f'<div style="display: flex; align-items: center; gap: 12px;">{left}<span style="flex-grow: 1;"></span>{right}</div>'
PRAZO={'atrasada':('▲','#C62828','#fff'),'vence hoje':('●','#EF6C00','#1B1B1B'),'até 3 dias':('◆','#F9A825','#1B1B1B'),'no prazo':('○','#2E7D32','#fff'),'irrigando':('●','#1E88E5','#fff')}
def prazo(faixa,detalhe=''):
    """pílula da régua de prazo: 4 faixas iguais em lista, detalhe, mapa, Hoje e celular."""
    ic,bg,fg=PRAZO[faixa]
    return f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; color: {fg}; background: {bg}; white-space: nowrap;">{ic} {esc(faixa)}{(" · "+esc(detalhe)) if detalhe else ""}</span>'
def nc_bar(valor, nc, unidade=''):
    """contagem contra o nível de controle: barra com o NC marcado; cor pela proporção."""
    pct = min(140, valor / nc * 100) if nc else 0
    c = ACC if pct < 70 else (YEL if pct < 100 else RED)
    return (f'<div style="display: flex; align-items: center; gap: 8px; min-width: 120px;"><div style="position: relative; flex-grow: 1; height: 8px; background: {GRAYS}; border-radius: 999px; overflow: visible;">'
            f'<div style="width: {min(pct,100)}%; height: 100%; background: {c}; border-radius: 999px;"></div><span style="position: absolute; left: 71%; top: -3px; width: 2px; height: 14px; background: {INK};"></span></div>'
            f'<span style="font-size: 12.5px; font-weight: 700; color: {c}; white-space: nowrap;">{esc(str(valor))} / {esc(str(nc))}{(" "+esc(unidade)) if unidade else ""}</span></div>')
def route_map(h=360):
    """mapa do talhão com rota em W e pontos de contagem coloridos pelo pior alvo do ponto."""
    pts=[(70,60,ACC),(170,120,ACC),(270,60,YEL),(370,120,RED),(470,60,RED),(570,120,YEL),(630,60,ACC),
         (630,230,ACC),(530,290,YEL),(430,230,RED),(330,290,ACC),(230,230,ACC),(130,290,ACC),(70,230,ACC)]
    s=f'<svg viewBox="0 0 700 {h}" style="width: 100%; height: {h}px; display: block; border-radius: 10px;" role="img" aria-label="Rota de monitoramento em W">'
    s+=f'<rect x="0" y="0" width="700" height="{h}" fill="#E3EBDD"/><polygon points="20,20 680,24 690,{h-20} 14,{h-24}" fill="#B5E61D" fill-opacity=".55" stroke="#fff" stroke-width="3"/>'
    s+='<polyline points="'+' '.join(f'{x},{y}' for x,y,_ in pts)+f'" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5" opacity=".6"/>'
    for i,(x,y,c) in enumerate(pts,1):
        s+=f'<circle cx="{x}" cy="{y}" r="13" fill="{c}" stroke="#fff" stroke-width="2.5"/><text x="{x}" y="{y+4}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{i}</text>'
    s+=f'<rect x="440" y="{h-58}" width="230" height="44" rx="8" fill="#fff" fill-opacity=".92"/><text x="452" y="{h-40}" font-size="11" font-weight="700" fill="{INK}">Mancha de percevejo · pontos 4, 5, 10</text><text x="452" y="{h-24}" font-size="10.5" fill="{MUTED}">bordadura leste · 41 ha · 3,2/pano</text></svg>'
    return s

def chev():
    return f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>'
def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def chip(text,kind='gray'):
    c={'green':(ACC,ACCS),'yellow':(YEL,YELS),'red':(RED,REDS),'gray':(GRAY,GRAYS)}[kind]
    return f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; color: {c[0]}; background: {c[1]}; white-space: nowrap;"><span style="width: 6px; height: 6px; border-radius: 999px; background: {c[0]};"></span>{esc(text)}</span>'
def tag(text):
    return f'<span style="display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 12px; font-weight: 600; color: {MUTED}; border: 1px solid {LINE}; white-space: nowrap;">{esc(text)}</span>'
_orig=lambda t: f'<span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {BG}; border: 1px solid {LINE}; font-size: 11px; color: {MUTED}; white-space: normal; line-height: 1.3; max-width: 150px;">{esc(t)}</span>'
def btn(text,primary=False,small=False,href=None):
    href=href or BTNHREF.get((CUR,text)) or BTNHREF.get(text)
    if not href:
        d=DRAWERS.get((CUR,text)) or DRAWERS.get(text)
        if d: return drawer_button(text,d,primary,small)
        m=MSGS.get((CUR,text)) or MSGS.get(text)
        if m: return msgbtn(text,m,primary,small)
    pad='7px 14px' if small else '11px 20px'; fs='13px' if small else '14px'
    st=(f"padding: {pad}; border-radius: 10px; font-size: {fs}; font-weight: 700; font-family: inherit; cursor: pointer; line-height: 1.25; letter-spacing: -.005em; white-space: nowrap; "
        + (f"background: {ACC}; color: #fff; border: 1px solid {ACC}; box-shadow: 0 1px 2px rgba(30,122,76,.25);" if primary else f"background: {SURF}; color: {INK}; border: 1px solid {LINE};"))
    if href: return f'<a href="{href}" style="text-decoration: none; display: inline-block; {st}">{esc(text)}</a>'
    return f'<button type="button" style="{st}">{esc(text)}</button>'
def integ(items,out=None):
    pills=''
    for L,txt in items:
        pills+=(f'<span style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px 6px 6px; border-radius: 999px; background: {SURF}; border: 1px solid {LINE}; font-size: 12.5px; font-weight: 500;">'
                f'<span style="width: 20px; height: 20px; border-radius: 999px; background: {INK}; color: #fff; font-weight: 700; font-size: 11px; display: inline-flex; align-items: center; justify-content: center;">{L}</span>{esc(txt)}</span>')
    o=f'<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; color: {ACC}; font-weight: 600; padding-left: 4px;">→ {esc(out)}</span>' if out else ''
    return f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;"><span style="font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: {MUTED}; font-weight: 600; padding-right: 4px;">Integração</span>{pills}{o}</div>'
ON,OFF,LOCK,AMBER='on','off','locked','amber'
CTX={
 'Main.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[]),
 'HomeCadastros.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'HomeAgronomia.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'HomePCP.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'HomePCM.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'HomeCompras.dc.html':(('2026/27',ON),('Todas',ON),[]),'HomeCampo.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[]),'HomeIrrigacao.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[]),'HomeOficina.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'HomeColheita.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[]),'HomeBeneficiamento.dc.html':(('Todas com saldo',ON),('Santa Rita',ON),[]),'HomeVendas.dc.html':(('Todas com saldo',ON),('Todas',ON),[]),'HomeLogistica.dc.html':(('Todas com saldo',ON),('Santa Rita',ON),[]),'HomeControle.dc.html':(('2025/26 · Encerrada',AMBER),('Santa Rita',ON),[]),
 'Talhoes.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False)]),'HomePCE.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'PlanosManutencao.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),'PlanoManutencao.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),'Indicadores.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'HomeEstoque.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'Politicas.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'Cobertura.dc.html':(('2026/27',ON),('Santa Rita',ON),[]),'Inventario.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'Recebimento.dc.html':(('2026/27',OFF),('Santa Rita',LOCK),[]),'Talhao.dc.html':(('2026/27',ON),('Santa Rita',LOCK),[]),'Operacoes.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),'Prescricao.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'Monitoramento.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),'Vistoria.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'MobileVistoria.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'MobileHoje.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'MobileOS.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'MobileOcorrencia.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'MobileCaixa.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'MobileAlmox.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),'Analises.dc.html':(('2026/27',OFF),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),'Operacao.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),'Insumo.dc.html':(('2026/27',ON),('Santa Rita',OFF),[]),
 'Maquinas.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'Maquina.dc.html':(('2026/27',OFF),('Santa Rita',LOCK),[]),
 'Planos.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False)]),'Plano.dc.html':(('2026/27',LOCK),('Santa Rita',ON),[]),
 'Insumos.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),
 'Diagnostico.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
 'Safras.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'Safra.dc.html':(('2026/27',LOCK),('Santa Rita',ON),[]),
 'Calculo.dc.html':(('2026/27',LOCK),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
 'Solo.dc.html':(('2026/27',LOCK),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
 'Programacao.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
 'Frota.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False)]),
 'Carga.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False)]),
 'Orcamento.dc.html':(('2026/27',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
 'PCM.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),'OSManutencao.dc.html':(('2026/27',OFF),('Santa Rita',LOCK),[]),
 'CompraLiquida.dc.html':(('2026/27',ON),('Todas',ON),[('Cultura','Todas',False)]),'Cotacoes.dc.html':(('2026/27',ON),('Todas',ON),[]),'Pagamento.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),
 'Almoxarifado.dc.html':(('2026/27',OFF),('Santa Rita',ON),[]),
 'OSCampoLista.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','T1, T2',True)]),'OSCampo.dc.html':(('2026/27',LOCK),('Santa Rita',LOCK),[]),
 'Balanco.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Pivô','Todos',False)]),'Pivos.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[]),
 'OSOficina.dc.html':(('2026/27',OFF),('Santa Rita',LOCK),[]),
 'Beneficiamento.dc.html':(('Todas com saldo',ON),('Santa Rita',ON),[('Produto','Todos',False)]),'Oferta.dc.html':(('Todas com saldo',ON),('Todas',ON),[]),'Expedicao.dc.html':(('Todas com saldo',ON),('Santa Rita',ON),[('Produto','Todos',False)]),
 'Realizado.dc.html':(('2025/26 · Encerrada',AMBER),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
 'Mercado.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),'Mercado.dc.html':(('2026/27',OFF),('Santa Rita',OFF),[]),
 'MapaFazenda.dc.html':(('Em andamento · 2',ON),('Santa Rita',ON),[('Cultura','Todas',False),('Talhão','Todos',False)]),
}
SAFRAS=['2026/27','2025/26','Feijão pivô inverno 2026','Em andamento · 2','Todas com saldo','2025/26 · Encerrada']
FAZENDAS=['Santa Rita','Boa Vista','Todas']
VALS={'Cultura':['Soja','Milho','Feijão'],'Talhão':['T1','T2','T3','T4','P1','P2'],'Pivô':['Pivô 1','Pivô 2'],'Produto':['Soja','Milho','Feijão']}
def pill(label,value,state):
    lock=f'<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" stroke-width="2.4" stroke-linecap="round" aria-label="fixo por este registro"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'
    base='display: inline-flex; align-items: center; gap: 7px; padding: 5px 11px; border-radius: 999px; font-size: 12.5px; line-height: 1.2; white-space: nowrap;'
    if state==OFF:
        return f'<span title="{esc(label)} não se aplica a esta tela" style="{base} background: transparent; border: 1px solid {LINE}; color: {MUTED}; opacity: .55;"><span style="font-weight: 600;">{esc(label)}</span><span>{esc(value)}</span></span>'
    if state==LOCK:
        return f'<span style="{base} background: {BG}; border: 1px solid {LINE}; color: {MUTED};"><span style="font-weight: 600;">{esc(label)}</span><span style="color: {INK}; font-weight: 700;">{esc(value)}</span>{lock}</span>'
    opts=[value]+[o for o in (SAFRAS if label=='Safra' else FAZENDAS) if o!=value]
    if state==AMBER:
        _,html_=pick(opts,0,none=-1,on=f'{base} background: {YELS}; border: 1px solid #E9D39B; color: {YEL}; font-family: inherit; cursor: pointer;',off=f'{base} background: {YELS}; border: 1px solid #E9D39B; color: {YEL}; font-family: inherit; cursor: pointer;',chipx=False)
        return html_.replace('<span style="font-weight: 700;">',f'<span style="width: 7px; height: 7px; border-radius: 999px; background: {YEL};"></span><span style="font-weight: 600;">{esc(label)}</span><span style="font-weight: 700;">',1)
    if True:
        _,html_=pick(opts,0,none=-1,on=f'{base} background: {SURF}; border: 1px solid {LINE}; color: {MUTED}; font-family: inherit; cursor: pointer;',off=f'{base} background: {SURF}; border: 1px solid {LINE}; color: {MUTED}; font-family: inherit; cursor: pointer;',chipx=False)
        return html_.replace('<span style="font-weight: 700;">',f'<span style="width: 7px; height: 7px; border-radius: 999px; background: {ACC};"></span><span style="font-weight: 600;">{esc(label)}</span><span style="font-weight: 700; color: {INK};">',1)
    if state==AMBER:
        return f'<button type="button" aria-haspopup="listbox" style="{base} background: {YELS}; border: 1px solid #E9D39B; color: {YEL}; font-family: inherit; cursor: pointer;"><span style="width: 7px; height: 7px; border-radius: 999px; background: {YEL};"></span><span style="font-weight: 600;">{esc(label)}</span><span style="font-weight: 700;">{esc(value)}</span><span aria-hidden="true" style="font-size: 10px;">▾</span></button>'
    return f'<button type="button" aria-haspopup="listbox" style="{base} background: {SURF}; border: 1px solid {LINE}; color: {MUTED}; font-family: inherit; cursor: pointer;"><span style="width: 7px; height: 7px; border-radius: 999px; background: {ACC};"></span><span style="font-weight: 600;">{esc(label)}</span><span style="color: {INK}; font-weight: 700;">{esc(value)}</span><span aria-hidden="true" style="font-size: 10px;">▾</span></button>'
def cultpill(fname):
    """macrofiltro Cultura no topo, ao lado de Safra e Fazenda; filtra a primeira tabela quando a tela tem recorte por cultura."""
    c=CTX.get(fname)
    if not c: return ''
    (sv,ss),(fv,fs),scope=c
    base='display: inline-flex; align-items: center; gap: 7px; padding: 5px 11px; border-radius: 999px; font-size: 12.5px; line-height: 1.2; white-space: nowrap;'
    ent=next((t for t in scope if t[0]=='Cultura'),None)
    if not ent and ss in (OFF,LOCK): return pill('Cultura','—',OFF)
    vals=VALS['Cultura']+['Mamão Formosa']
    if ent:
        _,val,active=ent
        if active: opts=[val,'Todas']+[v for v in vals if v not in val.split(', ')]; match=[val.split(', '),None]+[[v] for v in vals if v not in val.split(', ')]; none=1
        else: opts=['Todas']+vals; match=[None]+[[v] for v in vals]; none=0
        tbl=FIRST_TBL[0]
    else:
        opts=['Todas']+vals; match=None; none=0; tbl=None
    on=f'{base} background: {ACCS}; border: 1px solid {ACC}; color: {ACC}; font-family: inherit; cursor: pointer;'
    off=f'{base} background: {SURF}; border: 1px solid {LINE}; color: {MUTED}; font-family: inherit; cursor: pointer;'
    _,html_=pick(opts,0,none=none,tbl=tbl,match=match,on=on,off=off,chipx=False)
    return html_.replace('<span style="font-weight: 700;">',f'<span style="width: 7px; height: 7px; border-radius: 999px; background: {ACC};"></span><span style="font-weight: 600;">Cultura</span><span style="font-weight: 700; color: {INK};">',1)
def ctxpills(fname):
    c=CTX.get(fname)
    if not c: return ''
    (sv,ss),(fv,fs),_=c
    return f'<div style="display: inline-flex; align-items: center; gap: 6px;">{pill("Safra",sv,ss)}{pill("Fazenda",fv,fs)}{cultpill(fname)}</div>'
def scopechips(fname):
    c=CTX.get(fname)
    if not c or not c[2]: return ''
    out=''
    for name,val,active in c[2]:
        if name=='Cultura': continue
        allw='Todas' if name in ('Cultura',) else 'Todos'
        vals=VALS.get(name,[])
        if active:
            opts=[val,allw]+[v for v in vals if v not in val.split(', ')]; match=[val.split(', '),None]+[[v] for v in vals if v not in val.split(', ')]; none=1
        else:
            opts=[allw]+vals; match=[None]+[[v] for v in vals]; none=0
        on=f'display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; background: {ACCS}; border: 1px solid {ACC}; color: {ACC}; font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer;'
        off=f'display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; background: {SURF}; border: 1px solid {LINE}; color: {MUTED}; font-family: inherit; font-size: 12.5px; font-weight: 600; cursor: pointer;'
        _,html_=pick(opts,0,none=none,tbl=FIRST_TBL[0],match=match,label=name,on=on,off=off)
        out+=html_
    return f'<div style="display: inline-flex; align-items: center; gap: 6px; margin-left: auto;">{out}</div>'
def ctxbar(items):
    """items: list of (label, value, state) state in {'open','locked','derived'}; open = seletor; locked = fixo pela tela (cadeado); derived = herdado do registro"""
    out=''
    for label,value,state in items:
        if state=='locked':
            out+=(f'<span style="display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; background: {BG}; border: 1px solid {LINE}; font-size: 13px; color: {MUTED};">'
                  f'<span style="font-weight: 600;">{esc(label)}</span><span style="color: {INK}; font-weight: 700;">{esc(value)}</span>'
                  f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" stroke-width="2.2" stroke-linecap="round" aria-label="fixo nesta tela"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg></span>')
        elif state=='derived':
            out+=(f'<span style="display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; background: {SURF}; border: 1px dashed {LINE}; font-size: 13px; color: {MUTED};">'
                  f'<span style="font-weight: 600;">{esc(label)}</span><span style="color: {INK}; font-weight: 700;">{esc(value)}</span></span>')
        else:
            out+=(f'<button type="button" aria-haspopup="listbox" style="display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; background: {SURF}; border: 1px solid {LINE}; font-family: inherit; font-size: 13px; color: {MUTED}; cursor: pointer;">'
                  f'<span style="font-weight: 600;">{esc(label)}</span><span style="color: {INK}; font-weight: 700;">{esc(value)}</span><span aria-hidden="true" style="font-size: 10px; color: {MUTED};">▾</span></button>')
    return f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{out}</div>'
def cards_widget(items):
    k=wid('k'); reg(type='cards',id=k,opts=[t for t,_,_,_ in items],dflt=next((i for i,x in enumerate(items) if x[3]),0),on=f'background: {SURF}; border: 2px solid {ACC}; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 8px;',off=f'background: {SURF}; border: 2px solid {LINE}; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 8px;')
    return ''.join(f'<div style="{HL(k+"_s"+str(i))}"><div style="font-size: 15px; font-weight: 600;">{esc(t)}</div><div style="font-size: 22px; font-weight: 600; color: {ACC};">{esc(v)}</div><div style="font-size: 13px; color: {MUTED};">{esc(d)}</div><div style="flex-grow: 1;"></div><div style="display: flex; justify-content: flex-end;"><span style="{HL(k+"_c"+str(i))}">{chip("Escolhido","green")}</span><span style="{HL(k+"_b"+str(i))}"><button type="button" onClick="{HL(k+"_p"+str(i))}" style="{BTN_ST(False,True)}">Escolher</button></span></div></div>' for i,(t,v,d,sel) in enumerate(items))
def kpis(items):
    cells=''.join(f'<div style="flex-grow: 1; padding: 16px 18px; background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; display: flex; flex-direction: column; gap: 8px;"><div style="font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: {MUTED}; font-weight: 700;">{esc(l)}</div><div style="font-family: {DISP}; font-size: 30px; font-weight: 700; letter-spacing: -.02em; color: {ACC if i==len(items)-1 else INK}; font-variant-numeric: tabular-nums; line-height: 1.1;">{esc(v)} <span style="font-size: 12px; color: {MUTED}; font-weight: 400; letter-spacing: 0;">{esc(u)}</span></div></div>' for i,(l,v,u) in enumerate(items))
    return f'<div style="display: flex; gap: 14px;">{cells}</div>'
TABLEHREF={'PlanosManutencao.dc.html':'PlanoManutencao.dc.html','PlanoManutencao.dc.html':None,'Indicadores.dc.html':None,'Politicas.dc.html':'Insumo.dc.html','Cobertura.dc.html':'Insumo.dc.html','Inventario.dc.html':'Insumo.dc.html','Recebimento.dc.html':'Insumo.dc.html','Monitoramento.dc.html':'Vistoria.dc.html','Vistoria.dc.html':None,'Prescricao.dc.html':None,'Analises.dc.html':'Solo.dc.html','Operacoes.dc.html':'Operacao.dc.html','Operacao.dc.html':None,'Talhoes.dc.html':'Talhao.dc.html','Maquinas.dc.html':'Maquina.dc.html','Insumos.dc.html':'Insumo.dc.html','Planos.dc.html':'Plano.dc.html','Diagnostico.dc.html':'Talhao.dc.html','Safra.dc.html':'Talhao.dc.html','Solo.dc.html':'Talhao.dc.html','Calculo.dc.html':'Insumo.dc.html','Carga.dc.html':'Frota.dc.html','Frota.dc.html':'Carga.dc.html','Orcamento.dc.html':'Talhao.dc.html','PCM.dc.html':'Maquina.dc.html','OSManutencao.dc.html':'Insumo.dc.html','CompraLiquida.dc.html':'Cotacoes.dc.html','Cotacoes.dc.html':'LinkFornecedor.dc.html','Almoxarifado.dc.html':'Insumo.dc.html','OSCampoLista.dc.html':'OSCampo.dc.html','OSCampo.dc.html':'Insumo.dc.html','Balanco.dc.html':'Pivos.dc.html','Pivos.dc.html':'Balanco.dc.html','OSOficina.dc.html':'Insumo.dc.html','Beneficiamento.dc.html':'Expedicao.dc.html','Oferta.dc.html':'LinkCliente.dc.html','Expedicao.dc.html':'Oferta.dc.html','Realizado.dc.html':'Talhao.dc.html','MapaFazenda.dc.html':'Talhao.dc.html','Maquina.dc.html':'OSManutencao.dc.html','Talhao.dc.html':'OSCampo.dc.html','Insumo.dc.html':'OSCampo.dc.html','Mercado.dc.html':'Mercado.dc.html','Plano.dc.html':None}
def table(headers,rows,widths=None,sort=0,desc=False,filters=None,total=None,group=None,search=True,popover=None,dense=False,rowhref=None,extra_rows=None):
    filters=filters or {}
    n=len(headers)
    wide=n>=8 or dense; ultra=n>=11
    fs='12px' if ultra else ('12.5px' if wide else '13.5px'); pad='6px 8px' if ultra else ('8px 10px' if wide else '12px 14px'); thpad='7px 4px 7px 6px' if ultra else ('9px 4px 9px 8px' if wide else '12px 6px 12px 14px')
    tbl=wid('tbl')
    if FIRST_TBL[0] is None: FIRST_TBL[0]=tbl
    rh=rowhref or ROW or TABLEHREF.get(CUR)
    data=[r for r in rows if not (isinstance(r,tuple) and r and r[0]=='__group__')]
    shown=len(data); tot=total or shown
    cols=[hd for hd in headers if hd]
    gp,ghtml=pick(cols,(cols.index(group) if group in cols else -1),none=-1,right=True,on=f'font-family: inherit; font-size: 12.5px; font-weight: 700; color: {INK}; background: {SURF}; border: 1px solid {LINE}; border-radius: 999px; cursor: pointer; padding: 6px 12px;',off=f'font-family: inherit; font-size: 12.5px; font-weight: 700; color: {INK}; background: {SURF}; border: 1px solid {LINE}; border-radius: 999px; cursor: pointer; padding: 6px 12px;',chipx=False)
    ghtml=ghtml.replace('<span style="font-weight: 700;">'+HL(gp+'_label')+'</span>','+ Agrupar por')
    wget(gp)['cst']=GCHIP_ST()
    gchip=f'<span style="{HL(gp+"_cst")}">Agrupado por {HL(gp+"_label")}<button type="button" aria-label="Remover agrupamento" onClick="{HL(gp+"_clear")}" style="border: 0; background: transparent; color: #fff; cursor: pointer; font-size: 13px; padding: 0 4px;">×</button></span>'
    fchips=''.join(f'<span style="display: inline-flex; align-items: center; gap: 4px; padding: 3px 4px 3px 10px; border-radius: 999px; background: {ACCS}; color: {ACC}; font-size: 12px; font-weight: 700;">{esc(headers[i])}: {esc(v)} <button type="button" aria-label="Limpar filtro" onClick="{HL(tbl+"_clear")}" style="border: 0; background: transparent; color: {ACC}; cursor: pointer; font-size: 13px; padding: 0 4px;">×</button></span>' for i,v in filters.items())
    sicon=f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'
    tb=(f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-bottom: 1px solid {LINE};">'
        f'<label style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border: 1px solid {LINE}; border-radius: 999px; background: {BG}; font-size: 13px; color: {MUTED}; min-width: 170px;">{sicon}<input type="search" aria-label="Buscar na tabela" placeholder="Buscar nesta tabela…" style="font-family: inherit; font-size: 13px; border: 0; background: transparent; outline: none; width: 100%;"></label>'
        f'<span style="font-size: 12.5px; color: {MUTED}; font-weight: 600;">{HL(tbl+"_count")} de {tot} linhas</span>{fchips}{gchip}'
        f'<span style="flex-grow: 1;"></span>'
        + (f'<button type="button" onClick="{HL(tbl+"_clear")}" style="font-family: inherit; font-size: 12.5px; font-weight: 700; color: {ACC}; background: transparent; border: 0; cursor: pointer; padding: 4px 6px;">Limpar filtros</button>' if filters else '')
        + ghtml + '</div>') if search else ''
    th=''; hon=[]; hoff=[]
    funnel=f'<svg width="11" height="11" viewBox="0 0 24 24" fill="{ACC}" stroke="{ACC}" stroke-width="1.5" stroke-linejoin="round" aria-label="filtrada"><path d="M3 4h18l-7 8v6l-4 2v-8z"/></svg>'
    for i,hd in enumerate(headers):
        active=(i==sort); fil=filters.get(i)
        base=f'display: inline-flex; align-items: center; gap: 4px; padding: {thpad}; border: 0; background: transparent; cursor: pointer; font-family: inherit; font-size: {"10.5px" if wide else "11px"}; letter-spacing: {".03em" if wide else ".06em"}; text-transform: uppercase; font-weight: 700; text-align: left; white-space: {"normal" if wide else "nowrap"};'
        hon.append(base+f' color: {ACC};'); hoff.append(base+f' color: {ACC if fil else MUTED};')
        if hd=='': th+=f'<th style="padding: 12px 8px; background: {BG};"></th>'; continue
        th+=(f'<th aria-sort="{"descending" if (active and desc) else ("ascending" if active else "none")}" style="text-align: left; padding: 0; background: {ACCS if fil else BG}; vertical-align: bottom;"><div style="display: flex; align-items: center;">'
             f'<button type="button" onClick="{HL(tbl+"_p"+str(i))}" style="{HL(tbl+"_h"+str(i))}">{hd}{" "+funnel if fil else ""}<span aria-hidden="true" style="font-size: 10px;">{HL(tbl+"_a"+str(i))}</span><span style="color: {ACC}; font-size: 10px; font-weight: 700;">{HL(tbl+"_f"+str(i))}</span></button>'
             f'<button type="button" aria-label="Menu da coluna {esc(hd)}" onClick="{HL(tbl+"_m"+str(i))}" style="border: 0; background: transparent; cursor: pointer; color: #B7C1BA; font-size: 9px; padding: 4px 4px 4px 0; line-height: 1;">▾</button></div></th>')
    item=lambda t,hole,acc=False,red=False: f'<button type="button" onClick="{HL(hole)}" style="{ITEM_ON() if acc else ITEM_OFF()}{" color: "+RED+";" if red else ""}">{t}</button>'
    _CMENU_HEAD=(f'<div role="menu" style="{HL(tbl+"_mst")}">'
           + item('▲ Ordenar crescente',tbl+'_asc',True) + item('▼ Ordenar decrescente',tbl+'_desc')
           + f'<div style="padding: 6px 12px 2px; font-size: 11px; color: {MUTED}; font-weight: 700; letter-spacing: .08em;">FILTRAR {HL(tbl+"_mcol")}</div>'
           + f'<div style="padding: 0 12px 6px;"><input type="text" aria-label="Filtrar coluna" placeholder="contém · =exato · >10 · 10..50 · a|b" style="width: 100%; box-sizing: border-box; font-family: inherit; font-size: 13px; padding: 8px 10px; border: 1px solid {LINE}; border-radius: 8px; background: {BG};"></div>')
    trs=''; ri=0; rowtexts=[]; coltexts=[]
    for r in rows:
        if isinstance(r,tuple) and r and r[0]=='__group__':
            trs+=f'<tr><td colspan="{n}" style="padding: 9px 14px; font-size: 13px; font-weight: 700; background: {ACCS}; border-top: 1px solid {LINE}; color: {ACC};"><span aria-hidden="true" style="display: inline-block; margin-right: 8px;">▾</span>{r[1]}<span style="color: {MUTED}; font-weight: 600; margin-left: 10px;">{r[2]}</span></td></tr>'
            continue
        tds=''
        for c in r:
            c=str(c)
            if rh and '<a ' not in c and '<button' not in c and '<input' not in c:
                tds+=f'<td style="padding: 0; font-size: {fs}; border-top: 1px solid {LINE}; vertical-align: middle; font-variant-numeric: tabular-nums;"><a href="{rh}" style="display: block; padding: {pad}; color: inherit; text-decoration: none; min-height: 1em;">{c}</a></td>'
            else:
                tds+=f'<td style="padding: {pad}; font-size: {fs}; border-top: 1px solid {LINE}; vertical-align: middle; font-variant-numeric: tabular-nums;">{c}</td>'
        trs+=f'<tr style="{HL(tbl+"_r"+str(ri))}">{tds}</tr>'
        rowtexts.append(re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',' '.join(str(c) for c in r)))).strip())
        coltexts.append([re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(c)))).strip()[:40] for c in r]); ri+=1
    for did,cells in (extra_rows or []):
        tds=''.join(f'<td style="padding: {pad}; font-size: {fs}; border-top: 1px solid {LINE}; vertical-align: middle; font-variant-numeric: tabular-nums; background: {ACCS};">{c}</td>' for c in cells)
        trs+=f'<tr style="{HL(did+"_row")}">{tds}</tr>'
    vlists=''
    for i,hd in enumerate(headers):
        if hd=='' or not coltexts: continue
        cells=[(row[i] if i<len(row) else '') for row in coltexts]
        vals=sorted({c for c in cells if c and c!='—'})
        if len(vals)<2 or len(vals)>14: continue
        fid=wid('f')
        reg(type='multi',id=fid,tbl=tbl,col=i,opts=vals,cells=cells,rows=rowtexts,ion=ITEM_ON(),ioff=ITEM_OFF())
        opts_html=''.join(f'<button type="button" role="menuitemcheckbox" onClick="{HL(fid+"_p"+str(k))}" style="{HL(fid+"_i"+str(k))}"><span style="display: inline-block; width: 18px;">{HL(fid+"_c"+str(k))}</span>{esc(v)}<span style="color: {MUTED}; font-size: 12px; float: right;">{cells.count(v)}</span></button>' for k,v in enumerate(vals))
        vlists+=f'<sc-if value="{HL(tbl+"_mv"+str(i))}" hint-placeholder-val="{HL("false")}"><div style="max-height: 260px; overflow: auto;"><div style="padding: 2px 12px 4px; font-size: 11px; color: {MUTED};">valores desta coluna · {HL(fid+"_n")}</div>{opts_html}</div></sc-if>'
    cmenu=(_CMENU_HEAD + vlists + f'<div style="height: 1px; background: {LINE}; margin: 4px 0;"></div>'
           + item('Agrupar por esta coluna',tbl+'_grp') + item('Limpar filtro desta coluna',tbl+'_mclear') + item('Fechar','closeAll') + '</div>')
    reg(type='sort',id=tbl,tbl=tbl,n=n,cols=headers,dflt=sort,desc=desc,hon=hon,hoff=hoff,mst=CMENU_ST(),rows=rowtexts,group=gp)
    return f'<div style="position: relative; background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; min-width: 0;">{tb}<table style="width: 100%; border-collapse: collapse; table-layout: auto;"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>{cmenu}</div>'
G=lambda label,agg: ('__group__',label,agg)
def colmenu(hd,fil):
    item=lambda t,acc=False: f'<a href="#" style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; text-decoration: none; font-size: 13px; color: {ACC if acc else INK}; font-weight: {700 if acc else 500}; text-transform: none; letter-spacing: 0;">{t}</a>'
    vals=[('22/09',6,True),('23/09',4,True),('24/09',3,False),('20/09',5,False)]
    checks=''.join(f'<label style="display: flex; align-items: center; gap: 10px; padding: 6px 12px; font-size: 13px; text-transform: none; letter-spacing: 0; color: {INK}; font-weight: 500;"><input type="checkbox" {"checked" if c else ""} style="width: 16px; height: 16px; accent-color: {ACC};"><span style="flex-grow: 1;">{v}</span><span style="color: {MUTED}; font-size: 12px;">{n}</span></label>' for v,n,c in vals)
    return (f'<div role="menu" style="position: absolute; top: 44px; left: 0; z-index: 5; width: 260px; background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; box-shadow: 0 12px 32px -8px rgba(21,32,26,.28); padding: 8px; display: flex; flex-direction: column; gap: 2px; white-space: normal;">'
            + item('▲ Ordenar crescente',True) + item('▼ Ordenar decrescente')
            + f'<div style="padding: 6px 12px 2px; font-size: 11px; color: {MUTED}; font-weight: 700; letter-spacing: .08em;">FILTRAR {hd}</div>'
            + f'<div style="padding: 0 12px 6px;"><input type="text" aria-label="Filtrar {hd}" value="{esc(fil) if fil else ""}" placeholder="contém · =exato · >10 · 10..50 · a|b" style="width: 100%; box-sizing: border-box; font-family: inherit; font-size: 13px; padding: 8px 10px; border: 1px solid {ACC if fil else LINE}; border-radius: 8px; background: {BG}; letter-spacing: 0; text-transform: none;"></div>'
            + f'<div style="padding: 0 12px 6px;"><input type="search" aria-label="Buscar valor" placeholder="Buscar valor…" style="width: 100%; box-sizing: border-box; font-family: inherit; font-size: 12.5px; padding: 6px 10px; border: 1px solid {LINE}; border-radius: 8px; letter-spacing: 0; text-transform: none;"></div>'
            + checks
            + f'<div style="height: 1px; background: {LINE}; margin: 4px 0;"></div>'
            + item('Agrupar por esta coluna') + item('Limpar filtro desta coluna')
            + '</div>')
def section(title,summary,action,body,state='green'):
    dot={'green':ACC,'yellow':YEL,'red':RED,'gray':GRAY}[state]
    return (f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; display: flex; flex-direction: column; flex: 1 1 0; min-width: 0;">'
            f'<div style="display: flex; flex-direction: column; gap: 4px; padding: 14px 18px; border-bottom: 1px solid {LINE};"><div style="display: flex; align-items: center; gap: 10px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {dot}; flex-shrink: 0; box-shadow: 0 0 0 3px {dot}22;"></span><div style="font-size: 15px; font-weight: 700; letter-spacing: -.01em; flex-grow: 1;">{esc(title)}</div>{"".join((a if a.startswith("<") else btn(a,small=True)) for a in ([action] if isinstance(action,str) else action) if a)}</div>' + (f'<div style="font-size: 13px; color: {MUTED}; padding-left: 20px; line-height: 1.35;">{esc(summary)}</div>' if summary else '') + '</div>'
            f'<div style="padding: 14px 18px;">{body}</div></div>')
SELECT_KEYS=['se recusar','divisão','cobertura por','risco de roubo','ação do ajuste','atividade','decisão','análise de crédito','indexador','frete','cobrança','garantia','liberação','cultura','variedade','plano','máquina','implemento','operação','talhão','fazenda','insumo','produto','fornecedor','cliente','laborat','depósito','lote','grupo','categoria','marca','modelo','polític','fase','praça','condição','unidade','gatilho','método','tabela','extrator','profundidade','item','peça','operador','mecânico','pessoa','sensor','motivo','avisar por','canal','prioridade','pagamento','retirada','base','tipo','estado','origem','pivô','armazém','cultivar','múltiplo','responsável','alvo','estádio']
TEXT_HINTS=['(ler qr','r$','kg','(ha','dias','(h)','data','quantidade','preço','valor','litros','umidade','%','horas','km','(m)','l/ha','sc)','rendimento','custo','frete','área','velocidade','largura','eficiência','ciclo','consumo','potência','vida','câmbio','leitura','turno','antecipar','validade','entrega','arquivo','nome','observação','lâmina','horímetro','intervalo','itens','peso','contado','complemento']
OPTIONS={
 'ação do ajuste':['Aumentar dose','Reduzir dose','Incluir produto','Excluir produto','Adicionar atividade','Mudar época (gatilho)'],'atividade':['Plantio','Fungicida 1ª aplicação','Fungicida 2ª aplicação','Inseticida 3ª aplicação','Dessecação pós-colheita','Adubação de cobertura'],
 'decisão':['Aprovar com estas condições','Aprovar com ajustes (contraproposta)','Recusar (motivo obrigatório)','Pedir mais informações'],'análise de crédito':['Aprovada · limite R$ 2M','Aguarda análise (2 dias)','Só à vista'],
 'indexador':['Pré-fixado','CDI +','IPCA +','Dólar + juros'],'frete':['CIF fazenda','FOB origem','Comprador retira'],'cobrança':['Mensal automática (cartão)','Anual com desconto'],'garantia':['CPR + penhor de safra','CPR financeira','Aval','Hipoteca'],'liberação':['3 parcelas com NF vinculada','Parcela única','Conforme liberações do PCE'],
 'se recusar':['— (só ao recusar ou contrapropor)','Capacidade de pagamento insuficiente','Garantia insuficiente','Documentação pendente','Fora da política de crédito','Prazo ou taxa fora do apetite'],
 'cobertura por':['1 semana','2 semanas','3 semanas','1 mês','2 meses','Antes do 1º uso (dias)','Ondas do escalonamento','100 % antes da janela','Safra inteira','Por carga'],
 'risco de roubo':['Classe A (≤ 3 semanas, CFTV)','Classe B','Classe C'],
 'divisão':['Por área (%)','Por linhas de plantio','No mapa (linha de corte)'],
 'cultura':['Soja','Milho','Feijão','Café','Mamão Formosa','Cana-de-açúcar','Tomate','Alface americana','Maracujá'],
 'variedade':['58 W','M 5947','BRS 7380','Tainung 01','Aliança'],'cultivar':['58 W','M 5947','BRS 7380','Tainung 01'],
 'plano':['Soja alta tecnologia','Soja padrão','Milho safrinha','Feijão pivô','Mamão Formosa'],
 'máquina':['Trator 01 · JD 6M 155','Trator 02 · MF 7719','Pulverizador 01 · 24 m','Pulverizador 02 · 30 m','Distribuidor 01','Colhedora 01 · Axial-Flow 7250','Plantadeira 24 linhas'],
 'implemento':['Barra 24 m','Plantadeira 24 linhas','Distribuidor 3 t','Grade niveladora','Carreta 12 t'],
 'operação':['Calagem','Gessagem','Dessecação','Plantio','Cobertura','Pulverização','Colheita','Irrigação'],
 'talhão':['T1 · 312 ha','T2 · 298 ha','T3 · 96 ha','T4 · 204 ha','T5 · 180 ha','T7 · 42 ha (mamão)'],'fazenda':['Santa Rita','Boa Vista'],
 'insumo':['MAP 11-52','KCl 60 %','Calcário PRNT 80','Gesso agrícola','Semente 58 W','Glifosato 480','Fungicida A','Diesel S10'],
 'produto':['Soja em grão','Milho em grão','Mamão Formosa · cx 10 kg','Café beneficiado'],'item':['MAP 11-52','KCl 60 %','Glifosato 480','Diesel S10','Bico leque 110-02','Óleo hidráulico 68','Soja · CEPEA'],
 'fornecedor':['Fertisul','Santa Rita Insumos','Agro Norte','Coop. Vale','Casa do Adubo'],'cliente':['Armazém Geral','Coop. Vale','Trading Sul','Frutas Real','Ceasa Vitória'],
 'laborat':['Lab Solo Vale','Agrolab','Embrapa Solos (convênio)'],'depósito':['Galpão 1','Galpão 2','Armazém Sede','Tanque diesel'],'armazém':['Armazém Sede','Armazém 2','Galpão 1'],
 'lote':['F26-02','D26-11','L27-012 · 3.400 sc','L27-013 · 3.690 sc'],'grupo':['Fertilizantes','Sementes','Defensivos','Combustível','Peças','Lubrificantes','EPI','Grãos','Frutas','Café','Cana','HF'],
 'categoria':['Trator','Pulverizador','Colhedora','Plantadeira','Caminhão','Pivô','Fornecedor de insumos','Comprador de commodities','Crédito (banco, fintech, fundo)'],'marca':['John Deere','Case IH','Massey Ferguson','New Holland','Valtra','Jacto','Stara'],
 'modelo':['6M 155','Axial-Flow 7250','MF 7719','Uniport 3030','Hércules 6.0'],'polític':['Lote a lote pela necessidade datada','Ponto de pedido','Mínimo de peça crítica','Mínimo do tanque'],
 'fase':['1 · Preparo','2 · Plantio','3 · Cobertura','4 · Tratos culturais','5 · Colheita'],'praça':['Rondonópolis','Sorriso','Paranaguá','Rio Verde','CEPEA'],
 'condição':['acima de','abaixo de','FOB · à vista','CIF · 30 dias','FOB · 30 dias','Prazo safra','À vista com desconto','Barter (sacas)'],'unidade':['kg/ha','L/ha','t/ha','sc/ha','un','mm'],
 'método':['pano-de-batida','contagem direta','armadilha','saturação por bases','SMP','Al trocável'],'tabela':['IAC Boletim 100','Embrapa Cerrados','CQFS-RS/SC','CFSEMG 5ª aproximação'],
 'extrator':['Mehlich-1','Resina','DTPA','Água quente'],'profundidade':['0–20 cm','20–40 cm','0–10 cm','40–60 cm'],
 'peça':['Filtro de óleo JD','Bico leque 110-02','Selo mecânico bomba','Correia A-52'],'operador':['Marcos','Carlos','João','Paula'],'mecânico':['Rui','Sérgio'],'pessoa':['Ana','Rui','Carlos','Marcos','João','Paula'],'responsável':['Ana','Marcos','Rui','Paula'],
 'sensor':['Umidade P1 · 30 cm','Umidade P1 · 60 cm','Estação Sede','Pivô 2 · pressão'],'motivo':['Máquina diferente do padrão','Ajuste da fazenda','Sonda deslocada','Chuva','Quebra','Falta de insumo','Praga acima do NC'],
 'avisar por':['WhatsApp','E-mail','WhatsApp e e-mail','Push no app'],'canal':['WhatsApp','E-mail','Push no app'],'prioridade':['Alta','Normal','Baixa'],
 'pagamento':['À vista','30 dias','Crédito (Banco Terra)','Barter (sacas)'],'retirada':['Almoxarifado Sede','Galpão 2','Entrega no talhão'],
 'base':['Plano nativo · colhedora axial','Plano nativo · trator','Plano nativo · pulverizador'],'tipo':['Preventiva','Preditiva','Corretiva','Melhoria'],'estado':['Rascunho','Ativo','Em manutenção','Baixado'],
 'origem':['Almoxarifado · lote F26-02','Compra direta','Estoque de peças da oficina'],'pivô':['Pivô 1 · 95 ha','Pivô 2 · 80 ha'],'múltiplo':['carga 36 t','big bag 1 t','sc 40 kg','bombona 20 L','un'],
 'alvo':['Percevejo-marrom','Lagarta-da-soja','Ferrugem asiática','Mosca-branca','Ácaro','Mancha-de-phoma'],'estádio':['V4','V6','R1','R3','R5','0 · verde inchado','1 · pintado','2 · ¼ maduro','3 · ½ maduro'],
 'De':['Armazém 1','Armazém 2','Galpão 1','Galpão 2'],'Para':['Armazém 2','Armazém 1','Galpão 2','Galpão 1'],
}
def _opts_for(label,value):
    l=label.lower(); base=[]
    if label in ('De','Para'): base=OPTIONS[label]
    else:
        for k in SELECT_KEYS:
            if k in l and k in OPTIONS: base=OPTIONS[k]; break
    out=[value] if value else []
    for o in base:
        if o not in out: out.append(o)
    return out
def is_select(label):
    """campo que aponta para cadastro ou enumeração é lista suspensa; texto livre só para nome novo, número, data, observação."""
    l=label.lower()
    if label in ('De','Para'): return True
    return any(k in l for k in SELECT_KEYS) and not any(t in l for t in TEXT_HINTS)
def _iso(d):
    m=re.fullmatch(r'\s*(\d{2})/(\d{2})/(\d{4})\s*',d or '')
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
def is_date(label,value):
    l=label.lower()
    if re.fullmatch(r'\s*\d{2}/\d{2}/\d{4}\s*',value or ''): return True
    return (l.startswith('data') and 'datada' not in l) or 'plantio previsto' in l or 'vencimento' in l
_INP=lambda extra='': f'font-family: inherit; font-size: 14px; font-weight: 500; color: {INK}; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 10px; background: {SURF}; box-sizing: border-box; {extra}'
def date_field(label,value,w='1 1 0',idn=None):
    """data sempre com calendário nativo; o valor mostrado é dd/mm/aaaa."""
    idn=idn or ''.join(ch for ch in label.lower() if ch.isalnum())
    return (f'<div style="flex: {w}; display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{idn}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>'
            f'<input id="{idn}" type="date" value="{_iso(value)}" aria-label="{esc(label)} · calendário" style="{_INP("width: 100%;")}"></div>')
def trigger_field(label,value,w='1 1 0'):
    """gatilho = tipo (DAP · DAC · Data) + dias após o plantio/colheita ou data fixa com calendário; muda ao tocar."""
    m=re.match(r'\s*(DAP|Idade|DAF|DAC|Data)\D*(\d+)?\s*(\d{2}/\d{2}/\d{4})?',value or '',re.I)
    kind=(m.group(1).upper() if m else 'DAP'); days=(m.group(2) if m and m.group(2) else ''); date=(m.group(3) if m and m.group(3) else '')
    active={'DAP':0,'IDADE':1,'DAF':2,'DAC':3,'DATA':4}[kind]
    s,bs=seg_buttons(['DAP','Idade','DAF','DAC','Data'],active)
    segs='<div role="group" aria-label="Tipo de gatilho" style="display: inline-flex; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px;">'+''.join(bs)+'</div>'
    def scif(i,inner): return f'<sc-if value="{HL(s+"_v"+str(i))}" hint-placeholder-val="{HL("true") if i==active else HL("false")}">{inner}</sc-if>'
    def days_in(hint): return (f'<span style="display: inline-flex; align-items: center; gap: 8px;"><input type="number" min="0" max="400" value="{days}" placeholder="dias" aria-label="{hint}" style="{_INP("width: 84px;")}">'
                               f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap;">{hint}</span></span>')
    date_in=f'<input type="date" value="{_iso(date)}" aria-label="Data fixa · calendário" style="{_INP("width: 168px;")}">'
    return (f'<div style="flex: {w}; display: flex; flex-direction: column; gap: 4px; min-width: 0;"><span style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</span>'
            f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{segs}{scif(0,days_in("dias após o plantio da parcela"))}{scif(1,days_in("meses de idade da parcela"))}{scif(2,days_in("dias após a floração apontada"))}{scif(3,days_in("dias após a colheita"))}{scif(4,date_in)}</div></div>')
def field(label,value,w='1 1 0',ph=False,idn=None):
    if 'gatilho' in label.lower() and 'toler' not in label.lower(): return trigger_field(label,value,w)
    if is_date(label,value): return date_field(label,value,w,idn)
    if is_select(label): return select(label,value,w,idn)
    idn=idn or ''.join(ch for ch in label.lower() if ch.isalnum())
    col=MUTED if ph else INK
    return (f'<div style="flex: {w}; display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{idn}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>'
            f'<input id="{idn}" type="text" value="{esc(value)}" style="font-family: inherit; font-size: 14px; font-weight: 500; color: {col}; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 10px; background: {SURF}; width: 100%; box-sizing: border-box;"></div>')
def select(label,value,w='1 1 0',idn=None):
    if 'gatilho' in label.lower() and 'toler' not in label.lower(): return trigger_field(label,value,w)
    idn=idn or ''.join(ch for ch in label.lower() if ch.isalnum())
    opts=''.join(f'<option{" selected" if i==0 else ""}>{esc(o)}</option>' for i,o in enumerate(_opts_for(label,value)))
    return (f'<div style="flex: {w}; display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{idn}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>'
            f'<select id="{idn}" aria-label="{esc(label)} · lista do cadastro" style="font-family: inherit; font-size: 14px; font-weight: 500; color: {INK}; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 10px; background: {SURF}; width: 100%; appearance: auto;">{opts}<option disabled>──────────</option><option>Buscar no cadastro…</option><option>+ Novo (abre o cadastro)</option></select></div>')
def row(*cells,gap=12): return f'<div style="display: flex; gap: {gap}px; align-items: flex-end;">{"".join(cells)}</div>'
def col(*cells,gap=12): return f'<div style="display: flex; flex-direction: column; gap: {gap}px;">{"".join(cells)}</div>'
def srow(*cells,gap=12): return f'<div style="display: flex; gap: {gap}px; align-items: stretch;">{"".join(cells)}</div>'
def stepper(steps,hint):
    parts=''
    n=len(steps)
    for i,(name,st) in enumerate(steps):
        if st=='done':
            dot=f'<span style="width: 22px; height: 22px; border-radius: 999px; background: {ACC}; color: #fff; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg></span>'
        elif st=='now':
            dot=f'<span style="width: 22px; height: 22px; border-radius: 999px; border: 2px solid {ACC}; background: {SURF}; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; box-sizing: border-box;"><span style="width: 8px; height: 8px; border-radius: 999px; background: {ACC};"></span></span>'
        else:
            dot=f'<span style="width: 22px; height: 22px; border-radius: 999px; border: 2px solid {LINE}; background: {SURF}; display: inline-block; flex-shrink: 0; box-sizing: border-box;"></span>'
        color=INK if st!='todo' else MUTED
        line=f'<span style="flex-grow: 1; height: 2px; background: {ACC if st=="done" else LINE}; margin: 0 10px; min-width: 24px;"></span>' if i<n-1 else ''
        parts+=f'<div style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: {color}; font-weight: {700 if st=="now" else 600}; white-space: nowrap;">{dot}{esc(name)}</div>{line}'
    return f'<div style="display: flex; flex-direction: column; gap: 8px;"><div style="display: flex; align-items: center;">{parts}</div><div style="font-size: 13.5px; color: {MUTED};">{esc(hint)}</div></div>'
def linechart(vals,w=760,h=240,fut=None,ymin=None,ymax=None,labels=None,color=ACC,unit=''):
    n=len(vals); lo=ymin if ymin is not None else min(vals+(fut or []))*0.96; hi=ymax if ymax is not None else max(vals+(fut or []))*1.04
    L,R,T,B=44,16,14,30; iw=w-L-R; ih=h-T-B
    X=lambda i:L+iw*i/(n-1+(len(fut) if fut else 0)); Y=lambda v:T+ih*(1-(v-lo)/(hi-lo))
    pts=' '.join(f'{X(i):.1f},{Y(v):.1f}' for i,v in enumerate(vals))
    s=f'<svg viewBox="0 0 {w} {h}" style="width: 100%; height: auto; display: block;" role="img" aria-label="Série de preços">'
    for k in range(5):
        v=lo+(hi-lo)*k/4; y=Y(v)
        s+=f'<line x1="{L}" y1="{y:.1f}" x2="{w-R}" y2="{y:.1f}" stroke="{LINE}" stroke-width="1"/><text x="{L-6}" y="{y+4:.1f}" text-anchor="end" font-size="10.5" fill="{MUTED}">{v:.0f}</text>'
    s+=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round"/>'
    s+=f'<circle cx="{X(n-1):.1f}" cy="{Y(vals[-1]):.1f}" r="4" fill="{color}"/>'
    if fut:
        fp=' '.join(f'{X(n-1+i):.1f},{Y(v):.1f}' for i,v in enumerate([vals[-1]]+fut))
        s+=f'<polyline points="{fp}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="5 4"/>'
        for i,v in enumerate(fut): s+=f'<circle cx="{X(n+i):.1f}" cy="{Y(v):.1f}" r="3" fill="{SURF}" stroke="{color}" stroke-width="2"/>'
    if labels:
        for i,t in labels: s+=f'<text x="{X(i):.1f}" y="{h-10}" text-anchor="middle" font-size="10.5" fill="{MUTED}">{t}</text>'
    return s+'</svg>'
def barchart(vals,best,worst,w=1160,h=200,months=('jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'),ref=None):
    lo=min(vals)*0.92; hi=max(vals)*1.04; L,R,T,B=44,16,18,28; iw=w-L-R; ih=h-T-B; bw=iw/12*0.6
    s=f'<svg viewBox="0 0 {w} {h}" style="width: 100%; height: auto; display: block;" role="img" aria-label="Média por mês">'
    for k in range(4):
        v=lo+(hi-lo)*k/3; y=T+ih*(1-(v-lo)/(hi-lo))
        s+=f'<line x1="{L}" y1="{y:.1f}" x2="{w-R}" y2="{y:.1f}" stroke="{LINE}"/><text x="{L-6}" y="{y+4:.1f}" text-anchor="end" font-size="10.5" fill="{MUTED}">{v:.0f}</text>'
    if ref:
        y=T+ih*(1-(ref-lo)/(hi-lo)); s+=f'<line x1="{L}" y1="{y:.1f}" x2="{w-R}" y2="{y:.1f}" stroke="{INK}" stroke-dasharray="4 4" opacity=".5"/><text x="{w-R}" y="{y-4:.1f}" text-anchor="end" font-size="10.5" fill="{MUTED}">média do período</text>'
    for i,v in enumerate(vals):
        x=L+iw*i/12+(iw/12-bw)/2; y=T+ih*(1-(v-lo)/(hi-lo)); c=ACC if i==best else (RED if i==worst else '#B7C9BE')
        s+=f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{T+ih-y:.1f}" rx="5" fill="{c}"/><text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="11" font-weight="{700 if i in (best,worst) else 500}" fill="{INK if i in (best,worst) else MUTED}">{v:.0f}</text><text x="{x+bw/2:.1f}" y="{h-8}" text-anchor="middle" font-size="11" font-weight="{700 if i==best else 500}" fill="{ACC if i==best else (RED if i==worst else MUTED)}">{months[i]}</text>'
    return s+'</svg>'
def util(pct):
    c=ACC if pct<=90 else (YEL if pct<=100 else RED)
    return f'<div style="display: flex; align-items: center; gap: 8px; min-width: 96px;"><div style="flex-grow: 1; height: 8px; background: {GRAYS}; border-radius: 999px; overflow: hidden;"><div style="width: {min(pct,100)}%; height: 100%; background: {c};"></div></div><b style="color: {c}; font-size: 12.5px; width: 40px; text-align: right;">{pct} %</b></div>'
def bar(pct,color=ACC):
    return f'<div style="height: 6px; background: {GRAYS}; border-radius: 999px; overflow: hidden;"><div style="width: {pct}%; height: 100%; background: {color};"></div></div>'
def farm_map(h=300,labels=None,colors=None,draft=False):
    labels=labels or ['T1','T2','T3','T4','P1','P2']
    colors=colors or [ACC,ACC,YEL,ACC,RED,ACC]
    fills={ACC:'#3FBF2A',YEL:'#FFD500',RED:'#FF6A00'}
    polys=[('40,40 220,30 240,150 60,160',),('250,30 430,40 420,160 260,150',),('40,180 230,170 220,290 50,300',),('250,175 430,170 440,300 260,290',)]
    svg=f'<svg viewBox="0 0 700 {h+20}" style="width: 100%; height: {h}px; display: block;" role="img" aria-label="Mapa da fazenda com talhões e pivôs">'
    svg+=f'<rect x="0" y="0" width="700" height="{h+20}" fill="#E3EBDD"/>'
    for i,(pts,) in enumerate(polys):
        svg+=f'<polygon points="{pts}" fill="{fills[colors[i]]}" fill-opacity=".85" stroke="#fff" stroke-width="2"/>'
        xs=[int(p.split(",")[0]) for p in pts.split()]; ys=[int(p.split(",")[1]) for p in pts.split()]
        svg+=f'<text x="{sum(xs)//4}" y="{sum(ys)//4+8}" text-anchor="middle" font-size="26" font-weight="700" fill="#fff" stroke="#1B241F" stroke-width="4" paint-order="stroke">{labels[i]}</text>'
    for j,(cx,cy) in enumerate([(540,110),(540,240)]):
        svg+=f'<circle cx="{cx}" cy="{cy}" r="62" fill="{fills[colors[4+j]]}" fill-opacity=".85" stroke="#fff" stroke-width="2"/><text x="{cx}" y="{cy+9}" text-anchor="middle" font-size="26" font-weight="700" fill="#fff" stroke="#1B241F" stroke-width="4" paint-order="stroke">{labels[4+j]}</text>'
    if draft:
        svg+=f'<polygon points="470,330 640,320 660,420 500,440" fill="{ACC}" fill-opacity=".25" stroke="{ACC}" stroke-width="2.5" stroke-dasharray="7 5"/>'
        for x,y in [(470,330),(640,320),(660,420),(500,440)]:
            svg+=f'<circle cx="{x}" cy="{y}" r="6" fill="#fff" stroke="{ACC}" stroke-width="2.5"/>'
        svg+=f'<rect x="505" y="365" width="120" height="34" rx="8" fill="#fff" fill-opacity=".95"/><text x="565" y="379" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">T7 · rascunho</text><text x="565" y="393" text-anchor="middle" font-size="11" fill="{MUTED}">48,2 ha · 4 vértices</text>'
    return svg+'</svg>'

LAYER_NAMES=['Integrado','Vigor','Solo','Pragas e doenças','O.S. · prazo','Irrigação','Estádio e plano','Colheita sc/ha','Custo/ha']
LAYERS={
 'Integrado':({'T1':'#3FBF2A','T2':'#FFD500','T3':'#0B7A1E','T4':'#3FBF2A','P1':'#FF6A00','P2':'#3FBF2A'},{'T1':'DAP 0 · plantio 12/10','T2':'V8 · NDVI 0,62','T3':'milho · NDVI 0,81','T4':'DAP 0 · plantio 18/10','P1':'R5 · NDVI 0,41 · mancha 4,2 ha','P2':'V10 · NDVI 0,74'}),
 'Vigor':({'T1':'#3FBF2A','T2':'#FFD500','T3':'#0B7A1E','T4':'#3FBF2A','P1':'#FF6A00','P2':'#3FBF2A'},{'T1':'NDVI 0,70 · bom','T2':'NDVI 0,62 · atenção','T3':'NDVI 0,81 · alto','T4':'NDVI 0,68 · bom','P1':'NDVI 0,41 · crítico','P2':'NDVI 0,74 · bom'}),
 'Solo':({'T1':'#E4002B','T2':'#FF6A00','T3':'#3FBF2A','T4':'#FF6A00','P1':'#FFD500','P2':'#FFD500'},{'T1':'V 40 % · alvo 50 · calagem 1,2','T2':'V 46 % · alvo 50 · 0,54 t/ha','T3':'V 61 % · adequado','T4':'V 49 % · alvo 50 · 0,1','P1':'V 52 % · alvo 60 · 0,75','P2':'V 55 % · alvo 60 · 0,5'}),
 'Pragas e doenças':({'T1':'#3FBF2A','T2':'#E4002B','T3':'#9E9E9E','T4':'#FFD500','P1':'#FF6A00','P2':'#3FBF2A'},{'T1':'lagarta 6/20 · adiar','T2':'percevejo 3,2/2 · O.S. corretiva','T3':'sem lavoura','T4':'vistoria vence hoje','P1':'ferrugem 1ª pústula · antecipar','P2':'cigarrinha 0,3/1 · ok'}),
 'O.S. · prazo':({'T1':'#C62828','T2':'#F9A825','T3':'#9E9E9E','T4':'#F9A825','P1':'#EF6C00','P2':'#C62828'},{'T1':'▲ 0420 calagem · 71 d','T2':'◆ 0413 dessecação · 1 d','T3':'sem O.S. aberta','T4':'◆ 0421 dessecação · 1 d','P1':'● 0418 irrigação · hoje','P2':'▲ irrigação · bomba 0233'}),
 'Estádio e plano':({'T1':'#B5E61D','T2':'#B5E61D','T3':'#9E9E9E','T4':'#B5E61D','P1':'#0B7A1E','P2':'#3FBF2A'},{'T1':'pré-plantio · 3 de 14','T2':'pré-plantio · 2 de 14','T3':'colhido · 11 de 11','T4':'pré-plantio · 2 de 14','P1':'R5 · 9 de 12','P2':'V10 · 7 de 11'}),
 'Irrigação':({'T1':'#D9D9D9','T2':'#D9D9D9','T3':'#D9D9D9','T4':'#D9D9D9','P1':'#1D4ED8','P2':'#60A5FA'},{'T1':'sequeiro','T2':'sequeiro','T3':'sequeiro','T4':'sequeiro','P1':'336 de 320 mm · 8 mm hoje','P2':'14 mm em curso · 62 % CAD'}),
 'Colheita sc/ha':({'T1':'#3FBF2A','T2':'#FFD500','T3':'#0B7A1E','T4':'#B5E61D','P1':'#B5E61D','P2':'#D9D9D9'},{'T1':'71 sc/ha (25/26)','T2':'58 sc/ha (25/26)','T3':'126 sc/ha (25/26)','T4':'66 sc/ha (25/26)','P1':'38 sc/ha (inverno)','P2':'—'}),
 'Custo/ha':({'T1':'#3FBF2A','T2':'#FF6A00','T3':'#0B7A1E','T4':'#B5E61D','P1':'#FFD500','P2':'#FFD500'},{'T1':'R$ 2.740/ha','T2':'R$ 3.120/ha · +11 %','T3':'R$ 2.190/ha','T4':'R$ 2.310/ha','P1':'R$ 3.690/ha','P2':'R$ 3.585/ha'}),
}
LEGENDS={
 'Integrado':[('#E4002B','falha'),('#FF6A00','fraco'),('#FFD500','atenção'),('#B5E61D','médio'),('#3FBF2A','bom'),('#0B7A1E','vigor alto'),('#9E9E9E','nuvem')],
 'Vigor':[('#E4002B','< 0,30 falha'),('#FF6A00','0,30–0,45 fraco'),('#FFD500','0,45–0,60 atenção'),('#B5E61D','0,60–0,72 médio'),('#3FBF2A','0,72–0,82 bom'),('#0B7A1E','> 0,82 vigor alto'),('#9E9E9E','nuvem')],
 'Solo':[('#E4002B','V < 40 % muito baixo'),('#FF6A00','40–50 baixo'),('#FFD500','50–60 médio'),('#3FBF2A','60–70 adequado'),('#0B7A1E','> 70 alto'),('#9E9E9E','sem laudo')],
 'Pragas e doenças':[('#E4002B','≥ NC · O.S. corretiva'),('#FF6A00','antecipar aplicação'),('#FFD500','vistoria vencendo'),('#3FBF2A','abaixo do NC'),('#9E9E9E','sem lavoura')],
 'O.S. · prazo':[('#C62828','▲ atrasada'),('#EF6C00','● vence hoje'),('#F9A825','◆ até 3 dias'),('#2E7D32','○ no prazo'),('#9E9E9E','sem O.S.')],
 'Irrigação':[('#D9D9D9','sequeiro'),('#60A5FA','confortável'),('#1D4ED8','déficit na reserva')],
 'Estádio e plano':[('#B5E61D','pré-plantio'),('#3FBF2A','vegetativo'),('#0B7A1E','reprodutivo'),('#9E9E9E','colhido')],
 'Colheita sc/ha':[('#FFD500','< 60'),('#B5E61D','60–70'),('#3FBF2A','70–80'),('#0B7A1E','> 120 milho')],
 'Custo/ha':[('#0B7A1E','< R$ 2.300'),('#3FBF2A','2.300–2.800'),('#B5E61D','2.800–3.200'),('#FFD500','3.200–3.700'),('#FF6A00','> 3.700')],
}
def farm_layers(segid,h=470):
    out=''
    for i,name in enumerate(LAYER_NAMES):
        sel=''
        if name=='Vigor': sel=toolrow(seg(['NDVI','NDRE','EVI','SAVI','NDMI']),seg(['Talhão','Absoluto']))
        if name=='Solo': sel=toolrow(seg(['V %','P','K','Ca 20–40','m % 20–40','Argila','pH','CTC'])+seg(['0–20','20–40']),seg(['Atual','Aplicado × prescrito']))
        if name=='Irrigação': sel=toolrow(seg(['Hoje','7 dias']))
        if name=='Pragas e doenças': sel=toolrow(seg(['Pior alvo','Percevejo','Lagartas','Doenças','Estande']),seg(['Última vistoria','Tendência']))
        out+=f'<sc-if value="{HL(segid+"_v"+str(i))}" hint-placeholder-val="{HL("true") if i==0 else HL("false")}">{sel}{farm_map2(h,name)}{legend(LEGENDS[name])}</sc-if>'
    return out
def farm_map2(h=470,layer='Integrado'):
    """mapa integrado: cor e rótulo por camada; O.S. de hoje em cada talhão"""
    col,lab=LAYERS[layer]
    fills={'bom':'#3FBF2A','atencao':'#FFD500','critico':'#FF6A00','alto':'#0B7A1E'}
    plots=[('T1','40,40 220,30 240,150 60,160','bom','DAP 0 · plantio 12/10','O.S. hoje: dessecação 60 %','ok'),
           ('T2','250,30 430,40 420,160 260,150','atencao','V8 · NDVI 0,62','O.S. hoje: sem máquina','late'),
           ('T3','40,180 230,170 220,290 50,300','alto','milho · NDVI 0,81','O.S. concluída 20/09','ok'),
           ('T4','250,175 430,170 440,300 260,290','bom','DAP 0 · plantio 18/10','O.S. amanhã: dessecação','ok')]
    pivs=[('P1',540,110,'critico','R5 · NDVI 0,41 · mancha 4,2 ha','8 mm hoje · 336/320 mm','late'),('P2',540,240,'bom','V10 · NDVI 0,74','14 mm em curso · O.S. 0419','ok')]
    plots=[(n,p,c,lab[n],l2,st) for n,p,c,_,l2,st in plots]; pivs=[(n,x,y,c,lab[n],l2,st) for n,x,y,c,_,l2,st in pivs]
    fills=None
    s=f'<svg viewBox="0 0 700 {h+20}" style="width: 100%; height: {h}px; display: block;" role="img" aria-label="Mapa integrado da fazenda">'
    s+=f'<rect x="0" y="0" width="700" height="{h+20}" fill="#E3EBDD"/>'
    def badge(x,y,text,state):
        c={'ok':ACC,'late':RED}[state]
        return (f'<rect x="{x-78}" y="{y}" width="156" height="18" rx="9" fill="#fff" fill-opacity=".92"/>'
                f'<circle cx="{x-66}" cy="{y+9}" r="4" fill="{c}"/><text x="{x-58}" y="{y+13}" font-size="10.5" font-weight="600" fill="{INK}">{esc(text)}</text>')
    for name,pts,cls,l1,l2,st in plots:
        xs=[int(p.split(',')[0]) for p in pts.split()]; ys=[int(p.split(',')[1]) for p in pts.split()]
        cx=sum(xs)//4; cy=sum(ys)//4
        s+=f'<polygon points="{pts}" fill="{col[name]}" fill-opacity=".85" stroke="#fff" stroke-width="2"/>'
        s+=f'<text x="{cx}" y="{cy-16}" text-anchor="middle" font-size="26" font-weight="700" fill="#fff" stroke="#1B241F" stroke-width="4" paint-order="stroke">{name}</text>'
        s+=f'<rect x="{cx-78}" y="{cy-6}" width="156" height="18" rx="9" fill="#fff" fill-opacity=".92"/><text x="{cx}" y="{cy+7}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">{esc(l1)}</text>'
        s+=badge(cx,cy+16,l2,st)
    for name,cx,cy,cls,l1,l2,st in pivs:
        s+=f'<circle cx="{cx}" cy="{cy}" r="62" fill="{col[name]}" fill-opacity=".85" stroke="#fff" stroke-width="2"/>'
        if cls=='critico' and layer in ('Integrado','Vigor (NDVI 20/09)'): s+=f'<path d="M{cx},{cy} L{cx+47},{cy-40} A62,62 0 0 1 {cx+62},{cy-2} z" fill="#E4002B" fill-opacity=".9"/>'
        s+=f'<text x="{cx}" y="{cy-16}" text-anchor="middle" font-size="24" font-weight="700" fill="#fff" stroke="#1B241F" stroke-width="4" paint-order="stroke">{name}</text>'
        s+=f'<rect x="{cx-78}" y="{cy-6}" width="156" height="18" rx="9" fill="#fff" fill-opacity=".92"/><text x="{cx}" y="{cy+7}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">{esc(l1)}</text>'
        s+=badge(cx,cy+16,l2,st)
    return s+'</svg>'
HDR_EXTRA=22
def shell(fname,title,module,crumbs,subtitle,status,primary,body,footer=None,W=1280,H=820,search=False,chips=None):
    H=HEIGHTS.get(fname,H)+HDR_EXTRA
    nav=navgroups(module)
    modhome=MODHOME.get(module,'Main.dc.html')
    back=PARENT.get(fname) or modhome
    def _cr(i,c):
        href=(modhome if modhome!=fname else None) if i==0 else (back if (i==len(crumbs)-2 and back!=modhome) else None)
        return (f'<a href="{href}" style="color: {MUTED}; text-decoration: none;">{esc(c)}</a>' if href else f'<span style="color: {MUTED};">{esc(c)}</span>')
    _sep=f' <span style="color: {MUTED};">›</span> '
    crumb=_sep.join(_cr(i,c) for i,c in enumerate(crumbs[:-1]))+(_sep if len(crumbs)>1 else '')+f'<span>{esc(crumbs[-1])}</span>'
    st=chip(status[0],status[1]) if status else ''
    chipbar=''
    sc=scopechips(fname)
    if chips or sc:
        ch=''
        if chips:
            c=wid('c'); rows=(wget(FIRST_TBL[0])['rows'] if FIRST_TBL[0] else [])
            labels=[t[0] for t in chips]; active=next((i for i,t in enumerate(chips) if t[1]),0)
            match=[]
            for t in chips:
                name=t[0].split(' · ')[0]
                if len(t)>2: match.append(t[2]); continue
                if name.lower().startswith(('tod','hoje')): match.append(None); continue
                cands=[name,name[:-1] if name.endswith('s') else name,name.lower(),name.lower()[:-1]]
                mm=next((x for x in cands if any(x in r for r in rows)),None)
                if mm is None and rows: print('  chip sem linha:',fname,t[0])
                match.append(mm)
            reg(type='chips',id=c,opts=labels,dflt=active,on=CHIP_ON(),off=CHIP_OFF(),tbl=FIRST_TBL[0],rows=rows,match=match)
            ch=''.join(f'<button type="button" onClick="{HL(c+"_p"+str(i))}" style="{HL(c+"_s"+str(i))}">{esc(t)}</button>' for i,t in enumerate(labels))
        chipbar='<div style="display: flex; gap: 8px; align-items: center;">'+ch+sc+'</div>'
    foot=f'<div style="display: flex; align-items: center; gap: 10px; padding: 12px 32px; border-top: 1px solid {LINE}; background: {SURF};"><span style="width: 8px; height: 8px; border-radius: 999px; background: {ACC};"></span><div style="font-size: 13px; color: {MUTED};">{esc(footer)}</div></div>' if footer else ''
    html=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Sora:wght@600;700&amp;display=swap">
<style>
body{{margin:0;font-family:{FONT};color:{INK};background:{BG}}}
a{{color:{ACC}}}a:hover{{color:#15603a}}
</style>
</helmet>
<div style="position: relative; width: {W}px; height: {H}px; box-sizing: border-box; display: flex; background: {BG}; font-family: {FONT}; color: {INK}; overflow: hidden;">
<nav aria-label="Módulos" style="width: 224px; flex-shrink: 0; background: {SIDE}; display: flex; flex-direction: column; padding: 16px 12px 12px; gap: 1px; box-sizing: border-box; overflow: hidden;">
<div style="display: flex; align-items: center; gap: 10px; padding: 2px 12px 8px; font-family: {DISP}; font-weight: 700; font-size: 15px; letter-spacing: -.01em; color: #fff;"><span style="width: 28px; height: 28px; border-radius: 9px; background: {ACC}; display: inline-flex; align-items: center; justify-content: center;">{icon("Agronomia",16,"#fff")}</span>Talhão à O.S.</div>
{nav}
<div style="flex-grow: 1;"></div>
<div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; font-size: 12.5px; color: {SIDE_TX}; border-top: 1px solid rgba(255,255,255,.08);"><span style="width: 26px; height: 26px; border-radius: 999px; background: {ACC}; color: #fff; font-weight: 700; font-size: 12px; display: inline-flex; align-items: center; justify-content: center;">A</span><span style="display: flex; flex-direction: column; line-height: 1.2;"><span style="font-weight: 700; color: #fff;">Ana</span><span style="color: {SIDE_MUTED}; font-size: 11.5px;">Fazenda Santa Rita</span></span></div>
</nav>
<div style="flex-grow: 1; display: flex; flex-direction: column; min-width: 0;">
<header style="padding: 18px 32px 16px; background: {SURF}; border-bottom: 1px solid {LINE}; display: flex; flex-direction: column; gap: 12px;">
<div style="display: flex; align-items: center; gap: 12px; font-size: 12.5px; font-weight: 500;">{ctxpills(fname)}<span style="width: 1px; height: 18px; background: {LINE};"></span>{roletag(module)}<span>{crumb}</span></div>
<div style="display: flex; align-items: center; gap: 12px;">
<a href="{back}" aria-label="Voltar" style="text-decoration: none; display: inline-flex; align-items: center;">{chev()}</a>
<h1 style="margin: 0; font-family: {DISP}; font-size: 24px; font-weight: 700; letter-spacing: -.02em; white-space: nowrap; flex-shrink: 0;">{esc(title)}</h1>
<span style="flex-shrink: 0; max-width: 260px;">{st.replace('white-space: nowrap;','white-space: normal; line-height: 1.2;')}</span>
<span style="flex-grow: 1;"></span>
{btn(primary,True,href=PHREF.get(fname))}
</div>
<div style="font-size: 13px; color: {MUTED}; line-height: 1.35; max-width: 820px; margin-top: -4px; padding-left: 30px;">{esc(subtitle)}</div>
{chipbar}
</header>
<main style="flex-grow: 1; overflow: hidden; padding: 24px 32px; display: grid; grid-template-columns: minmax(0, 1fr); grid-auto-rows: max-content; align-content: start; gap: 18px; box-sizing: border-box; min-width: 0;">
{body}
</main>
{foot}
</div>
{extra_html()}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
{engine()}
</script>
</body>
</html>
'''
    open(os.path.join(P,fname),'w').write(html)

def mobile(fname,title,sub,status,primary,body,W=390,H=844,module=None):
    _mn=re.search(r'<!--MNAV-->.*?<!--/MNAV-->',body,flags=re.S)
    _nav=_mn.group(0) if _mn else ''
    body=body.replace(_nav,'') if _nav else body
    H=HEIGHTS.get(fname,H)
    back=MPARENT.get(fname) or (MODHOME.get(module,'Main.dc.html') if module else 'Main.dc.html')
    html=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Sora:wght@600;700&amp;display=swap">
<style>
body{{margin:0;font-family:{FONT};color:{INK};background:{BG}}}
a{{color:{ACC}}}a:hover{{color:#15603a}}
</style>
</helmet>
<div style="position: relative; width: {W}px; height: {H}px; box-sizing: border-box; display: flex; flex-direction: column; background: {BG}; font-family: {FONT}; color: {INK}; overflow: hidden;">
<header style="padding: 54px 20px 14px; background: {SURF}; border-bottom: 1px solid {LINE}; display: flex; flex-direction: column; gap: 6px;">
<div style="display: flex; align-items: center; gap: 10px;"><a href="{back}" aria-label="Voltar" style="text-decoration: none; display: inline-flex; align-items: center;">{chev()}</a><h1 style="margin: 0; font-family: {DISP}; font-size: 20px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">{esc(title)}</h1>{chip(status[0],status[1]) if status else ''}</div>
<div style="font-size: 13px; color: {MUTED};">{esc(sub)}</div>
</header>
<main style="flex-grow: 1; overflow: hidden; padding: 16px 20px; display: flex; flex-direction: column; gap: 14px; box-sizing: border-box;">
{body}
</main>
<div style="padding: 12px 20px 28px; background: {SURF}; border-top: 1px solid {LINE};"><a href="{PHREF.get(fname,'#')}" style="display: block; text-align: center; text-decoration: none; box-sizing: border-box; width: 100%; padding: 18px; border-radius: 16px; box-shadow: 0 1px 2px rgba(30,122,76,.25); font-size: 17px; font-weight: 800; letter-spacing: -.01em; font-family: inherit; background: {ACC}; color: #fff; border: 1px solid {ACC};">{esc(primary)}</a></div>
{_nav}
{extra_html().replace('left: 248px;','left: 16px; right: 16px;')}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
{engine()}
</script>
</body>
</html>
'''
    open(os.path.join(P,fname),'w').write(html)

def mfield(label,value,ph=False,big=False):
    idn=''.join(ch for ch in label.lower() if ch.isalnum())
    return (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="{idn}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>'
            f'<input id="{idn}" type="text" value="{esc(value)}" style="font-family: {DISP if big else "inherit"}; font-size: {"24px" if big else "16px"}; font-weight: {700 if big else 500}; color: {MUTED if ph else INK}; padding: 14px 16px; border: 1px solid {LINE}; border-radius: 14px; background: {SURF}; width: 100%; box-sizing: border-box;"></div>')
def mcard(title,lines,state='gray',cta=None):
    dot={'green':ACC,'yellow':YEL,'red':RED,'gray':GRAY}[state]
    body=''.join(f'<div style="font-size: 13px; color: {MUTED};">{esc(l)}</div>' for l in lines)
    return f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; box-shadow: {SH}; padding: 14px 16px; display: flex; flex-direction: column; gap: 4px;"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; border-radius: 999px; background: {dot};"></span><div style="font-size: 15px; font-weight: 700; flex-grow: 1;">{esc(title)}</div>{btn(cta,small=True) if cta else ""}</div>{body}</div>'

BOARDS=[]  # (file, title, W, H, row)

# ---------- v3.7: fecho do módulo reutilizável ----------
BOARDS=[]  # (file, title, W, H, row)
def add(f,t,W,H,r):
    _reset_screen(f); BOARDS.append((f,t,W,H,r))
