# Progress log

Every progress summary should be added in a different section titled with the date and the
incremental number of the progress (+1 the previous).

---

## 1 — 2026-09-13

### Scope

Investigated why an uploaded SVG kept showing the default sunburst, then added the wall
standoff. Features 1–4 of the five requested (cover artwork from a second SVG, hollow
pillar, manual XY supports with a coordinate grid, XY shadow placement) already existed by
the time the merge happened — see *Collision* below.

Everything stated here was rendered and measured with OpenSCAD 2021.01, not reasoned about
on paper.

### Why an uploaded SVG showed the default sunburst

Not a bug — a gate, in `normalized_artwork()`:

```
if(Embedded_artwork) embedded_artwork();
else if(Use_svg)     import(file=Svg_file, ...);
else                 demo_artwork();          // the sunburst
```

`Use_svg` defaulted to `false`. MakerWorld's upload convention swaps the *contents* of
`default.svg`; the variable's name and value never change, so nothing in the script can
detect that an upload happened. Uploading without ticking `Use_svg` did nothing.

Two follow-on traps found at the same time:

- A file produced by `prepare_svg.py` sets `Embedded_artwork = true`, which short-circuits
  before `Use_svg`. Its upload control stays visible but is inert by design.
- Enabling direct SVG mode switches the envelope factor `k` from 0.5 to `sqrt(2)/2`. At the
  stock 300 mm / 5% detail that gives a **0.384 mm** cut estimate against the 0.4 mm limit,
  so it reports GENERATION NOT POSSIBLE. 280 mm clears it (0.411 mm).

The `Artwork_source` dropdown that replaced the boolean removes the footgun.

### Collision with a parallel session

Mid-session, `modular_shadow_lamp.scad` on disk grew from 17 KB to 27 KB and new files
appeared (`run_local.py`, `Open two SVGs locally.cmd`). Another Claude session had
implemented the cover artwork, manual XY supports, the coordinate grid and the XY shadow
placement.

Work already built here against the stale baseline was **discarded rather than committed**.
Only the wall standoff — the one feature that version lacked — was ported onto it. Nothing
the other session wrote was overwritten.

*If two sessions run on this folder again, give each one a file it owns.*

### Added: the wall standoff

`Wall_standoff` is the clear gap held between the room wall and the module's back. **0 is
flush and reproduces the previous geometry byte for byte.** The gap is a closed compartment
with the keyholes and cable route on its own back plate (`Standoff_back`).

`Standoff_mode` chooses how it is built:

- **Separate ring** — `Output = "Standoff"` prints it as its own part, driving the standard
  keyed tongue into the body's existing rear socket. Change the standoff without reprinting
  the optical body. Requires `Wall_standoff >= Standoff_back`.
- **Extended body** — the body grows backwards as one piece, no extra joint. Its rear socket
  is suppressed, because a blind socket there would seal a void inside the part.

Optically a standoff is identical to mounting the module further into the room: every
mechanical plane translates with it, so the source rises by exactly the standoff and radial
resolution improves in proportion. It is not free — `rho_dead = R*h/(h-A)` has `h` and `A`
rising together, so the hidden centre widens at a similar rate.

| Standoff | Source height | Cut estimate | Hidden radius |
|---:|---:|---:|---:|
| 0 mm | 24 mm | 0.768 mm | 64.9 mm |
| 20 mm | 44 mm | 1.408 mm | 118.9 mm |
| 50 mm | 74 mm | 2.368 mm | 200.0 mm |

So it pays off only if the image grows with the gap. On the default 100 × 30 mm module,
50 mm of standoff **rejects** a 300 mm image — the 200 mm dead radius swallows it — while
projecting **600 mm** comfortably at a 1.184 mm cut estimate, a length the flush module
cannot reach at all.

`prepare_svg.py` gained `--wall-standoff` and `--standoff-mode`. The ring is mesh-checked
alongside the body and cover and written to `<name>_standoff.stl`.

```powershell
python prepare_svg.py artwork.svg --wall-standoff 25 --length 500 --output output/my_lamp.scad
```

### The hollow pillar already existed

No change needed. `Pillar_wire_bore` (3 mm) has always run the full pillar height into the
rear cable route under the opaque back. `tests/check_feature_meshes.py` already proves the
axial path is clear by ray-casting through the exported mesh at x=y=0.

### Evidence

- **22 unit tests pass** — 13 existing, 9 new in `tests/test_standoff.py`.
- **No regression**: at `Wall_standoff = 0`, Body, Cover and Cover base render identical
  triangle counts, volumes and bounds to the pre-merge file.
- **Joint fit**: `tests/check_joint_fit.py` now also intersects the standoff ring with the
  seated body. Empty at 0.01 mm separation, like the cover and stacking pairs.
