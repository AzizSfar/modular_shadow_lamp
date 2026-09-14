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

---

## 3 — 2026-09-13

### Added: light limit for dark silhouette

`Light_limit` bounds the lit field in `Artwork_mode = "Dark silhouette"`. Off, the shadow sits
in a disc reaching the full beam radius. On, light is a band of `Light_limit_thickness` mm
hugging the shadow, and beyond it the wall is dark again. `Light_limit_shape` picks the
bounding region:

- **Same as shadow** — `offset(r=T)` of the artwork. Rounded corners: a mitred outset spikes
  at acute corners into slivers too fine to print.
- **Circle** — the artwork's bounding circle plus T. Larger than the unlimited disc whenever
  T exceeds `Dark_field_border`, so it sizes the disc explicitly rather than shrinking it.
- **Rectangle** — the artwork's **true** bounding box plus T, turning with `Artwork_rotation`.
  `prepare_svg.py` now measures the proportions and writes `Embedded_extent`; a directly
  imported SVG has no measured extent and falls back to a square.

Helper flags: `--light-limit`, `--light-limit-shape`, `--light-limit-thickness`.

### Design decisions taken

| Question | Chosen |
|---|---|
| Corner treatment for "Same as shadow" | Rounded (`offset(r=)`) |
| Rectangle sizing | True artwork bounding box, measured by the helper |
| Band too thin to print | Warn, report the minimum, build anyway |

### The band width is a known feature, not a declared one

Unlike `Smallest_detail_percent`, the band width is a real dimension the generator knows, so
it computes the slot exactly and warns rather than guessing. Flush, 300 mm image:

| Band | Slot in the shell |
|---:|---|
| 5 mm | 0.240 mm — warned |
| 10 mm | 0.450 mm |
| 25 mm | 0.940 mm |
| 50 mm | 1.440 mm |

Thinnest band clearing a 0.4 mm slot: 8.8 mm flush at 300 mm, 4.5 mm with a 20 mm standoff,
10.9 mm at 50 mm standoff / 600 mm. `rho_max` contains T, so the floor has no closed form —
the generator settles it by repeated substitution, and a test confirms the number it suggests
really does clear the limit.

### Follow-up: bounding one side only

The first cut bounded both sides at once, which is wrong for a closed outline. On
`monza_example.svg` the track is a thin closed ribbon, so `offset(r=T)` grew the outside
correctly and simultaneously ate the infield, leaving a band on each side of the track
instead of a lit interior.

`Light_limit_outside` and `Light_limit_inside` are now separate switches. All four
combinations work; `outside on / inside off` is the circuit-map case.

The fix needs the artwork's **silhouette** — its outermost contours with every hole filled —
because `offset()` moves every boundary at once and no morphological trick recovers a filled
hole faithfully (a closing fills only up to its own radius and rounds everything else). The
helper now derives it from contour topology: flatten through OpenSCAD, count how many
contours of the same path contain each contour, keep those at even-odd depth zero, and write
them into the file as a separate `embedded_artwork_outline()` module. On Monza that selects
exactly one contour out of three — the outer boundary at 48,215 units against the enclosed
interior at −41,971 and a degenerate 7-point sliver.

The field then splits at the silhouette: outside it, bounded by the chosen shape or not;
inside it, bounded by the T band or not. Both switches off reproduce the plain dark
silhouette to within 0.2%, which is asserted rather than assumed.

This is only available on prepared artwork. A directly uploaded SVG has no silhouette —
contour nesting is a property of the path data, not of what `import()` returns — so the
generator applies one setting to both sides and echoes a note explaining why. Helper flags:
`--light-limit-outside on|off`, `--light-limit-inside on|off`.

Marker collision worth remembering: the new block was first called
`// BEGIN EMBEDDED ARTWORK OUTLINE`, which the existing non-greedy
`// BEGIN EMBEDDED ARTWORK.*?// END EMBEDDED ARTWORK` substitution matches as a prefix. Renamed
to `// BEGIN ARTWORK SILHOUETTE`. Any future block must not be a prefix of another.

### The failure mode this created

Reported as "inside off does nothing". It did nothing, correctly: the artwork was a direct
SVG import with no silhouette, so the fallback applied the outside setting to both sides. The
only sign was a console echo, and the Projection view looked exactly like the feature being
broken.

Every prepared file in `output/` predates the silhouette, so no file on disk could have
worked; the setting has to be used on artwork prepared after this change.

Two fixes so it cannot happen silently again:

- The Diagnostics **overlay** now carries `Limited outside: yes, inside: no` and appends
  `<- IGNORED, artwork has no silhouette: rerun prepare_svg.py` when the fallback is active.
  On screen, where the person actually is, not only in the console.
