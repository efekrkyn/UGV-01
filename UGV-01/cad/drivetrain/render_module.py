"""Render actual STEP solids: assembled and a physical longitudinal cutaway."""
import json
import sys
from pathlib import Path
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

root=Path(__file__).resolve().parents[2]
m=json.loads((root/'cad/drivetrain/manifest.json').read_text())
light='--lightweight' in sys.argv
fig=plt.figure(figsize=(16,8),facecolor='#f5f6f4')
axes=[fig.add_subplot(121,projection='3d'),fig.add_subplot(122,projection='3d')]
cut=cq.Workplane('XY').box(100,250,200).translate((50,80,60)).val()
for p in m['parts']:
    path=root/p['step']
    if light and p['name'] in ('UGV-MECH-042','UGV-MECH-046','UGV-MECH-047'):
        path=root/f'cad/drivetrain/generated/lightweight/{p["name"]}-B.step'
    shape=cq.importers.importStep(str(path)).val()
    for i,ax in enumerate(axes):
        s=shape if i==0 else shape.cut(cut)
        if s.Volume()<.001: continue
        verts,tris=s.tessellate(.3,.15)
        polygons=[[(verts[k].x,verts[k].y,verts[k].z) for k in t] for t in tris]
        ax.add_collection3d(Poly3DCollection(polygons,facecolor=p['color'],edgecolor='#30362f',linewidth=.08))
for ax,title in zip(axes,['Tam modül','x > 0 yarısı kesilmiş görünüm']):
    ax.set(xlim=(-65,65),ylim=(0,160),zlim=(0,125),xlabel='x / mm',ylabel='y dışa / mm',zlabel='z / mm')
    ax.set_box_aspect((130,160,125));ax.view_init(elev=23,azim=-35)
    ax.set_facecolor('#f5f6f4');ax.set_title(title,pad=16)
fig.suptitle('UGV-01 • '+('D2A hafif teker adayı' if light else 'D1 tahrik modülü'),fontsize=23,fontweight='bold',x=.05,ha='left')
fig.text(.05,.91,'Ø120 teker | 10 mm bağımsız mil | 2 × 6000 rulman | 6–10 mm Oldham kaplin',fontsize=12)
fig.text(.05,.05,'STEP katılarından üretildi. REF bileşenler tedarikçi zarflarıdır; bağlantı elemanları ve nihai toleranslar eksiktir.',fontsize=10)
fig.text(.05,.025,'TASARIM ADAYI — ÜRETİME GÖNDERMEYİN',fontsize=10,color='#944414')
fig.subplots_adjust(left=.03,right=.98,top=.85,bottom=.12,wspace=.04)
output=root/'cad/drivetrain'/('module_preview_D2A.png' if light else 'module_preview.png')
fig.savefig(output,dpi=140)
print('Rendered',output.name)
