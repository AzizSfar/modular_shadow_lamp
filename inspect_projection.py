"""Render a prepared model's footprint and verify it against its actual STL.

Requires NumPy/Pillow, as does tests/verify_mesh_projection.py. Works with either
housing, standoff mode and module index. Reports artwork loss separately from IoU.
"""
import argparse
import json
import hashlib
import re
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from prepare_svg import ROOT, run_scad, find_openscad, read_stl
sys.path.insert(0,str(ROOT/'tests'))
import verify_mesh_projection as projection


def inspect(source, resolution=1200):
    folder=source.parent/(source.stem+'_projection')
    folder.mkdir(exist_ok=True)
    prefix=source.read_text(encoding='utf-8').split('\nif(Output=="Cover")')[0]
    diagnostic=folder/'measure.scad'
    diagnostic.write_text(prefix+'\necho("INSPECT",[h,wall_offset,body_base,Rx,Ry,r_far]);\nsquare(1);',encoding='utf-8')
    log=run_scad(find_openscad(),diagnostic,folder/'measure.csg')
    h,wall_offset,body_base,rx,ry,r_far=map(float,re.search(r'"INSPECT", \[([^\]]+)\]',log).group(1).split(','))
    projection.N=resolution
    projection.EXTENT=r_far*1.08
    projection.SOURCE=(0,0,h)
    masks={}
    for name,call in [('original','raw_intended_light();'),('unrepaired','projected_light();'),
                      ('repaired','projected_light();')]:
        model=folder/(name+'.scad')
        model.write_text(prefix+'\n'+call,encoding='utf-8')
        definitions=[] if name!='unrepaired' else ['Minimum_web_width=0','Support_bridges=false']
        run_scad(find_openscad(),model,folder/(name+'.svg'),definitions)
        masks[name]=projection.mask_from_svg(folder/(name+'.svg'))
    body=source.with_suffix('.stl')
    metadata=json.loads(source.with_suffix('.json').read_text()) if source.with_suffix('.json').exists() else {}
    matching_mesh=metadata.get('mesh_source_sha256')==hashlib.sha256(source.read_bytes()).hexdigest()
    if body.exists() and (matching_mesh or not metadata.get('source_sha256')):
        triangles=[tuple((x,y,z+wall_offset-body_base) for x,y,z in t) for t in read_stl(body)]
        masks['mesh']=ImageChops.invert(projection.shadow_mask(triangles))
    arrays={name:np.asarray(mask,dtype=bool) for name,mask in masks.items()}
    a=arrays['original']; b=arrays['unrepaired']; e=arrays['repaired']
    report={'source':str(source),'source_height_mm':h,'pixels':resolution,
            'visible_before_repairs_percent':round(100*np.count_nonzero(a&b)/max(1,a.sum()),2),
            'original_artwork_retained_percent':round(100*np.count_nonzero(a&e)/max(1,a.sum()),2),
            'visible_light_removed_by_repairs_percent':round(100*np.count_nonzero(b&~e)/max(1,b.sum()),2),
            'extra_light_percent_of_original_visible':round(100*np.count_nonzero(e&~b)/max(1,b.sum()),2),
            'shadow_fidelity_iou':float(np.count_nonzero(b&e)/max(1,np.count_nonzero(b|e)))}
    if 'mesh' in arrays:
        m=arrays['mesh']
        report['mesh_projection_iou']=float(np.count_nonzero(m&e)/max(1,np.count_nonzero(m|e)))
    thumbs=[]
    titles={'original':'Original SVG','unrepaired':'Housing obstruction only',
            'repaired':'Thin-web simplification + supports','mesh':'Independent STL projection'}
    for name,mask in masks.items():
        rgb=Image.new('RGB',mask.size,(16,22,30))
        rgb.paste((255,210,117),(0,0,*mask.size),mask.convert('L'))
        rgb.save(folder/(name+'.png'))
        thumb=Image.new('RGB',(520,565),(16,22,30))
        thumb.paste(rgb.resize((500,500)),(10,45))
        ImageDraw.Draw(thumb).text((15,16),titles[name],fill='white')
        thumbs.append(thumb)
    sheet=Image.new('RGB',(1040,565*((len(thumbs)+1)//2)),(16,22,30))
    for i,thumb in enumerate(thumbs): sheet.paste(thumb,((i%2)*520,(i//2)*565))
    sheet.save(folder/'comparison.png')
    (folder/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path,nargs='+')
    parser.add_argument('--resolution',type=int,default=1200)
    args=parser.parse_args()
    for source in args.source: inspect(source.resolve(),args.resolution)