- `run_local.py` now passes `--dark-silhouette`, `--light-limit`, `--light-limit-shape`,
  `--light-limit-thickness`, `--light-limit-outside` and `--light-limit-inside` through to the
  helper, so the quick preview can drive the feature instead of needing a hand edit afterwards.

A setting that is silently ignored looks identical to a broken feature. Anything that can be
overridden by a missing prerequisite belongs in the overlay, not in an echo.

Neither fix was enough, because the answer was still "use the helper" and the helper cannot
run on MakerWorld at all. `Interior_span` now makes the direct-import path work: the widest
enclosed area to treat as interior, in mm, with the interior found by a mitred morphological
closing instead of a measured silhouette.

Measured against the exact silhouette on Monza at L=300 (true fill 19,304 mm^2), the closing
lands within **0.6% at S=60 mm and 1.5% at S=200 mm**, under-fills sharply below half the
enclosed width (60% error at S=40), and drifts toward the convex hull far above it (13% at
S=450, hull 28,628). The usable window spans roughly half the enclosed width to the artwork's
own length. Rounded joins were rejected: `offset(r=)` pulls the outer boundary inwards during
erosion; mitred joins restore it exactly.

A measured silhouette still wins where one exists, and Diagnostics states which method
produced the interior so the approximation is never passed off as exact.

### Follow-up: a wrong `Svg long axis` was lying to the optics

Reported as "the shadow doesn't show complete" when switching the axis from Y to X.

`resize([1,0],auto=true)` normalises the **declared** axis. Monza is three times taller than
wide, so declaring X scales it up until Y reaches 257 mm at `Shadow_length = 300`, a corner
reach of 298 mm -- while `k = sqrt(2)/2` and everything built on it still assumed the artwork
fits a 300 mm square, a declared radius of 212 mm. A **38% understatement of the envelope**:
source height, cut, blur and feasibility were all computed against an artwork smaller than the
one actually being cut, and the preview spilled off the wall board.

Fixed two ways:

- A direct import is now intersected with a `Shadow_length` square. A correct declaration
  already fits, so the clamp is a no-op; a wrong one crops with a visible straight edge and
  the optics stay honest. Measured: axis X now reaches 209.9 mm against the declared 212.1,
  where it previously reached 298.
- `view_extent` now covers `1.05*r_far`, so the dark board reaches past the footprint instead
  of letting the projection spill onto the background and read as a clipped shadow.

Prepared artwork carries its measured radius and is not clamped.

### Customizer descriptions: OpenSCAD shows only the LAST comment line

Every multi-line description written for these parameters was being truncated to its final
line, so `Interior_span` displayed "for a single closed outline. Prepared artwork measures
this exactly and ignores it." and dropped the half saying what to set and that 0 means
ignored. That is a large part of why this feature looked broken twice.

All parameter descriptions are now single self-contained lines, with longer rationale on the
lines **above** -- ignored by the customizer, still read in the file. Anything a user must
know in order to set a value correctly belongs on the last line.

### Follow-up: `Interior_span` had to become automatic

Reported a third time as "even with internal light limit off you still get light limit
inside". Measured on Monza at `Shadow_length = 1000`, lit area with the inside limit ON is
131,459 mm^2:

| Interior_span | Silhouette found | Lit area | Effect |
|---:|---:|---:|---|
| 0 (was: ignored) | 27,737 = the artwork | 131,459 | nothing |
| 100 | 26,565 | 131,459 | nothing, silently |
| 300 | 215,259 | 255,217 | works |
| 500 | 215,802 | 255,217 | works |

The feature was correct; the default was useless and a too-small value did nothing while the
console still claimed the interior had been closed. Below the threshold the closing returns
roughly the artwork back, so the union changes nothing.

`Interior_span = 0` now means **automatic = `Shadow_length`**. An enclosed area cannot be
wider than the artwork enclosing it, so that value can never under-fill -- it is the only
setting with that property. Verified: automatic and a hand-picked 500 mm give an identical
255,217 mm^2 at L=1000, and at L=300 both give 38,641 against 36,660 with the limit on.

Over-filling was the worry, and it was measured rather than assumed. On `two_rings`, which is
two separate shapes, spans of 0.25L, 0.5L and 1.0L all leave **two pieces** -- no fusion --
costing 16% extra outline area at 1.0L. On Monza at 1000, 0.25L finds only a partial interior
in two pieces, and 0.5L and above find the whole thing in one. Under-filling silently is far
worse than over-filling visibly, so the guaranteed value wins.

The fallback that made the two sides share one setting is gone: the interior is now always
computable, so `Light_limit_inside` is always honoured.

### Two consequences, both measured

- **The band strands what it encircles.** With supports off, a limited field leaves exactly the
  same number of detached components as the unlimited disc already did. Structural, not a
  regression, and no thickness avoids it — but bridges must stay on and their lines cross
  the band.
