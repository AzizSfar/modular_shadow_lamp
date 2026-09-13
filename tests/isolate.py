from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import find_openscad, run_scad
root=Path(__file__).resolve().parents[1]
s=(root/'modular_shadow_lamp.scad').read_text().split('\nif(Output=="Cover")')[0]
for name in sys.argv[1:]:
    p=root/'tests'/f'{name}_debug.scad'
    p.write_text(s+f'\n{name}();\n')
    print(run_scad(find_openscad(),p,root/'output'/f'{name}_debug.stl'),flush=True)
