"""Passos de conferência pela UI real; preserva o perfil anterior. Somente apoio de QA."""
import json,time
from app_lib import SETV

def conferir_dias(J,osid,dias):
    selector='[aria-label="Trocar perfil de demonstração"]'
    perfil=J(f'document.querySelector({json.dumps(selector)}).value')
    def setv(sel,val):
        J(f'({SETV})({json.dumps(sel)},{json.dumps(val)})');time.sleep(.2)
    setv(selector,'Paula')
    for dia in dias:
        J("[...document.querySelectorAll('aside[role=dialog] section[aria-label] > button[aria-expanded=\"false\"]')].forEach(b=>b.click())")
        fid='cd_'+osid+'_'+str(dia)
        assert J(f"(()=>{{const b=document.getElementById({json.dumps(fid+'_open')});if(!b)return false;b.click();return true}})()"),'Dia não oferece conferência'
        time.sleep(.2)
        setv('#'+fid+'_mot','Execução e evidências do dia conferidas por Paula')
        assert J("(()=>{const b=[...document.querySelectorAll('section[aria-label=\"Conferência diária\"] button')].find(b=>b.innerText==='Registrar conferência');if(!b)return false;b.click();return true})()"),'Ação de conferir indisponível'
        time.sleep(.3)
        rec=J(f"window.__cen.cenGet().ordens[{json.dumps(osid)}].ap.find(a=>a.dia==={dia}).conferenciaDia")
        assert rec and rec['estado']=='Conferido' and rec['por']=='Paula (conferência)' and rec['motivo'],'Conferência não confirmada'
    setv(selector,perfil)
