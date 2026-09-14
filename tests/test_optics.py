"""Independent geometry and generator regression checks (standard library)."""
import math
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import find_openscad, run_scad, mesh_report, read_flat_svg, embedded_module

ROOT=Path(__file__).resolve().parents[1]

def echo_number(log, label):
    match=re.search(re.escape('ECHO: "'+label+'", ')+r'([-+\d.eE]+)',log)
    if not match:
        raise AssertionError(label+" not found in output")
    return float(match.group(1))

class OpticsTests(unittest.TestCase):
    def test_inverse_forward_round_trip_and_wall_thickness(self):
        for h in (15,24,49.5,95):
            for r in (70,100,250,700):
                for angle in (0,23,117,244):
                    p=(r*math.cos(math.radians(angle)),r*math.sin(math.radians(angle)))
                    for radius in (48,50):
                        q=(radius/r*p[0],radius/r*p[1],h*(1-radius/r))
                        self.assertAlmostEqual(math.hypot(q[0],q[1]),radius)
                        recovered=tuple(q[i]*h/(h-q[2]) for i in (0,1))
                        for i in (0,1):
                            self.assertAlmostEqual(p[i],recovered[i],places=9)
                    self.assertLess(h*(1-50/r),h*(1-48/r))

    def test_surface_jacobian_by_finite_difference(self):
        h,Ri,r=24,48,150
        dr=1e-4
        dz=(h*(1-Ri/(r+dr))-h*(1-Ri/(r-dr)))/(2*dr)
        self.assertAlmostEqual(dz,h*Ri/r**2,places=9)
        dy=1e-4
        ds=Ri*(math.atan2(dy,r)-math.atan2(-dy,r))/(2*dy)
        self.assertAlmostEqual(ds,Ri/r,places=9)

    def test_blur_derivative_with_fixed_aperture(self):
        h,ri,r=24,48,150
        z=h*(1-ri/r)
        dt=1e-5
        axial=abs(((h+dt)*ri/(h+dt-z)-(h-dt)*ri/(h-dt-z))/(2*dt))
        self.assertAlmostEqual(axial,(r/ri-1)*r/h,places=6)
        lateral=abs((dt+h/(h-z)*(ri-dt)-(-dt+h/(h-z)*(ri+dt)))/(2*dt))
        self.assertAlmostEqual(lateral,r/ri-1,places=6)

    def test_default_and_impossible_suggestions(self):
        exe=find_openscad()
        log=run_scad(exe,ROOT/'modular_shadow_lamp.scad',ROOT/'output'/'test_default.csg',['Output="Diagnostics"'])
        self.assertIn('OPTICAL ENVELOPE PASSES',log)
        self.assertIn('[0, 0, 24]',log)
        self.assertAlmostEqual(echo_number(log,'Central occlusion radius mm'),50*24/(24-5.5),places=3)
        log=run_scad(exe,ROOT/'modular_shadow_lamp.scad',ROOT/'output'/'test_impossible.csg',
                     ['Output="Diagnostics"','Use_svg=true','Shadow_length=1000'])
        # Missing the cut limit is a quality judgement now, not a refusal to build.
        self.assertIn('BELOW QUALITY LIMITS',log)
        pair=re.search(r'SUGGESTED sampled compromise.*?\[([\d.]+), ([\d.]+)\]',log)
        self.assertIsNotNone(pair)
        height,length=map(float,pair.groups())
        retry=run_scad(exe,ROOT/'modular_shadow_lamp.scad',ROOT/'output'/'test_suggestion.csg',
                       ['Output="Diagnostics"','Use_svg=true',f'Shadow_length={length}',f'Cylinder_height={height}'])
        self.assertIn('OPTICAL ENVELOPE PASSES',retry)

    def test_zero_height_and_extended_source_fail(self):
        """A source below the pillar is geometry; a wide emitter is only bad quality."""
        exe=find_openscad()
        for extra,expected in [(['LED_position="Manual height"','Manual_LED_height=0'],
                                'GENERATION NOT POSSIBLE'),
                               (['Emitter_diameter=5'],'BELOW QUALITY LIMITS'),
                               (['Emitter_axial_depth=1'],'BELOW QUALITY LIMITS')]:
            log=run_scad(exe,ROOT/'modular_shadow_lamp.scad',ROOT/'output'/'test_bad_source.csg',
                         ['Output="Diagnostics"']+extra)
            self.assertIn(expected,log)
            self.assertNotIn('OPTICAL ENVELOPE PASSES',log)

    def test_stacked_module_absolute_height(self):
        log=run_scad(find_openscad(),ROOT/'modular_shadow_lamp.scad',ROOT/'output'/'test_stack.csg',
                     ['Output="Diagnostics"','Module_index=1','Shadow_length=500'])
        self.assertIn('OPTICAL ENVELOPE PASSES',log)
        self.assertIn('[0, 0, 49.5]',log)
        self.assertIn('[0, 0, 24]',log)
        self.assertAlmostEqual(echo_number(log,'Central occlusion radius mm'),50*49.5/18.5,places=3)

if __name__=='__main__':
    unittest.main(verbosity=2)
