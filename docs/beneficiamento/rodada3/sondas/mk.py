# gera <lado>_motor.js com o motor do lado (o mesmo do ben_unit_test.motor()); lado = caminho do gen37
import os, sys
os.environ['SAFRION_DADOS']='sintetico'
nome,D=sys.argv[1],sys.argv[2]; R=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,D); os.chdir(D)
import ben_unit_test as T
open(os.path.join(R,nome+'_motor.js'),'w',encoding='utf-8').write(T.motor())
print(nome,'ok')
