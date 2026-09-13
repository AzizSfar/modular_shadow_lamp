"""Small comparison sheet from the verified projection artifacts."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
font_path=Path('C:/Windows/Fonts/segoeui.ttf')
def font(size):
    return ImageFont.truetype(str(font_path),size) if font_path.exists() else ImageFont.load_default()

canvas=Image.new('RGB',(1350,650),(16,22,30))
draw=ImageDraw.Draw(canvas)
draw.text((25,15),'REFERENCE PROTOTYPES',fill=(255,255,255),font=font(27))
draw.text((25,52),'Ideal point-source light patterns · STL-checked geometry · not physically tested',
          fill=(171,184,199),font=font(18))
for i,(name,title,dimensions) in enumerate([
        ('itachi_final','Itachi · cylinder','Ø80 · body 44 + gap 10 mm · image 800 mm'),
        ('monza_final','Monza · cylinder','Ø80 · body 36 + gap 10 mm · image 600 mm'),
        ('monza_rectangle_final','Monza · rectangle','80 × 80 · body 36 + gap 10 mm · image 600 mm')]):
    folder=ROOT/'output'/(name+'_projection')
    report=json.loads((folder/'report.json').read_text())
    pattern=Image.open(folder/'repaired.png').convert('RGB')
    pattern.thumbnail((420,420),Image.Resampling.LANCZOS)
    x=15+i*450
    canvas.paste(pattern,(x,126))
    draw.text((x+8,95),title,fill=(255,210,117),font=font(22))
    draw.text((x+8,555),dimensions,fill='white',font=font(16))
    draw.text((x+8,582),f"Original light area retained: {report['original_artwork_retained_percent']:.1f}%",
              fill=(179,195,211),font=font(17))
    if i<2: draw.line((x+434,96,x+434,610),fill=(49,61,73),width=1)
draw.text((25,620),'0.4 mm nozzle confirmed · 0.2 mm emitter still assumed · inspect fine openings in the slicer',
          fill=(171,184,199),font=font(17))
canvas.save(ROOT/'output'/'reference_comparison.png')
