from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import ROOT,run_scad,find_openscad
w=ROOT/'output'/'svg_debug'
w.mkdir(exist_ok=True)
(w/'default.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 25" width="100mm" height="25mm"><rect width="100" height="25"/></svg>')
for name,expr in [('raw','import("default.svg",center=true);'),('resized','resize([1,0],auto=true) import("default.svg",center=true);')]:
    p=w/(name+'.scad')
    p.write_text(expr)
    print(run_scad(find_openscad(),p,w/(name+'.svg')))
    print((w/(name+'.svg')).read_text())