- **Widening the band fuses nearby halos.** On `two_rings` at 160 mm, 3/8/20 mm bands keep four
  separate lit regions; a 40 mm band drops to three. Nothing warns about this.

### Evidence

- **21 new tests** in `tests/test_light_limit.py`; **50 in the suite, all passing.**
- **Side independence**: freeing the inside and freeing the outside separately add up to
  freeing both, measured on real renders rather than argued.
- **Silhouette normalisation**: the silhouette and the artwork are asserted to share the same
  centre and scale, since a mismatch would slide the fill off the artwork.
- **No regression**: with the limit off, both Light shapes and Dark silhouette bodies render
  identical triangle counts and volumes to the pre-change file.
- **Identity check**: the band's area equals the grown artwork minus the artwork, rendered and
  measured as three separate probes rather than asserted.
- **Envelope check**: a rectangle's reported reach is `hypot(175,175)` where a circle's is 175,
  confirming the optics use the corner.
- **Full helper run** with `--dark-silhouette --light-limit` passed mesh preflight, and the
  measured `Embedded_extent` for `two_rings` came out `[0.333, 1.0]` as expected.
- Joint fit still passes both pairs.

### Also investigated: Inkscape clips are ignored

`clip-path`, `mask`, `display:none` and `visibility:hidden` are all discarded by OpenSCAD's
SVG importer — a clipped 180 mm bar imports at exactly the same 47.62 mm width and 504 volume
as the unclipped one. Content outside the page imports too. Cropping must be baked into the
geometry (`Path > Union`, then `Path > Intersection`), and hidden layers deleted rather than
hidden. **Not yet handled in code**: `prepare_svg.py` flattens through OpenSCAD, so it inherits
the same blindness and will pass preflight on artwork that is not what you see in Inkscape. A
`--crop` option plus a refusal when `clip-path`/`mask`/`display:none` is present was offered
and not yet built.

### Open / untested

- Nothing printed. No band has been cut in plastic, so the slot-width floor is geometry, not
  a measured print result.
- The halo-fusion behaviour is silent; Diagnostics does not detect or report it.
- The Diagnostics suggestion search varies module height only — it will not propose widening
  the band or adding a standoff when a band is too fine.

---

## 4 — 2026-09-14

### Quality limits warn instead of refusing

"Too much impossible in generation." Fair: one verdict was covering two unrelated things.

`feasible()` mixed hard geometry with print-quality thresholds, so a cut estimate 0.03 mm under
the minimum refused exactly as hard as a pillar that does not fit its own cavity. Split into:

- `buildable(H,L)` — mechanical clearances, source between the floor and the ceiling, and an
  image that still reaches outside the occluded centre. Refuses, always, in any mode.
- `quality_ok(H,L)` — cut width and blur. Warns; the part builds.

`feasible = buildable && quality_ok` still drives the suggestion search, so the suggested
dimensions remain fully feasible rather than merely buildable.

`Quality_limits = "Warn"` is the default; `"Refuse"` restores the old gate.

Classified against real renders before the tests were written:

| Request | Verdict |
|---|---|
| direct SVG at 1000 mm | BELOW QUALITY LIMITS — builds |
| `Emitter_diameter = 5` | BELOW QUALITY LIMITS — builds |
| `Emitter_axial_depth = 1` | BELOW QUALITY LIMITS — builds |
| `Shadow_length = 600` flush | BELOW QUALITY LIMITS — builds |
| `Manual_LED_height = 0` | GENERATION NOT POSSIBLE — source below the pillar |
| 50 mm standoff, 300 mm image | GENERATION NOT POSSIBLE — dead disc swallows it |

Monza at 1000 mm now exports a closed single-component body of 15,112 triangles where it
previously refused outright, and the helper completes with
`CONNECTED BODY; CLOSED TWO-MANIFOLD EDGES; BELOW QUALITY LIMITS`.

Diagnostics shows amber for "builds but coarse" and red only for geometry that cannot exist,
and the warning names the failing number rather than saying the request is impossible.

### Evidence

- **68 tests, all passing**; 5 new in `tests/test_standoff.py::QualityGateTests`.
- Three existing tests asserted the old combined refusal and were updated to assert the
  correct half of the split — including one that now checks a source below the pillar still
  refuses **while Quality_limits is set to Warn**, which is the property that matters.
- The default demo body is byte-identical: 46,590.745 mm^3.

### Open / untested

- The suggestion search still varies module height only. It will not propose a standoff, a
  larger diameter or a wider band when one of those is the real fix.
- Nothing here changes what actually prints. A 0.114 mm slot still will not open on a 0.4 mm
  nozzle; the generator now shows it to you instead of deciding for you.
