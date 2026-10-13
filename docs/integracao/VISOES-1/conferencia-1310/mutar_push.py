import sys
p=sys.argv[1]; s=open(p).read()
a="try{ history.replaceState(history.state,'',g2visaoUrl(location.pathname,location.search,location.hash,k)); }catch(e){}"
assert s.count(a)==1, s.count(a)
open(p,'w').write(s.replace(a,a.replace('replaceState','pushState')))
print('mutante pushState aplicado em', p)
