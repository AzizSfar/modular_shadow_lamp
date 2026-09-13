"""Filter fragile opaque slivers in millimetres on the developed inner shell.

Only used by prepare_svg --minimum-web. NumPy/Pillow are optional dependencies.
The raster is a preprocessing approximation; the final STL is still CGAL CSG
through a perspective cone, and is checked independently for connectivity.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from prepare_svg import embedded_module


def mask_in_wall(groups, extent, n=4096):
    result=Image.new('1',(n,n))
    for group in groups:
        part=Image.new('1',(n,n))
        for contour in group:
            layer=Image.new('1',(n,n))
            ImageDraw.Draw(layer).polygon([((x/extent+1)*(n-1)/2,(1-y/extent)*(n-1)/2)
                                           for x,y in contour],fill=1)
            part=ImageChops.logical_xor(part,layer)
        result=ImageChops.logical_or(result,part)
    return np.asarray(result)


def boundaries(mask):
    """Oriented pixel-union boundaries; resolve diagonal contact by right turn."""
    height,width=mask.shape
    padded=np.pad(mask,1)
    edges={}
    def add(x,y,a,b): edges.setdefault(a,[]).append(b)
    # Clockwise in image coordinates: filled cells stay to the right.
    for y,x in zip(*np.nonzero(mask & ~padded[:-2,1:-1])): add(x,y,(int(x),int(y)),(int(x+1),int(y)))
    for y,x in zip(*np.nonzero(mask & ~padded[1:-1,2:])): add(x,y,(int(x+1),int(y)),(int(x+1),int(y+1)))
    for y,x in zip(*np.nonzero(mask & ~padded[2:,1:-1])): add(x,y,(int(x+1),int(y+1)),(int(x),int(y+1)))
    for y,x in zip(*np.nonzero(mask & ~padded[1:-1,:-2])): add(x,y,(int(x),int(y+1)),(int(x),int(y)))
    loops=[]
    while edges:
        start=next(iter(edges)); point=start; previous=(start[0]-1,start[1]); loop=[]
        while True:
            loop.append(point)
            options=edges[point]
            dx,dy=point[0]-previous[0],point[1]-previous[1]
            # Right, straight, left, reverse. This separates point-only contacts.
            directions=[(-dy,dx),(dx,dy),(dy,-dx),(-dx,-dy)]
            next_point=min(options,key=lambda p:directions.index((p[0]-point[0],p[1]-point[1])))
            options.remove(next_point)
            if not options: del edges[point]
            previous,point=point,next_point
            if point==start: break
        if len(loop)>=4: loops.append(loop)
    return loops


def surface_repair(groups, shape, rx, ry, source_height, wall_offset, bottom, top, web, extent,
                   wall_thickness=2, minimum_cut=0.4):
    """Return wall-coordinate polygon paths and measured raster edits.

    Closing uses a square in developed millimetres, with wraparound at the seam.
    Only added light is exported. Original vector detail is retained everywhere
    else. Splitting into 16 sectors avoids a polar seam crossing in any polygon.
    """
    step=min(0.06,web/10)
    ix,iy=rx-wall_thickness,ry-wall_thickness
    perimeter=4*(ix+iy) if shape=='Rectangle' else 2*math.pi*ix
    ns=int(math.ceil(perimeter/step/16))*16
    nz=int(math.ceil((top-bottom)/step))
    ds,dz=perimeter/ns,(top-bottom)/nz
    # Use the finer of the two pitches to avoid undershooting the chosen width.
    kernel=int(math.ceil(web/min(ds,dz)))
    if kernel%2==0: kernel+=1
    margin=kernel+2
    def xy_at(s):
        if shape!='Rectangle': return ix*np.cos(s/ix),ix*np.sin(s/ix)
        s=np.mod(s,perimeter)
        # Clockwise perimeter starting at the lower left; each face unrolls flat.
        x=np.where(s<2*ix,-ix+s,np.where(s<2*ix+2*iy,ix,
             np.where(s<4*ix+2*iy,ix-(s-2*ix-2*iy),-ix)))
        y=np.where(s<2*ix,-iy,np.where(s<2*ix+2*iy,-iy+s-2*ix,
             np.where(s<4*ix+2*iy,iy,iy-(s-4*ix-2*iy))))
        return x,y
    sx,sy=xy_at((np.arange(ns)+0.5)*ds)
    z=bottom+(np.arange(nz)+0.5)*dz
    magnification=source_height/(source_height-wall_offset-z)
    x=magnification[:,None]*sx[None,:]; y=magnification[:,None]*sy[None,:]
    wall=mask_in_wall(groups,extent)
    px=np.rint((x/extent+1)*(wall.shape[1]-1)/2).astype(int)
    py=np.rint((1-y/extent)*(wall.shape[0]-1)/2).astype(int)
    inside=(px>=0)&(px<wall.shape[1])&(py>=0)&(py<wall.shape[0])
    light=np.zeros((nz,ns),dtype=bool)
    light[inside]=wall[py[inside],px[inside]]
    periodic=np.pad(light,((0,0),(margin,margin)),mode='wrap')
    padded=np.pad(periodic,((margin,margin),(0,0)),constant_values=False)
    image=Image.fromarray(padded.astype(np.uint8)*255)
    closed=np.asarray(image.filter(ImageFilter.MaxFilter(kernel)).filter(ImageFilter.MinFilter(kernel)))>0
    closed=closed[margin:-margin,margin:-margin]
    added=closed & ~light
    # One cell of overlap seats each correction into the exact vector boundary.
    # Without it, centre-sampled cells can leave detached sub-cell dark splinters.
    overlap=np.pad(added,((1,1),(1,1)),mode='wrap')
    overlap[0,:]=False; overlap[-1,:]=False
    added=np.asarray(Image.fromarray(overlap.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)))>0
    added=added[1:-1,1:-1]
    # Opening the LIGHT mask is an independent small-aperture diagnostic. Do not
    # silently widen or delete these light strokes to make a printability claim.
    cut_kernel=int(math.ceil(minimum_cut/min(ds,dz)))
    if cut_kernel%2==0: cut_kernel+=1
    opened_light=np.asarray(image.filter(ImageFilter.MinFilter(cut_kernel)).filter(ImageFilter.MaxFilter(cut_kernel)))>0
    opened_light=opened_light[margin:-margin,margin:-margin]
    narrow_light=light & ~opened_light
    # Export ONLY the changed dark cells. Exporting the whole raster would put
    # stair steps along every original vector edge, even untouched light strokes.
    paths=[]
    sector=ns//16
    for start in range(0,ns,sector):
        part=added[:,start:start+sector]
        for loop in boundaries(part):
            points=[]
            # Keep grid edges: mapping straight developed edges into wall space
            # is nonlinear, so ordinary collinear simplification would be wrong.
            for u,v in loop:
                x0,y0=xy_at(np.array((start+u)*ds))
                zz=bottom+v*dz
                mag=source_height/(source_height-wall_offset-zz)
                points.append((float(x0*mag),float(y0*mag)))
            paths.append(points)
    return [paths],dict(method='Closing in developed inner-shell coordinates, union with original vector light',
                        shell_sample_pitch_mm=[ds,dz],kernel_cells=kernel,
                        changed_surface_cells=int(added.sum()),light_surface_cells=int(light.sum()),
                        aperture_screen_width_mm=minimum_cut,
                        light_area_in_small_features_percent=round(100*int(narrow_light.sum())/max(1,int(light.sum())),2),
                        approximation='Raster contours mapped back to the wall; narrow necks and overhangs still require slicer review')


def scad_module(groups):
    import json
    points=[]; paths=[]
    for group in groups:
        for contour in group:
            paths.append(list(range(len(points),len(points)+len(contour))))
            points.extend([[round(x,6),round(y,6)] for x,y in contour])
    if not points: return 'module embedded_print_light() {}'
    return 'module embedded_print_light() { polygon(points='+json.dumps(points,separators=(',',':'))+\
           ',paths='+json.dumps(paths,separators=(',',':'))+',convexity=40); }'
