"""Check interference between the real body, seated cover, and next module."""
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import find_openscad
root=Path(__file__).resolve().parents[1]
source=(root/'modular_shadow_lamp.scad').read_text().split('\nif(Output=="Cover")')[0]
source+='''
// 0.01 mm axial separation excludes intended coplanar seating contact.
union() {
    intersection() { body(); translate([0,0,pitch+0.01]) cover(); }
    translate([200,0,0]) intersection() { body(); translate([0,0,pitch+0.01]) body(); }
}
'''
path=root/'tests'/'joint_interference.scad'
path.write_text(source)
result=subprocess.run([find_openscad(),'-o',str(root/'output'/'joint_interference.stl'),str(path)],
                      text=True,capture_output=True,timeout=600)
log=result.stdout+result.stderr
(root/'output'/'joint_fit.log').write_text(log)
print(log)
assert 'Current top level object is empty' in log
assert 'ERROR:' not in log
print('PASS: no positive-volume interference in the seated cover or two-module stack.')

# The standoff ring drives the same keyed tongue into the body's existing rear socket.
standoff=(root/'modular_shadow_lamp.scad').read_text().split('\nif(Output=="Cover")')[0]+'''
intersection() { standoff_ring(); translate([0,0,stand+0.01]) body(); }
'''
path=root/'tests'/'standoff_interference.scad'
path.write_text(standoff)
result=subprocess.run([find_openscad(),'-o',str(root/'output'/'standoff_interference.stl'),
                       '-D','Wall_standoff=20',str(path)],
                      text=True,capture_output=True,timeout=600)
log=result.stdout+result.stderr
(root/'output'/'standoff_fit.log').write_text(log)
print(log)
assert 'Current top level object is empty' in log
assert 'ERROR:' not in log
print('PASS: the standoff ring seats in the rear socket without interference.')
