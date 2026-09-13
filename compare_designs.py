"""Bounded optical design study using the actual filled SVG area (NumPy/Pillow).

Candidates are estimates, never mesh or printer certificates. The search counts
the electronics standoff in total depth, and separates image size from visibility.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from prepare_svg import ROOT, find_openscad, run_scad, read_flat_svg, embedded_module


def artwork_mask(groups, n=700):
    vertices = [p for g in groups for c in g for p in c]
    lo = np.min(vertices, axis=0)
    hi = np.max(vertices, axis=0)
    center = (lo+hi)/2
    span = max(hi-lo)
    result = Image.new('1', (n,n))
    for group in groups:
        part = Image.new('1', (n,n))
        for contour in group:
            layer = Image.new('1', (n,n))
            pts = [((x-center[0])/span*(n-2)+(n-1)/2,
                    -(y-center[1])/span*(n-2)+(n-1)/2) for x,y in contour]
            ImageDraw.Draw(layer).polygon(pts, fill=1)
            part = ImageChops.logical_xor(part, layer)
        result = ImageChops.logical_or(result,part)
    return result


def evaluate(shape, width, depth, height, standoff, length, radius, points,
             detail_percent=2, emitter=0.2, max_blur=2, shadow_x=0, shadow_y=0):
    # Defaults of modular_shadow_lamp.scad; no manual source or stacked modules.
    offset=math.hypot(shadow_x,shadow_y)
    r = radius*length+offset
    ri = min(width,depth)/2-2
    rf = min(width,depth)/2-4
    h = min(standoff+height-6,
            (standoff+height-7.5)/(1-rf/r) if r>rf else standoff+height-6,
            3*(offset+length/2-0.42)/4)
    scale = h*ri/(r*math.sqrt(r*r+h*h)) if shape=='Rectangle' else min(ri/r,h*ri/r**2)
    cut = length*detail_percent/100*scale
    blur = max(0,r/ri-1)*emitter
    if h-standoff-3<=5.5 or h<=standoff+6.5 or cut<0.4 or blur>max_blur:
        return None
    xy = points*length+np.array([shadow_x,shadow_y])
    rho = np.hypot(xy[:,0],xy[:,1])
    if shape=='Rectangle':
        rout = np.minimum(width/2/np.maximum(np.abs(xy[:,0])/np.maximum(rho,1e-9),1e-9),
                          depth/2/np.maximum(np.abs(xy[:,1])/np.maximum(rho,1e-9),1e-9))
    else:
        rout = width/2
    visible = (rho>rout*h/(h-standoff-5.5)) & (rho>4*h/3)
    retained = float(np.mean(visible))
    return dict(shape=shape,width_mm=width,depth_mm=depth,height_mm=height,
                standoff_mm=standoff,total_depth_mm=height+standoff,length_mm=length,
                shadow_x_mm=shadow_x,shadow_y_mm=shadow_y,
                source_height_mm=round(h,4),declared_cut_mm=round(cut,4),blur_mm=round(blur,4),
                visible_artwork_percent=round(retained*100,2),
                score=length/(height+standoff)/math.sqrt(width*depth)*retained)


def study(svg, output, detail_percent=2, emitter=0.2, minimum_visible=85):
    output.mkdir(parents=True,exist_ok=True)
    importer=output/(svg.stem+'_import.scad')
    importer.write_text('import('+json.dumps(svg.resolve().as_posix())+',center=true,$fn=180);')
    flat=importer.with_suffix('.svg')
    run_scad(find_openscad(),importer,flat)
    groups=read_flat_svg(flat)
    _,radius,_,_=embedded_module(groups)
    mask=artwork_mask(groups)
    y,x=np.nonzero(np.asarray(mask))
    points=np.column_stack(((x-(mask.width-1)/2)/(mask.width-2),
                            -(y-(mask.width-1)/2)/(mask.width-2)))
    # Deterministic coverage sample bounds runtime; final previews use all pixels.
    sample=points[::max(1,len(points)//5000)]
    candidates=[]
    for shape,w,d in [('Cylinder',s,s) for s in (60,80,100)]+[
            ('Rectangle',w,d) for w,d in ((60,60),(60,80),(80,60),(80,80),(80,100),(100,80))]:
        for height in (22,26,30,36,44,60):
            for stand in (0,10,20,30):
                for length in (300,450,600,800):
                    for x,y in ((0,0),(0,-0.25),(0,0.25),(-0.25,0),(0.25,0)):
                        row=evaluate(shape,w,d,height,stand,length,radius,sample,detail_percent,emitter,
                                     shadow_x=x*length,shadow_y=y*length)
                        if row:
                            candidates.append(row)
    candidates.sort(key=lambda row:row['score'],reverse=True)
    with (output/(svg.stem+'_candidates.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(candidates[0]) if candidates else ['score'])
        writer.writeheader(); writer.writerows(candidates)
    accepted=[r for r in candidates if r['visible_artwork_percent']>=minimum_visible]
    best={shape:next((r for r in accepted if r['shape']==shape),None) for shape in ('Cylinder','Rectangle')}
    report=dict(artwork=svg.name,detail_percent=detail_percent,emitter_diameter_mm=emitter,
                minimum_visible_percent=minimum_visible,ranked_by='length / total depth / sqrt(footprint area) * visible fraction',
                scope='216 housing configurations x 4 lengths x 5 XY placements; light shapes, no bridges or web simplification',
                warning='Declared detail is not measured SVG detail. Retained area does not measure semantic fidelity. Rerun mesh preflight.',
                passing_optical_candidates=len(candidates),passing_visible_candidates=len(accepted),best=best,
                best_visibility=sorted(candidates,key=lambda r:r['visible_artwork_percent'],reverse=True)[:4])
    (output/(svg.stem+'_study.json')).write_text(json.dumps(report,indent=2))
    canvas=Image.new('RGB',(780,810),(16,22,30))
    draw=ImageDraw.Draw(canvas)
    draw.text((24,16),svg.name+' | original filled artwork',fill='white')
    colored=Image.new('RGB',mask.size,(16,22,30)); colored.paste((255,210,117),(0,0,*mask.size),mask.convert('L'))
    canvas.paste(colored,(40,60)); canvas.save(output/(svg.stem+'_original.png'))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg',type=Path,nargs='+')
    parser.add_argument('--output',type=Path,default=ROOT/'output'/'reference_study')
    parser.add_argument('--detail-percent',type=float,default=2)
    parser.add_argument('--emitter-diameter',type=float,default=0.2)
    parser.add_argument('--minimum-visible',type=float,default=85)
    args=parser.parse_args()
    for svg in args.svg:
        print(json.dumps(study(svg,args.output,args.detail_percent,args.emitter_diameter,args.minimum_visible),indent=2))
