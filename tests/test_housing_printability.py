"""Regression tests for shape optics, developed stencils and finite support ribs."""
import math
from pathlib import Path
import sys
import unittest
import subprocess
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import ROOT, find_openscad, run_scad, set_value, mesh_report, clean_stl
from stencil_surface import boundaries
from compare_designs import evaluate


class SurfaceTests(unittest.TestCase):
    def test_pixel_boundaries_preserve_holes_and_diagonal_components(self):
        for mask in [np.array([[1,0],[0,1]],bool),
                     np.array([[1,1,1],[1,0,1],[1,1,1]],bool)]:
            loops=boundaries(mask)
            area=sum(sum(x*b-y*a for (x,y),(a,b) in zip(p,p[1:]+p[:1]))/2 for p in loops)
            self.assertEqual(area,int(mask.sum()))
            self.assertEqual(len(loops),2)

    def test_rectangular_face_inverse_map_and_compression_bound(self):
        a,h,x,y=38,54,230,160
        def inverse(x,y): return np.array([a*y/x,h*(1-a/x)])
        delta=1e-4
        jac=np.column_stack(((inverse(x+delta,y)-inverse(x-delta,y))/(2*delta),
                             (inverse(x,y+delta)-inverse(x,y-delta))/(2*delta)))
        r=math.hypot(x,y)
        conservative=a*h/(r*math.sqrt(r*r+h*h))
        self.assertLessEqual(conservative,np.linalg.svd(jac,compute_uv=False)[-1])
        q=inverse(x,y)
        self.assertAlmostEqual(h*a/(h-q[1]),x)
        self.assertAlmostEqual(h*q[0]/(h-q[1]),y)


class HousingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work=ROOT/'output'/'housing_tests'; cls.work.mkdir(exist_ok=True)
        cls.source=(ROOT/'modular_shadow_lamp.scad').read_text(encoding='utf-8').split('\nif(Output=="Cover")')[0]
        cls.exe=find_openscad()

    def render(self,name,body,definitions=(),extension='stl'):
        source=self.work/(name+'.scad'); source.write_text(self.source+'\n'+body,encoding='utf-8')
        result=self.work/(name+'.'+extension)
        log=run_scad(self.exe,source,result,['Cylinder_facets=72']+list(definitions))
        return result,log

    def test_rectangular_parts_and_standoff_are_closed_and_sized(self):
        definitions=['Housing_shape="Rectangle"','Rectangle_width=60','Rectangle_depth=90','Wall_standoff=20']
        for name,call in [('body','body();'),('cover','printable_cover();'),('ring','standoff_ring();')]:
            with self.subTest(part=name):
                path,_=self.render('rectangle_'+name,call,definitions)
                report=mesh_report(path)
                self.assertTrue(report['closed_two_manifold_edges'])
                self.assertEqual(report['surface_components'],1)
                self.assertAlmostEqual(report['bounds_mm'][0][1]-report['bounds_mm'][0][0],60,places=4)
                self.assertAlmostEqual(report['bounds_mm'][1][1]-report['bounds_mm'][1][0],90,places=4)
                self.assertAlmostEqual(report['bounds_mm'][2][0],0,places=4)

    def test_rectangular_joints_have_no_positive_volume_interference(self):
        path=self.work/'rectangle_joints.scad'
        path.write_text(self.source+'''\nunion() {
            intersection() { body(); translate([0,0,pitch+0.01]) cover(); }
            intersection() { standoff_ring(); translate([0,0,stand+0.01]) body(); }
            intersection() { body(); translate([0,0,pitch+0.01]) body(); }
        }''',encoding='utf-8')
        result=subprocess.run([self.exe,'-o',str(self.work/'rectangle_interference.stl'),
            '-D','Housing_shape="Rectangle"','-D','Rectangle_width=60','-D','Rectangle_depth=90',
            '-D','Wall_standoff=20','-D','Cylinder_facets=72',str(path)],capture_output=True,text=True,timeout=600)
        log=result.stdout+result.stderr
        self.assertNotIn('ERROR:',log)
        self.assertIn('Current top level object is empty',log)

    def test_export_roundoff_cleanup_keeps_a_closed_solid(self):
        a,b,c,d=(0,0,0),(1,0,0),(0,1,0),(0,0,1)
        almost_b=(1-1e-8,1e-8,0)
        triangles=[(a,c,almost_b),(a,almost_b,b),(a,b,d),(a,d,c),(b,c,d)]
        path=self.work/'roundoff.stl'
        text='solid test\n'
        for tri in triangles:
            text+='facet normal 0 0 0\nouter loop\n'
            text+=''.join('vertex '+' '.join(map(str,p))+'\n' for p in tri)
            text+='endloop\nendfacet\n'
        path.write_text(text+'endsolid test\n')
        self.assertEqual(clean_stl(path),1)
        report=mesh_report(path)
        self.assertEqual(report['triangles'],4)
        self.assertEqual(report['surface_components'],1)
        self.assertTrue(report['closed_two_manifold_edges'])

    def test_prepared_stencil_refuses_stale_print_export(self):
        with self.assertRaises(RuntimeError):
            self.render('stale','body();',['Embedded_artwork=true','Embedded_surface_repair=true',
                        'Output="Body"'],extension='csg')

    def test_search_source_and_standoff_match_scad(self):
        row=evaluate('Rectangle',60,90,30,20,300,0.5,np.array([[0.5,0]]),5)
        self.assertIsNotNone(row)
        _,log=self.render('study','square(1);',['Housing_shape="Rectangle"',
            'Rectangle_width=60','Rectangle_depth=90','Wall_standoff=20'],extension='csg')
        self.assertIn('[0, 0, 44]',log)
        self.assertEqual(row['source_height_mm'],44)


if __name__=='__main__': unittest.main(verbosity=2)
