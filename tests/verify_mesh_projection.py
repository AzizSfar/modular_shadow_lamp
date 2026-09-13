"""Project opaque STL triangles independently, then compare with SCAD's footprint.

This is a geometric visibility test, not a lighting/brightness simulation.
Pillow and NumPy are used only to rasterize and compare the test images.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import read_stl, read_flat_svg, find_openscad, run_scad, mesh_report

ROOT=Path(__file__).resolve().parents[1]
N=2000
EXTENT=180
SOURCE=(0,0,24)

def clip(poly,axis,bound,keep_lower):
    if not poly:
        return []
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia=a[axis]<=bound if keep_lower else a[axis]>=bound
        ib=b[axis]<=bound if keep_lower else b[axis]>=bound
        if ia:
            out.append(a)
        if ia != ib:
            t=(bound-a[axis])/(b[axis]-a[axis])
            out.append(tuple(a[j]+t*(b[j]-a[j]) for j in range(len(a))))
    return out

def pixels(poly):
    return [((p[0]+EXTENT)*N/(2*EXTENT),(EXTENT-p[1])*N/(2*EXTENT)) for p in poly]

def shadow_mask(triangles,source=None):
    if source is None:
        source=SOURCE
    result=Image.new('1',(N,N))
    draw=ImageDraw.Draw(result)
    for tri in triangles:
        poly=clip(list(tri),2,source[2]-1e-5,True)
        if len(poly)<3:
            continue
        poly=[(source[0]+source[2]*(p[0]-source[0])/(source[2]-p[2]),
               source[1]+source[2]*(p[1]-source[1])/(source[2]-p[2])) for p in poly]
        for axis in (0,1):
            poly=clip(poly,axis,EXTENT,True)
            poly=clip(poly,axis,-EXTENT,False)
        if len(poly)>=3:
            draw.polygon(pixels(poly),fill=255)
    return result

def mask_from_svg(path):
    result=Image.new('1',(N,N))
    for group in read_flat_svg(path):
        combined=Image.new('1',(N,N))
        for contour in group:
            one=Image.new('1',(N,N))
            ImageDraw.Draw(one).polygon(pixels(contour),fill=255)
            combined=ImageChops.logical_xor(combined,one)
        result=ImageChops.logical_or(result,combined)
    return result

def display_mask(mask,path):
    rgb=Image.new('RGB',(N,N),(14,19,27))
    rgb.paste((255,210,117),(0,0,N,N),mask.convert('L'))
    draw=ImageDraw.Draw(rgb)
    a,b=pixels([(-50,50),(50,-50)])
    draw.ellipse([a,b],fill=(45,56,70),outline=(91,109,130),width=2)
    rgb.save(path)

def main():
    global EXTENT,SOURCE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'modular_shadow_lamp.scad')
    parser.add_argument('--body',type=Path,default=ROOT/'output'/'demo_body.stl')
    parser.add_argument('--cover',type=Path,default=ROOT/'output'/'demo_cover.stl')
    parser.add_argument('--source-height',type=float,default=24)
    parser.add_argument('--extent',type=float,default=180)
    parser.add_argument('--prefix',default='')
    args=parser.parse_args()
    EXTENT=args.extent
    SOURCE=(0,0,args.source_height)
    exe=find_openscad()
    source=args.source.read_text().split('\nif(Output=="Cover")')[0]
    expected_scad=ROOT/'tests'/(args.prefix+'expected_projection.scad')
    expected_scad.write_text(source+'\nprojected_light();\n')
    svg=ROOT/'output'/(args.prefix+'expected_projection.svg')
    run_scad(exe,expected_scad,svg)
    actual=ImageChops.invert(shadow_mask(read_stl(args.body)))
    # The lamp physically covers the wall inside its outer radius.
    ImageDraw.Draw(actual).ellipse(pixels([(-50,50),(50,-50)]),fill=0)
    expected=mask_from_svg(svg)
    a,e=np.asarray(actual,dtype=bool),np.asarray(expected,dtype=bool)
    iou=np.count_nonzero(a&e)/max(1,np.count_nonzero(a|e))
    report={"method":"Perspective projection of opaque STL triangles versus independently exported analytic footprint",
            "source_xyz_mm":SOURCE,"wall_extent_mm":2*EXTENT,"pixels":N,
            "intersection_over_union":iou,"disagreement_percent_of_wall":100*np.count_nonzero(a^e)/a.size,
            "body":mesh_report(args.body),"cover":mesh_report(args.cover)}
    (ROOT/'output'/(args.prefix+'validation.json')).write_text(json.dumps(report,indent=2))
    display_mask(actual,ROOT/'output'/(args.prefix+'mesh_verified_projection.png'))
    display_mask(expected,ROOT/'output'/(args.prefix+'analytic_projection.png'))
    print(json.dumps(report,indent=2))
    assert iou>0.97, 'Actual mesh projection differs materially from the analytic preview'
    for part in ('body','cover'):
        assert report[part]['surface_components']==1
        assert report[part]['closed_two_manifold_edges']

if __name__=='__main__':
    main()
