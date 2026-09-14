#!/usr/bin/env python3
"""SVG -> standalone MakerWorld SCAD, with real OpenSCAD mesh preflight.

Python standard library only. Requires OpenSCAD (the bundled portable copy is
detected automatically). The geometry is interpreted by OpenSCAD itself so the
helper and final generator agree on SVG fill rules and supported SVG features.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import hashlib
import math
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def find_openscad(explicit=None):
    candidates = [explicit, shutil.which("openscad.com"), shutil.which("openscad")]
    candidates += list((ROOT / "tools").glob("**/openscad.com"))
    candidates += [r"C:\Program Files\OpenSCAD\openscad.com"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise RuntimeError("OpenSCAD was not found. Install it or pass --openscad PATH.")


def run_scad(exe, source, destination, definitions=()):
    pending=destination.with_name(destination.stem+'.pending'+destination.suffix)
    if pending.exists(): pending.unlink()
    args = [exe, "-o", str(pending)]
    if destination.suffix.lower()=='.stl':
        # ASCII's six significant figures can collapse nearby stencil vertices.
        args += ['--export-format','binstl']
    for definition in definitions:
        args += ["-D", definition]
    args.append(str(source))
    result = subprocess.run(args, capture_output=True, text=True, timeout=600)
    log = result.stdout + result.stderr
    destination.with_suffix(destination.suffix + ".log").write_text(log, encoding="utf-8")
    if result.returncode or "ERROR:" in log or not pending.exists():
        raise RuntimeError(f"OpenSCAD could not generate {destination.name}:\n{log}")
    pending.replace(destination)
    if destination.suffix.lower()=='.stl':
        removed=clean_stl(destination)
        if removed:
            log+=f'\nSTL numeric cleanup: removed {removed} collapsed triangles at 0.000001 mm vertex precision.\n'
            destination.with_suffix(destination.suffix+'.log').write_text(log,encoding='utf-8')
    return log


def read_flat_svg(path):
    """Read only M/L/Z polygon paths produced by OpenSCAD, never arbitrary SVG."""
    import xml.etree.ElementTree as ET
    groups = []
    for element in ET.parse(path).getroot().iter():
        if element.tag.split("}")[-1] != "path":
            continue
        data = element.get("d", "")
        # OpenSCAD's own SVG writer outputs straight absolute M/L commands.
        unexpected = re.sub(r"[MLZmlzEe\d.,+\-\s]", "", data)
        if unexpected:
            raise ValueError(f"Unexpected command in OpenSCAD SVG output: {unexpected}")
        tokens = re.findall(r"[MLZmlz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", data)
        contours, current, command, i = [], [], None, 0
        while i < len(tokens):
            token = tokens[i]
            if token in "MLZmlz":
                command = token
                i += 1
                if token in "Zz":
                    if current:
                        contours.append(current)
                        current = []
                    continue
                if token in "Mm" and current:
                    contours.append(current)
                    current = []
            else:
                if command not in ("M", "L") or i + 1 >= len(tokens):
                    raise ValueError("Unsupported polygon output from OpenSCAD")
                # SVG is Y down; OpenSCAD's model coordinates are Y up.
                current.append((float(tokens[i]), -float(tokens[i + 1])))
                i += 2
        if current:
            contours.append(current)
        contours = [c[:-1] if len(c)>1 and c[-1]==c[0] else c for c in contours]
        contours = [c for c in contours if len(c)>=3]
        if contours:
            groups.append(contours)
    if not groups:
        raise ValueError("SVG contains no OpenSCAD-supported filled geometry. Outline strokes/text first.")
    return groups


def artwork_normalisation(groups):
    """Centre and longest side of the whole artwork; every module must share these."""
    vertices = [p for g in groups for c in g for p in c]
    xmin, xmax = min(p[0] for p in vertices), max(p[0] for p in vertices)
    ymin, ymax = min(p[1] for p in vertices), max(p[1] for p in vertices)
    longest = max(xmax-xmin, ymax-ymin)
    if longest <= 0:
        raise ValueError("The SVG has zero extent")
    return (xmin+xmax)/2, (ymin+ymax)/2, longest


def contour_area(contour):
    return 0.5*sum(contour[i][0]*contour[(i+1) % len(contour)][1]
                   - contour[(i+1) % len(contour)][0]*contour[i][1]
                   for i in range(len(contour)))


def point_inside(point, contour):
    """Ray cast. The point comes off a contour vertex, never off an edge."""
    x, y = point
    inside = False
    for i in range(len(contour)):
        x1, y1 = contour[i]
        x2, y2 = contour[(i+1) % len(contour)]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
            inside = not inside
    return inside


def silhouette_contours(groups, longest):
    """Outermost contours only: the artwork with every hole filled in.

    OpenSCAD fills a path even-odd, so a contour sitting inside another one is a hole.
    Nesting depth is counted within its own group; a contour that ends up inside some
    other group is simply absorbed by the union, so cross-group nesting can be ignored.
    """
    kept = []
    for group in groups:
        for index, contour in enumerate(group):
            if abs(contour_area(contour)) < 1e-9*longest*longest:
                continue  # a degenerate sliver contributes nothing and upsets CGAL
            depth = sum(1 for other_index, other in enumerate(group)
                        if other_index != index and point_inside(contour[0], other))
            if depth == 0:
                kept.append(contour)
    if not kept:
        raise ValueError("The artwork has no outer contour to take a silhouette from")
    return kept


def outline_module(groups, name="embedded_artwork_outline"):
    cx, cy, longest = artwork_normalisation(groups)
    lines = [f"module {name}() {{", "    union() {"]
    for contour in silhouette_contours(groups, longest):
        points = [[round((x-cx)/longest, 9), round((y-cy)/longest, 9)] for x, y in contour]
        lines.append("        polygon(points="+json.dumps(points, separators=(",", ":"))
                     + ",convexity=30);")
    lines += ["    }", "}"]
    return "\n".join(lines)


def embedded_module(groups):
    vertices = [p for g in groups for c in g for p in c]
    xmin, xmax = min(p[0] for p in vertices), max(p[0] for p in vertices)
    ymin, ymax = min(p[1] for p in vertices), max(p[1] for p in vertices)
    longest = max(xmax-xmin, ymax-ymin)
    if longest <= 0:
        raise ValueError("The SVG has zero extent")
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
    radius = 0
    lines = ["module embedded_artwork() {", "    union() {"]
    for group in groups:
        points, paths = [], []
        for contour in group:
            paths.append(list(range(len(points), len(points)+len(contour))))
            for x,y in contour:
                q = [(x-cx)/longest, (y-cy)/longest]
                radius = max(radius, math.hypot(*q))
                points.append([round(q[0],9), round(q[1],9)])
        lines.append("        polygon(points="+json.dumps(points,separators=(",",":"))+",")
        lines.append("            paths="+json.dumps(paths,separators=(",",":"))+",convexity=30);")
    lines += ["    }", "}"]
    return "\n".join(lines), radius, (xmax-xmin, ymax-ymin), len(vertices)


def set_value(source, name, value):
    text = json.dumps(value, separators=(",",":"))
    source, count = re.subn(r"(?m)^"+re.escape(name)+r"\s*=\s*[^;]*;", name+" = "+text+";", source)
    if count != 1:
        raise ValueError(f"Expected one parameter {name}, found {count}")
    return source


def read_stl(path):
    raw = Path(path).read_bytes()
    if len(raw)>=84 and len(raw)==84+50*struct.unpack_from("<I",raw,80)[0]:
        return [tuple(tuple(struct.unpack_from("<3f",raw,84+50*i+12+12*j)) for j in range(3))
                for i in range(struct.unpack_from("<I",raw,80)[0])]
    numbers = re.findall(rb"vertex\s+([-+eE.\d]+)\s+([-+eE.\d]+)\s+([-+eE.\d]+)",raw)
    verts = [tuple(float(v) for v in p) for p in numbers]
    if not verts or len(verts)%3:
        raise ValueError("Invalid or empty STL")
    return [tuple(verts[i:i+3]) for i in range(0,len(verts),3)]


def triangle_area(triangle):
    a,b,c=triangle
    u=[b[i]-a[i] for i in range(3)]
    v=[c[i]-a[i] for i in range(3)]
    return math.sqrt(sum(x*x for x in (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])))/2


def clean_stl(path):
    """Weld export-roundoff coincidences; never remove finite stencil islands."""
    triangles=read_stl(path)
    vertices={}; result=[]
    for triangle in triangles:
        keys=[tuple(round(x,6) for x in p) for p in triangle]
        if len(set(keys))<3: continue
        result.append(tuple(vertices.setdefault(k,p) for k,p in zip(keys,triangle)))
    removed=len(triangles)-len(result)
    if not removed: return 0
    with Path(path).open('wb') as f:
        f.write(b'OpenSCAD; welded export coincidences at 1e-6 mm'.ljust(80,b'\0'))
        f.write(struct.pack('<I',len(result)))
        for a,b,c in result:
            u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]
            normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            norm=math.sqrt(sum(x*x for x in normal))
            normal=[x/norm for x in normal] if norm else [0,0,0]
            f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))
    return removed


def convex_hull(points):
    points=sorted(set(points))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]; upper=[]
    for p in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0: lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0: upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]


def mesh_report(path, source_height=None, body_wall_z=0, small_volume=0):
    triangles=read_stl(path)
    parents=list(range(len(triangles)))
    def root(i):
        while parents[i]!=i:
            parents[i]=parents[parents[i]]
            i=parents[i]
        return i
    edges=defaultdict(list)
    volume=0
    for index,(a,b,c) in enumerate(triangles):
        volume += (a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        keys=[tuple(round(x,6) for x in p) for p in (a,b,c)]
        for j in range(3):
            edges[tuple(sorted((keys[j],keys[(j+1)%3])))].append(index)
    for incident in edges.values():
        for i in incident[1:]:
            parents[root(i)]=root(incident[0])
    groups=defaultdict(list)
    for i in range(len(triangles)):
        groups[root(i)].append(i)
    # The printable base is the lowest component, even if an intricate floating
    # island happens to have more triangles than the base.
    components=sorted(groups.values(),key=lambda c:(min(p[2] for i in c for p in triangles[i]),-len(c)))
    # A point inside a large face supplies a reliable angle for a bridge to an island.
    extra_angles=[]
    bridge_segments=[]
    removed_polygons=[]
    for component in components[1:]:
        volume_component=abs(sum(
            a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
            for a,b,c in (triangles[i] for i in component))/6)
        if source_height is not None and volume_component<small_volume:
            points=[(source_height*x/(source_height-z-body_wall_z),source_height*y/(source_height-z-body_wall_z))
                    for i in component for x,y,z in triangles[i] if source_height-z-body_wall_z>0.01]
            hull=convex_hull(points)
            if len(hull)>=3:
                removed_polygons.append(hull)
                continue
        tri=max((triangles[i] for i in component),key=triangle_area)
        x,y=[sum(p[axis] for p in tri)/3 for axis in (0,1)]
        extra_angles.append(round(math.degrees(math.atan2(y,x))%360,5))
        # Attach below an island so its support grows continuously from the rear
        # collar. Stop inside it rather than crossing the full optical height.
        candidates=[triangles[i] for i in component if triangle_area(triangles[i])>1e-6]
        low=min(candidates,key=lambda t:sum(p[2] for p in t)/3)
        x,y,z=[sum(p[axis] for p in low)/3 for axis in (0,1,2)]
        bridge_segments.append([round(math.degrees(math.atan2(y,x))%360,5),round(z,5)])
    bounds=[[min(p[j] for t in triangles for p in t),max(p[j] for t in triangles for p in t)] for j in range(3)]
    return {"triangles":len(triangles),"surface_components":len(components),
            "edge_incidence_histogram":dict(Counter(len(v) for v in edges.values())),
            "closed_two_manifold_edges":all(len(v)==2 for v in edges.values()),
            "signed_volume_mm3":round(volume,3),"bounds_mm":bounds,
            "suggested_bridge_angles":extra_angles,"suggested_bridge_segments":bridge_segments,
            "suggested_removed_polygons":removed_polygons}


def prepare_surface(source, output, work, exe, width):
    """Interpret artwork with the same OpenSCAD code, then filter on the shell."""
    from stencil_surface import surface_repair, scad_module
    prefix=source.split('\nif(Output=="Cover")')[0]
    model=work/'surface_source.scad'
    model.write_text(prefix+'\necho("SURFACE",[Rx,Ry,h,wall_offset,aperture_bottom,aperture_top,r_far]);\nraw_intended_light();',encoding='utf-8')
    log=run_scad(exe,model,work/'surface_source.svg')
    rx,ry,h,wall_offset,bottom,top,rfar=map(float,re.search(r'"SURFACE", \[([^\]]+)\]',log).group(1).split(','))
    names=['Cylinder_diameter','Rectangle_width','Rectangle_depth','Cylinder_height',
           'Wall_standoff','Module_index','Shadow_length','Shadow_x','Shadow_y','Artwork_rotation',
           'Minimum_web_width','Manual_LED_height','Emitter_above_pillar','Pillar_diameter',
           'Wall_thickness','Joint_depth','Cover_plate','LED_position','Artwork_mode','Dark_field_border','Housing_shape']
    signature=[json.loads(re.search(r'(?m)^'+name+r'\s*=\s*([^;]+);',source).group(1)) for name in names]
    groups,metadata=surface_repair(read_flat_svg(work/'surface_source.svg'),signature[-1],rx,ry,h,
                                   wall_offset,bottom,min(top,h-wall_offset-0.1),width,rfar*1.1,
                                   wall_thickness=signature[14],
                                   minimum_cut=json.loads(re.search(r'(?m)^Minimum_cut_width\s*=\s*([^;]+);',source).group(1)))
    source=re.sub(r'// BEGIN EMBEDDED PRINT LIGHT.*?// END EMBEDDED PRINT LIGHT',
                  '// BEGIN EMBEDDED PRINT LIGHT\n'+scad_module(groups)+'\n// END EMBEDDED PRINT LIGHT',source,flags=re.S)
    source=set_value(source,'Embedded_surface_repair',True)
    source=set_value(source,'Embedded_surface_signature',signature)
    output.write_text(source,encoding='utf-8')
    return source,metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg",type=Path)
    parser.add_argument("--length",type=float,default=300,help="Longest shadow dimension, mm")
    parser.add_argument("--diameter",type=float,default=100)
    parser.add_argument("--shape",choices=["Cylinder","Rectangle"],default="Cylinder")
    parser.add_argument("--rectangle-width",type=float,default=80)
    parser.add_argument("--rectangle-depth",type=float,default=100)
    parser.add_argument("--minimum-web",type=float,default=0,
                        help="Simplify opaque slivers below this approximate shell width, mm; 0 keeps original artwork")
    parser.add_argument("--bridge-width",type=float,default=0.9)
    parser.add_argument("--automatic-bridges-only",action="store_true",
                        help="Start without regular spokes; add short vertical ribs only to disconnected islands")
    parser.add_argument("--height",type=float,default=30,help="Closed single-module depth, mm")
    parser.add_argument("--module-index",type=int,default=0)
    parser.add_argument("--shadow-x",type=float,default=0,help="Artwork centre X on the wall, mm")
    parser.add_argument("--shadow-y",type=float,default=0,help="Artwork centre Y on the wall, mm")
    parser.add_argument("--cover-svg",type=Path,help="Independent white artwork for the circular cover")
    parser.add_argument("--cover-hole",type=float,default=0,help="Central cover hole diameter, mm; 0 disables it")
    parser.add_argument("--wall-standoff",type=float,default=0,
                        help="Gap held between the room wall and the module back, mm; 0 is flush")
    parser.add_argument("--standoff-mode",choices=["Separate ring","Extended body"],
                        default="Separate ring")
    parser.add_argument("--support-layout",choices=["Radial","Manual XY","Radial and XY"],default="Radial")
    parser.add_argument("--support",type=float,nargs=5,action="append",metavar=("X1","Y1","X2","Y2","WIDTH"),
                        help="Manual support endpoints and wall width, mm; repeat up to four times")
    parser.add_argument("--detail-percent",type=float,default=5,help="Smallest IMPORTANT detail as %% of length; not auto-measured")
    parser.add_argument("--emitter-diameter",type=float,default=0.2)
    parser.add_argument("--emitter-depth",type=float,default=0)
    parser.add_argument("--dark-silhouette",action="store_true")
    parser.add_argument("--light-limit",action="store_true",
                        help="Dark silhouette only: bound the lit field to a band round the shadow")
    parser.add_argument("--light-limit-shape",default="Same as shadow",
                        choices=["Same as shadow","Circle","Rectangle"])
    parser.add_argument("--light-limit-thickness",type=float,default=25,
                        help="Band width on the wall, mm")
    parser.add_argument("--light-limit-outside",choices=["on","off"],default="on",
                        help="Bound the light outside the artwork silhouette")
    parser.add_argument("--light-limit-inside",choices=["on","off"],default="on",
                        help="off leaves an enclosed interior fully lit")
    parser.add_argument("--no-auto-bridges",action="store_true",help="Report floating parts instead of adding bridges")
    parser.add_argument("--skip-mesh-check",action="store_true",help="Fast conversion only; no printability evidence")
    parser.add_argument("--output",type=Path,default=ROOT/"output"/"my_shadow_lamp.scad")
    parser.add_argument("--openscad")
    args=parser.parse_args()
    if min(args.length,args.diameter,args.height,args.detail_percent)<=0:
        parser.error("Dimensions and detail percentage must be positive")
    if args.minimum_web<0 or args.bridge_width<=0 or min(args.rectangle_width,args.rectangle_depth)<=0:
        parser.error("Web width must be non-negative; bridge and rectangle dimensions must be positive")
    exe=find_openscad(args.openscad)
    svg=args.svg.resolve(strict=True)
    output=args.output.resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    work=output.parent/(output.stem+"_preflight")
    work.mkdir(exist_ok=True)
    importer=work/"import.scad"
    importer.write_text("import(file="+json.dumps(svg.as_posix())+",center=true,dpi=96,$fn=180);\n",encoding="utf-8")
    flat=work/"flattened.svg"
    run_scad(exe,importer,flat)
    shadow_groups=read_flat_svg(flat)
    module,radius,size,vertex_count=embedded_module(shadow_groups)
    source=(ROOT/"modular_shadow_lamp.scad").read_text(encoding="utf-8")
    source=re.sub(r"// BEGIN EMBEDDED ARTWORK.*?// END EMBEDDED ARTWORK",
                  "// BEGIN EMBEDDED ARTWORK\n"+module+"\n// END EMBEDDED ARTWORK",source,flags=re.S)
    cover_metadata=None
    if args.cover_svg:
        cover_svg=args.cover_svg.resolve(strict=True)
        cover_importer=work/"import_cover.scad"
        cover_importer.write_text("import(file="+json.dumps(cover_svg.as_posix())+",center=true,dpi=96,$fn=180);\n",encoding="utf-8")
        cover_flat=work/"flattened_cover.svg"
        run_scad(exe,cover_importer,cover_flat)
        cover_module,cover_radius,cover_size,cover_vertices=embedded_module(read_flat_svg(cover_flat))
        cover_module=cover_module.replace("module embedded_artwork()", "module embedded_cover_artwork()",1)
        source=re.sub(r"// BEGIN EMBEDDED COVER ARTWORK.*?// END EMBEDDED COVER ARTWORK",
            "// BEGIN EMBEDDED COVER ARTWORK\n"+cover_module+"\n// END EMBEDDED COVER ARTWORK",source,flags=re.S)
        cover_metadata={"input":str(cover_svg),"original_geometry_size_mm":cover_size,"polygon_vertices":cover_vertices}
    values={"Embedded_artwork":True,"Embedded_radius_factor":radius,"Use_svg":False,
            "Housing_shape":args.shape,"Rectangle_width":args.rectangle_width,"Rectangle_depth":args.rectangle_depth,
            "Minimum_web_width":args.minimum_web,"Bridge_width":args.bridge_width,
            "Automatic_bridges_only":args.automatic_bridges_only,
            "Shadow_length":args.length,"Cylinder_diameter":args.diameter,"Cylinder_height":args.height,
            "Module_index":args.module_index,"Smallest_detail_percent":args.detail_percent,
            "Emitter_diameter":args.emitter_diameter,"Emitter_axial_depth":args.emitter_depth,
            "Shadow_x":args.shadow_x,"Shadow_y":args.shadow_y,"Cover_hole_diameter":args.cover_hole,
            "Embedded_cover_artwork":bool(args.cover_svg),"Support_layout":args.support_layout,
            "Wall_standoff":args.wall_standoff,"Standoff_mode":args.standoff_mode,
            "Light_limit":bool(args.light_limit),"Light_limit_shape":args.light_limit_shape,
            "Light_limit_thickness":args.light_limit_thickness,
            "Light_limit_outside":args.light_limit_outside=="on",
            "Light_limit_inside":args.light_limit_inside=="on","Embedded_outline":True,
            "Artwork_mode":"Dark silhouette" if args.dark_silhouette else "Light shapes"}
    # The generator can only wrap a true rectangle round artwork whose real
    # proportions it knows, so measure them here rather than assume a square.
    values["Embedded_extent"]=[round(size[0]/max(size),9),round(size[1]/max(size),9)]
    # offset() moves every boundary at once, so bounding the light outside a closed
    # outline without eating its interior needs the silhouette as separate geometry.
    source=re.sub(r"// BEGIN ARTWORK SILHOUETTE.*?// END ARTWORK SILHOUETTE",
                  "// BEGIN ARTWORK SILHOUETTE\n"+outline_module(shadow_groups)+
                  "\n// END ARTWORK SILHOUETTE",source,flags=re.S)
    if args.light_limit and not args.dark_silhouette:
        parser.error("--light-limit only applies with --dark-silhouette")
    if args.light_limit_thickness<=0:
        parser.error("The light limit band must have a positive thickness")
    if args.wall_standoff<0:
        parser.error("The wall standoff cannot be negative")
    if args.support:
        if len(args.support)>4:
            parser.error("At most four manual supports are available")
        if args.support_layout=="Radial":
            values["Support_layout"]="Radial and XY"
        for i in range(1,5):
            values[f"Support_{i}_enabled"]=i<=len(args.support)
            if i<=len(args.support):
                x1,y1,x2,y2,width=args.support[i-1]
                values.update({f"Support_{i}_start":[x1,y1],f"Support_{i}_end":[x2,y2],f"Support_{i}_width":width})
    for name,value in values.items():
        source=set_value(source,name,value)
    source="// Artwork is embedded. To replace it, select Artwork_source = SVG file, or rerun prepare_svg.py.\n"+source
    output.write_text(source,encoding="utf-8")
    report={"input":str(svg),"output":str(output),"original_geometry_size_mm":size,
            "polygon_vertices":vertex_count,"normalized_radius":radius,"settings":values,
            "detail_measurement":"USER DECLARED; not automatically measured",
            "validation":"NOT CHECKED","automatic_bridge_angles":[],"automatic_bridge_segments":[]}
    report["cover_artwork"]=cover_metadata
    try:
        log=run_scad(exe,output,work/"diagnostics.csg",['Output="Diagnostics"'])
        report["optical_log"]=log
        if "GENERATION NOT POSSIBLE" in log:
            report["validation"]="GEOMETRY IMPOSSIBLE"
            print(log)
            raise RuntimeError("The geometry itself cannot be built. "
                               "The generated SCAD contains specific suggestions.")
        # Cut width and blur are print-quality judgements: the part builds either way, so
        # carry the warning through to the report instead of refusing on the user's behalf.
        warnings=[line for line in log.splitlines() if "WARNING: this builds" in line]
        report["quality_warnings"]=warnings
        for line in warnings:
            print(line.replace('ECHO: "','').rstrip('"'),flush=True)
        if args.minimum_web>0:
            print('Simplifying fragile opaque slivers on the developed shell surface.',flush=True)
            source,report['surface_preparation']=prepare_surface(source,output,work,exe,args.minimum_web)
        if not args.skip_mesh_check:
            for attempt in range(8):
                mesh=work/f"body_{attempt}.stl"
                run_scad(exe,output,mesh,['Output="Body"'])
                world_h=float(re.search(r'"LED centre, wall XYZ mm", \[0, 0, ([^\]]+)\]',log).group(1))
                base=args.wall_standoff if args.standoff_mode=="Extended body" and args.module_index==0 else 0
                world_z=float(re.search(r'"Wall standoff mm / optical back above wall mm", \[[^,]+, ([^\]]+)\]',log).group(1))-base
                result=mesh_report(mesh,world_h,world_z,args.minimum_web**3)
                report["body_mesh"]=result
                if result["surface_components"]==1 and result["closed_two_manifold_edges"]:
                    report["validation"]=("CONNECTED BODY; CLOSED TWO-MANIFOLD EDGES; "
                        +("BELOW QUALITY LIMITS" if warnings else "OPTICAL ENVELOPE PASSES"))
                    shutil.copy2(mesh,output.with_suffix(".stl"))
                    report['mesh_source_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
                    break
                if args.no_auto_bridges or attempt==7 or result['surface_components']==1:
                    raise RuntimeError("Mesh preflight failed: inspect the reported components/edges before printing.")
                segments=[[a,z-base+args.bridge_width/2] for a,z in result["suggested_bridge_segments"]]
                report["automatic_bridge_segments"] += segments
                source=set_value(source,"Embedded_bridge_segments",report["automatic_bridge_segments"])
                removed=report.setdefault('removed_tiny_islands',[])
                removed+=result['suggested_removed_polygons']
                source=set_value(source,'Embedded_removed_islands',removed)
                output.write_text(source,encoding="utf-8")
                print(f"Adding {len(segments)} short vertical ribs below floating parts.",flush=True)
                if result['suggested_removed_polygons']:
                    print(f"Removing {len(result['suggested_removed_polygons'])} sub-print-size detached specks.",flush=True)
            run_scad(exe,output,work/"cover.stl",['Output="Cover"'])
            report["cover_mesh"]=mesh_report(work/"cover.stl")
            if not report["cover_mesh"]["closed_two_manifold_edges"] or report["cover_mesh"]["surface_components"]!=1:
                raise RuntimeError("Cover mesh failed preflight")
            shutil.copy2(work/"cover.stl",output.with_name(output.stem+"_cover.stl"))
            if args.wall_standoff>0 and args.standoff_mode=="Separate ring" and args.module_index==0:
                run_scad(exe,output,work/"standoff.stl",['Output="Standoff"'])
                report["standoff_mesh"]=mesh_report(work/"standoff.stl")
                if not report["standoff_mesh"]["closed_two_manifold_edges"] or \
                        report["standoff_mesh"]["surface_components"]!=1:
                    raise RuntimeError("Standoff ring mesh failed preflight")
                shutil.copy2(work/"standoff.stl",output.with_name(output.stem+"_standoff.stl"))
            if args.cover_svg:
                for part,label in [("Cover base","cover_base"),("Cover artwork","cover_artwork")]:
                    run_scad(exe,output,work/(label+".stl"),['Output='+json.dumps(part)])
                    report[label+"_mesh"]=mesh_report(work/(label+".stl"))
                    if not report[label+"_mesh"]["closed_two_manifold_edges"]:
                        raise RuntimeError(label+" mesh has non-manifold edges")
                    shutil.copy2(work/(label+".stl"),output.with_name(output.stem+"_"+label+".stl"))
        print(f"Created: {output}\n{report['validation']}")
        print("Mesh checks do not certify minimum wall thickness, overhangs, joint fit, heat or brightness.")
        if report.get('surface_preparation',{}).get('light_area_in_small_features_percent',0)>0:
            print('Small-aperture screen: '+str(report['surface_preparation']['light_area_in_small_features_percent'])+
                  '% of sampled inner-shell light area lies in features flagged by the 0.4 mm filter. Inspect the slicer.',flush=True)
    except Exception as error:
        report["validation"]="FAILED"
        report["error"]=str(error)
        raise
    finally:
        report['source_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
        output.with_suffix(".json").write_text(json.dumps(report,indent=2),encoding="utf-8")


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,ValueError,FileNotFoundError,subprocess.TimeoutExpired) as error:
        print(f"PREPARATION FAILED: {error}",file=sys.stderr)
        sys.exit(1)
