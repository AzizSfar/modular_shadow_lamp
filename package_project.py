"""Collect the deliverables without bundling the downloaded OpenSCAD runtime."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parent
files=['modular_shadow_lamp.scad','prepare_svg.py','README.md','OPTICS.md',
       'stencil_surface.py','compare_designs.py','inspect_projection.py','DESIGN_REVIEW.md','PROGRESS.md',
       'itachi_example.svg','monza_example.svg','tests/test_housing_printability.py',
       'tools/render_reference_overview.py','output/reference_comparison.png',
       'run_local.py','Open lamp locally.cmd','Open SVG locally.cmd','tests/test_artwork_source.py',
       'examples/two_rings.svg','tests/test_optics.py','tests/check_joint_fit.py','tests/test_standoff.py','tests/test_light_limit.py',
       'tests/verify_mesh_projection.py','output/demo_body.stl','output/demo_cover.stl',
       'output/demo_assembly.png','output/demo_projection.png',
       'output/mesh_verified_projection.png','output/validation.json','output/joint_fit.log',
       'output/two_rings_lamp.scad','output/two_rings_lamp.stl',
       'output/two_rings_lamp_cover.stl','output/two_rings_lamp.json',
       'output/two_rings_projection.png']
for name in ['itachi_final','monza_final','monza_rectangle_final']:
    files += ['output/'+name+suffix for suffix in ['.scad','.json','.stl','_cover.stl','_standoff.stl']]
    files += ['output/'+name+'_projection/'+suffix for suffix in ['comparison.png','report.json']]
for study in ['reference_study','reference_study_5percent']:
    files += [str(path.relative_to(root)).replace('\\','/') for path in (root/'output'/study).glob('*_study.json')]
    files += [str(path.relative_to(root)).replace('\\','/') for path in (root/'output'/study).glob('*_candidates.csv')]
with zipfile.ZipFile(root/'modular_shadow_lamp_bundle.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    for name in files:
        bundle.write(root/name,name)
print(root/'modular_shadow_lamp_bundle.zip')
