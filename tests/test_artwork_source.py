"""Regression tests use actual exported SVG geometry, not only selector strings."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_svg import ROOT, embedded_module, find_openscad, read_flat_svg, run_scad


class ArtworkSourceTests(unittest.TestCase):
    def test_source_selection_and_embedded_override(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as work:
            work=Path(work)
            svg=work/'default.svg'
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 25" width="100mm" height="25mm"><rect width="100" height="25"/></svg>')
            source=(ROOT/'modular_shadow_lamp.scad').read_text().split('\nif(Output=="Cover")')[0]
            model=work/'selector.scad'
            model.write_text(source+'\nnormalized_artwork();\n')
            path='Svg_file='+json.dumps(svg.as_posix())
            cases=[
                ('default',[],1,'Built-in demo'),
                ('auto_uploaded',[path,'Svg_long_axis="X"'],4,'SVG file'),
                ('forced_svg',['Artwork_source="SVG file"','Svg_file="default.svg"','Svg_long_axis="X"'],4,'SVG file'),
                ('legacy',['Use_svg=true',path,'Svg_long_axis="X"'],4,'SVG file'),
                ('demo_override',['Artwork_source="Built-in demo"',path],1,'Built-in demo'),
                ('embedded',['Embedded_artwork=true'],1,'Embedded artwork'),
                ('replace_embedded',['Embedded_artwork=true','Embedded_radius_factor=0.1',path,'Svg_long_axis="X"'],4,'SVG file'),
                ('force_embedded',['Embedded_artwork=true','Artwork_source="Embedded artwork"',path],1,'Embedded artwork'),
            ]
            for name,definitions,ratio,active in cases:
                with self.subTest(name=name):
                    output=work/('result_'+name+'.svg')
                    log=run_scad(find_openscad(),model,output,definitions)
                    self.assertIn('"ACTIVE ARTWORK", "'+active+'"',log)
                    _,_,size,_=embedded_module(read_flat_svg(output))
                    self.assertAlmostEqual(size[0]/size[1],ratio,places=4)
                    if active=='SVG file':
                        self.assertIn('[212.132, 15]',log)  # SVG bound, even if embedded metadata differs.

    def test_embedded_bridges_do_not_leak_into_replacement_svg(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as work:
            work=Path(work)
            source=(ROOT/'modular_shadow_lamp.scad').read_text().split('\nif(Output=="Cover")')[0]
            model=work/'bridges.scad'
            model.write_text(source+'\nbridge_wedges_2d(100);\n')
            for mode,count in [('Built-in demo',3),('Embedded artwork',4),('SVG file',3)]:
                output=work/(mode.replace(' ','_')+'.svg')
                run_scad(find_openscad(),model,output,
                    ['Embedded_artwork=true','Embedded_bridge_angles=[50]','Bridge_count=3',
                     'Artwork_source='+json.dumps(mode)])
                contours=[c for g in read_flat_svg(output) for c in g]
                self.assertEqual(len(contours),count)


if __name__=='__main__':
    unittest.main(verbosity=2)
