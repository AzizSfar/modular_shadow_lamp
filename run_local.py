"""Open the lamp locally, optionally preparing a selected SVG for a quick preview."""
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from prepare_svg import ROOT, find_openscad


def choose_svg(title="Choose the lamp's shadow SVG"):
    import tkinter as tk
    from tkinter import filedialog
    app=tk.Tk()
    app.withdraw()
    try:
        return filedialog.askopenfilename(title=title,
            filetypes=[("SVG artwork","*.svg")],parent=app)
    finally:
        app.destroy()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--choose-svg',action='store_true')
    parser.add_argument('--svg',type=Path)
    parser.add_argument('--cover-svg',type=Path)
    parser.add_argument('--choose-cover',action='store_true')
    parser.add_argument('--cover-hole',type=float,default=0)
    parser.add_argument('--length',type=float,default=300)
    parser.add_argument('--height',type=float,default=30)
    parser.add_argument('--diameter',type=float,default=100)
    parser.add_argument('--shape',choices=['Cylinder','Rectangle'],default='Cylinder')
    parser.add_argument('--rectangle-width',type=float,default=80)
    parser.add_argument('--rectangle-depth',type=float,default=100)
    parser.add_argument('--wall-standoff',type=float,default=0)
    parser.add_argument('--minimum-web',type=float,default=0)
    parser.add_argument('--automatic-bridges-only',action='store_true')
    parser.add_argument('--dark-silhouette',action='store_true')
    parser.add_argument('--light-limit',action='store_true')
    parser.add_argument('--light-limit-thickness',type=float,default=25)
    parser.add_argument('--light-limit-shape',default='Same as shadow',
                        choices=['Same as shadow','Circle','Rectangle'])
    parser.add_argument('--light-limit-outside',choices=['on','off'],default='on')
    parser.add_argument('--light-limit-inside',choices=['on','off'],default='on')
    parser.add_argument('--no-open',action='store_true',help='Prepare only, without opening a window')
    args=parser.parse_args()
    exe=Path(find_openscad())
    model=ROOT/'modular_shadow_lamp.scad'
    svg=args.svg
    cover_svg=args.cover_svg
    if args.choose_svg:
        selection=choose_svg()
        if not selection:
            return
        svg=Path(selection)
    if args.choose_cover:
        selection=choose_svg("Choose the white cover artwork SVG (Cancel for none)")
        cover_svg=Path(selection) if selection else None
    if svg:
        svg=svg.resolve(strict=True)
        # A fresh file preserves edits made to earlier local previews.
        model=ROOT/'output'/('local_lamp_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.scad')
        command=[sys.executable,str(ROOT/'prepare_svg.py'),str(svg),'--skip-mesh-check',
                 '--length',str(args.length),'--height',str(args.height),
                 '--diameter',str(args.diameter),'--output',str(model),'--openscad',str(exe)]
        command+=['--cover-hole',str(args.cover_hole)]
        for name in ['shape','rectangle_width','rectangle_depth','wall_standoff','minimum_web']:
            command+=['--'+name.replace('_','-'),str(getattr(args,name))]
        if args.automatic_bridges_only: command+=['--automatic-bridges-only']
        if args.dark_silhouette: command+=['--dark-silhouette']
        if args.light_limit:
            command+=['--light-limit','--light-limit-thickness',str(args.light_limit_thickness),
                      '--light-limit-shape',args.light_limit_shape,
                      '--light-limit-outside',args.light_limit_outside,
                      '--light-limit-inside',args.light_limit_inside]
        if cover_svg:
            command+=['--cover-svg',str(cover_svg.resolve(strict=True))]
        result=subprocess.run(command)
        # Optical failures still produce a useful SCAD diagnostics view with suggestions.
        if result.returncode and not model.exists():
            raise RuntimeError('SVG preparation failed; see the message above.')
        print('Quick preview only. Run prepare_svg.py without --skip-mesh-check before printing.',flush=True)
    print('Local model: '+str(model),flush=True)
    if not args.no_open:
        gui=exe.with_suffix('.exe') if exe.suffix.lower()=='.com' else exe
        subprocess.Popen([str(gui),str(model)],cwd=str(ROOT))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        print('Could not open the lamp: '+str(error),file=sys.stderr)
        sys.exit(1)
