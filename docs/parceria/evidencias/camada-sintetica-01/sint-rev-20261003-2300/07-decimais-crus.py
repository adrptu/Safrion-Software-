import glob,re,collections
c=collections.Counter(); ex=[]
for f in sorted(glob.glob('project/*.dc.html')):
    t=open(f,encoding='utf-8').read()
    for m in re.finditer(r'(?<![\d.,\w])\d+\.\d+ ?ha\b',t):
        if not re.fullmatch(r'\d{1,3}(\.\d{3})+ ?ha',m.group(0)): c[f]+=1; ex.append((f,m.group(0)))
print('TOTAL',sum(c.values()),ex[:10])
