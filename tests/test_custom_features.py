"""Geometry regressions for offsets, XY supports, cover SVG, bore and display grid."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import ROOT,find_openscad,run_scad,read_flat_svg

def bounds(path):
    points=[p for group in read_flat_svg(path) for contour in group for p in contour]
    return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]


class CustomFeaturesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'output')
        self.work=Path(self.temp.name)
        self.source=(ROOT/'modular_shadow_lamp.scad').read_text().split('\nif(Output=="Cover")')[0]

    def tearDown(self):
        self.temp.cleanup()

    def export(self,name,call,defs=()):
        model=self.work/(name+'.scad')
        model.write_text(self.source+'\n'+call+'\n')
        output=self.work/(name+'.svg')
        log=run_scad(find_openscad(),model,output,defs)
        return output,log

    def test_artwork_moves_in_wall_coordinates(self):
        out,log=self.export('shifted','target_artwork();',['Shadow_x=40','Shadow_y=-30','Cylinder_height=40'])
        self.assertEqual(bounds(out),[-110,-180,190,120])
        self.assertIn('[200, 15]',log)

    def test_support_endpoints_and_width(self):
        out,_=self.export('support','xy_support_shapes();',
            ['Support_layout="Manual XY"','Support_1_start=[10,20]','Support_1_end=[80,40]',
             'Support_1_width=10','Shadow_x=99'])
        self.assertEqual(bounds(out),[5,15,85,45])

    def test_second_svg_is_independent(self):
        svg=self.work/'cover.svg'
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="25mm" viewBox="0 0 100 25"><rect width="100" height="25"/></svg>')
        out,log=self.export('cover','cover_artwork_2d();',
            ['Cover_artwork_source="SVG file"','Cover_svg_file='+json.dumps(svg.as_posix()),
             'Cover_svg_long_axis="X"','Cover_artwork_length=40'])
        self.assertEqual(bounds(out),[-20,-5,20,5])
        self.assertIn('"ACTIVE ARTWORK", "Built-in demo"',log)
        self.assertIn('"COVER ARTWORK", "SVG file"',log)

    def test_grid_is_not_in_print_geometry(self):
        for part in ['Body','Cover','Cover base']:
            outputs=[]
            for enabled in ['true','false']:
                dest=self.work/(part.replace(' ','_')+enabled+'.csg')
                run_scad(find_openscad(),ROOT/'modular_shadow_lamp.scad',dest,
                    ['Output='+json.dumps(part),'Show_grid='+enabled])
                outputs.append(dest.read_text())
            self.assertEqual(*outputs)

    def test_disabling_cover_hole_and_invalid_bore(self):
        # No volume through the centre when hole enabled, positive volume when zero.
        for diameter,expected in [(0,True),(6,False)]:
            p=self.work/f'probe{diameter}.scad'
            p.write_text(self.source+'\nintersection() { cover_base(); translate([0,0,-0.1]) cylinder(r=0.25,h=6); }\n')
            dest=self.work/f'probe{diameter}.stl'
            result=subprocess.run([find_openscad(),'-o',str(dest),'-D',f'Cover_hole_diameter={diameter}',str(p)],capture_output=True,text=True)
            self.assertEqual(dest.exists() and dest.stat().st_size>100,expected)
            self.assertNotIn('ERROR:',result.stdout+result.stderr)
        p=self.work/'bore.scad'
        p.write_text(self.source+'\nbody();\n')
        result=subprocess.run([find_openscad(),'-o',str(self.work/'bad.csg'),'-D','Pillar_wire_bore=8',str(p)],capture_output=True,text=True)
        self.assertIn('GENERATION NOT POSSIBLE',result.stdout+result.stderr)

if __name__=='__main__':
    unittest.main(verbosity=2)