- **Mesh quality**: the ring, the body-with-ring and the extended body are each one closed
  two-manifold surface component, each sitting on z=0 as exported.
- **The compartment is vented, not sealed** — it breathes through the pillar bore, which is
  why the assembly stays a single surface component. Tested directly.
- **Full helper run** with a standoff produced body, cover and ring, all passing preflight.

### Files touched

`modular_shadow_lamp.scad`, `prepare_svg.py`, `README.md`, `OPTICS.md`,
`package_project.py`, `tests/check_joint_fit.py`, and new `tests/test_standoff.py`.

### Open / untested

- Nothing has been printed. The ring's tongue clears in CGAL; that is not a fit felt in PLA.
- The compartment is a void with a cable route. Driver placement, insulation, clearances,
  heat and any mains-side design are untouched and untested.
- The Diagnostics suggestion search varies module height, never the standoff. When it
  refuses a length it will not propose a standoff as the fix — try one by hand.
- `Standoff_back` is not checked against the pull-out load of the keyhole screws.
- A `.git` folder appeared in the project during the session. These files are uncommitted
  working-tree changes; check `git status` before anything checks out over them.

## 2 — 2026-09-13

### Reference-driven housing and stencil improvements

Used the supplied `itachi_example.svg` and `monza_example.svg`. Confirmed that the
standoff is already included in the source, cone and clipping calculations. Fixed
the lower-module stack display to include it too. The new `compare_designs.py`
samples 4,320 combinations per reference across housing size/shape, optical height,
standoff, image length and XY placement; it measures visible filled-SVG area and
counts body plus standoff as total depth. Reports retain the explicit assumptions
and sampled bounds rather than claiming a global optimum.

Added `Housing_shape = Rectangle`, with independent width and depth. The body,
cover, joints, electronics standoff and actual projected obstruction all follow
the footprint. Rectangular compression uses a conservative bound that includes
the shear of the flat-face inverse projection.

Added optional `--minimum-web` preparation on the developed inner shell, using
NumPy/Pillow. This simplifies fine opaque slivers and retains original vector
light elsewhere. `--automatic-bridges-only` starts without blanket spokes; mesh
preflight removes explicitly reported tiny detached specks and adds short 0.9 mm
ribs beneath larger islands. Finite rib shadows are included in Projection.
Relevant edits invalidate prepared surface data and block stale body exports.

The user confirmed a 0.4 mm nozzle. The 0.2 mm LED emitting-area assumption is
still unconfirmed. The 0.4 mm small-aperture screen is diagnostic, not an exact
stroke-width measurement or a printability certificate.

### Prepared results

| Model | Housing | Optical height + standoff | Artwork length | Original light area retained |
|---|---|---|---|---|
| `itachi_final` | Ø80 mm | 44 + 10 mm | 800 mm | 88.39% |
| `monza_final` | Ø80 mm | 36 + 10 mm | 600 mm | 97.25% |
| `monza_rectangle_final` | 80 × 80 mm | 36 + 10 mm | 600 mm | 94.69% |

Each has a standalone SCAD, body/cover/standoff STL and JSON report in `output/`.
Itachi uses eight short ribs and removes four tiny specks. Monza needs no added
ribs in either final housing. A taller optical section with a smaller standoff
preserved much more Itachi artwork than the earlier 30 + 30 mm trial, despite
being shallower in total.

### Evidence and limits

- 29 distinct automated tests passed: the 28-test suite plus a new rectangular
  cover/body/stack/standoff interference check.
- All nine final parts have one surface component and closed two-manifold edges.
- Binary STL export exposed four collapsed triangles at the retaining holes in
  the cylindrical reference bodies. Welding export coincidences at 0.000001 mm
  and removing collapsed triangles resolves the numerical failure; real islands
  are handled separately and never hidden by that cleanup.
- `inspect_projection.py` independently projects the opaque STL at the correct
  wall offset. Agreement with the analytic preview is 99.02% for Itachi at
  5,000 pixels and 97.84% / 97.95% for cylindrical / rectangular Monza at 10,000
  pixels. Narrow outlines have measurable raster-boundary error.
- Cleanup changes the artwork. Itachi gains light equivalent to 8.13% of the
  visible reference area and loses 1.68%; Monza gains 3.91% / 2.33%. Side-by-side
  images expose these changes.
- These candidate sizes use the original 5% declared-detail assumption, not a
  measurement of the finest SVG detail. The stricter 2% study gives much less
  compact results. Monza still has significant small-aperture flags.
- No slicer, physical print, real LED, driver fit, thermal or mechanical-load
  test was performed. The 10 mm compartment is a candidate, not a measured fit.

See `DESIGN_REVIEW.md` for the findings and remaining trade-offs, `README.md` for
commands, and `OPTICS.md` for the rectangular projection and surface processing.
