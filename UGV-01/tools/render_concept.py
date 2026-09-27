"""Render the actual generated CAD solids for engineering inspection."""
from pathlib import Path
import json
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

root=Path(__file__).resolve().parents[1]
m=json.loads((root/'cad/assembly/manifest.json').read_text())
fig=plt.figure(figsize=(16,8),facecolor='#f5f6f4')
axes=[fig.add_subplot(121,projection='3d'),fig.add_subplot(122,projection='3d')]
for p in m['parts']:
    shape=cq.importers.importStep(str(root/p['step'])).val()
    verts,tris=shape.tessellate(0.4,0.2)
    polygons=[[(verts[i].x,verts[i].y,verts[i].z) for i in t] for t in tris]
    for j,ax in enumerate(axes):
        if j==1 and (p['name'].startswith(('UGV-MECH-013','UGV-MECH-018')) or p['name'] in ['UGV-MECH-010--1','UGV-MECH-011--1','UGV-MECH-012--1','UGV-MECH-022-+1']
                     or p['name'] in m['arm_chain']['links']):
            continue
        ax.add_collection3d(Poly3DCollection(polygons,facecolor=p['color'],edgecolor='#30362f',linewidth=0.09,alpha=1))
# M3: the right arm in two working poses (manifest arm_chain: back from stow to zero, then forward to the pose).
chain,G=m['arm_chain'],m['parameters']['geometry']
stow=G['arm']['poses_deg']['stow']
def posed(shape,link,q):
    for j in range(link+1):  # inverse of the stow pose, root first
        o,d,sg=chain['joints'][j]['origin'],chain['joints'][j]['axis'],chain['joints'][j]['sign']
        if stow[j]: shape=shape.rotate(cq.Vector(*o),cq.Vector(*o)+cq.Vector(*d),-sg*stow[j])
    for j in range(link,-1,-1):  # forward to q, tip first
        o,d,sg=chain['joints'][j]['origin'],chain['joints'][j]['axis'],chain['joints'][j]['sign']
        if q[j]: shape=shape.rotate(cq.Vector(*o),cq.Vector(*o)+cq.Vector(*d),sg*q[j])
    return shape
for pose,colour in (('reach_low','#d9a441'),('reach_center','#6fa8dc')):
    for name,link in chain['links'].items():
        shape=posed(cq.importers.importStep(str(root/f'cad/assembly/generated/{name}.step')).val(),link,G['arm']['poses_deg'][pose])
        verts,tris=shape.tessellate(0.4,0.2)
        axes[1].add_collection3d(Poly3DCollection([[(verts[i].x,verts[i].y,verts[i].z) for i in t] for t in tris],
                                                  facecolor=colour,edgecolor='#735131',linewidth=0.05,alpha=0.4))
for ax,title in zip(axes,['Montaj görünümü (kollar park, çamurlukta)','Kapaklar, sağ yan ve ön duvar gizli; sağ kol "yere" (sarı) ve "öne-orta" (mavi)']):
    ax.set(xlim=(-180,320),ylim=(-180,180),zlim=(0,380),xlabel='x ileri / mm',ylabel='y sol / mm',zlabel='z / mm')
    ax.set_box_aspect((500,360,380));ax.view_init(elev=22,azim=-35)
    ax.set_facecolor('#f5f6f4');ax.set_title(title,fontsize=13,pad=15)
fig.suptitle(f"UGV-01 • {m['parameters']['revision']} Lite, M3 karakter gövdesi ve 5 eksenli kol",fontsize=21,fontweight='bold',x=0.06,ha='left')
fig.text(0.06,0.91,f"{G['overall_length_mm']} × {G['overall_width_mm']} mm dış ölçü  |  gövde üstü {G['body_top_z_mm']} mm  |  "
         f"eğim ekseni gövdenin {G['tilt_axis_z_mm']-G['body_top_z_mm']} mm üstünde  |  Ø{G['wheel_diameter_mm']} mm teker  |  iz {G['track_mm']} mm",fontsize=12,color='#475047')
fig.text(0.06,0.055,'Turuncu: 3S batarya   Mavi: ESP32-S3 + sürücüler   Kırmızı: E-stop   Gri: JGA25 motor / servo / baskı şasi   Sarı: teker göbeği   Siyah: TPU lastik ve tampon   Açık mavi: ışık şeridi',fontsize=10)
fig.text(0.06,0.025,'Pan/tilt boyun, iki ESP32-CAM göz, yan duvardan çıkan 5 eksenli sağ kol, pasif sol kol, çamurluklar, kargo ağzı, ön tamponda iki ToF. Vida, korna ve kablolar modellenmedi. Üretim dosyası değildir.',fontsize=10,color='#735131')
fig.subplots_adjust(left=0.02,right=0.98,top=0.85,bottom=0.12,wspace=0.04)
fig.savefig(root/'cad/assembly/concept_preview.png',dpi=125)
print('Rendered concept_preview.png from STEP solids')
