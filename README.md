# Modular shadow lamp

A wall lamp with a cylindrical or rectangular SVG-controlled optical sidewall, hollow LED pillar, removable cover, keyed stacking joints and a geometric wall-projection preview. The original default remains a 100 mm diameter, **30 mm closed-depth** cylinder.

**Start with `modular_shadow_lamp.scad`.** It contains an original sunburst demo and needs no external library. All dimensions are in millimetres. `OPTICS.md` contains the derivation, assumptions and limits.

## Try it in MakerWorld

1. Open [MakerWorld Parametric Model Maker](https://makerworld.com/en/makerlab/parametricModelMaker) and load the SCAD source.
2. Generate the built-in demo first. Default dimensions are diameter **100**, closed height **30**, shadow length **300**.
3. Choose **Projection** to see the ideal wall footprint, **Assembly** for the body and exploded cover, or **Diagnostics** for the numerical result.
4. To use your own SVG directly, set **Artwork_source = SVG file**, upload through **Svg_file**, and set **Svg_long_axis** to the longer *drawn artwork* axis. `resize()` normalises whichever axis you declare, so naming the shorter one scales the artwork up until the other axis overshoots the envelope every optical estimate assumes. A direct import is therefore **clamped to a `Shadow_length` square**: a correct declaration already fits and nothing changes, a wrong one is cropped on two sides with a straight edge. That crop is the symptom to look for, and Diagnostics states the clamp on screen. Monza is taller than wide, so `Y` is right — with `X` it would reach a 298 mm radius against a declared 212 mm, a 38% understatement that would make the feasibility numbers meaningless. The other dimension scales proportionally. The requested length is the full artwork's longest dimension before obstruction. The report and console identify the active artwork source.
5. Set **Smallest_detail_percent** to the smallest line or gap you need to preserve. Example: a 6 mm important detail in a 300 mm image is **2%**. Also enter your LED's effective emitting-area dimensions. These quantities materially affect feasibility.
6. Export **Body** and **Cover** separately, or use **Print layout**. Assembly, Projection and Diagnostics contain display geometry and are **not print exports**.

The `Svg_file = "default.svg";` file control follows [Bambu Lab's documented SVG-upload convention](https://forum.bambulab.com/t/paramatric-model-maker-v0-8-0-support-uploading-files/91853). The generator was rendered and tested locally with OpenSCAD 2021.01; its execution in your MakerWorld account has not been tested.

## Run locally — no MakerWorld required

On this computer, OpenSCAD is already available in `tools/openscad-2021.01/`.

- Double-click **Open lamp locally.cmd** to open the main generator in OpenSCAD.
- Double-click **Open SVG locally.cmd** to choose an SVG. It measures and embeds the artwork automatically, saves a fresh local SCAD file in `output/`, and opens it in OpenSCAD. This quick route skips the slow mesh preflight; run the full helper before printing.

In OpenSCAD, use its **Customizer** panel for dimensions and the **Output** selector. Use **Preview (F5)** after changes. For an STL, select **Body** or **Cover**, use **Render (F6)**, then export STL. If the preview reports an impossible combination, use the printed suggestions to adjust the dimensions.

To load an SVG directly without the helper, select **Artwork_source = SVG file**, enter its full path in **Svg_file** (forward slashes, for example `C:/Users/Aziz/Documents/design.svg`), and select the longer axis. **Automatic** mode recognizes changed file paths, while **SVG file** forces import even if the file is named `default.svg`. **Built-in demo** explicitly restores the sunburst.

The old generator needed `Use_svg = true`; uploading a file by itself could leave the demo selected. Its prepared examples also gave embedded artwork unconditional priority. The new selector fixes both cases and prevents old embedded support bridges from being applied to a replacement SVG. Reload the updated SCAD in MakerWorld to get the new controls.

The launcher needs Python 3 and OpenSCAD; both are already present here. On another computer, install OpenSCAD first. The helper's direct command also works locally:

```powershell
python run_local.py --svg "C:/path/to/artwork.svg"
```

## Automatic SVG preparation — recommended

For the Itachi and Monza reference investigation, see `DESIGN_REVIEW.md`. New
preparation controls and the dimension comparison tool are described below.

OpenSCAD imports SVG geometry but does not expose its dimensions, smallest feature or connected components to its scripting language. Consequently, direct MakerWorld mode requires the longer-axis selection and a declared minimum detail, and uses a conservative square envelope. **A pass in direct mode is not a complete SVG printability certificate.**

The included `prepare_svg.py` helper uses OpenSCAD itself to interpret the SVG, then:

- finds the actual drawn bounds and preserves the aspect ratio automatically;
- calculates a tighter outer-radius bound from the resulting polygons;
- embeds the artwork into a **single SCAD file** that can be uploaded to MakerWorld;
- checks the optical limits, exports the actual body mesh, and checks its edge closure and connectivity;
- adds short vertical ribs underneath disconnected stencil islands, rerenders and checks again;
- produces a checked body STL, cover STL and JSON report when successful.

From this project folder:

```powershell
python prepare_svg.py "C:/path/to/artwork.svg" --length 300 --diameter 100 --height 30 --detail-percent 2 --output output/my_lamp.scad
```

Python 3 and OpenSCAD are required. Default conversion uses the standard library; surface cleanup with `--minimum-web`, the design study and projection comparison also require NumPy and Pillow (already installed here). It finds the portable OpenSCAD in this project, an installed copy, or the executable given with `--openscad`. The distribution ZIP does not bundle OpenSCAD; [download it here](https://openscad.org/downloads.html) if needed.

The result is self-contained: upload `output/my_lamp.scad`. **Automatic** initially selects its embedded artwork. To replace it, select **Artwork_source = SVG file** and upload another SVG, or rerun the helper for automatic sizing and mesh checks. Dimension, source and support settings remain customizable. **Changing them after preflight invalidates the old mesh-check result; rerun the helper before printing the changed design.**

Try `examples/two_rings.svg` to exercise disconnected-island detection:

```powershell
python prepare_svg.py examples/two_rings.svg --output output/two_rings_lamp.scad
```

Use `--dark-silhouette` for filled SVG areas to remain dark within a circular lit field. By default, filled SVG areas become **light**, matching the luminous contour effect in the reference photograph. Convert strokes and text to paths, remove bitmap images and unwanted background rectangles, and inspect the imported result. OpenSCAD supports geometric SVG, not every SVG rendering effect; see its [SVG import documentation](https://files.openscad.org/documentation/manual/SVG_Import.html).

The helper deliberately does **not** invent a smallest-detail measurement: pointed corners mathematically taper to zero, and a minimum edge length is not a stroke width. `--detail-percent` is the detail you actually require. Automated bridges can change the appearance; inspect Projection after preparation.

## Reference preparation, fragile webs and housing shape

`Housing_shape = "Rectangle"` switches the body, cover, joints, standoff and wall
footprint together. `Rectangle_width` and `Rectangle_depth` are the two outer XY
dimensions. `Cylinder_height` remains the closed optical-module depth for either
shape. The wire pillar and its bore remain circular. Matching parts must share
the shape and both XY dimensions.

Use this preparation route for the supplied references:

```powershell
python prepare_svg.py itachi_example.svg --length 800 --diameter 80 --height 44 --wall-standoff 10 --minimum-web 0.6 --bridge-width 0.9 --automatic-bridges-only --output output/itachi_final.scad
python prepare_svg.py monza_example.svg --length 600 --diameter 80 --height 36 --wall-standoff 10 --minimum-web 0.6 --bridge-width 0.9 --automatic-bridges-only --output output/monza_final.scad
python prepare_svg.py monza_example.svg --shape Rectangle --rectangle-width 80 --rectangle-depth 80 --length 600 --height 36 --wall-standoff 10 --minimum-web 0.6 --automatic-bridges-only --output output/monza_rectangle_final.scad
```

These are **comparison prototypes**, using the existing 5% declared-detail
assumption and a 0.2 mm emitting area. Five percent is not a measurement of either
SVG's fine details. The new small-aperture screen reports features the 0.4 mm
filter flags; neither a broad optical pass nor mesh closure certifies that every
aperture will survive slicing with a 0.4 mm nozzle.

- `--automatic-bridges-only` starts without the twelve regular spokes. Mesh
  preflight adds vertical ribs only where needed and stops them inside each
  retained island. Projection includes the finite rib shadows.
- `--minimum-web 0.6` simplifies thin **opaque** slivers in developed inner-shell
  coordinates, sampled at about 0.06 mm. Corrections are projected back onto the
  wall and combined with the original vector light geometry. It does not thicken
  every stroke. Detached specks smaller than the width cubed (0.216 mm³ here)
  are removed through their projected footprints; larger islands receive ribs.
- `--bridge-width 0.9` is a starting point for approximately two extrusion lines
  with a 0.4 mm nozzle. Use your slicer's actual line-width settings. Simplification
  may erase dark detail; supports remove light. Check the comparison images.
- `--minimum-web 0` disables surface simplification. The default remains zero
  for compatibility. The native SCAD control uses a more conservative wall-space
  filter when no prepared surface stencil exists; its result is different.
- After changing geometry or artwork placement in a prepared surface file,
  rerun the helper. A stale prepared surface blocks Body/Print layout exports.
  Preview falls back to the native filter and warns; it is not a refreshed preflight.
- STL preflight welds export coincidences at 0.000001 mm and removes triangles
  collapsed by that rounding. This fixes export noise, not real disconnected parts.

Compare dimensions and actual artwork visibility:

```powershell
python compare_designs.py itachi_example.svg monza_example.svg --detail-percent 5 --output output/reference_study_5percent
python compare_designs.py itachi_example.svg monza_example.svg --detail-percent 2
python inspect_projection.py output/itachi_final.scad output/monza_final.scad output/monza_rectangle_final.scad --resolution 5000
```

The bounded study samples 4,320 combinations per reference: housing shape/size,
optical height, standoff, image length and XY placement. It counts the standoff
in **total depth**, and ranks `length / total depth / sqrt(footprint area) × visible
artwork fraction`, with an 85% visibility threshold. This is an explicit trade-off,
not a global optimum. Area retention does not know which parts of a character
are important. The 2% study demonstrates how much stricter detail requirements
can change the answer.

Projection inspection exports original artwork, housing-only clipping, the
modified footprint and an independent projection of the opaque STL. Its JSON
separates hidden artwork, removed light, added light and mesh/preview agreement.
Raster edge coverage affects the last metric, especially on narrow outlines.
Changing a generated source invalidates the stored mesh fingerprint.

## What the LED optimization means

The supported layout is a **concentric image surrounding the lamp**, as in the reference. The source is on the housing axis: **x = 0, y = 0**. This is the minimax position for a circular 360-degree field in the cylinder; the rectangle uses conservative on-axis bounds. The script analytically maximizes z subject to the upper collar, next module, pillar and source clearances. This is not an unrestricted optimizer for an asymmetric picture placed entirely beside the lamp.

The default demo gives:

| Quantity | Result |
|---|---:|
| Closed single-module depth | 30 mm |
| Body diameter | 100 mm |
| Emitting centre above module back | 24 mm |
| Printed pillar top | 21 mm |
| Ideal artwork length | 300 mm |
| Hidden central radius | 64.86 mm |
| Minimum local cut estimate, for declared 15 mm detail | 0.768 mm |
| Geometric source-blur estimate, 0.2 mm planar emitter | 0.425 mm |

The 0.2 mm emitter is an **optical assumption**, not a supplied or selected LED. Use the apparent emitting area seen through the side apertures; a domed lens may change it. A normal large or diffused LED may fail the sharpness limit. Zero source depth assumes a planar emitter parallel to the room wall. The LED must actually emit into the rays directed sideways and back toward the wall; a narrow forward-facing beam will not reproduce this preview.

The physical pillar prevents z=0, and the cover/next module prevents z=H. Manual-height mode reports incompatible positions instead of constructing a negative or colliding pedestal.

## Buildable versus worth printing

Two very different things used to share one verdict. They are now separate.

**Hard geometry** — a pillar wider than its cavity, a source below the floor, or an image that falls entirely inside the occluded centre — still refuses. There is nothing to build, and no warning rescues it. Diagnostics says *GENERATION NOT POSSIBLE: the geometry itself cannot be built*.

**Print quality** — the minimum cut width and the maximum blur — no longer blocks anything. The part builds, and Diagnostics reports *BUILDS — BELOW QUALITY LIMITS* in amber with the number that failed:

```
WARNING: this builds, but the smallest cut is 0.114 mm against a 0.4 mm minimum.
Blur is 2.76 mm against a 2 mm maximum. Fine detail will be lost or unprintable.
Try height 37 mm, shadow 363.4 mm.
```

`Quality_limits = "Refuse"` restores the old behaviour if you would rather be stopped. The helper carries the warning into its JSON report as `quality_warnings` and marks the validation string `BELOW QUALITY LIMITS`, so a preflight run tells you without refusing on your behalf.

This is a real choice, not a loosened check. A 0.114 mm slot will not print on a 0.4 mm nozzle — the detail closes up and you get a blob. The generator now assumes you would rather see the result and judge it yourself.

## Why some requests fail

“30 mm deep and a 1 m image” is not intrinsically impossible. It depends on diameter, feature size, source extent and image placement. Height alone cannot fix blur from a source that is too wide.

For example, with the **direct-SVG square envelope**, 100 mm diameter, 30 mm height, 1,000 mm length, 5% detail, 0.4 mm minimum cuts, 0.2 mm planar emitter and 2 mm maximum blur, the requirements fail. Diagnostics shows:

- an alternative shadow length at the same height;
- an alternative height at the same length, if one exists;
- a compromise minimizing the sum of the squared *relative* height and length changes.

The compromise searches larger heights in 1 mm steps up to the displayed limit (at most 300 mm), with a binary search for shadow length at each height. These are **nearest sampled alternatives under that stated metric**, not a claim of the globally closest dimensions. A conservative direct-import failure may disappear after the helper measures the actual SVG envelope. Suggested results do not establish brightness or physical printability.

For that example, the calculated compromise is **37 mm height / 371.9 mm shadow**. Keeping 30 mm height gives **287.9 mm shadow**. No tested height preserves the 1,000 mm request with the assumed emitter and 2 mm blur limit. Direct SVG mode's conservative bound also means a 300 mm request with the default 5% detail narrowly fails; start at **280 mm** or use the helper's tighter artwork measurement.

For the prepared **two-ring SVG**, the actual outer radius is smaller than the square bound. Requesting the same 1,000 mm length at 30 mm depth instead gives a **36 mm / 719.9 mm** compromise, **575.9 mm** at the original height, or **48 mm height** to retain the full 1,000 mm length under the selected optical limits. These are optical suggestions; rerun mesh preflight at the chosen dimensions.

## Cover, mounting and stacking

The wall is the XY plane at z=0; positive z points into the room. The wall-facing back has two keyholes with 7 mm head entries, 3.5 mm shaft slots and 5 mm upward slots. With the screw heads through the larger entries, slide the lamp downward to engage the narrow slots. Use a fastener and wall fixing appropriate to the actual wall and load.

The back is 4.5 mm thick, with a recessed keyed female socket. The front has the matching male tongue. The cover carries the same female socket. The default fit has **0.2 mm radial clearance** and **0.2 mm axial clearance**. This is a locating slip fit; use the three optional retaining screws when a positive hold is needed. The pilot-hole diameter is 2.1 mm; select and test compatible short screws. The fit and screw choice have not been physically tested.

The closed 30 mm assembly includes a 4.5 mm cover. Remove it and seat the next cylinder onto the tongue. Each added module increases the depth by **25.5 mm**. Two modules plus one final cover are 55.5 mm deep. Keep diameter, wall, joint and cover dimensions the same across a stack.

Generate each optical cylinder for its own **Module_index**: 0 at the wall, 1 next, and so forth. Every optical module needs its own LED at its own calculated height. The solid rear floor separates the modules. Moving a cylinder farther from the wall without regenerating it changes its projection. The central obscured area grows for farther modules; increasing the target length may be necessary. Stack preview displays the selected module's light and simplified lower-module envelopes, not a summed multi-LED lighting simulation.

The pillar contains a wire bore and terminates 3 mm below the nominal emitting centre. It is a generic mounting land, not a fit for an unspecified LED package. Attach an LED carrier whose **optical centre** has the stated offset. Larger boards, wiring, screw heads or electronics entering the optical rays can create additional shadows. The cover opens the electronics compartment; electrical design, heatsinking and thermal testing remain to be done with the actual hardware. Keep retaining holes occupied or plugged during optical tests.

## Wall standoff and the electronics compartment

`Wall_standoff` is the clear gap held between the room wall and this module's back. **0 is flush to the wall and reproduces the previous geometry exactly.** The gap is a closed compartment with the keyholes and cable route on its own back plate, whose thickness is `Standoff_back`.

- **Separate ring** (`Output = "Standoff"`) prints the gap as its own part, driving the same keyed tongue into the body's existing rear socket. Change the standoff without reprinting the optical body. Needs `Wall_standoff >= Standoff_back`.
- **Extended body** grows the body backwards instead: one part, no extra joint, but any change means reprinting the whole optical body.

Optically, a standoff is identical to mounting the module further into the room. Every mechanical plane translates with it, so the source rises by exactly the standoff and radial resolution improves in direct proportion. **It is not free.** `rho_dead = R*h/(h-A)` has both `h` and `A` rising together, so the hidden centre widens at a similar rate:

| Standoff | Source height | Cut estimate | Hidden radius |
|---:|---:|---:|---:|
| 0 mm | 24 mm | 0.768 mm | 64.9 mm |
| 20 mm | 44 mm | 1.408 mm | 118.9 mm |
| 50 mm | 74 mm | 2.368 mm | 200.0 mm |

So a standoff pays off only if the image grows with it. On the default 100 × 30 mm module, 50 mm of standoff **rejects** a 300 mm image — the 200 mm dead radius swallows it — while projecting 600 mm comfortably at a 1.184 mm cut estimate. Flush, the same lamp cannot reach 600 mm at all and manages 300 mm at 0.768 mm. Read the Diagnostics suggestion when it refuses.

From the helper:

```powershell
python prepare_svg.py artwork.svg --wall-standoff 25 --length 500 --output output/my_lamp.scad
```

The ring is mesh-checked alongside the body and cover and written to `<name>_standoff.stl`.

The compartment is a void with a cable route, nothing more. Electrical design, insulation, driver placement, clearances and heat inside it are yours to work out, and none of it has been tested.

## Bounding the light in dark silhouette

By default a dark silhouette sits in a lit disc that reaches the whole beam radius. **Light limit** replaces that disc with a band of chosen width hugging the shadow; past the band the wall goes dark again.

```
Artwork_mode          = "Dark silhouette";
Light_limit           = true;
Light_limit_shape     = "Same as shadow";   // or Circle, Rectangle
Light_limit_thickness = 25;                 // band width on the WALL, mm
```

- **Same as shadow** follows the outline, offset outwards by the thickness. Corners come out rounded at the band radius; a mitred outset would spike at acute corners into slivers too fine to print.
- **Circle** wraps the artwork's bounding circle. Note this is *larger* than the unlimited disc whenever the thickness exceeds `Dark_field_border`, so it is a way to size the lit disc explicitly rather than a way to shrink it.
- **Rectangle** wraps the artwork's true bounding box, and turns with `Artwork_rotation` so it stays tight. The real proportions can only be measured by the helper — a directly imported SVG falls back to a square, which for a tall or wide design lights a lot of empty wall. A rectangle also reaches furthest at its **corners**, so its optical envelope is `sqrt(2)` times a circle of the same half-width and it fails the feasibility test sooner.

From the helper:

```powershell
python prepare_svg.py artwork.svg --dark-silhouette --light-limit --light-limit-thickness 22 --light-limit-shape "Same as shadow" --output output/my_lamp.scad
```

### Which side of the artwork gets bounded

`offset()` moves every boundary at once, so on a closed outline — a circuit map, a monogram, any loop — it eats the enclosed interior as well as bounding the outside. The two sides are therefore separate switches:

```
Light_limit_outside = true;   // bound the light outside the artwork's silhouette
Light_limit_inside  = false;  // leave an enclosed interior fully lit
```

For a circuit map that combination is almost always what you want: a band tracing the outside of the track, and the whole infield lit. All four combinations are legal — `outside off / inside on` lights the entire beam except a ring inside the loop, which is the inverse effect.

**`Light_limit_inside` works on any artwork, with nothing else to configure.** Splitting the field needs to know which enclosed areas are interior. Prepared artwork carries a measured silhouette; a direct import — including every MakerWorld upload, where the helper cannot run — has none, so the interior is found by closing anything narrower than `Interior_span`.

`Interior_span = 0` means **automatic, and automatic is `Shadow_length`**. An enclosed area cannot be wider than the artwork that encloses it, so that is the one value which can never under-fill. Set a smaller number only if you want a tighter result: too small silently finds nothing, which is the failure this default exists to prevent. Diagnostics names the method — measured silhouette, or closed at N mm, marked *(automatic)* or *(set)* — so you never have to guess whether it took effect.

Artwork prepared by the helper needs none of that: it carries a measured **silhouette** and ignores `Interior_span` entirely. Telling a hole from the outside needs the artwork's **silhouette** — its outermost contours with every hole filled. Only the helper can work that out, by testing the nesting depth of each flattened contour, so it writes the silhouette into the file as separate geometry. A directly uploaded SVG has none, and the generator then applies one setting to both sides and echoes a note saying why. Use `--light-limit-inside off` / `--light-limit-outside off` on the helper.

### Two things the band does to you

**A thin band is a thin slot.** Unlike `Smallest_detail_percent`, which you declare, the band width is a feature the generator knows exactly, so it reports the slot the band opens in the shell and warns when that falls under `Minimum_cut_width`. Flush, 300 mm image:

| Band | Slot in the shell |
|---:|---|
| 5 mm | 0.240 mm — warned |
| 10 mm | 0.450 mm |
| 25 mm | 0.940 mm |
| 50 mm | 1.440 mm |

The minimum that clears a 0.4 mm slot is **8.8 mm** flush at 300 mm, **4.5 mm** with a 20 mm standoff, **10.9 mm** at 50 mm standoff / 600 mm — roughly 2–3% of image length, and a standoff nearly halves it. A band under the limit still builds, with the warning and the suggested width in Diagnostics, so you can preview something you know is too fine to print.

**A closed band strands whatever it encircles.** Every shape inside a loop of light is disconnected from the frame. This is not new — an unlimited dark silhouette does exactly the same, and the mesh preflight measures the identical component count either way — but it means `Support_bridges` or the helper's automatic ribs must stay on, and their lines will cross the band. A narrower band means shorter, less obtrusive bridges.

One behaviour worth watching: widening the band fuses the halos of nearby shapes into one. On `two_rings` at 160 mm, 3/8/20 mm bands keep four separate lit regions and a 40 mm band drops to three. Nothing warns about this — inspect Projection after changing the thickness.

## Print and physical test

Print the body with its flat rear face on the bed. The Cover output is already flipped with its solid face on the bed. Preview the sloped apertures and small underside socket bridges in your slicer; support requirements depend on the artwork and printer. Use opaque material and remove any support that blocks the optical tunnels. Print a joint-fit sample or check the first module before producing a stack.

First test at the calculated LED position on a wall in a dark room. Measure image length, adjust the source to the *emitting centre*, and compare detail sharpness. The preview is an ideal geometric light footprint, not a prediction of brightness, colour, scattering, lens effects or diffraction. The lamp inevitably hides the centre; no sidewall pattern can recover artwork behind its opaque body. Narrow connecting bridges also cast dark lines. Exact reproduction of an arbitrary, unmodified SVG is therefore not always physically possible with this architecture.

## Validation supplied

`output/validation.json` records checks on the default exported body and cover. Both have one connected surface component and every mesh edge belongs to two triangles. An independent perspective projection of the opaque STL triangles agrees with the analytic footprint with intersection-over-union **0.9864** at 2,000 × 2,000 pixels over a 360 mm wall field. Raster edge coverage accounts for much of the residual difference; this is not a physical optical test.

`tests/test_optics.py` checks inverse/forward ray mapping through both shell radii, finite-difference surface compression and source blur, stacked-module offsets, invalid source cases and a suggested dimension pair. `tests/verify_mesh_projection.py` additionally requires NumPy and Pillow. The helper's SVG test checks the exported stencil and adds two retaining bridges to the supplied two-ring example.

`tests/check_joint_fit.py` checks the actual body against a seated cover, a following body, and a seated standoff ring. All three intersections are empty after a 0.01 mm separation to exclude intended coplanar seating contact; the default parts have no positive-volume interference in this test.

`tests/test_light_limit.py` covers the light limit: that switching it off changes nothing, that a band lights less wall than the unlimited disc, that the band is exactly the artwork grown by the thickness minus the artwork, that each shape reaches as far as its geometry predicts and a rectangle's envelope uses its corner rather than its side, that the reported slot scales with the band and the suggested minimum really clears the limit, that a band too fine to print warns and still builds, and that the band strands exactly the same number of islands as the unlimited disc already did.

`tests/test_standoff.py` covers the standoff against real rendered meshes: that the source rises by exactly the standoff while the local height is untouched, that sharper detail and a wider hidden centre move together across 0/20/50 mm, that 600 mm is reachable at 50 mm of standoff and not at 0, that 50 mm of standoff correctly *refuses* a 300 mm image, that a zero standoff leaves the body identical, that the ring and both body modes are single closed solids sitting on the bed, and that the compartment is a vented shell rather than a sealed cavity. A ring thinner than its own back plate, and a Standoff export with no ring configured, are checked to fail loudly.

No physical lamp has been printed or illuminated yet. Mesh closure does not prove minimum ligament thickness, support-free printing, mechanical strength, thermal performance or an exact match to the photograph.
