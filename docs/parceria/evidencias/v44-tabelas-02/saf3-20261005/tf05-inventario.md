# TF05 · Inventário estrutural das grades (gerado por `tabelas_inventario.py`)

Páginas com grade G2: 123 · grades: 260 · colunas: 1550 · colunas com suspeita de variável composta: 296 em 150 grades · páginas com tabela manual fora do G2: 2 (6 tabelas).

Menu vigente (39 telas): 83 grades · 61 colunas com suspeita em 41 grades (vêm primeiro na lista).

Motivos: rótulo composto (o cabeçalho junta duas variáveis); duas medidas ("190 / 350 ha", "95 ha · 100 %"); início–fim (intervalo numa célula); número + texto; data + texto. Triagem heurística: a suspeita não prova defeito, e a ausência de suspeita não prova conformidade. Cada linha vira decisão no incremento da tela.

## Colunas com suspeita

| Menu | Página | Grade | Coluna | Motivo | Exemplo |
|---|---|---|---|---|---|
| sim | AG-01.dc.html | g_vis | Talhão · cultura | rótulo composto |  |
| sim | AG-07.dc.html | g_agf | Produto · registro | rótulo composto |  |
| sim | AG-07.dc.html | g_agf | Ingrediente ativo · grupo químico | rótulo composto |  |
| sim | AG-07.dc.html | g_agf | Classe · modo de ação | rótulo composto |  |
| sim | AG-07.dc.html | g_agf | Tox · amb | rótulo composto |  |
| sim | CA-01det.dc.html | g_ap | Acumulado | duas medidas (7) | 50 / 350 ha |
| sim | CA-01det.dc.html | g_ap | Origem · sincronização | rótulo composto |  |
| sim | CA-01det.dc.html | g_mat | Item · lote | rótulo composto |  |
| sim | CA-01x-os0420.dc.html | g_ins | Dose da v2 | duas medidas (1) | 120 kg/ha · zonas 140 / 120 / 95 |
| sim | CA-01x-os0420.dc.html | g_ap0420 | Acumulado | duas medidas (2) | 18 / 100 ha |
| sim | CA-01x-os0420.dc.html | g_ap0420 | Origem · sincronização | rótulo composto |  |
| sim | CD-01det.dc.html | g_parc | Safra · parcela | rótulo composto |  |
| sim | CD-01det.dc.html | g_parc | Cultura · variedade | rótulo composto |  |
| sim | CD-02.dc.html | g_cv | Cultura · cultivar | rótulo composto |  |
| sim | CD-02.dc.html | g_rend | Operação · conjunto | rótulo composto |  |
| sim | CD-04.dc.html | g_pes | Pessoa · equipe | rótulo composto |  |
| sim | CD-05.dc.html | g_forn | Parceiro · CPF/CNPJ | rótulo composto |  |
| sim | CD-06.dc.html | g_itm | Grupo · item | rótulo composto |  |
| sim | CD-06.dc.html | g_itm | Unidade · embalagem | rótulo composto |  |
| sim | CD-07.dc.html | g_dim | Dimensão · código | rótulo composto |  |
| sim | CMP.dc.html | g_dem | Grupo · insumo | rótulo composto |  |
| sim | CMP.dc.html | g_conv | Grupo · fornecedor | rótulo composto |  |
| sim | CMP.dc.html | g_conv | Canal e contato | rótulo composto |  |
| sim | CMP.dc.html | g_cmp | Grupo · insumo · proposta | rótulo composto |  |
| sim | CMP.dc.html | g_apr | Pedido · fornecedor · insumo | rótulo composto |  |
| sim | CMP.dc.html | g_ent | Pedido · fornecedor · insumo | rótulo composto |  |
| sim | EST.dc.html | g_rec | Item · lote | rótulo composto |  |
| sim | EST.dc.html | g_ent | Requisição · O.S. | rótulo composto |  |
| sim | EST.dc.html | g_ent | Item · lote · embalagem | rótulo composto |  |
| sim | EST.dc.html | g_dev | Requisição · O.S. | rótulo composto |  |
| sim | EST.dc.html | g_dev | Item · lote | rótulo composto |  |
| sim | EST.dc.html | g_lot | Item · lote | rótulo composto |  |
| sim | EST.dc.html | g_cnt | Item · lote | rótulo composto |  |
| sim | EST.dc.html | g_mov | Item · lote | rótulo composto |  |
| sim | IR-02.dc.html | g_ag | Captação · ordem | rótulo composto |  |
| sim | IR-02.dc.html | g_ag | Setor · bomba | rótulo composto |  |
| sim | IR-02.dc.html | g_ag | Etapa · pendência | rótulo composto |  |
| sim | MA-01.dc.html | g_at | Ativo · local · contador | rótulo composto |  |
| sim | MA-02.dc.html | g_cs | Sintoma · contador · evidência | rótulo composto |  |
| sim | MA-02.dc.html | g_cs | Condição recomendada · responsável | rótulo composto |  |
| sim | MA-02.dc.html | g_ct | Tratamento | duas medidas (1) | 30 ha feitos preservados · Trator 02 · MF 7719: Proposto · OS-0420 sal |
| sim | MA-03.dc.html | g_vc | Leitura · última | rótulo composto |  |
| sim | MA-04.dc.html | g_om | Ordem · ativo | rótulo composto |  |
| sim | MA-04.dc.html | g_om | Serviço · tipo | rótulo composto |  |
| sim | MA-04.dc.html | g_om | Fase · selos | rótulo composto |  |
| sim | MA-04.dc.html | g_om | Checklist · peças | rótulo composto |  |
| sim | MA-05.dc.html | g_ab | Lançamento · operador | rótulo composto |  |
| sim | MA-05.dc.html | g_ab | Tanque/lote · nível após | rótulo composto |  |
| sim | MA-05.dc.html | g_ab | Data · contador | rótulo composto |  |
| sim | MA-05.dc.html | g_ab | Método / taxa | rótulo composto |  |
| sim | PA.dc.html | g_cv | Cultura e variedade | rótulo composto |  |
| sim | PM.dc.html | g_pv | Leitura · última | rótulo composto |  |
| sim | SAF.dc.html | g_cult_S2627 | Plano e ajustes | rótulo composto |  |
| sim | SAF.dc.html | g_cult_S27SF | Plano e ajustes | rótulo composto |  |
| sim | SAF.dc.html | g_cult_S2526 | Plano e ajustes | rótulo composto |  |
| sim | SAF.dc.html | g_cult_LG2627 | Plano e ajustes | rótulo composto |  |
| sim | SAF.dc.html | g_cult_NOVA | Plano e ajustes | rótulo composto |  |
| sim | SAF.dc.html | g_op | Operação · atividade · cultivo · conjunto | rótulo composto |  |
| sim | SAF.dc.html | g_op | Gatilho · data | rótulo composto |  |
| sim | SAF.dc.html | g_res | Recurso · indicador | rótulo composto |  |
| sim | SAF.dc.html | g_dem | Grupo · insumo | rótulo composto |  |
| oculto | AG-02.dc.html | g_lau | Laudo · amostra | rótulo composto |  |
| oculto | AG-02.dc.html | g_lau | Local · área representada | rótulo composto |  |
| oculto | AG-02.dc.html | g_lau | Método · extrator | rótulo composto |  |
| oculto | AG-03.dc.html | g_dia | Talhão · cultura | rótulo composto |  |
| oculto | AG-03.dc.html | g_dia | Hipótese · causa | rótulo composto |  |
| oculto | AG-03.dc.html | g_dia | Situação · decisão | rótulo composto |  |
| oculto | AG-04.dc.html | g_rec | Operação · talhão | rótulo composto |  |
| oculto | AG-04.dc.html | g_rec | Produto · dose · janela | rótulo composto; início–fim (1) | KCl 60 % por zona + TS nematicida janela: 20/09–05/10 |
| oculto | AG-04.dc.html | g_rec | Situação | duas medidas (1) | Aprovada OS-0421 · 190/350 ha |
| oculto | AG-04det.dc.html | g_ver | O que muda | duas medidas (1) | Dose por zona (140/120/95 kg/ha) + TS nematicida |
| oculto | AG-04det.dc.html | g_exe | O que é | duas medidas (2) | Necessidade de plantio do T4 · 204 ha · 1ª onda de 100 ha |
| oculto | AG-05.dc.html | g_bib | Item · tipo | rótulo composto |  |
| oculto | AG-05.dc.html | g_bib | Unidade · gatilhos | rótulo composto |  |
| oculto | AG-05.dc.html | g_bib | Validade · revisão | rótulo composto; data + texto (2) | safra 26/27 · rev. 08/26 |
| oculto | AG-06.dc.html | g_ef | Datas | data + texto (5) | pré 19/09 · pós 27/09 (7 DAA) |
| oculto | BO-01.dc.html | g_pl | Plano e versão | rótulo composto |  |
| oculto | BO-01.dc.html | g_pl | Contratante / segmento | rótulo composto |  |
| oculto | BO-01.dc.html | g_pl | Vigência | início–fim (4) | 01/07/26 – 30/06/27 |
| oculto | BO-01.dc.html | g_pl | Tarifa, mínimo e excedentes | rótulo composto |  |
| oculto | BO-01.dc.html | g_tm | Versão e coorte | rótulo composto |  |
| oculto | BO-01.dc.html | g_tm | Franquias e esgotamento | rótulo composto |  |
| oculto | BO-01.dc.html | g_tm | Retenção e exportação | rótulo composto |  |
| oculto | BO-01det.dc.html | g_ct | Vigência | início–fim (4) | 01/07/2026 – 30/06/2027 |
| oculto | BO-02.dc.html | g_as | Próximo evento | data + texto (3) | renovação 01/07/2027 · exige aceite do preço |
| oculto | BO-02.dc.html | g_fat | Confirmação / origem | rótulo composto |  |
| oculto | BO-03.dc.html | g_med | Contratante e base | rótulo composto |  |
| oculto | BO-03det.dc.html | g_mem | Fonte e versão | rótulo composto |  |
| oculto | CA-01.dc.html | g_os | Atividade · local | rótulo composto; duas medidas (3) | Irrigação · água P2 · 80 ha · 13,5 mm em 2 passadas de 6,75 mm |
| oculto | CA-01.dc.html | g_os | Janela | início–fim (1) | 24/09 21:00–25/09 11:15 |
| oculto | CA-01.dc.html | g_os | Condição · próxima ação | rótulo composto; data + texto (2) | Impedida · ativo bloqueado OM-0233 · Manutenção · substituto a partir  |
| oculto | CA-01.dc.html | g_os | Realizado · saldo | rótulo composto; duas medidas (12) | 0 / 95 ha saldo 95 ha |
| oculto | CA-01.dc.html | g_os | Equipe · conjunto | rótulo composto |  |
| oculto | CA-02.dc.html | g_fila | Equipe · conjunto | rótulo composto |  |
| oculto | CA-02.dc.html | g_fila | Realizado · acumulado | rótulo composto; duas medidas (4) | 40 ha 150 conf. + 40 prov. · saldo 160 ha |
| oculto | CA-02.dc.html | g_fila | Consumos e sobras | rótulo composto; duas medidas (2) | Semente 58 W 624 kg  horas acima do previsto · 1,8 h |
| oculto | CA-02.dc.html | g_fila | Origem · sincronização | rótulo composto |  |
| oculto | CA-02.dc.html | g_fila | Conferência · ação | rótulo composto |  |
| oculto | CA-02.dc.html | g_proj | Evento | duas medidas (1) | 40 kg declarados · 40 kg medidos e recebidos |
| oculto | CA-03.dc.html | g_oc | Local · instante | rótulo composto |  |
| oculto | CA-03.dc.html | g_oc | Destino · responsável | rótulo composto |  |
| oculto | CA-03det.dc.html | g_vinc | Efeito | duas medidas (1) | 30/100 ha · saldo de 70 ha preservado e parado |
| oculto | CA-04.dc.html | g_req | Requisição · ordem | rótulo composto |  |
| oculto | CA-04.dc.html | g_req | Item · lote | rótulo composto |  |
| oculto | CA-04.dc.html | g_req | Devolvido decl. · receb. | rótulo composto; número + texto (1) | 20 · 20 sc |
| oculto | CF-01.dc.html | g_usr | Situação · ação | rótulo composto |  |
| oculto | CF-01.dc.html | g_dev | Dispositivo · usuário | rótulo composto |  |
| oculto | CF-01.dc.html | g_dev | Pacote offline | data + texto (1) | Sincronizado · APT-1187 recibo REC-7741 pacote válido até 25/09 · agor |
| oculto | CF-02.dc.html | g_alc | Comando · alçada · fonte | rótulo composto |  |
| oculto | CF-02.dc.html | g_alc | Valor / limite | rótulo composto |  |
| oculto | CF-02.dc.html | g_pol | Regra/ID · proprietário | rótulo composto |  |
| oculto | CF-02.dc.html | g_pol | Limites | duas medidas (1) | lâmina ≤ 12,0 mm por passada · intervalo ≥ 18 h |
| oculto | CF-02.dc.html | g_pol | Situação · ação | rótulo composto |  |
| oculto | CF-02det.dc.html | g_obj | Condição | duas medidas (1) | eventual dispensa do saldo de 70 ha passaria por AL-05 · 30 ha realiza |
| oculto | CF-03.dc.html | g_con | Conector / escopo | rótulo composto |  |
| oculto | CF-03.dc.html | g_con | Estado · erros | rótulo composto |  |
| oculto | CF-03.dc.html | g_con | Atualização · evento | rótulo composto |  |
| oculto | CF-03.dc.html | g_err | Item · direção | rótulo composto |  |
| oculto | CF-03.dc.html | g_err | Erro / estado | rótulo composto |  |
| oculto | CF-03.dc.html | g_err | Correlação · tentativas | rótulo composto |  |
| oculto | CF-03.dc.html | g_off | Registro | duas medidas (1) | APT-1187  · OS-0421 dia 4 · 40 ha |
| oculto | CF-03.dc.html | g_off | Identidade · recibo | rótulo composto |  |
| oculto | CF-03.dc.html | g_off | Situação · ação | rótulo composto |  |
| oculto | CF-03det.dc.html | g_rec | Documento / linha | rótulo composto |  |
| oculto | CF-03det.dc.html | g_syn | Relato · dispositivo | rótulo composto |  |
| oculto | CF-04.dc.html | g_tr | Objeto / versão | rótulo composto |  |
| oculto | CF-04.dc.html | g_tr | Autor / origem | rótulo composto |  |
| oculto | CF-04.dc.html | g_tr | Antes → depois · motivo | rótulo composto; duas medidas (1) | 90.000 kg → 89.400 kg MAP 11-52 (-600 kg · -12 sc) motivo: divergência |
| oculto | CF-04.dc.html | g_doc | Exemplo | duas medidas (1) | OS-0421 · 190 de 350 ha · dia 4 (40 ha) |
| oculto | CF-05.dc.html | g_ar | Talhão / área | rótulo composto |  |
| oculto | CF-05.dc.html | g_ar | Exclusões e deduplicação | rótulo composto |  |
| oculto | CF-05det.dc.html | g_ver | Vigência | início–fim (1) | 01/06 – 15/07/2026 |
| oculto | CO-01.dc.html | g_of | Parcela · cultura · área | rótulo composto |  |
| oculto | CO-01.dc.html | g_of | Ciclo / estádio | rótulo composto |  |
| oculto | CO-01.dc.html | g_of | Peso · curva | rótulo composto |  |
| oculto | CO-01.dc.html | g_of | Rend. comercial · perdas | rótulo composto |  |
| oculto | CO-02.dc.html | g_oc | Ordem · origem | rótulo composto |  |
| oculto | CO-02.dc.html | g_oc | Janela | início–fim (2) | 29/09–04/10 |
| oculto | CO-02.dc.html | g_oc | Etapa · selo | rótulo composto |  |
| oculto | CO-02.dc.html | g_oc | Previsto | duas medidas (1) | 96 ha · 8.640 sc |
| oculto | CO-02.dc.html | g_oc | Realizado | duas medidas (2) | 6,3 t hoje · 9,3 t acum. |
| oculto | CO-03.dc.html | g_cg | Carga · hora · veículo | rótulo composto |  |
| oculto | CO-03.dc.html | g_cg | Ordem · origem | rótulo composto |  |
| oculto | CO-03.dc.html | g_cg | Situação · romaneio | rótulo composto |  |
| oculto | CO-04.dc.html | g_rc | Entrada · origem | rótulo composto |  |
| oculto | CO-05.dc.html | g_ob | Ordem · produto · rota | rótulo composto |  |
| oculto | CO-05.dc.html | g_ob | Janela | início–fim (1) | 29/09–04/10 |
| oculto | CO-05.dc.html | g_ob | Lotes de entrada · origem | rótulo composto; número + texto (1) | 12,0 t · OC-0507 (T7 · S38) · L38-115 a 118 |
| oculto | CO-05.dc.html | g_ob | Saídas · balanço · qualidade do lote | rótulo composto; duas medidas (2) | 9,6 t A · 1,8 t B · descarte 0,6 t · em processo 0,0 t balanço 0,0 t · |
| oculto | CO-05det.dc.html | g_bal | Classe / destino | rótulo composto |  |
| oculto | CO-06.dc.html | g_in | Inspeção · lote | rótulo composto |  |
| oculto | CO-06.dc.html | g_in | Padrão · amostra | rótulo composto |  |
| oculto | CO-06.dc.html | g_in | Resultado | número + texto (1) | 14,0% · 0,9% conforme |
| oculto | CO-06.dc.html | g_in | Responsável · prazo | rótulo composto |  |
| oculto | CO-07.dc.html | g_es | Lote · local · proprietário | rótulo composto |  |
| oculto | CO-07.dc.html | g_es | Produto · classe · validade | rótulo composto |  |
| oculto | CO-07.dc.html | g_es | Disponível | número + texto (2) | 0 · bloqueado |
| oculto | GE-02.dc.html | g_ver | Estado · aprovação | rótulo composto |  |
| oculto | GE-02det.dc.html | g_cmp | Orçado V1 | número + texto (1) | 100 ha·operação |
| oculto | GE-02det.dc.html | g_cmp | Previsão V2 | número + texto (1) | 110 ha·operação |
| oculto | GE-02det.dc.html | g_cmp | Real (encerrada) | número + texto (1) | 120 ha·operação |
| oculto | GE-04.dc.html | g_tit | Credor · documento | rótulo composto |  |
| oculto | GE-04.dc.html | g_tit | Principal · pago / saldo | rótulo composto |  |
| oculto | GE-04.dc.html | g_tit | Conciliação · próxima ação | rótulo composto |  |
| oculto | GE-05.dc.html | g_rec | Cliente · título | rótulo composto |  |
| oculto | GE-05.dc.html | g_rec | Pedido · entrega | rótulo composto |  |
| oculto | GE-05.dc.html | g_rec | Vencimento | data + texto (1) | recebido 15/09 · conciliado |
| oculto | GE-05.dc.html | g_rec | Divergência · caso | rótulo composto |  |
| oculto | GE-06.dc.html | g_ind | Fórmula · fonte | rótulo composto |  |
| oculto | GE-06.dc.html | g_ind | Meta · período | rótulo composto |  |
| oculto | GE-06.dc.html | g_ind | Realizado · tendência | rótulo composto |  |
| oculto | GE-06.dc.html | g_atv | Ativo · classe | rótulo composto |  |
| oculto | GE-06.dc.html | g_atv | Disponibilidade | número + texto (1) | 62% · bloqueado |
| oculto | GE-07.dc.html | g_ac | Origem · indicador | rótulo composto |  |
| oculto | GE-07.dc.html | g_ac | Hipótese · ação definida | rótulo composto |  |
| oculto | IN-01.dc.html | g_dia | Objeto · local | rótulo composto |  |
| oculto | IN-02.dc.html | g_ap | Objeto e decisão | rótulo composto |  |
| oculto | IN-02.dc.html | g_ap | Solicitante · alçada | rótulo composto |  |
| oculto | IN-02.dc.html | g_ap | Efeito · valor | rótulo composto |  |
| oculto | IN-03.dc.html | g_ag | Condição · bloqueio | rótulo composto |  |
| oculto | LO-01.dc.html | g_ag | Carga · tipo | rótulo composto |  |
| oculto | LO-01.dc.html | g_ag | Produto · rota | rótulo composto |  |
| oculto | LO-01.dc.html | g_ag | Veículo · compatibilidade | rótulo composto; duas medidas (5) | Cliente · Rota Norte ocupação 37/37 t Compatível · granel |
| oculto | LO-01.dc.html | g_cp | Produto · conservação | rótulo composto |  |
| oculto | LO-01.dc.html | g_sl | Carga · transportador | rótulo composto |  |
| oculto | LO-02.dc.html | g_fi | Chegada real · espera | rótulo composto |  |
| oculto | LO-02.dc.html | g_fi | Situação · elegibilidade | rótulo composto |  |
| oculto | LO-02.dc.html | g_ex | Pedido · destino | rótulo composto |  |
| oculto | LO-02.dc.html | g_ex | Lote · quantidade | rótulo composto; duas medidas (1) | MZ-26-03 · 37,00 t líquido bruto 51,20 t · tara 14,20 t |
| oculto | LO-02.dc.html | g_ex | Veículo · doca | rótulo composto |  |
| oculto | LO-02.dc.html | g_ex | Etapa · checklist | rótulo composto |  |
| oculto | LO-02det.dc.html | g_cf | Saldo da parcela | duas medidas (1) | 0 t · 2ª de 3 cargas (37,00 t na 3ª) |
| oculto | LO-02det.dc.html | g_ps | Umidade · base | rótulo composto; número + texto (1) | 13,8% · base 14% |
| oculto | LO-02det.dc.html | g_sa | Quem · quando | rótulo composto |  |
| oculto | LO-03.dc.html | g_vg | Eventos · evidência | rótulo composto |  |
| oculto | LO-03.dc.html | g_vg | Recebido · ocorrência | rótulo composto; duas medidas (1) | 9,0 t  aceitas ·  0,4 t  recusadas OC-77 · avaria em 2 pallets Caso RC |
| oculto | LO-03.dc.html | g_rt | Direcionador · versão | rótulo composto |  |
| oculto | LO-04.dc.html | g_pr | Prestador · rota | rótulo composto |  |
| oculto | LO-04.dc.html | g_pr | Documentos | data + texto (1) | Seguro vencido 15/09 · não elegível |
| oculto | ON-01.dc.html | g_passos | Passo | número + texto (6) | 1 · Organização |
| oculto | ON-01.dc.html | g_passos | Dado pedido no momento do uso | data + texto (1) | cultura Soja · safra 2026/27 · datas com a precisão que você tiver |
| oculto | ON-01.dc.html | g_trial | Ao esgotar ou expirar | data + texto (1) | termina 18/10/2026 · aviso desde a entrada |
| oculto | PL-01.dc.html | g_saf | Cultivos · área | rótulo composto |  |
| oculto | PL-02.dc.html | g_op | Parcela · cultivo | rótulo composto |  |
| oculto | PL-02.dc.html | g_op | Atividade · necessidade | rótulo composto |  |
| oculto | PL-02.dc.html | g_op | Situação | duas medidas (1) | Convertida · OS-0420 30 de 100 ha feitos · saldo 70 ha impedido |
| oculto | PL-02det.dc.html | g_tal | Estado | data + texto (1) | Realizada 05/09 · preservada |
| oculto | PL-03.dc.html | g_mi3 | Produção afetada | duas medidas (1) | OS-0420 saldo 70 ha OS-0431 · plantio T2 · 102 ha |
| oculto | PL-04.dc.html | g_ord | Janela · duração | rótulo composto; duas medidas (1); início–fim (1) | 24–26/09 dias 5–7 · saldo 160 ha 3 turnos |
| oculto | PL-04.dc.html | g_ord | Conjunto · operador | rótulo composto |  |
| oculto | PL-04.dc.html | g_ord | Impedimento · selo | rótulo composto |  |
| oculto | PL-04.dc.html | g_ord | Etapa · material | rótulo composto |  |
| oculto | PL-04.dc.html | g_mi4 | Produção afetada | duas medidas (1) | OS-0420 saldo 70 ha OS-0431 · plantio T2 · 102 ha |
| oculto | PL-05.dc.html | g_imp | Causa · origem | rótulo composto |  |
| oculto | PL-05.dc.html | g_imp | Afetados · impacto | rótulo composto; duas medidas (1) | NEC-028 · plantio T4 (saldo 70 ha) cobertura da soja · DAP +20 8,4 t p |
| oculto | PL-05.dc.html | g_imp | Alternativa · aprovação | rótulo composto; duas medidas (1); data + texto (1) | atender a NEC-028 com as 50 t aptas 10 t em quarentena · 40 t para a c |
| oculto | PL-06.dc.html | g_par | Parcela · geometria | rótulo composto |  |
| oculto | PL-06.dc.html | g_par | Ciclo e ocupação | rótulo composto; data + texto (3) | Safra 2026/27 · soja |
| oculto | PL-06.dc.html | g_par | Janela de colheita | início–fim (2) | 05/02–15/02 |
| oculto | PT-01.dc.html | g_op | Convite e acesso | rótulo composto |  |
| oculto | PT-02.dc.html | g_cot | Itens e volume | rótulo composto |  |
| oculto | PT-02.dc.html | g_cot | Proposta e situação | rótulo composto |  |
| oculto | PT-02det.dc.html | g_dos | Valor | data + texto (1) | até 08/10 · só esta cotação |
| oculto | PT-02det.dc.html | g_dos | Fonte | data + texto (1) | SOL-2026-07 · Planejar safra · Safra 2026/27 · etapa 6 |
| oculto | PT-02det.dc.html | g_esc | De · quando | rótulo composto |  |
| oculto | PT-03.dc.html | g_of | Produto e padrão | rótulo composto |  |
| oculto | PT-03.dc.html | g_of | Volume e janela | rótulo composto; início–fim (3) | 2.000 kg · 05/10–11/10 |
| oculto | PT-03.dc.html | g_of | Preço, condição e local | rótulo composto |  |
| oculto | PT-03.dc.html | g_pp | Janela de entrega | início–fim (1) | 05/10–11/10 |
| oculto | PT-04.dc.html | g_ds | Dossiê | data + texto (1) | CRE-0102 custeio 2026/27 · R$ 850 mil |
| oculto | PT-04.dc.html | g_ds | Finalidade e blocos concedidos | rótulo composto |  |
| oculto | PT-04det.dc.html | g_con | Valor | data + texto (1) | até 31/12/2026 · por bloco |
| oculto | PT-05.dc.html | g_ng | Pedido e documento | rótulo composto |  |
| oculto | PT-05.dc.html | g_ng | Entrega | duas medidas (1) | 60 t recebidas carga 3 · 40 t em 02/10 |
| oculto | PT-05.dc.html | g_msg | De · quando | rótulo composto |  |
| oculto | PT-05det.dc.html | g_cond | Valor | duas medidas (2) | KCl 60% · contrato 140 t · liberado 100 t no PC-088 |
| oculto | PT-06.dc.html | g_fu | Conversão da etapa | número + texto (1) | 67% · 1 em execução |
| oculto | PT-06.dc.html | g_co | Categoria · região | rótulo composto |  |
| oculto | PT-07.dc.html | g_emp | Empresa · CNPJ | rótulo composto |  |
| oculto | PT-07.dc.html | g_pl | Vigência | início–fim (1) | 01/09/2026 – 31/08/2027 |
| oculto | SU-01.dc.html | g_nec | Item · origem | rótulo composto |  |
| oculto | SU-01.dc.html | g_nec | Pedir até · necessária | rótulo composto |  |
| oculto | SU-02.dc.html | g_pol | Item/grupo · depósito | rótulo composto |  |
| oculto | SU-02.dc.html | g_pol | ABC · criticidade | rótulo composto |  |
| oculto | SU-02.dc.html | g_pol | Segurança · prazo | rótulo composto |  |
| oculto | SU-02.dc.html | g_pol | Versão · estado | rótulo composto |  |
| oculto | SU-03.dc.html | g_sal | Item · lote | rótulo composto |  |
| oculto | SU-04.dc.html | g_cot | Cotação · origem | rótulo composto |  |
| oculto | SU-05.dc.html | g_ctr | Contraparte · contrato | rótulo composto |  |
| oculto | SU-05.dc.html | g_ctr | Item · unidade | rótulo composto |  |
| oculto | SU-05.dc.html | g_ctr | Preço · condição | rótulo composto |  |
| oculto | SU-05.dc.html | g_ctr | Exposição · limite | rótulo composto |  |
| oculto | SU-05.dc.html | g_ped | Pedido · fornecedor | rótulo composto |  |
| oculto | SU-05.dc.html | g_car | Carga · contrato/pedido | rótulo composto |  |
| oculto | SU-05.dc.html | g_car | Chegada | data + texto (1) | 19/09 · NF 4501 |
| oculto | SU-05.dc.html | g_dep | Capacidade | duas medidas (1) | 250 t · 36 t/dia |
| oculto | SU-05.dc.html | g_mes | Quantidade | duas medidas (1); número + texto (1) | 60 t · 15 mil L |
| oculto | SU-05det.dc.html | g_lib | Liberação · carga | rótulo composto |  |
| oculto | SU-06.dc.html | g_rec | Documento · pedido | rótulo composto |  |
| oculto | SU-06.dc.html | g_rec | Item · lote | rótulo composto |  |
| oculto | SU-06.dc.html | g_rec | Apto · retido | rótulo composto |  |
| oculto | SU-06.dc.html | g_rec | Inspeção · divergência | rótulo composto |  |
| oculto | SU-06.dc.html | g_rec | Físico · título · ação | rótulo composto |  |
| oculto | SU-07.dc.html | g_req | Requisição · O.S. | rótulo composto |  |
| oculto | SU-07.dc.html | g_req | Item · lote | rótulo composto |  |
| oculto | SU-07.dc.html | g_req | Estado · próxima ação | rótulo composto |  |
| oculto | SU-08.dc.html | g_mov | Documento · data | rótulo composto |  |
| oculto | SU-08.dc.html | g_mov | Movimento · motivo | rótulo composto |  |
| oculto | SU-08.dc.html | g_mov | Item · lote | rótulo composto |  |
| oculto | SU-09.dc.html | g_inv | Inventário · escopo | rótulo composto |  |
| oculto | SU-09.dc.html | g_inv | Corte · contador | rótulo composto |  |
| oculto | SU-09.dc.html | g_inv | Observado × sistema · recontagem | rótulo composto |  |
| oculto | SU-09.dc.html | g_inv | Diferença · causa | rótulo composto |  |
| oculto | SU-09.dc.html | g_inv | Estado · ação | rótulo composto |  |
| oculto | VE-01.dc.html | g_bal | Produto · classe | rótulo composto |  |
| oculto | VE-01.dc.html | g_bal | Janela | início–fim (3) | 28/09–04/10 |
| oculto | VE-01.dc.html | g_bal | Demanda | número + texto (4) | 10,0 t ·  PV-031  a confirmar |
| oculto | VE-01.dc.html | g_bal | Oferta | número + texto (4) | 9,6 t ·  L39-120  em inspeção |
| oculto | VE-02.dc.html | g_pr | Fonte · licença | rótulo composto |  |
| oculto | VE-03.dc.html | g_of | Janela | início–fim (3) | 05/10–11/10 |
| oculto | VE-03.dc.html | g_of | Destino · clientes | rótulo composto |  |
| oculto | VE-03.dc.html | g_of | Preço · condição | rótulo composto |  |
| oculto | VE-03.dc.html | g_of | Estado · validade | rótulo composto |  |
| oculto | VE-04.dc.html | g_cart | Item · classe | rótulo composto |  |
| oculto | VE-04.dc.html | g_cart | Quantidade · janela | rótulo composto; início–fim (6) | 1,2 t 28/09–04/10 |
| oculto | VE-04.dc.html | g_cart | Preço · condição | rótulo composto |  |
| oculto | VE-04.dc.html | g_cart | Alocação · estado | rótulo composto; duas medidas (1) | Entregue 9,0 t · recusa 0,4 t (RC-15) |
| oculto | VE-04det.dc.html | g_ver | Preço · medição | rótulo composto |  |
| oculto | VE-04det.dc.html | g_ver | Janela | início–fim (1) | 28/09–04/10 |
| oculto | VE-05.dc.html | g_ob | Obrigação · contraparte | rótulo composto |  |
| oculto | VE-05.dc.html | g_ob | Produto · janela | rótulo composto; data + texto (4) | Soja 25/26 · sc 50 kg · FOB set–out/26 |
| oculto | VE-05.dc.html | g_ob | Condições · vínculo | rótulo composto |  |
| oculto | VE-06.dc.html | g_rc | Pedido · entrega | rótulo composto; data + texto (2) | PV-026 · VG-117 entrega 22/09 · recusa em LO-03 |
| oculto | VE-06.dc.html | g_rc | Motivo · evidências | rótulo composto |  |
| oculto | VE-06.dc.html | g_rc | Lote · quantidade | rótulo composto |  |
| oculto | VE-06.dc.html | g_rc | Decisão · financeiro | rótulo composto |  |

