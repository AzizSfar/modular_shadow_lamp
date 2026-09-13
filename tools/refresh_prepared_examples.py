"""Refresh our two bundled generated examples, preserving their artwork/settings."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
template=(root/'modular_shadow_lamp.scad').read_text(encoding='utf-8')
for name in ('two_rings_lamp.scad','infeasible_example.scad'):
    path=root/'output'/name
    if not path.exists():
        continue
    old=path.read_text(encoding='utf-8')
    block=re.search(r'// BEGIN EMBEDDED ARTWORK.*?// END EMBEDDED ARTWORK',old,re.S).group()
    new=re.sub(r'// BEGIN EMBEDDED ARTWORK.*?// END EMBEDDED ARTWORK',lambda _:block,template,flags=re.S)
    parameter_text=old.split('/* [Hidden] */')[0]
    names=re.findall(r'(?m)^(\w+)\s*=\s*[^;]*;',parameter_text)
    names+=['Embedded_artwork','Embedded_radius_factor','Embedded_bridge_angles']
    for param in names:
        pattern=r'(?m)^'+re.escape(param)+r'\s*=\s*[^;]*;'
        match=re.search(pattern,old)
        if match:
            new=re.sub(pattern,lambda _:match.group(),new)
    path.write_text('// Prepared example. Select Artwork_source = SVG file to replace its embedded artwork.\n'+new,encoding='utf-8')
    print('Updated '+str(path))
