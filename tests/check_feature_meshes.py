"""Inspect exported feature meshes for clear axial wire paths and aligned inlay."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import ROOT,read_stl,mesh_report

def vertical_hits(triangles,x,y):
    hits=[]
    for a,b,c in triangles:
        denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator)<1e-12:
            continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/denominator
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/denominator
        if u>=-1e-9 and v>=-1e-9 and u+v<=1+1e-9:
            hits.append(u*a[2]+v*b[2]+(1-u-v)*c[2])
    return sorted(set(round(z,4) for z in hits))

parts={name:ROOT/'output'/('features_demo'+suffix+'.stl') for name,suffix in
       [('body',''),('cover','_cover'),('base','_cover_base'),('artwork','_cover_artwork')]}
reports={name:mesh_report(path) for name,path in parts.items()}
body=read_stl(parts['body'])
cover=read_stl(parts['cover'])
assert vertical_hits(body,0,0)==[], 'Pillar bore is blocked'
assert vertical_hits(body,0.7,0.4)==[], 'Bore is not continuously open'
assert vertical_hits(body,2,0), 'No pillar wall beside the bore'
assert vertical_hits(cover,0,0)==[], 'Cover centre hole is blocked'
assert vertical_hits(cover,4,0), 'No cover material beside the centre hole'
assert abs(reports['artwork']['bounds_mm'][2][1]-0.6)<1e-4
total=reports['base']['signed_volume_mm3']+reports['artwork']['signed_volume_mm3']
assert abs(total-reports['cover']['signed_volume_mm3'])<0.02
assert all(r['closed_two_manifold_edges'] for r in reports.values())
(ROOT/'output'/'feature_mesh_checks.json').write_text(json.dumps({
    'pillar_bore_clear':True,'cover_hole_clear':True,'inlay_depth_mm':0.6,
    'base_plus_inlay_volume_matches_cover':True,'parts':reports},indent=2))
print('PASS: hollow pillar, clear cover hole, aligned 0.6 mm inlay, closed meshes.')