## Todas as grades

| Página | Grade | Linhas | Colunas (tipo) |
|---|---|---|---|
| AG-01.dc.html | g_vis | 0 | Vistoria, Talhão · cultura, Alvo, Contagem × NC [num], Data [date], Situação, Próximo passo |
| AG-01det.dc.html | g_pts | 0 | Ponto, GPS, Hora, Contagem [num], × NC, Fotos [num], Qualidade |
| AG-02.dc.html | g_lau | 6 | Laudo · amostra, Local · área representada, Profund., Data [date], Laboratório, Método · extrator, Validação, Próxima ação |
| AG-02.dc.html | g_ext | 4 | Atributo, Valor [num], Unidade, LD |
| AG-03.dc.html | g_dia | 0 | Diagnóstico, Talhão · cultura, Evidências, Hipótese · causa, Risco, Situação · decisão, Próximo passo |
| AG-03det.dc.html | g_ev | 3 | Evidência, Tipo, Data [date], O que mostra, Fonte |
| AG-04.dc.html | g_rec | 4 | Recomendação, Origem, Operação · talhão, Produto · dose · janela, Situação, Próximo passo |
| AG-04det.dc.html | g_ver | 3 | Versão, O que muda, Alcance, Situação, Quando [date] |
| AG-04det.dc.html | g_it | 3 | Produto, Unidade, Dose sugerida, Dose informada, Registro Agrofit |
| AG-04det.dc.html | g_zon | 3 | Zona, Área [num], K trocável, KCl 60 % (v2) [num], Saldo na v3 [num] |
| AG-04det.dc.html | g_exe | 2 | Registro, O que é, Situação |
| AG-04det.dc.html | g_cus | 4 | Recurso, Origem, Quantidade × preço, Custo [num], Situação |
| AG-05.dc.html | g_bib | 6 | Item · tipo, Escopo (cultura · região · fase), Referência, Unidade · gatilhos, Validade · revisão, Aprovador técnico, Situação, Ação |
| AG-06.dc.html | g_ef | 5 | Avaliação, Recomendação → execução, Método pré/pós, Datas, Resultado, Confiança, Custo [num], Ação |
| AG-06.dc.html | g_eco | 2 | Economia, Valor [num], O que entra, Situação |
| AG-07.dc.html | g_agf | 0 | Produto · registro, Ingrediente ativo · grupo químico, Classe · modo de ação, Culturas [num], Tox · amb, Na fazenda [num] |
| BO-01.dc.html | g_pl | 5 | Plano e versão, Contratante / segmento, Moeda, Vigência, Tarifa, mínimo e excedentes, Estado |
| BO-01.dc.html | g_tm | 2 | Versão e coorte, Duração, Limite de área, Franquias e esgotamento, Retenção e exportação, Estado |
| BO-01det.dc.html | g_par | 4 | Área contratada [num], Sem mínimo (R$/mês) [num], Com mínimo R$ 299 (R$/mês) [num], Efetivo (R$/ha·mês) [num], Recorrente anual [num] |
| BO-01det.dc.html | g_ct | 4 | Contratante, Vigência, Área contratada [num], Consulta do contratante |
| BO-02.dc.html | g_as | 6 | Contratante, Plano, Estado, Próximo evento, Pagamento (token) |
| BO-02.dc.html | g_fat | 6 | Fatura, Contratante, Valor [num], Estado, Confirmação / origem, Ação |
| BO-02det.dc.html | g_tl | 5 | Evento, Data, Origem, Resultado |
| BO-03.dc.html | g_med | 5 | Contratante e base, Contratada → medida, Franquias usadas, Estado, Divergência, Ação |
| BO-03det.dc.html | g_mem | 6 | Parcela, Fonte e versão, Valor, Entra na base?, Observação |
| BO-03det.dc.html | g_aj | 1 | Ajuste, Tipo, Valor [num], Origem, Estado |
| BO-04.dc.html | g_co | 5 | Coorte, Perfil, Contas [num], Ativação, Conversão trial → pago, Retenção 90 d, Receita/conta·mês, Suporte h/conta |
| CA-01.dc.html | g_os | 12 | O.S., Atividade · local, Janela, Fase, Condição · próxima ação, Realizado · saldo [num], Equipe · conjunto |
| CA-01det.dc.html | g_ap | 7 | Data, Turno, Área do dia [num], Acumulado [num], Conferência, Origem · sincronização |
| CA-01det.dc.html | g_mat | 1 | Item · lote, Solicitado [num], Entregue [num], Consumido [num], Em custódia [num], A entregar [num], Custódia de |
| CA-01x-os0420.dc.html | g_ins | 3 | Produto, Dose da v2, Quantidade para 100 ha [num], Saldo de 70 ha na v3, Fonte |
| CA-01x-os0420.dc.html | g_ap0420 | 2 | Data, Turno, Área do dia [num], Acumulado [num], Conferência, Origem · sincronização |
| CA-01x-os0420.dc.html | g_req0420 | 1 | Requisição, Item, Solicitado [num], Entregue [num], Consumido [num], Em custódia [num], Custo apontado [num] |
| CA-02.dc.html | g_fila | 4 | Apontamento, Equipe · conjunto, Realizado · acumulado [num], Horas [num], Consumos e sobras, Origem · sincronização, Conferência · ação |
| CA-02.dc.html | g_proj | 8 | Quando, Evento, Efeito, Quem |
| CA-03.dc.html | g_oc | 4 | Ocorrência, Local · instante, Relato, Gravidade, Evidência, Destino · responsável, Próxima ação |
| CA-03det.dc.html | g_vinc | 4 | Registro, Tipo, Estado, Efeito |
| CA-03det.dc.html | g_trilha | 6 | Instante, Evento, Quem, Efeito |
| CA-04.dc.html | g_req | 4 | Requisição · ordem, Item · lote, Solicitado [num], Entregue [num], Consumido [num], Devolvido decl. · receb., Em custódia [num], Próxima ação |
| CD-01.dc.html | g_faz | 3 | Fazenda, Área total [num] |
| CD-01.dc.html | g_tal | 35 | Talhão, Área cultivável [num], Polígono [num], Diferença [num], Safra 2026/27, Situação |
| CD-01.dc.html | g_amb | 18 | Área ambiental, Fazenda, Tipo, Área [num] |
| CD-01.dc.html | g_agua | 16 | Ponto de água, Fazenda, Uso, Vazão, Situação |
| CD-01det.dc.html | g_idt | 32 | Fazenda, Sistema, Área cultivável [num], Polígono, Diferença, Situação |
| CD-01det.dc.html | g_parc | 42 | Safra · parcela, Cultura · variedade, Área [num], Livre, Plantio [date], Polígono |
| CD-02.dc.html | g_cv | 12 | Cultura · cultivar, Ciclo, Item de semente, Cultivos, Situação |
| CD-02.dc.html | g_cult | 5 | Cultura |
| CD-02.dc.html | g_rend | 22 | Operação · conjunto, Cultura, Rendimento [num], Custo por hora [num], Custo por hectare [num], Fonte |
| CD-02.dc.html | g_op | 11 | Operação |
| CD-03.dc.html | g_atv | 15 | Máquina ou instalação, Classe, Capacidade, Custo por hora [num], Conjuntos [num], Situação |
| CD-03.dc.html | g_cj | 7 | Conjunto, Operações, Largura [num], Condição, Operadores alocáveis, Rendimento [num] |
| CD-04.dc.html | g_pes | 10 | Pessoa · equipe, Habilidades, Vínculo, Custo-hora [num], Situação |
| CD-04.dc.html | g_eq | 6 | Equipe, Líder, Pessoas ativas [num], Calendário |
| CD-05.dc.html | g_forn | 20 | Parceiro · CPF/CNPJ, Papéis, Contato, Situação do papel |
| CD-05.dc.html | g_cob | 0 | Grupo de insumo, Fornecedores que recebem cotação [num], Situação |
| CD-06.dc.html | g_itm | 50 | Grupo · item, Unidade · embalagem, Controle, Preço de referência [num], Situação |
| CD-06.dc.html | g_grp | 12 | Grupo |
| CD-06.dc.html | g_loc | 10 | Local, Fazenda, Tipo, Capacidade, Itens com este local padrão [num] |
| CD-07.dc.html | g_dim | 30 | Dimensão · código, Vigência, Vínculos, Tradução no ERP (Sankhya), Situação |
| CF-01.dc.html | g_usr | 7 | Identidade, Papel, Escopo, Vigência, Autenticação, Situação · ação |
| CF-01.dc.html | g_dev | 4 | Dispositivo · usuário, Último sincronismo, Pacote offline, Ação |
| CF-02.dc.html | g_alc | 6 | Comando · alçada · fonte, Dono (quem decide), Valor / limite, Classe de bloqueio, Vigência, Abrir |
| CF-02.dc.html | g_pol | 4 | Regra/ID · proprietário, Escopo, Limites, Aprovadores, Vigência, Situação · ação |
| CF-02det.dc.html | g_def | 6 | Campo, Valor vigente (v2), Proposta (v3 · em revisão) |
| CF-02det.dc.html | g_tst | 4 | Caso, Entrada, Resultado esperado, Situação |
| CF-02det.dc.html | g_obj | 2 | Objeto, Condição, Abrir |
| CF-02det.dc.html | g_v3 | 1 | Versão, Mudança proposta, Proposta por, Situação |
| CF-03.dc.html | g_con | 3 | Conector / escopo, Fonte oficial (escritor), Estado · erros, Atualização · evento, Responsável, Ação |
| CF-03.dc.html | g_err | 3 | Item · direção, Erro / estado, Correlação · tentativas, Responsável, Ação |
| CF-03.dc.html | g_off | 2 | Dispositivo, Registro, Identidade · recibo, Comportamento verificado, Situação · ação |
| CF-03det.dc.html | g_rec | 2 | Documento / linha, Correlação, Plataforma, ERP (Sankhya), Diferença, Estado |
| CF-03det.dc.html | g_syn | 2 | Relato · dispositivo, Identidade local, Recibo, Área [num], Servidor, Estado |
| CF-04.dc.html | g_tr | 6 | Instante (BRT), Objeto / versão, Autor / origem, Antes → depois · motivo, Efeito |
| CF-04.dc.html | g_par | 3 | Parâmetro, Valor, Fonte, Situação |
| CF-04.dc.html | g_doc | 3 | Tipo, Processo, O que garante, Exemplo, Abrir |
| CF-05.dc.html | g_pl | 6 | Campo, Valor, Observação |
| CF-05.dc.html | g_ar | 9 | Talhão / área, Física [num], Elegível [num], Exclusões e deduplicação, Situação |
| CF-05.dc.html | g_fat | 3 | Competência, Base (ha), Regra aplicada, Valor, Estado, Memória |
| CF-05det.dc.html | g_cmp | 6 | Componente, Base, Regra, Valor |
| CF-05det.dc.html | g_ver | 3 | Versão, Vigência, Área elegível, Mudança, Aceite |
| CMP.dc.html | g_saf | 0 | Safra, Solicitação de compra, Origem, Compra, Ação |
| CMP.dc.html | g_dem | 0 | Grupo · insumo, Bruta [num], Estoque apto [num], A receber [num], Necessidade [num], Un., Falta a partir de [date], Preço ref. [num], Valor (R$) [num], Na compra |
| CMP.dc.html | g_conv | 0 | Grupo · fornecedor, Homologação, Convite, Canal e contato, Responder até, Resposta |
| CMP.dc.html | g_cmp | 0 | Grupo · insumo · proposta, A pedir [num], Preço (R$) [num], Entrega [num], Frete, Pagamento, Validade, Custo (R$) [num], Escolha |
| CMP.dc.html | g_apr | 0 | Pedido · fornecedor · insumo, Quantidade [num], Preço (R$/un) [num], Entrega (dias) [num], Frete, Pagamento, Valor (R$) [num] |
| CMP.dc.html | g_ent | 0 | Pedido · fornecedor · insumo, Pedido [num], Recebido [num], A entregar [num], Valor (R$) [num], Previsão [date], Situação, Ação |
| CO-01.dc.html | g_of | 4 | Parcela · cultura · área, Ciclo / estádio, Plantas vivas, Peso · curva, Rend. comercial · perdas, Faixa prevista, Destino, Ação |
| CO-01.dc.html | g_ped | 1 | Pedido, Cliente pede, Futuras em classe A, Falta, Semana, Situação |
| CO-01.dc.html | g_wape | 2 | Ciclo, Versão congelada, Antecedência, WAPE, Viés, Amostra, Meta |
| CO-02.dc.html | g_oc | 6 | Ordem · origem, Janela, Etapa · selo, Previsto, Realizado, Saldo, Equipe, Ação |
| CO-02det.dc.html | g_ap | 2 | Dia, Quantidade [num], Horas de equipe, Cargas do dia, Situação |
| CO-02det.dc.html | g_cv | 3 | Carga, Líquido [num], Qualidade inicial, Destino, Vínculo |
| CO-03.dc.html | g_cg | 5 | Carga · hora · veículo, Ordem · origem, Bruto − tara (kg), Líquido [num], Qualidade inicial, Destino, Situação · romaneio, Ação |
| CO-04.dc.html | g_rc | 6 | Entrada · origem, Peso recebido, Local, Condição, Amostra, Divergência, Lote criado, Ação |
| CO-05.dc.html | g_ob | 4 | Ordem · produto · rota, Janela, Etapa, Lotes de entrada · origem, Saídas · balanço · qualidade do lote, Ação |
| CO-05det.dc.html | g_bal | 4 | Fluxo, Quantidade [num], Classe / destino, Lote, Situação |
| CO-06.dc.html | g_in | 5 | Inspeção · lote, Produto, Padrão · amostra, Resultado, Decisão, Responsável · prazo, Ação |
| CO-06det.dc.html | g_pd | 1 | Pendência, Lote, Quantidade, Responsável, Prazo, Condição de resolução |
| CO-06det.dc.html | g_am | 3 | Critério, Padrão do tipo 6, Medido, Situação |
| CO-06det.dc.html | g_ef | 2 | Tentativa, Origem, Resultado |
| CO-07.dc.html | g_es | 7 | Lote · local · proprietário, Produto · classe · validade, Físico, Qualidade, Reservado, Disponível, Origem, Ação |
| EST.dc.html | g_rec | 0 | Nota fiscal, Pedido, Item · lote, Na nota [num], Conferida [num], Apta [num], Quarentena [num], Situação |
| EST.dc.html | g_ent | 0 | Requisição · O.S., Fase da O.S., Item · lote · embalagem, Solicitado [num], Entregue [num], A entregar [num], Situação |
| EST.dc.html | g_dev | 0 | Requisição · O.S., Item · lote, Entregue [num], Consumido [num], Devolvido [num], Em custódia [num], Encerramento da O.S. |
| EST.dc.html | g_lot | 0 | Item · lote, Local, Físico [num], Reservado [num], Bloqueado [num], Disponível [num], Em custódia (fora do depósito) [num], Validade |
| EST.dc.html | g_cnt | 0 | Contagem, Item · lote, Local, Sistema na data de corte [num], Contado [num], Diferença [num], Situação, Ação |
| EST.dc.html | g_mov | 0 | Hora, Movimento, Documento, Item · lote, Quantidade, Quem, Origem |
| GE-01.dc.html | g_res | 5 | Cultura, Área [num], Receita [num], Margem [num], Custo unitário, Capital com terra [num], ROIC [num], Causa prioritária |
| GE-01.dc.html | g_cau | 3 | Desvio, Onde, Efeito, Origem do dado, Próxima ação |
| GE-02.dc.html | g_ver | 3 | Versão, Premissas, Volume soja [num], Preço soja (R$/sc) [num], Custo total [num], Pico de caixa, Estado · aprovação |
| GE-02.dc.html | g_cx | 4 | Trimestre, Desembolso V1 [num], Desembolso V2 [num], Diferença [num], Maior componente |
| GE-02det.dc.html | g_cmp | 6 | Grandeza, Orçado V1, Previsão V2, Real (encerrada), Diferença V1→real, Fonte |
| GE-03.dc.html | g_lan | 10 | Origem (documento), Componente, Dimensões, Qtd × preço, Valor [num], Rateio, Estado |
| GE-04.dc.html | g_tit | 7 | Credor · documento, Origem, Vencimento [date], Principal · pago / saldo [num], Programado [date], Conciliação · próxima ação |
| GE-05.dc.html | g_rec | 9 | Cliente · título, Pedido · entrega, Vencimento [date], Valor [num], Saldo [num], Divergência · caso, Próxima cobrança [date] |
| GE-06.dc.html | g_ind | 5 | Indicador, Processo, Fórmula · fonte, Meta · período, Realizado · tendência, Causa apontada, Ação |
| GE-06.dc.html | g_atv | 4 | Ativo · classe, Disponibilidade, Utilização, MTBF, MTTR, Custo/h realizado |
| GE-06det.dc.html | g_cau | 3 | Causa, Efeito, Evidência, Hipótese a validar |
| GE-06det.dc.html | g_doc | 4 | Documento, O que sustenta, Data, Abrir |
| GE-07.dc.html | g_ac | 5 | Caso, Origem · indicador, Hipótese · ação definida, Dono, Prazo [date], Estado, Ação |
| GE-08.dc.html | g_cre | 4 | Solicitação, Finalidade, Credor, Valor [num], Garantia, Custo (CET), Estado, Ação |
| GE-08.dc.html | g_dos | 3 | Bloco do dossiê, Conteúdo, Autorizado para, Prazo de acesso [date], Consentimento |
| IN-01.dc.html | g_dia | 8 | Objeto · local, Tarefa, Prazo, Responsável, Impedimento, Próxima ação |
| IN-02.dc.html | g_ap | 4 | Objeto e decisão, Solicitante · alçada, Vencimento, Efeito · valor, Conflito, Situação |
| IN-03.dc.html | g_ag | 7 | Data [date], Compromisso, Responsável, Prioridade, Condição · bloqueio, Prazo limite, Abrir |
| IR-01.dc.html | g_set | 0 | Setor, Déficit hoje [num], Necessidade, Situação, Próximo passo |
| IR-02.dc.html | g_ag | 0 | Captação · ordem, Setor · bomba, Janela, Lâmina [num], Etapa · pendência |
| IR-03.dc.html | g_os | 0 | Ordem, Setor, Janela, Lâmina [num], Etapa, Próximo passo |
| IR-03det.dc.html | g_pas | 0 | Passada, Janela, Lâmina [num], Duração, Estado, Área coberta |
| IR-03det.dc.html | g_trl | 0 | Quando, Recibo, Evento, Quem |
| IR-04.dc.html | g_src | 0 | Fonte, Atualização, Calibração, Cobertura, Estado, Efeito no balanço |
| IR-04.dc.html | g_cap | 0 | Captação, Vazão outorgada [num], Vencimento [date], Situação, Uso hoje, Setores ligados |
| IR-04.dc.html | g_des | 3 | Setor, Volume [num], Energia [num], Lâmina aplicada [num], Eficiência [num], Indicador |
| LO-01.dc.html | g_ag | 5 | Carga · tipo, Produto · rota, Janela, Veículo · compatibilidade, Frete, Ação |
| LO-01.dc.html | g_cp | 2 | Candidata a agrupar com a Carga 07, Produto · conservação, Rota, Janela, Compatibilidade |
| LO-01.dc.html | g_sl | 5 | Slot, Doca, Carga · transportador, Duração, Responsabilidade, Estado |
| LO-02.dc.html | g_fi | 5 | Veículo, Pos. [num], Janela original, Chegada real · espera, Situação · elegibilidade, Por que está nesta posição, Ação |
| LO-02.dc.html | g_ex | 5 | Pedido · destino, Lote · quantidade, Veículo · doca, Documento, Etapa · checklist, Ação |
| LO-02.dc.html | g_po | 4 | Veículo, Janela original, Chegada real, Pontualidade (vs. janela original), Espera desde a chegada |
| LO-02det.dc.html | g_cf | 1 | Item, Lote, Pedido (parcela), Separado, Carregado, Saldo da parcela, Conferência |
| LO-02det.dc.html | g_ps | 1 | Ticket, Tara, Bruto, Líquido, Umidade · base, Origem da medição |
| LO-02det.dc.html | g_ck | 5 | Verificação, Estado, Responsável |
| LO-02det.dc.html | g_sa | 4 | Evento, Estado, Quem · quando |
| LO-03.dc.html | g_vg | 4 | Viagem, Carga → destinatário, Eventos · evidência, Recebido · ocorrência, Estado, Ação |
| LO-03.dc.html | g_tar | 5 | Registro, Valor |
| LO-03.dc.html | g_rt | 1 | Viagem, Direcionador · versão, Base, Componentes, Total [num], Reconciliação |
| LO-04.dc.html | g_ct | 3 | Prestador, Base, Custo total [num], Prazo, Conservação, Itens incluídos, Situação |
| LO-04.dc.html | g_pr | 3 | Prestador · rota, Preço, Condição, Documentos, Desempenho 90 d, Ação |
| LO-04.dc.html | g_sv | 2 | Viagem, Prestador, Medição, Rateio aplicado, Valor do serviço [num], Estado, Ação |
| LO-04.dc.html | g_ra | 3 | Direcionador, Versão, Quando usar, Salvaguardas |
| MA-01.dc.html | g_at | 16 | Ativo · local · contador, Condição, Agenda, Elegível, Próxima manutenção, Uso 30 d [num] |
| MA-01.dc.html | g_ut | 5 | Grupo/classe, Ativos [num], Horas trabalhadas 30 d [num], Horas disponíveis 30 d [num], Utilização [num] |
| MA-02.dc.html | g_cs | 6 | Caso, Ativo, Sintoma · contador · evidência, Criticidade, Condição recomendada · responsável, Ação |
| MA-02.dc.html | g_pa | 4 | Item/sistema, Achados [num], Ativos afetados [num], Horas paradas [num], % das horas paradas [num], Acumulado [num] |
| MA-02.dc.html | g_ct | 2 | Ordem de campo, Efeito, Tratamento, Abrir |
| MA-03.dc.html | g_vc | 0 | Ativo, Serviço, Leitura · última, Próximo vencimento [num], Situação, Ordem |
| MA-03.dc.html | g_mi | 0 | Manutenção, Janela, Produção afetada, Situação, Abrir |
| MA-04.dc.html | g_om | 0 | Ordem · ativo, Serviço · tipo, Janela, Fase · selos, Checklist · peças, Ação |
| MA-04det.dc.html | g_ib | 0 | Objeto afetado, Efeito, Tratamento, Situação, Abrir |
| MA-04det.dc.html | g_tk | 3 | Tarefa, Situação, Horas [num], Peças aplicadas |
| MA-04det.dc.html | g_te | 0 | Teste, Quando, Resultado, Efeito |
| MA-04det.dc.html | g_sb | 2 | Item, Destinação, Responsável |
| MA-05.dc.html | g_ab | 4 | Lançamento · operador, Ativo, Tanque/lote · nível após, Volume [num], Data · contador, Método / taxa, Ação |
| MA-05.dc.html | g_co | 3 | Ativo, Litros no período [num], Horas trabalhadas [num], Taxa [num], Método, Desvio vs. referência |
| ON-01.dc.html | g_passos | 6 | Passo, Estado, Dado pedido no momento do uso, Próxima ação |
| ON-01.dc.html | g_trial | 6 | Recurso, Habilitação, Franquia, Unidade, Ao esgotar ou expirar |
| ON-01det.dc.html | g_imp | 4 | Objeto, Linhas [num], Mapeamento, Sistema de coordenadas, Erro, Estado |
| OS.dc.html | g_os | 0 | O.S., Atividade, Talhão [multi], Local, Área (ha) [num], Início [date], Fim [date], Fase, Situação [multi], Observação, Quem resolve, Próxima ação, Prazo, Realizado (ha) [num], Saldo (ha) [num], Dispensado (ha) [num], Progresso (%) [num], Lâmina, Responsável |
| PA.dc.html | g_cv | 0 | Safra, Talhão ou parcela, Cultura e variedade, Área [num], Versão aplicada, Situação |
| PL-01.dc.html | g_saf | 4 | Safra, Período, Fazenda, Cultivos · área, Situação, Abrir |
| PL-01.dc.html | g_cult | 9 | Talhão/parcela, Cultura, Variedade, Área [num], Plantio previsto [date], Meta (hipótese), Plano |
| PL-02.dc.html | g_op | 7 | Parcela · cultivo, Atividade · necessidade, Dose/quantidade, Gatilho por extenso → data, Situação, Abrir |
| PL-02det.dc.html | g_tal | 9 | Atividade, Gatilho por extenso, Data resultante, Estado, Dose local, Dose padrão |
| PL-03.dc.html | g_cap | 5 | Recurso/classe, Operação dominante, Carga out/26 [num], Capacidade líquida [num], Ocupado [num], Livre [num], Sem alocação [num], Indisponível, Déficit |
| PL-03.dc.html | g_cen | 5 | Cenário, Cobre [num], Custo estimado (hipótese) [num], Restrição, Comparação |
| PL-03.dc.html | g_mi3 | 3 | Manutenção, Janela, Produção afetada, Situação, Abrir |
| PL-04.dc.html | g_ord | 8 | Ordem, Janela · duração, Conjunto · operador, Impedimento · selo, Etapa · material, Abrir |
| PL-04.dc.html | g_maq | 4 | Máquina, Condição, Ocupação no período, Elegibilidade |
| PL-04.dc.html | g_pen | 2 | Ordem, Etapa, Selo, Pendência, Ação |
| PL-04.dc.html | g_mi4 | 3 | Manutenção, Janela, Produção afetada, Situação, Abrir |
| PL-05.dc.html | g_imp | 5 | Causa · origem, Afetados · impacto, Responsável, Prazo, Alternativa · aprovação, Ação |
| PL-06.dc.html | g_par | 4 | Parcela · geometria, Área [num], Ciclo e ocupação, Variedade, Plantio próprio [date], Janela de colheita, Preparo/limpeza, Situação |
| PL-06.dc.html | g_sem | 4 | Semana, Oferta [num], Entregas contratadas [num], Saldo, Capacidade colheita/secagem [num] |
| PM.dc.html | g_pv | 0 | Ativo, Serviço, Leitura · última, Próximo vencimento [num], Situação, Ordem |
| PT-01.dc.html | g_op | 3 | Oportunidade, Convite e acesso, Prazo, Situação, Abrir |
| PT-01.dc.html | g_av | 4 | Aviso, Registro, Abrir |
| PT-02.dc.html | g_cot | 3 | Cotação, Itens e volume, Responder até, Proposta e situação, Abrir |
| PT-02det.dc.html | g_dos | 4 | Campo, Valor, Fonte |
| PT-02det.dc.html | g_it | 4 | Item, Quantidade [num], Preço (R$/kg) [num], Total [num] |
| PT-02det.dc.html | g_cd | 1 | Frete, Pagamento, Prazo de entrega [num], Validade [date], Observações |
| PT-02det.dc.html | g_esc | 2 | Pergunta, De · quando, Resposta, Situação |
| PT-03.dc.html | g_of | 3 | Oferta, Produto e padrão, Volume e janela, Preço, condição e local, Validade, Situação, Ação |
| PT-03.dc.html | g_rv | 1 | Reserva, Tipo, Quantidade [num], Vencimento, Estado, Efeito |
| PT-03.dc.html | g_pp | 1 | Volume [num], Janela de entrega, Preço proposto [num], Local de entrega, Observações |
| PT-04.dc.html | g_ds | 2 | Dossiê, Finalidade e blocos concedidos, Vigência do acesso, Situação, Abrir |
| PT-04.dc.html | g_hist | 3 | Quando, Usuário, Bloco acessado, Finalidade |
| PT-04det.dc.html | g_con | 4 | Campo, Valor |
| PT-04det.dc.html | g_blk | 4 | Bloco, Conteúdo, Fonte, Validade, Situação |
| PT-05.dc.html | g_ng | 3 | Negócio, Resultado, Condição aceita, Pedido e documento, Entrega, Abrir |
| PT-05.dc.html | g_msg | 3 | Negócio, De · quando, Mensagem |
| PT-05det.dc.html | g_cond | 4 | Campo, Valor |
| PT-05det.dc.html | g_cg | 3 | Carga, Quantidade [num], Data prevista [date], Placa, Documento, Situação |
| PT-05det.dc.html | g_dc | 3 | Documento, Carga, Prazo, Situação |
| PT-06.dc.html | g_fu | 4 | Etapa, Quantidade [num], Valor [num], Conversão da etapa |
| PT-06.dc.html | g_co | 2 | Categoria · região, Convites [num], Ganhos [num], Receita própria [num], Cobertura, Ação |
| PT-06.dc.html | g_ag | 2 | Indicador agregado, Sua posição, Amostra, Situação |
| PT-07.dc.html | g_emp | 1 | Empresa · CNPJ, Categorias, Regiões, Culturas atendidas, E-mail de cotação, WhatsApp, Situação |
| PT-07.dc.html | g_pref | 4 | Aviso, Canal |
| PT-07.dc.html | g_us | 3 | Usuário, E-mail, Papel, Situação, Ação |
| PT-07.dc.html | g_pl | 3 | Item, Condição, Vigência, Situação |
| SAF.dc.html | g_saf | 4 | Safra, Fazenda, Cultivos [num], Área [num], Estado, Próximo passo |
| SAF.dc.html | g_cult_S2627 | 10 | Talhão ou parcela, Cultura, Variedade, Área [num], Plantio [num], Meta, Plano e ajustes |
| SAF.dc.html | g_cult_S27SF | 4 | Talhão ou parcela, Cultura, Variedade, Área [num], Plantio [num], Meta, Plano e ajustes |
| SAF.dc.html | g_cult_S2526 | 3 | Talhão ou parcela, Cultura, Variedade, Área [num], Plantio [num], Meta, Plano e ajustes |
| SAF.dc.html | g_cult_LG2627 | 23 | Talhão ou parcela, Cultura, Variedade, Área [num], Plantio [num], Meta, Plano e ajustes |
| SAF.dc.html | g_cult_NOVA | 0 | Talhão ou parcela, Cultura, Variedade, Área [num], Plantio [num], Meta, Plano e ajustes |
| SAF.dc.html | g_rend_S2627 | 55 | Operação, Atividade, Conjunto, Rendimento (ha/h) [num], Custo (R$/h) [num], Custo (R$/ha) [num], Custo (R$/kg), Modo, Largura (m) [num], Velocidade (km/h) [num], Eficiência (%) [num], Parte da área (%) [num], Trabalha, Janela (h por talhão) [num], Planos |
| SAF.dc.html | g_rend_S27SF | 53 | Operação, Atividade, Conjunto, Rendimento (ha/h) [num], Custo (R$/h) [num], Custo (R$/ha) [num], Custo (R$/kg), Modo, Largura (m) [num], Velocidade (km/h) [num], Eficiência (%) [num], Parte da área (%) [num], Trabalha, Janela (h por talhão) [num], Planos |
| SAF.dc.html | g_rend_S2526 | 53 | Operação, Atividade, Conjunto, Rendimento (ha/h) [num], Custo (R$/h) [num], Custo (R$/ha) [num], Custo (R$/kg), Modo, Largura (m) [num], Velocidade (km/h) [num], Eficiência (%) [num], Parte da área (%) [num], Trabalha, Janela (h por talhão) [num], Planos |
| SAF.dc.html | g_rend_LG2627 | 53 | Operação, Atividade, Conjunto, Rendimento (ha/h) [num], Custo (R$/h) [num], Custo (R$/ha) [num], Custo (R$/kg), Modo, Largura (m) [num], Velocidade (km/h) [num], Eficiência (%) [num], Parte da área (%) [num], Trabalha, Janela (h por talhão) [num], Planos |
| SAF.dc.html | g_rend_NOVA | 53 | Operação, Atividade, Conjunto, Rendimento (ha/h) [num], Custo (R$/h) [num], Custo (R$/ha) [num], Custo (R$/kg), Modo, Largura (m) [num], Velocidade (km/h) [num], Eficiência (%) [num], Parte da área (%) [num], Trabalha, Janela (h por talhão) [num], Planos |
| SAF.dc.html | g_op | 0 | Operação · atividade · cultivo · conjunto, Gatilho · data, Mês, Área (ha) [num], Horas-conjunto (h) [num], Decorrido (h) [num], Operação (R$) [num], Insumos (R$) [num], Total (R$) [num], R$/ha [num], Diesel (L) [num] |
| SAF.dc.html | g_mat | 0 | Indicador, set/26 [num], out/26 [num], nov/26 [num], dez/26 [num], jan/27 [num], fev/27 [num], mar/27 [num], abr/27 [num], mai/27 [num], jun/27 [num], jul/27 [num], ago/27 [num], Total do período [num] |
| SAF.dc.html | g_recp_maq | 5 | Recurso, Unidades [num], Jornada (h/dia) [num], Turnos [num], Disponibilidade (%) [num], Necessárias no pico [num], Mês do pico |
| SAF.dc.html | g_recp_pes | 1 | Recurso, Pessoas [num], Jornada (h/dia) [num], Absenteísmo (%) [num], Necessárias no pico [num], Mês do pico |
| SAF.dc.html | g_res | 0 | Recurso · indicador, set/26 [num], out/26 [num], nov/26 [num], dez/26 [num], jan/27 [num], fev/27 [num], mar/27 [num], abr/27 [num], mai/27 [num], jun/27 [num], jul/27 [num], ago/27 [num], Total [num] |
| SAF.dc.html | g_resd | 0 | Atividade, set/26 [num], out/26 [num], nov/26 [num], dez/26 [num], jan/27 [num], fev/27 [num], mar/27 [num], abr/27 [num], mai/27 [num], jun/27 [num], jul/27 [num], ago/27 [num], Total (h) [num] |
| SAF.dc.html | g_dem | 0 | Grupo · insumo, 1º uso [num], Demanda bruta [num], Estoque apto [num], Recebimentos previstos [num], Necessidade líquida [num], Preço (R$/un) [num], Valor (R$) [num], Situação |
| SU-01.dc.html | g_nec | 72 | Item · origem, Falta firme [num], Pedir até · necessária [date], Demanda [num], Disponível [num], Receb. firmes [num], Próxima ação |
| SU-02.dc.html | g_pol | 6 | Item/grupo · depósito, ABC · criticidade, Método, Segurança · prazo, Lote/múltiplo, Validade, Limite econômico [num], Versão · estado |
| SU-03.dc.html | g_sal | 12 | Item · lote, Local, Físico [num], Retido, Utilizável [num], Reservado [num], Disponível [num], Custódia [num], Valor [num] |
| SU-03det.dc.html | g_lot | 5 | Medida, Quantidade [num], Situação |
| SU-04.dc.html | g_cot | 8 | Cotação · origem, Itens, Fornecedores, Respostas [num], Melhor custo equalizado [num], Estado |
| SU-04.dc.html | g_cmp | 3 | Fornecedor, Mercadoria [num], Frete [num], Prazo de entrega [num], Condição, Custo comparável [num], Situação |
| SU-05.dc.html | g_ctr | 3 | Contraparte · contrato, Item · unidade, Contratado [num], Tolerância (versão aceita), Preço · condição [num], Exposição · limite [num], Estado |
| SU-05.dc.html | g_ped | 5 | Pedido · fornecedor, Item, Quantidade [num], Recebido [num], A entregar [num], Chegada prevista [date], Uso previsto, Depósito, Estado |
| SU-05.dc.html | g_car | 6 | Carga · contrato/pedido, Item, Quantidade, Chegada, Uso previsto (cobertura), Depósito, Exposição projetada [num], Estado |
| SU-05.dc.html | g_itm | 3 | Item, Contratado, Recebido, Liberado pendente, Proposto, Estado |
| SU-05.dc.html | g_dep | 3 | Depósito, Capacidade, Ocupação na chegada, Exposição projetada, Limite, Estado |
| SU-05.dc.html | g_mes | 3 | Mês, Cargas, Quantidade, Exposição de pico, Estado |
| SU-05det.dc.html | g_sal | 7 | Medida, Valor, Fonte |
| SU-05det.dc.html | g_lib | 3 | Liberação · carga, Quantidade, Chegada prevista, Cobertura atendida, Exposição projetada [num], Estado |
| SU-06.dc.html | g_rec | 5 | Documento · pedido, Item · lote, Conferido [num], Apto · retido [num], Inspeção · divergência, Físico · título · ação |
| SU-07.dc.html | g_req | 7 | Requisição · O.S., Item · lote, Solicitado [num], Entregue [num], Consumido [num], Em custódia [num], Estado · próxima ação |
| SU-07det.dc.html | g_bal | 5 | Medida, Quantidade [num], Situação |
| SU-08.dc.html | g_mov | 10 | Documento · data, Movimento · motivo, Origem → destino, Item · lote, Quantidade [num], Estado |
| SU-09.dc.html | g_inv | 4 | Inventário · escopo, Corte · contador [date], Observado × sistema · recontagem, Diferença · causa, Estado · ação |
| VE-01.dc.html | g_bal | 5 | Produto · classe, Janela, Demanda, Oferta, Falta ou excesso, Próximo passo |
| VE-01.dc.html | g_res | 3 | Reserva, Tipo, Quantidade, Vencimento, Estado, Efeito no saldo |
| VE-02.dc.html | g_pr | 7 | Instrumento, Fonte · licença, Praça, Unidade, Moeda, Vencimento/data, Preço/basis, Atraso |
| VE-02.dc.html | g_al | 2 | Instrumento, Condição, Limite [num], Avisar por, Validade [date], Estado |
| VE-03.dc.html | g_of | 5 | Oferta, Volume, Janela, Destino · clientes, Preço · condição, Estado · validade, Ação |
| VE-03.dc.html | g_cmp | 2 | Proposta, Cliente, Preço, Frete por conta, Prazo, Líquido/kg, Diferença |
| VE-04.dc.html | g_cart | 9 | Pedido, Cliente, Item · classe, Quantidade · janela, Preço · condição, Alocação · estado, Ação |
| VE-04det.dc.html | g_ver | 1 | Versão, Quantidade, Preço · medição, Janela, Frete, Vencimento, Motivo, Estado |
| VE-04det.dc.html | g_at | 3 | Origem, Tipo de alocação, Quantidade, Estado, Rastreio |
| VE-04det.dc.html | g_fin | 2 | Evento, Base, Valor previsto, Vencimento, Estado |
| VE-05.dc.html | g_ob | 5 | Obrigação · contraparte, Produto · janela, Volume [num], Condições · vínculo, Estado, Ação |
| VE-05.dc.html | g_dim | 3 | Dimensão, Volume [num], % da previsão V2, Composição |
| VE-06.dc.html | g_rc | 5 | Caso, Pedido · entrega, Motivo · evidências, Lote · quantidade, Decisão · financeiro, Ação |

## Tabelas manuais (role=table fora do G2)

| Página | Tabelas |
|---|---|
| AG-07.dc.html | 5 |
| OS.dc.html | 1 |
