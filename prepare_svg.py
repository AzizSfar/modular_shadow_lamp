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
    args = [exe, "-o", str(destination)]
    for definition in definitions:
        args += ["-D", definition]
    args.append(str(source))
    result = subprocess.run(args, capture_output=True, text=True, timeout=600)
    log = result.stdout + result.stderr
    destination.with_suffix(destination.suffix + ".log").write_text(log, encoding="utf-8")
    if result.returncode or "ERROR:" in log or not destination.exists():
        raise RuntimeError(f"OpenSCAD could not generate {destination.name}:\n{log}")
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


def mesh_report(path):
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
    components=sorted(groups.values(),key=len,reverse=True)
    # A point inside a large face supplies a reliable angle for a bridge to an island.
    extra_angles=[]
    for component in components[1:]:
        tri=max((triangles[i] for i in component),key=triangle_area)
        x,y=[sum(p[axis] for p in tri)/3 for axis in (0,1)]
        extra_angles.append(round(math.degrees(math.atan2(y,x))%360,5))
    bounds=[[min(p[j] for t in triangles for p in t),max(p[j] for t in triangles for p in t)] for j in range(3)]
    return {"triangles":len(triangles),"surface_components":len(components),
            "edge_incidence_histogram":dict(Counter(len(v) for v in edges.values())),
            "closed_two_manifold_edges":all(len(v)==2 for v in edges.values()),
            "signed_volume_mm3":round(volume,3),"bounds_mm":bounds,
            "suggested_bridge_angles":extra_angles}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg",type=Path)
    parser.add_argument("--length",type=float,default=300,help="Longest shadow dimension, mm")
    parser.add_argument("--diameter",type=float,default=100)
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
    parser.add_argument("--no-auto-bridges",action="store_true",help="Report floating parts instead of adding bridges")
    parser.add_argument("--skip-mesh-check",action="store_true",help="Fast conversion only; no printability evidence")
    parser.add_argument("--output",type=Path,default=ROOT/"output"/"my_shadow_lamp.scad")
    parser.add_argument("--openscad")
    args=parser.parse_args()
    if min(args.length,args.diameter,args.height,args.detail_percent)<=0:
        parser.error("Dimensions and detail percentage must be positive")
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
    module,radius,size,vertex_count=embedded_module(read_flat_svg(flat))
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
            "Shadow_length":args.length,"Cylinder_diameter":args.diameter,"Cylinder_height":args.height,
            "Module_index":args.module_index,"Smallest_detail_percent":args.detail_percent,
            "Emitter_diameter":args.emitter_diameter,"Emitter_axial_depth":args.emitter_depth,
            "Shadow_x":args.shadow_x,"Shadow_y":args.shadow_y,"Cover_hole_diameter":args.cover_hole,
            "Embedded_cover_artwork":bool(args.cover_svg),"Support_layout":args.support_layout,
            "Wall_standoff":args.wall_standoff,"Standoff_mode":args.standoff_mode,
            "Artwork_mode":"Dark silhouette" if args.dark_silhouette else "Light shapes"}
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
            "validation":"NOT CHECKED","automatic_bridge_angles":[]}
    report["cover_artwork"]=cover_metadata
    try:
        log=run_scad(exe,output,work/"diagnostics.csg",['Output="Diagnostics"'])
        report["optical_log"]=log
        if "GENERATION NOT POSSIBLE" in log:
            report["validation"]="OPTICAL LIMITS FAILED"
            print(log)
            raise RuntimeError("Optical limits failed. The generated SCAD contains specific suggestions.")
        if not args.skip_mesh_check:
            for attempt in range(4):
                mesh=work/f"body_{attempt}.stl"
                run_scad(exe,output,mesh,['Output="Body"'])
                result=mesh_report(mesh)
                report["body_mesh"]=result
                if result["surface_components"]==1 and result["closed_two_manifold_edges"]:
                    report["validation"]="CONNECTED BODY; CLOSED TWO-MANIFOLD EDGES; OPTICAL ENVELOPE PASSES"
                    shutil.copy2(mesh,output.with_suffix(".stl"))
                    break
                if args.no_auto_bridges or attempt==3 or not result["closed_two_manifold_edges"]:
                    raise RuntimeError("Mesh preflight failed: inspect the reported components/edges before printing.")
                report["automatic_bridge_angles"] += result["suggested_bridge_angles"]
                source=set_value(source,"Embedded_bridge_angles",report["automatic_bridge_angles"])
                output.write_text(source,encoding="utf-8")
                print(f"Adding {len(result['suggested_bridge_angles'])} narrow radial bridges to retain floating parts.",flush=True)
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
    except Exception as error:
        report["validation"]="FAILED"
        report["error"]=str(error)
        raise
    finally:
        output.with_suffix(".json").write_text(json.dumps(report,indent=2),encoding="utf-8")


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,ValueError,FileNotFoundError,subprocess.TimeoutExpired) as error:
        print(f"PREPARATION FAILED: {error}",file=sys.stderr)
        sys.exit(1)
