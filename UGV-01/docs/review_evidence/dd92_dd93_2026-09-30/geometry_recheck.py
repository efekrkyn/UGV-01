from pathlib import Path
import math,json,itertools
root=Path(__file__).resolve().parents[3]
src=(root/'cad/assembly/build_concept.py').read_text().split('\nARM_POSES=')[0]
a=src.index('def add(');b=src.index('\nW=G',a)
src=src[:a]+'''def add(name, shape, color, printable=False, role='interface_concept'):
    PARTS.append({'name':name,'shape':shape,'printable':printable,'role':role,'color':color})
\n'''+src[b:]
ns={'__file__':str(root/'cad/assembly/build_concept.py')};exec(compile(src,'cad_prefix','exec'),ns)
R=ns['RIGHT'];O=ns['OTHERS'];P=ns['POSES'];cq=ns['cq'];XG=ns['XG'];zs=ns['zs'];YA=ns['YA'];GP=ns['GP'];out={}
# fine jaw self-sweep beyond production5deg samples.
js=[(n,s) for n,s,l,_ in R if n in ns['JAW_PIVOT']]
fixed=[(n,s) for n,s,l,_ in R if l==4 and n not in ns['JAW_PIVOT']]
hits=[]
for k in range(241):
 ang=k/4;j=[(n,ns['jaw'](n,s,ang)) for n,s in js]
 pairs=[(a,b) for a in j for b in fixed]+[(a,b) for a,b in itertools.combinations(j,2) if ns['JAW_PIVOT'][a[0]][0]!=ns['JAW_PIVOT'][b[0]][0]]
 for (n1,s1),(n2,s2) in pairs:
  if ns['overlap'](s1.BoundingBox(),s2.BoundingBox()) and (v:=s1.intersect(s2).Volume())>.01:hits.append(dict(angle=ang,a=n1,b=n2,mm3=v))
 if k%40==0:print('JAW_PROGRESS',ang,flush=True)
out['jaw_self_0_25deg']={'samples':241,'hits':hits}
# The actual pad midpoint versus legacy grip_point.
mid=cq.Vertex.makeVertex(XG+21,-(YA-16.5),zs+GP/2)
out['grip_points']={}
for name,q in P.items():
 p=ns['posed'](mid,4,q,-1).toTuple();g=ns['grip_point'](q)
 out['grip_points'][name]={'pad_mid':p,'legacy_grip':g,'error_mm':math.dist(p,g)}
left={name:s for name,s,_,_ in ns['arm_zero'](1)}
out['left_twist_connection']={'adapter_present':'UGV-MECH-059' in left,'bearing_present':any('TWIST' in k for k in left),'A_B_gap_mm':left['UGV-MECH-050'].distance(left['UGV-MECH-051'])}
out['open_stow_hits']=ns['arm_hits'](P['stow'],alpha=60)
# Wall-only tolerance corners at all integer shoulder positions onpark→lift.
walls=[p for p in O if p['name'] in ('UGV-MECH-010--1','UGV-MECH-011--1','UGV-MECH-012--1')]
best=(99,None);low=[]
for shoulder in range(90,181):
 for es in itertools.product((-1,1),repeat=5):
  q=[shoulder+es[0],90+es[1],es[2],es[3],es[4]]
  for n,s,l,_ in R:
   if l<1:continue
   ps=ns['posed'](s,l,q,-1);bb=ps.BoundingBox()
   for p in walls:
    if ns['overlap'](bb,p['bb'],12) and (d:=ps.distance(p['shape']))<best[0]:best=(d,dict(q=q,error=es,shoulder=shoulder,pair=n+' / '+p['name']))
 if shoulder%10==0:print('WALL_PROGRESS',shoulder,best,flush=True)
out['transition_1deg_32corners']={'samples':91*32,'minimum':best}
print(json.dumps(out,indent=2),flush=True)
